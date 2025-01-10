import json
import boto3

cognito_client = boto3.client('cognito-idp')
GROUP_NAME = "Team-Members"
USER_POOL_ID = "eu-west-1_xEP7m4WPV"

def get_user_emails(user_ids):
    """Fetch email addresses for a list of user IDs from a specific Cognito group."""
    emails = []
    
    try:
        
        response = cognito_client.list_users_in_group(
            UserPoolId=USER_POOL_ID,
            GroupName=GROUP_NAME
        )

        
        for user in response['Users']:
            
            for attribute in user['Attributes']:
                if attribute['Name'] == 'sub' and attribute['Value'] in user_ids:
                    
                    email = next((attr['Value'] for attr in user['Attributes'] if attr['Name'] == 'email'), None)
                    if email:
                        emails.append(email)
                    break

        
        while 'NextToken' in response:
            response = cognito_client.list_users_in_group(
                UserPoolId=USER_POOL_ID,
                GroupName=GROUP_NAME,
                NextToken=response['NextToken']
            )
            
            for user in response['Users']:
                for attribute in user['Attributes']:
                    if attribute['Name'] == 'sub' and attribute['Value'] in user_ids:
                        email = next((attr['Value'] for attr in user['Attributes'] if attr['Name'] == 'email'), None)
                        if email:
                            emails.append(email)
                        break

    except Exception as e:
        print(f"Error fetching user emails: {e}")
        return []
    
    return emails