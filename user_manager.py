import boto3
import json
import uuid

# Initialize DynamoDB Resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:**********:**********:notify-on-create-task'

# Allowed roles
VALID_ROLES = {"admin", "member"}

def subscribe_user_to_sns(email):
    """Subscribes a user to the SNS topic."""
    try:
        response = sns.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=email
        )
        print(f"Subscription request sent for {email}. ARN: {response['SubscriptionArn']}")
    except Exception as e:
        print(f"Error subscribing {email} to SNS: {str(e)}")
        raise

def create_user(event, response_headers):
    """Create a new user."""
    try:
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('id')
        email = body.get('email')
        role = body.get('role')
        username = body.get('username')

        # Validate user_id, email, and role
        if not user_id or not email or not role:
            return {
                'statusCode': 400,
                "headers": response_headers,
                'body': json.dumps("User ID, email, and role are required.")
            }
        if role not in VALID_ROLES:
            return {
                'statusCode': 400,
                "headers": response_headers,
                'body': json.dumps(f"Invalid role. Allowed roles are: {', '.join(VALID_ROLES)}.")
            }

        # Add user to DynamoDB
        table.put_item(
            Item={
                'id': user_id,
                'email': email,
                'role': role,
                'username': username
            }
        )

        # Subscribe user to SNS topic
        subscribe_user_to_sns(email)


        return {
            'statusCode': 201,
            "headers": response_headers,
            'body': json.dumps({
                'message': 'User created successfully and subscription request sent.',
                'user': {'id': user_id, 'email': email, 'role': role}
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error creating user: {str(e)}")
        }

def get_user(event, response_headers):
    """Get a user by ID."""
    try:
        user_id = event.get('queryStringParameters', {}).get('id')

        if not user_id:
            return {
                'statusCode': 400,
                "headers": response_headers,
                'body': json.dumps("User ID is required.")
            }

        # Retrieve user from DynamoDB
        response = table.get_item(Key={'id': user_id})
        user = response.get('Item')

        if not user:
            return {
                'statusCode': 404,
                "headers": response_headers,
                'body': json.dumps(f"User with ID {user_id} not found.")
            }

        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(user)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error retrieving user: {str(e)}")
        }

def get_all_users(event, response_headers):
    """Get all users."""
    try:
        response = table.scan()
        users = response.get('Items', [])

        if not users:
            return {
                'statusCode': 404,
                "headers": response_headers,
                'body': json.dumps("No users found.")
            }

        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(users)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error retrieving users: {str(e)}")
        }

def lambda_handler(event, context):
    """Route Lambda calls to specific operations."""
    # Extract method and path from the request context
    http_method = event.get('requestContext', {}).get('http', {}).get('method')
    resource_path = event.get('requestContext', {}).get('http', {}).get('path')

    response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }

    # Route to specific operations based on method and path
    if http_method == 'POST' and resource_path == '/users':
        return create_user(event, response_headers)
    elif http_method == 'GET' and resource_path == '/users':
        query_params = event.get('queryStringParameters', {})
        if query_params and 'id' in query_params:
            return get_user(event, response_headers)
        else:
            return get_all_users(event, response_headers)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps("Method Not Allowed.")
        }

