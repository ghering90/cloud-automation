import os
import boto3

aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key_id = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Initialize a session
session = boto3.Session(
    aws_access_key_id=aws_access_key,       
    aws_secret_access_key=aws_secret_access_key_id,    
    region_name='us-east-1'                      
)

# Create an EC2 client
ec2 = session.client('ec2')

# Create a VPC 
response = ec2.create_vpc(
    CidrBlock='10.0.0.0/16',                    
    TagSpecifications=[
        {
            'ResourceType': 'vpc',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'MyAPI-VPC' 
                }
            ]
        }
    ]
)

# Extract the VPC ID from the response
vpc_id = response['Vpc']['VpcId']
print(f"VPC Created with ID: {vpc_id}")

# Enable DNS support and hostnames
ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})

# Create an Internet Gateway and attach it to the VPC (required for public subnet)
igw_response = ec2.create_internet_gateway()
igw_id = igw_response['InternetGateway']['InternetGatewayId']
ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
print(f"Internet Gateway Created and Attached with ID: {igw_id}")

# Create a Public Subnet
public_subnet_response = ec2.create_subnet(
    VpcId=vpc_id,
    CidrBlock='10.0.1.0/24',
    AvailabilityZone='us-east-1a',  
    TagSpecifications=[
        {
            'ResourceType': 'subnet',
            'Tags': [{'Key': 'Name', 'Value': 'PublicSubnet'}]
        }
    ]
)

public_subnet_id = public_subnet_response['Subnet']['SubnetId']
print(f"Public Subnet Created with ID: {public_subnet_id}")


# Modify the subnet to enable auto-assign public IPs
ec2.modify_subnet_attribute(SubnetId=public_subnet_id, MapPublicIpOnLaunch={'Value': True})


# Create a Private Subnet
private_subnet_response = ec2.create_subnet(
    VpcId=vpc_id,
    CidrBlock='10.0.2.0/24',
    AvailabilityZone='us-east-1a',  # Optional: Specify availability zone
    TagSpecifications=[
        {
            'ResourceType': 'subnet',
            'Tags': [{'Key': 'Name', 'Value': 'PrivateSubnet'}]
        }
    ]
)

private_subnet_id = private_subnet_response['Subnet']['SubnetId']
print(f"Private Subnet Created with ID: {private_subnet_id}")

# Create a Route Table for the Public Subnet and associate it with the Internet Gateway
public_route_table_response = ec2.create_route_table(VpcId=vpc_id)
public_route_table_id = public_route_table_response['RouteTable']['RouteTableId']


# Add a route to the Internet Gateway in the public route table
ec2.create_route(
    RouteTableId=public_route_table_id,
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=igw_id
)

# Associate the public route table with the public subnet
ec2.associate_route_table(RouteTableId=public_route_table_id, SubnetId=public_subnet_id)
print(f"Public Route Table Created and Associated with ID: {public_route_table_id}")

# Create a Route Table for the Private Subnet (Private subnets use NAT Gateway or VPN for internet access)
private_route_table_response = ec2.create_route_table(VpcId=vpc_id)
private_route_table_id = private_route_table_response['RouteTable']['RouteTableId']

# Associate the private route table with the private subnet
ec2.associate_route_table(RouteTableId=private_route_table_id, SubnetId=private_subnet_id)
print(f"Private Route Table Created and Associated with ID: {private_route_table_id}")

print("VPC, public subnet, and private subnet configuration complete.")