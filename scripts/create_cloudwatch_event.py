import boto3

# Initialize CloudWatch Events Client
events_client = boto3.client('events')

# Configuration Variables
RULE_NAME = 'sk-mern-daily-db-backup-rule'

def create_cloudwatch_event():
    try:
        response = events_client.put_rule(
            Name=RULE_NAME,
            ScheduleExpression='cron(0 0 * * ? *)',
            State='ENABLED',
            Description='Daily Database Backup'
        )
        print(f"CloudWatch Event Rule Created: {response['RuleArn']}")
        return response['RuleArn']
    except Exception as e:
        print(f"Error creating CloudWatch Event Rule: {e}")

def add_lambda_permission():
    try:
        lambda_client.add_permission(
            FunctionName='mern-db-backup-lambda',
            StatementId='AllowEventTrigger',
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=create_cloudwatch_event()
        )
        print("Permission Added for CloudWatch Event to Trigger Lambda.")
    except Exception as e:
        print(f"Error adding permission: {e}")

def create_event_target():
    try:
        events_client.put_targets(
            Rule=RULE_NAME,
            Targets=[
                {
                    'Id': '1',
                    'Arn': f"arn:aws:lambda:'us-east-1':975050024946:function:'mern-db-backup-lambda'"
                }
            ]
        )
        print("CloudWatch Event Target Created.")
    except Exception as e:
        print(f"Error creating Event Target: {e}")

if __name__ == '__main__':
    add_lambda_permission()
    create_event_target()
