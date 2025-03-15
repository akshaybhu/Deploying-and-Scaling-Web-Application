import boto3

# Initialize Route 53 client
route53 = boto3.client('route53')

# Configuration Variables
HOSTED_ZONE_ID = 'ZXXXXXXXXXXXXX'  
LOAD_BALANCER_DNS = 'sk-frontend-microservices-alb-1114314583.us-east-1.elb.amazonaws.com'

def create_dns_record(domain_name, lb_dns):
    try:
        response = route53.change_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            ChangeBatch={
                'Comment': f'Creating DNS record for {domain_name}',
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain_name,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': 'Z35SXDOTRQ7X7K',  # AWS ALB Hosted Zone ID
                            'DNSName': f'dualstack.{lb_dns}',
                            'EvaluateTargetHealth': False
                        }
                    }
                }]
            }
        )
        print(f"DNS Record Created for {domain_name}")
    except Exception as e:
        print(f"Error creating DNS record: {e}")

if __name__ == '__main__':
    create_dns_record('frontend.your-domain.com', LOAD_BALANCER_DNS)
