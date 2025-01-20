import boto3
import json

sns = boto3.client('sns')
event_bridge = boto3.client('events')
GROUP_NAME = "Team-Members"
SNS_TOPIC_ARN = 'arn:aws:sns:eu-west-1:241533136420:notify-on-create-task'

def lambda_handler(event, context):
    """Send a reminder email for an upcoming task."""
    try:
        print('I am in the try block ooo')
        print(event)
        print(context)
        task = event
        
        message = (
            f"Reminder: You have an upcoming task deadline.\n\n"
            f"Title: {task['title']}\n"
            f"Due Date: {task['due_date']}\n\n"
            f"Please complete your task before the deadline."
        )
        subject = f"Task Reminder: {task['title']}"
        print(task['assigned_emails'])

        for email in task['assigned_emails']:
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
        
        rule_name = f"TaskReminder_{task['task_id']}"
        target_id = f"ReminderTarget_{task['task_id']}"
        print(f"Deleting EventBridge Rule: {rule_name}")

        event_bridge.remove_targets(
            Rule=rule_name,
            Ids=[target_id]
        )

        event_bridge.delete_rule(
            Name=rule_name
        )

    except Exception as e:
        print('I am in the catch block oo')
        print(f"An unhandled error occured: {e}")
