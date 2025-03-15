import boto3

# Initialize clients
ec2 = boto3.client('ec2')
autoscaling = boto3.client('autoscaling')

# Configuration Variables
LAUNCH_TEMPLATE_NAME = 'sk-backend-microservices-launch-template'
ASG_NAME = 'sk-backend-microservices-asg'
TARGET_GROUP_ARN = 'arn:aws:elasticloadbalancing:us-east-1:975050024946:targetgroup/SkMernTravelMemory/ee0bb9a6a36066eb'
VPC_ZONE_IDENTIFIER = 'subnet-01874c4512136bd62'  
MIN_SIZE = 1
MAX_SIZE = 2
DESIRED_CAPACITY = 1

def create_auto_scaling_group():
    try:
        # Create the Auto Scaling Group
        response = autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=ASG_NAME,
            LaunchTemplate={
                'LaunchTemplateName': LAUNCH_TEMPLATE_NAME
            },
            MinSize=MIN_SIZE,
            MaxSize=MAX_SIZE,
            DesiredCapacity=DESIRED_CAPACITY,
            VPCZoneIdentifier=VPC_ZONE_IDENTIFIER,
            TargetGroupARNs=[
                TARGET_GROUP_ARN
            ],
            HealthCheckType='EC2',
            HealthCheckGracePeriod=500,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'sk-backend-microservices-instance',
                    'PropagateAtLaunch': True
                }
            ]
        )
        print(f"Auto Scaling Group Created: {ASG_NAME}")
    except Exception as e:
        print(f"Error creating Auto Scaling Group: {e}")

def create_scaling_policy():
    try:
        # Create Scaling Policy for CPU Utilization
        response = autoscaling.put_scaling_policy(
            AutoScalingGroupName=ASG_NAME,
            PolicyName='cpu-scale-out-policy',
            PolicyType='TargetTrackingScaling',
            TargetTrackingConfiguration={
                'PredefinedMetricSpecification': {
                    'PredefinedMetricType': 'ASGAverageCPUUtilization'
                },
                'TargetValue': 50.0  # Scale out if CPU usage > 50%
            }
        )
        print(f"Scaling Policy Created: {response['PolicyARN']}")
    except Exception as e:
        print(f"Error creating scaling policy: {e}")

if __name__ == '__main__':
    create_auto_scaling_group()
    create_scaling_policy()
