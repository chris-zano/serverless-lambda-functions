import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

def get_all_tasks():
    try:
        response = table.scan()
        return response['Items']
    except Exception as e:
        # Return a proper error response in case of failure
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error retrieving tasks: {str(e)}")
        }


def lambda_handler(event, context):
    try:
        # Get all tasks from the table
        tasks = get_all_tasks()
        
        # Check if the response is an error message or valid tasks
        if isinstance(tasks, dict) and 'statusCode' in tasks:
            return tasks  # If it's an error response from get_all_tasks

        print('Successfully fetched all tasks')

        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        }

        # Return the tasks in a proper format
        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(tasks)  # Ensure the response is JSON-encoded
        }
    except Exception as e:
        # Improved error handling with error message
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error fetching all tasks: {str(e)}")
        }
