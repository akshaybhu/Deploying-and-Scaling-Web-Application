import boto3
import json
import base64

# Initialize EC2 client
ec2 = boto3.client('ec2')

# Configuration Variables
LAUNCH_TEMPLATE_NAME = 'sk-backend-microservices-launch-template'
AMI_ID = 'ami-0f1d5364c75ad7f0f'  # Amazon Linux 2 AMI ID
INSTANCE_TYPE = 't2.micro'
SECURITY_GROUP_ID = 'sg-0ab76133c54e16736'  # Security group ID
KEY_PAIR_NAME = 'skJenkins.pem'  # Key pair name
ECR_REGION = 'us-east-1'  # Region
HELLO_SERVICE_IMAGE = '975050024946.dkr.ecr.us-east-1.amazonaws.com/mern-backend-helloservice-repo:latest'
PROFILE_SERVICE_IMAGE = '975050024946.dkr.ecr.us-east-1.amazonaws.com/mern-backend-profileservice-repo:latest'

def create_launch_template():
    try:
        # Define User Data script to set up Docker and pull images
        user_data_script = f"""#!/bin/bash
        sudo yum update -y
        sudo yum install -y docker
        sudo service docker start
        sudo usermod -a -G docker ec2-user
        sudo yum install -y amazon-linux-extras
        sudo amazon-linux-extras install docker
        sudo systemctl start docker
        sudo systemctl enable docker
        docker login -u AWS -p $(aws ecr get-login-password --region {ECR_REGION}) {HELLO_SERVICE_IMAGE.split('/')[0]}
        docker pull {HELLO_SERVICE_IMAGE}
        docker pull {PROFILE_SERVICE_IMAGE}
        docker run -d -p 3001:3001 {HELLO_SERVICE_IMAGE}
        docker run -d -p 3002:3002 {PROFILE_SERVICE_IMAGE}
        """

        # Encode User Data Script
        encoded_user_data = base64.b64encode(user_data_script.encode('utf-8')).decode('utf-8')

        # Pass the encoded User Data to the Launch Template
        response = ec2.create_launch_template(
            LaunchTemplateName=LAUNCH_TEMPLATE_NAME,
            LaunchTemplateData={
                'ImageId': AMI_ID,
                'InstanceType': INSTANCE_TYPE,
                'KeyName': KEY_PAIR_NAME,
                'SecurityGroupIds': [SECURITY_GROUP_ID],
                'UserData': encoded_user_data  # <- Corrected line
            }
        )
        print(f"Launch Template Created: {response['LaunchTemplate']['LaunchTemplateId']}")
    except Exception as e:
        print(f"Error creating launch template: {e}")

if __name__ == '__main__':
    create_launch_template()
