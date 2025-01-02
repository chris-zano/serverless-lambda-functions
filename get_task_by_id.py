import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

def get_task_by_id(task_id):
    try:
        # Query the table using the task_id
        response = table.get_item(Key={'id': task_id})
        
        # Check if the task exists
        if 'Item' in response:
            return response['Item']
        else:
            # Return error if task not found
            return {
                'statusCode': 404,
                'body': json.dumps(f"Task with id {task_id} not found")
            }
    except Exception as e:
        # Return a proper error response in case of failure
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error retrieving task: {str(e)}")
        }

def lambda_handler(event, context):
    try:
        # Retrieve task_id from the event path parameters
        task_id = event.get('queryStringParameters', {}).get('id')
        
        # Get task by id
        task = get_task_by_id(task_id)
        
        # Check if the response is an error message (in case task not found)
        if isinstance(task, dict) and 'statusCode' in task:
            return task  # If it's an error response from get_task_by_id

        print(f'Successfully fetched task with id: {task_id}')

        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        }

        # Return the task in a proper format
        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(task)  # Ensure the response is JSON-encoded
        }
    except Exception as e:
        # Improved error handling with error message
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error fetching task: {str(e)}")
        }
