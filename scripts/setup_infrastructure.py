import boto3
import json

# Initialize Boto3 clients
ec2 = boto3.client('ec2')
autoscaling = boto3.client('autoscaling')
iam = boto3.client('iam')

# Step 1: Create VPC
def create_vpc():
    response = ec2.create_vpc(
        CidrBlock='10.0.0.0/16',
        TagSpecifications=[{
            'ResourceType': 'vpc',
            'Tags': [{'Key': 'Name', 'Value': 'MERN-VPC'}]
        }]
    )
    vpc_id = response['Vpc']['VpcId']
    print(f"VPC Created: {vpc_id}")
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
    return vpc_id

# Step 2: Create Subnets (Public and Private)
def create_subnets(vpc_id):
    public_subnet = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock='10.0.1.0/24',
        AvailabilityZone='us-east-1a',
        TagSpecifications=[{
            'ResourceType': 'subnet',
            'Tags': [{'Key': 'Name', 'Value': 'Public-Subnet'}]
        }]
    )
    private_subnet = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock='10.0.2.0/24',
        AvailabilityZone='us-east-1a',
        TagSpecifications=[{
            'ResourceType': 'subnet',
            'Tags': [{'Key': 'Name', 'Value': 'Private-Subnet'}]
        }]
    )
    print(f"Public Subnet: {public_subnet['Subnet']['SubnetId']}")
    print(f"Private Subnet: {private_subnet['Subnet']['SubnetId']}")
    return public_subnet['Subnet']['SubnetId'], private_subnet['Subnet']['SubnetId']

# Step 3: Create Security Groups
def create_security_groups(vpc_id):
    frontend_sg = ec2.create_security_group(
        GroupName='FrontendSG',
        Description='Frontend Security Group',
        VpcId=vpc_id
    )
    backend_sg = ec2.create_security_group(
        GroupName='BackendSG',
        Description='Backend Security Group',
        VpcId=vpc_id
    )
    print(f"Frontend SG: {frontend_sg['GroupId']}")
    print(f"Backend SG: {backend_sg['GroupId']}")
    return frontend_sg['GroupId'], backend_sg['GroupId']

# Step 4: Create IAM Role for EC2 Instances
def create_iam_role():
    role_name = 'EC2RoleForMERN'
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(assume_role_policy),
        Description='Role for EC2 instances in MERN ASG'
    )
    print(f"IAM Role Created: {response['Role']['RoleName']}")
    return response['Role']['RoleName']

# Step 5: Main Function to Call All Steps
def main():
    vpc_id = create_vpc()
    public_subnet, private_subnet = create_subnets(vpc_id)
    frontend_sg, backend_sg = create_security_groups(vpc_id)
    create_iam_role()

if __name__ == '__main__':
    main()
