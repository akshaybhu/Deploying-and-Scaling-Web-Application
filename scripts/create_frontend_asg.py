import boto3

# Initialize Auto Scaling Client
autoscaling = boto3.client('autoscaling')

# Configuration Variables
ASG_NAME = 'sk-frontend-microservices-asg'
LAUNCH_TEMPLATE_NAME = 'sk-frontend-microservices-launch-template'
VPC_SUBNETS = 'subnet-01874c4512136bd62' 
TARGET_GROUP_ARN = 'arn:aws:elasticloadbalancing:us-east-1:975050024946:targetgroup/SkMernTravelMemory/ee0bb9a6a36066eb'

def create_auto_scaling_group():
    try:
        # Create Auto Scaling Group
        response = autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=ASG_NAME,
            LaunchTemplate={
                'LaunchTemplateName': LAUNCH_TEMPLATE_NAME
            },
            MinSize=1,
            MaxSize=2,
            DesiredCapacity=1,
            VPCZoneIdentifier=VPC_SUBNETS,
            TargetGroupARNs=[TARGET_GROUP_ARN],
            HealthCheckType='ELB',
            HealthCheckGracePeriod=300
        )
        print(f"Auto Scaling Group Created: {ASG_NAME}")
    except Exception as e:
        print(f"Error creating Auto Scaling Group: {e}")

if __name__ == '__main__':
    create_auto_scaling_group()
