import os
import boto3

aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key_id = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Initialize a session using your credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key,         # Replace with your AWS Access Key
    aws_secret_access_key=aws_secret_access_key_id,     # Replace with your AWS Secret Key
    region_name='us-east-1'                      # Specify the region you want to use
)

# Create an EC2 client
ec2 = session.client('ec2')

# Create a VPC with a specified CIDR block
response = ec2.create_vpc(
    CidrBlock='10.0.0.0/16',                    # Specify the CIDR block for your VPC
    TagSpecifications=[
        {
            'ResourceType': 'vpc',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'MyAPI-VPC'            # Optional: Add a name tag to the VPC
                }
            ]
        }
    ]
)

# Extract the VPC ID from the response
vpc_id = response['Vpc']['VpcId']
print(f"VPC Created with ID: {vpc_id}")