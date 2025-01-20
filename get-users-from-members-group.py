import json
import boto3

cognito_client = boto3.client('cognito-idp')
GROUP_NAME = "Team-Members"
USER_POOL_ID = "eu-west-1_xEP7m4WPV"

def get_users_from_group():
    """
    Retrieves a list of users from a specified Cognito user group.

    This function interacts with AWS Cognito using the boto3 client to fetch
    all users belonging to a specific group in a user pool. The users are returned
    as a list of dictionaries containing their username, email, and unique identifier (sub).

    Returns:
        list: A list of dictionaries where each dictionary contains:
            - 'Username' (str): The user's username.
            - 'Email' (str or None): The user's email address, if available.
            - 'Sub' (str or None): The user's unique identifier (sub), if available.

    Notes:
        - The function handles pagination to retrieve all users in the group.
        - In case of an error (e.g., network issues or invalid parameters), the function
          prints an error message and returns an empty list.
    """
    
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
            
            for user in response['Users']:
                user_info = {
                    'Username': user['Username'],
                    'Email': None,
                    'Sub': None
                }
                
                for attr in user['Attributes']:
                    if attr['Name'] == 'email':
                        user_info['Email'] = attr['Value']
                    elif attr['Name'] == 'sub':
                        user_info['Sub'] = attr['Value']
                
                users.append(user_info)
            
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
