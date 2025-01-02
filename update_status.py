import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

def update_status(task_id, new_status):
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }
    try:
        response = table.update_item(
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
        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(response['Attributes'])
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
        new_status = body.get('status')

        if not task_id or not new_status:
            return {
                'statusCode': 400,
                "headers": response_headers,
                'body': json.dumps("Missing 'id' or 'status'")
            }

        return update_status(task_id, new_status)
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error processing request: {str(e)}")
        }
