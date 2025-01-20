import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

def update_status(task_id, new_status, user):
    """
    Updates the status of a task in a DynamoDB table.

    This function updates the `status` attribute of a task and, if applicable, 
    appends the user's name to the `completed_by` attribute when the task is marked 
    as completed. It ensures that all updates are atomic and handles any errors 
    gracefully.

    Args:
        task_id (str): The unique identifier of the task to update.
        new_status (str): The new status to set for the task (e.g., "completed", "in progress").
        user (str): The user making the update, to be recorded when marking the task as completed.

    Returns:
        dict: A response object containing:
            - 'statusCode' (int): The HTTP status code (e.g., 200 for success, 404 for not found, 500 for errors).
            - 'headers' (dict): CORS headers for API Gateway.
            - 'body' (str): A JSON string with the updated task attributes or an error message.

    Notes:
        - If the task is not found, the function returns a 404 status code.
        - If the new status is "completed" and the user is not already listed in `completed_by`, 
          the user's name is appended to the `completed_by` attribute.
        - The function handles DynamoDB operations, including updates and error handling.
        - Ensures proper CORS headers for API Gateway integration.

    Raises:
        Exception: Catches all exceptions and returns a 500 status code with an error message.
    """

    print(user)
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }
    try:
        task = table.get_item(Key={'id': task_id}).get('Item')

        if not task:
            return {
                'statusCode': 404,
                "headers": response_headers,
                'body': json.dumps("Task not found")
            }
        
        if new_status == 'completed':
            assigned_users = task.get('assigned_to', [])
            completed_users = task.get('completed_by', [])
        
            if len(completed_users) < len(assigned_users):
                res = table.update_item(
                    Key={'id': task_id},
                    UpdateExpression="SET #completedByAttr = list_append(#completedByAttr, :completedByValue)",
                    ExpressionAttributeNames={
                        '#completedByAttr': 'completed_by'
                    },
                    ExpressionAttributeValues={
                        ':completedByValue': [user]
                    },
                    ReturnValues="ALL_NEW"
                )

                return {
                    'statusCode': 200,
                    "headers": response_headers,
                    'body': json.dumps(res['Attributes'])
                }

        res = table.update_item(
            Key={'id': task_id},
            UpdateExpression="SET #statusAttr = :statusValue",
            ExpressionAttributeNames={
                '#statusAttr': 'status'
            },
            ExpressionAttributeValues={
                ':statusValue': new_status 
            },
            ReturnValues="ALL_NEW"
        )

        if new_status == "completed":
            res = table.update_item(
                Key={'id': task_id},
                UpdateExpression="SET #completedByAttr = list_append(#completedByAttr, :completedByValue)",
                ExpressionAttributeNames={
                    '#completedByAttr': 'completed_by'
                },
                ExpressionAttributeValues={
                    ':completedByValue': [user]
                },
                ReturnValues="ALL_NEW"
            )
            
        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(res['Attributes'])
        }
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error updating status: {str(e)}")
        }

def lambda_handler(event, context):
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }

    try:
        body = json.loads(event.get('body', '{}'))
        task_id = body.get('id')
        user = body.get('user')
        new_status = body.get('status')

        if not task_id or not new_status:
            return {
                'statusCode': 400,
                "headers": response_headers,
                'body': json.dumps("Missing 'id' or 'status'")
            }

        return update_status(task_id, new_status, user)
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error processing request: {str(e)}")
        }
