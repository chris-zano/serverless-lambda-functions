import json
import boto3

cognito_client = boto3.client('cognito-idp')
GROUP_NAME = "Team-Members"
USER_POOL_ID = "eu-west-1_xEP7m4WPV"

def get_users_from_group():
    try:
        users = []
        pagination_token = None
        
        while True:
            if pagination_token:
                response = cognito_client.list_users_in_group(
                    UserPoolId=USER_POOL_ID,
                    GroupName=GROUP_NAME,
                    NextToken=pagination_token
                )
            else:
                response = cognito_client.list_users_in_group(
                    UserPoolId=USER_POOL_ID,
                    GroupName=GROUP_NAME
                )
            
            # Append users from the current page
            for user in response['Users']:
                print(user)
                users.append(user['Username'])
            
            # Check if there is a NextToken for more users
            pagination_token = response.get('NextToken')
            if not pagination_token:
                break
        return users
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def lambda_handler(event, context):
    users = get_users_from_group()
    print(users)
    return {
        'statusCode': 200,
        'body': json.dumps(users)
    }
