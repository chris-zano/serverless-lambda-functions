import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

def delete_task_by_id(task_id):
    try:
        # Check if the task exists before attempting to delete
        response = table.get_item(Key={'id': task_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Task with id {task_id} not found")
            }

        # Delete the task
        table.delete_item(Key={'id': task_id})
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Task with id {task_id} has been successfully deleted")
        }
    except Exception as e:
        # Return an error response in case of failure
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error deleting task: {str(e)}")
        }

def lambda_handler(event, context):
    try:
        # Retrieve task_id from the event path parameters
        task_id = event.get('queryStringParameters', {}).get('id')
        
        # Attempt to delete the task
        response = delete_task_by_id(task_id)
        
        print(f'Deletion response: {response}')
        
        # Set headers for CORS
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,DELETE",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        }
        
        # Return the response
        return {
            'statusCode': response['statusCode'],
            "headers": response_headers,
            'body': response['body']
        }
    except Exception as e:
        # Handle any unexpected exceptions
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error handling delete task request: {str(e)}")
        }
