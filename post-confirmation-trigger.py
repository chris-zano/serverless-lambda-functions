import json
import boto3

sns_client = boto3.client('sns')
cognito_client = boto3.client('cognito-idp')

SNS_TOPIC_ARN = "arn:aws:sns:eu-west-1:241533136420:notify-on-create-task"
GROUP_NAME = "Team-Members"
USER_POOL_ID = "eu-west-1_xEP7m4WPV"

def lambda_handler(event, context):
    """
    This handler is a post confirmation trigger attached to cognito
    After the user has been confirmed, this trigger retrieves the user information 
    from the event object, then subscribes the user to an sns topic, then adds the user
    to a group

    This trigger is for members. Admins are added manually on the aws console.
    Since this is a triggered function, it returns the event back to the trigger.
    """

    print(f"event: {event}")

    username = event['userName']
    email = event['request']['userAttributes']['email']
    user_id = event['request']['userAttributes']['sub']

    filter_policy = {
        'email': [email],
        'group': [GROUP_NAME]
    }

    try:
        # subscribe the user to sns topic
        # attach the filter policy as an attribute of the subscription
        # topic arn is the target topic notifications will be sent to
        # protocol is how notifications will be sent to the topic
        # endpoint is the target where the topic broadcast should hit
        sns_response = sns_client.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=email,
            Attributes={
                'FilterPolicy': json.dumps(filter_policy)
            }
        )

        print(f"SNS Subscription successful: {sns_response}")

        # add the new user to a group
        # should I use the username or the sub or the email ??
        cognito_response = cognito_client.admin_add_user_to_group(
            UserPoolId=USER_POOL_ID,
            Username=email,
            GroupName=GROUP_NAME
        )

        print(f"User added to group {GROUP_NAME}: {cognito_response}")
    except Exception as e:
        print(f"An error occured while subscribing the user and adding them to a group: {e}")

    return event