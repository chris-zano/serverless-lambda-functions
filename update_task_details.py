import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

# Function to update task details
def update_task_details(task_id, updated_task):
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }

    update_expression = "SET "
    expression_attribute_names = {}
    expression_attribute_values = {}

    for key, value in updated_task.items():
        if key != 'id':
            placeholder = f"#{key}Attr"
            update_expression += f"{placeholder} = :{key}Value, "
            expression_attribute_names[placeholder] = key
            expression_attribute_values[f":{key}Value"] = value

    # Remove the last comma from the update expression
    update_expression = update_expression.rstrip(", ")

    try:
        response = table.update_item(
            Key={'id': task_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
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
            'body': json.dumps(f"Error updating task: {str(e)}")
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
        updated_task = {
            'title': body.get('title'),
            'description': body.get('description', ''),
            'start_date': body.get('start_date'),
            'due_date': body.get('due_date'),
            'status': body.get('status'),
            'assigned_to': body.get('assigned_to', [])
        }

        if not task_id:
            return {
                'statusCode': 400,
                "headers": response_headers,
                'body': json.dumps("Missing 'id' in the request body")
            }

        return update_task_details(task_id, updated_task)

    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error processing request: {str(e)}")
        }
