import json
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
tasks_table = dynamodb.Table('Tasks')

cognito_client = boto3.client('cognito-idp')
GROUP_NAME = "************"
USER_POOL_ID = "************"

eventbridge = boto3.client('events')
sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:************:************:notify-on-create-task'

ADMIN_EMAIL = "************"

def schedule_deadline_reminder(task_id, title, due_date, assigned_emails):
    """Schedule a reminder for task deadline."""
    
    lambda_client = boto3.client('lambda')
    eventbridge = boto3.client('events')
    
    reminder_time = datetime.strptime(due_date, '%Y-%m-%d') - timedelta(days=1)
    
    reminder_time_hour = reminder_time.replace(hour=8, minute=0, second=0, microsecond=0)
    reminder_time_iso = reminder_time_hour.strftime('%Y-%m-%dT%H:%M:%S') + "Z"
    
    rule_name = f"TaskReminder_{task_id}"
 
    cron_expression = f"cron(0 8 {reminder_time_hour.day} {reminder_time_hour.month} ? {reminder_time_hour.year})"
    
    eventbridge.put_rule(
        Name=rule_name,
        ScheduleExpression=cron_expression,
        State='ENABLED'
    )

    eventbridge.put_targets(
        Rule=rule_name,
        Targets=[
            {
                'Id': f"ReminderTarget_{task_id}",
                'Arn': 'arn:aws:lambda:************:************:function:sendTaskReminder',
                'Input': json.dumps({
                    'task_id': task_id,
                    'title': title,
                    'due_date': due_date,
                    'assigned_emails': assigned_emails
                })
            }
        ]
    )

    print(f"Reminder scheduled for {reminder_time_iso}")


def create_task_id():
    """Generates a new task ID in the format T_XXXX."""
    import random
    task_id = "T_" + str(random.randint(1000, 9999))
    return task_id


def send_task_notification(emails, admin_email, title, start_date, due_date):
    """Sends notifications via SNS to specific users based on filter policy."""
    print(emails, admin_email, title, start_date, due_date)

    message = (
        f"You have been assigned a new task:\n\n"
        f"Title: {title}\n"
        f"Start Date: {start_date}\n"
        f"Due Date: {due_date}\n\n"
        f"Please check the system for more details."
    )
    subject = f"New Task Assigned: {title}"

    for email in emails:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message,
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': email
                },
                'group': {
                    'DataType': 'String',
                    'StringValue': GROUP_NAME
                }
            }
        )


def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))

    task_id = create_task_id()
    task_item = {
        'id': task_id,
        'title': body['title'],
        'description': body.get('description', ''),
        'files': [],
        'status': 'not-started',
        'start_date': body['startDate'],
        'due_date': body['dueDate'],
        'assigned_to': body['assigned_to'],
        'completed_by': []
    }

    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }

    try:
        tasks_table.put_item(Item=task_item)
        
        assigned_users = body['assigned_to']
        assigned_users_emails = [user['email'] for user in assigned_users]

        if assigned_users_emails:
            send_task_notification(
                emails=assigned_users_emails,
                admin_email=ADMIN_EMAIL,
                title=body['title'],
                start_date=body['startDate'],
                due_date=body['dueDate']
            )

        schedule_deadline_reminder(task_id, body['title'], body['dueDate'], assigned_users_emails)

        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(f"Task {task_id} added successfully and notifications sent!")
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error adding task or sending notifications: {str(e)}")
        }
