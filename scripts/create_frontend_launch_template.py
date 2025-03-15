import boto3
import json
import base64

# Initialize EC2 client
ec2 = boto3.client('ec2')

# Configuration Variables
LAUNCH_TEMPLATE_NAME = 'sk-frontend-microservices-launch-template'
AMI_ID = 'ami-0f1d5364c75ad7f0f'  # Amazon Linux 2 AMI
INSTANCE_TYPE = 't2.micro'
SECURITY_GROUP_ID = 'sg-0ab76133c54e16736'  # Replace with your security group
KEY_PAIR_NAME = 'skJenkins'  # Replace with your EC2 key pair name
ECR_REGION = 'us-east-1'
FRONTEND_IMAGE = '975050024946.dkr.ecr.us-east-1.amazonaws.com/mern-frontend-repo:latest'

def create_launch_template():
    try:
        # User Data Script for Frontend Deployment
        user_data_script = f"""#!/bin/bash
        yum update -y
        yum install -y docker
        service docker start
        usermod -a -G docker ec2-user
        yum install -y amazon-linux-extras
        amazon-linux-extras install docker
        systemctl start docker
        systemctl enable docker
        docker login -u AWS -p $(aws ecr get-login-password --region {ECR_REGION}) {FRONTEND_IMAGE.split('/')[0]}
        docker pull {FRONTEND_IMAGE}
        docker run -d -p 80:3000 {FRONTEND_IMAGE}
        """

        # Encode User Data Script
        encoded_user_data = base64.b64encode(user_data_script.encode('utf-8')).decode('utf-8')

        # Create Launch Template
        response = ec2.create_launch_template(
            LaunchTemplateName=LAUNCH_TEMPLATE_NAME,
            LaunchTemplateData={
                'ImageId': AMI_ID,
                'InstanceType': INSTANCE_TYPE,
                'KeyName': KEY_PAIR_NAME,
                'SecurityGroupIds': [SECURITY_GROUP_ID],
                'UserData': encoded_user_data,
                'IamInstanceProfile': {
                    'Name': 'ECR-Access-Role'  # Replace with your IAM Role Name
                }
            }
        )
        print(f"Launch Template Created: {response['LaunchTemplate']['LaunchTemplateId']}")
    except Exception as e:
        print(f"Error creating launch template: {e}")

if __name__ == '__main__':
    create_launch_template()
