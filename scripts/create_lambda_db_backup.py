import boto3
import json

# Initialize Boto3 Clients
lambda_client = boto3.client('lambda')
iam = boto3.client('iam')

# Configuration Variables
LAMBDA_FUNCTION_NAME = 'mern-db-backup-lambda'
ROLE_NAME = 'Lambda-Backup-Role'
S3_BUCKET_NAME = 'skbatch8'
MONGODB_URI = 'mongodb+srv://syamalakadimi:wtxdlQgzhnW2ismd@clusterd8.3ylu1.mongodb.net/merndb?retryWrites=true&w=majority'
REGION = 'us-east-1'

def create_lambda_role():
    try:
        # Create IAM Role for Lambda
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        role_response = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )

        # Attach Policies to Role
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
        )
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/CloudWatchLogsFullAccess'
        )

        print(f"Role Created: {role_response['Role']['Arn']}")
        return role_response['Role']['Arn']

    except Exception as e:
        print(f"Error creating IAM Role: {e}")

def create_lambda_function(role_arn):
    try:
        # Lambda Function Code
        lambda_code = """
import boto3
import datetime
import subprocess

S3_BUCKET = 'mern-db-backup-bucket'
MONGODB_URI = 'mongodb+srv://syamalakadimi:wtxdlQgzhnW2ismd@clusterd8.3ylu1.mongodb.net/merndb?retryWrites=true&w=majority'

def lambda_handler(event, context):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_filename = f"backup-{timestamp}.gz"
    subprocess.run([
        'mongodump',
        f'--uri={MONGODB_URI}',
        '--archive=/tmp/dump.gz',
        '--gzip'
    ], check=True)
    
    s3 = boto3.client('s3')
    with open('/tmp/dump.gz', 'rb') as data:
        s3.upload_fileobj(data, S3_BUCKET, backup_filename)
    
    return {
        'statusCode': 200,
        'body': f"Backup {backup_filename} uploaded successfully."
    }
        """

        # Create Lambda Function
        response = lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime='python3.9',
            Role=role_arn,
            Handler='index.lambda_handler',
            Code={
                'ZipFile': lambda_code.encode('utf-8')
            },
            Timeout=300,
            MemorySize=128,
            Publish=True
        )
        print(f"Lambda Function Created: {response['FunctionArn']}")

    except Exception as e:
        print(f"Error creating Lambda Function: {e}")

if __name__ == '__main__':
    role_arn = create_lambda_role()
    create_lambda_function(role_arn)
