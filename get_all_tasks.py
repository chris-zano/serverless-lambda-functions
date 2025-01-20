import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

def get_all_tasks():
    """
    Retrieves all tasks from the DynamoDB table.

    This function performs a full table scan on the DynamoDB table to fetch all tasks.
    It returns a list of all items in the table or an error response in case of failure.

    Returns:
        list: A list of task items if the operation is successful.
        dict: An error response object containing:
            - 'statusCode' (int): HTTP status code (500 for errors).
            - 'body' (str): A JSON string with an error message.

    Notes:
        - Uses the `scan` operation to fetch all items from the 'Tasks' table.
        - Handles exceptions and returns an error response in case of unexpected issues.
    """

    try:
        response = table.scan()
        return response['Items']
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error retrieving tasks: {str(e)}")
        }


def lambda_handler(event, context):
    try:
        tasks = get_all_tasks()
        
        if isinstance(tasks, dict) and 'statusCode' in tasks:
            return tasks
        print('Successfully fetched all tasks')

        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        }

        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(tasks)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error fetching all tasks: {str(e)}")
        }
