import boto3
import json

sns = boto3.client('sns')

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

        # Send email via SNS
        sns.publish(
            TopicArn='arn:aws:sns:**********:**********:notify-on-create-task',
            Subject=subject,
            Message=message
        )
    except Exception as e:
        print('I am in the catch block oo')
        print(f"An unhandled error occured: {e}")
