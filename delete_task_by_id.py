import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

def delete_task_by_id(task_id):
    """
    Deletes a task from the DynamoDB table by its unique ID.

    This function retrieves a task by its `id` from the DynamoDB table. If the task exists, 
    it deletes the task and returns a success message. If the task does not exist, 
    it returns a 404 status with an appropriate message.

    Args:
        task_id (str): The unique identifier of the task to be deleted.

    Returns:
        dict: A response object containing:
            - 'statusCode' (int): The HTTP status code (e.g., 200 for success, 404 for not found, 500 for errors).
            - 'body' (str): A JSON string with a success message or error details.

    Notes:
        - The function checks if the task exists before attempting deletion.
        - Catches exceptions and returns a 500 status code with an error message in case of unexpected errors.
        - This function interacts with a DynamoDB table named 'Tasks'.

    Raises:
        Exception: Handles all exceptions gracefully by returning a 500 status code.
    """

    try:
        response = table.get_item(Key={'id': task_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Task with id {task_id} not found")
            }

        table.delete_item(Key={'id': task_id})
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Task with id {task_id} has been successfully deleted")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error deleting task: {str(e)}")
        }

def lambda_handler(event, context):
    try:
        task_id = event.get('queryStringParameters', {}).get('id')
        
        response = delete_task_by_id(task_id)
        
        print(f'Deletion response: {response}')
        
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,DELETE",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        }
        
        return {
            'statusCode': response['statusCode'],
            "headers": response_headers,
            'body': response['body']
        }
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error handling delete task request: {str(e)}")
        }
