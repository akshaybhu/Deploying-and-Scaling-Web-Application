import boto3
import json

# Initialize clients
ec2 = boto3.client('ec2')
elbv2 = boto3.client('elbv2')

# Configuration Variables
VPC_ID = 'vpc-09f02049d6176fe30'  
SUBNETS = ['subnet-01874c4512136bd62', 'subnet-0821f7ef16566e9a4']  
SECURITY_GROUP_ID = 'sg-0ab76133c54e16736' 

LOAD_BALANCER_NAME = 'sk-backend-microservices-alb'
HELLO_TARGET_GROUP_NAME = 'helloservice-target-group'
PROFILE_TARGET_GROUP_NAME = 'profileservice-target-group'

def create_load_balancer():
    try:
        # Create Application Load Balancer
        response = elbv2.create_load_balancer(
            Name=LOAD_BALANCER_NAME,
            Subnets=SUBNETS,
            SecurityGroups=[SECURITY_GROUP_ID],
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )
        
        lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
        dns_name = response['LoadBalancers'][0]['DNSName']
        print(f"Load Balancer Created: {dns_name}")
        
        return lb_arn, dns_name
    except Exception as e:
        print(f"Error creating Load Balancer: {e}")

def create_target_groups():
    try:
        # Create Target Group for HelloService
        hello_response = elbv2.create_target_group(
            Name=HELLO_TARGET_GROUP_NAME,
            Protocol='HTTP',
            Port=3001,
            VpcId=VPC_ID,
            TargetType='instance',
            HealthCheckProtocol='HTTP',
            HealthCheckPort='3001',
            HealthCheckPath='/health',
            HealthCheckIntervalSeconds=30,
            HealthCheckTimeoutSeconds=5,
            HealthyThresholdCount=2,
            UnhealthyThresholdCount=2
        )
        
        hello_tg_arn = hello_response['TargetGroups'][0]['TargetGroupArn']
        print(f"HelloService Target Group ARN: {hello_tg_arn}")

        # Create Target Group for ProfileService
        profile_response = elbv2.create_target_group(
            Name=PROFILE_TARGET_GROUP_NAME,
            Protocol='HTTP',
            Port=3002,
            VpcId=VPC_ID,
            TargetType='instance',
            HealthCheckProtocol='HTTP',
            HealthCheckPort='3002',
            HealthCheckPath='/health',
            HealthCheckIntervalSeconds=30,
            HealthCheckTimeoutSeconds=5,
            HealthyThresholdCount=2,
            UnhealthyThresholdCount=2
        )
        
        profile_tg_arn = profile_response['TargetGroups'][0]['TargetGroupArn']
        print(f"ProfileService Target Group ARN: {profile_tg_arn}")
        
        return hello_tg_arn, profile_tg_arn
    except Exception as e:
        print(f"Error creating Target Groups: {e}")

def create_listeners(lb_arn, hello_tg_arn, profile_tg_arn):
    try:
        # Create HTTP Listener
        response = elbv2.create_listener(
            LoadBalancerArn=lb_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[{
                'Type': 'fixed-response',
                'FixedResponseConfig': {
                    'MessageBody': 'Not Found',
                    'StatusCode': '404',
                    'ContentType': 'text/plain'
                }
            }]
        )
        listener_arn = response['Listeners'][0]['ListenerArn']
        print(f"Listener Created: {listener_arn}")
        
        # Create Listener Rules for Routing
        elbv2.create_rule(
            ListenerArn=listener_arn,
            Priority=10,
            Conditions=[{
                'Field': 'host-header',
                'Values': ['helloservice.your-domain.com']
            }],
            Actions=[{
                'Type': 'forward',
                'TargetGroupArn': hello_tg_arn
            }]
        )
        
        elbv2.create_rule(
            ListenerArn=listener_arn,
            Priority=20,
            Conditions=[{
                'Field': 'host-header',
                'Values': ['profileservice.your-domain.com']
            }],
            Actions=[{
                'Type': 'forward',
                'TargetGroupArn': profile_tg_arn
            }]
        )
        
        print("Listener rules created for HelloService and ProfileService.")
        
    except Exception as e:
        print(f"Error creating Listener: {e}")

if __name__ == '__main__':
    lb_arn, dns_name = create_load_balancer()
    hello_tg_arn, profile_tg_arn = create_target_groups()
    create_listeners(lb_arn, hello_tg_arn, profile_tg_arn)
