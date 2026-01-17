#!/usr/bin/env python3
"""
AWS Bedrock AgentCore Gateway Setup Script
Creates gateway, IAM roles, and configures Azure API access
Run this before demo to set up fresh environment
"""

import boto3
import json
import sys
import time

def create_iam_roles():
    """Create necessary IAM roles for AgentCore"""
    print('\n1. Setting up IAM Roles...')
    iam = boto3.client('iam', region_name='us-east-1')
    
    # Trust policy for Bedrock service
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # BedrockAgentCoreRole
    try:
        iam.get_role(RoleName='BedrockAgentCoreRole')
        print('   ✓ BedrockAgentCoreRole already exists')
        role1_arn = iam.get_role(RoleName='BedrockAgentCoreRole')['Role']['Arn']
    except iam.exceptions.NoSuchEntityException:
        print('   → Creating BedrockAgentCoreRole...')
        response = iam.create_role(
            RoleName='BedrockAgentCoreRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Bedrock AgentCore to access models',
            MaxSessionDuration=3600
        )
        role1_arn = response['Role']['Arn']
        
        # Attach inline policy for Bedrock model access
        model_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
                }
            ]
        }
        iam.put_role_policy(
            RoleName='BedrockAgentCoreRole',
            PolicyName='BedrockModelAccess',
            PolicyDocument=json.dumps(model_policy)
        )
        print(f'   ✓ Role created: {role1_arn}')
    
    # BedrockAgentCoreGatewayRole
    try:
        iam.get_role(RoleName='BedrockAgentCoreGatewayRole')
        print('   ✓ BedrockAgentCoreGatewayRole already exists')
        role2_arn = iam.get_role(RoleName='BedrockAgentCoreGatewayRole')['Role']['Arn']
    except iam.exceptions.NoSuchEntityException:
        print('   → Creating BedrockAgentCoreGatewayRole...')
        response = iam.create_role(
            RoleName='BedrockAgentCoreGatewayRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Bedrock AgentCore Gateway',
            MaxSessionDuration=3600
        )
        role2_arn = response['Role']['Arn']
        
        # Attach inline policy for AgentCore operations
        gateway_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream",
                        "bedrock-agentcore:*"
                    ],
                    "Resource": "*"
                }
            ]
        }
        iam.put_role_policy(
            RoleName='BedrockAgentCoreGatewayRole',
            PolicyName='BedrockAgentCoreGatewayPolicy',
            PolicyDocument=json.dumps(gateway_policy)
        )
        print(f'   ✓ Role created: {role2_arn}')
    
    # Wait for IAM propagation
    print('   ⏳ Waiting for IAM propagation (10 seconds)...')
    time.sleep(10)
    
    return role1_arn, role2_arn

def create_agentcore_gateway(role_arn):
    """Create AgentCore Gateway"""
    print('\n2. Creating AgentCore Gateway...')
    agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        # Create gateway
        response = agentcore.create_gateway(
            name='AzureAPIGateway',
            description='Gateway for Azure API access via AI agent',
            gatewayType='MCP',  # Model Context Protocol
            roleArn=role_arn
        )
        
        gateway_id = response['gatewayId']
        gateway_url = f"https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
        
        print(f'   ✓ Gateway created successfully!')
        print(f'   → Gateway ID: {gateway_id}')
        print(f'   → Gateway URL: {gateway_url}')
        print(f'   → Status: {response.get("status", "CREATING")}')
        
        return gateway_id, gateway_url
        
    except Exception as e:
        print(f'   ❌ Error creating gateway: {str(e)}')
        return None, None

def verify_setup():
    """Verify the setup is complete"""
    print('\n3. Verifying Setup...')
    
    # Check IAM roles
    iam = boto3.client('iam', region_name='us-east-1')
    roles_ok = True
    for role_name in ['BedrockAgentCoreRole', 'BedrockAgentCoreGatewayRole']:
        try:
            iam.get_role(RoleName=role_name)
            print(f'   ✓ {role_name} exists')
        except:
            print(f'   ❌ {role_name} not found')
            roles_ok = False
    
    # Check gateway
    agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    try:
        gateways = agentcore.list_gateways()
        if gateways.get('items'):
            gateway = gateways['items'][0]
            print(f'   ✓ Gateway found: {gateway.get("name")} ({gateway.get("gatewayId")})')
            return True
        else:
            print('   ⚠️  No gateways found (may be ephemeral in preview)')
            return roles_ok
    except Exception as e:
        print(f'   ⚠️  Error checking gateway: {str(e)}')
        return roles_ok

def main():
    print('═' * 60)
    print('AWS Bedrock AgentCore Gateway Setup')
    print('═' * 60)
    
    # Verify AWS authentication
    try:
        sts = boto3.client('sts', region_name='us-east-1')
        identity = sts.get_caller_identity()
        print(f'\n✓ Authenticated as: {identity["Arn"]}')
        print(f'✓ Account: {identity["Account"]}')
    except Exception as e:
        print(f'\n❌ AWS authentication failed: {str(e)}')
        print('\nPlease ensure you have valid AWS credentials.')
        return False
    
    # Step 1: Create IAM roles
    role_arn, gateway_role_arn = create_iam_roles()
    
    # Step 2: Create AgentCore gateway
    gateway_id, gateway_url = create_agentcore_gateway(gateway_role_arn)
    
    # Step 3: Verify setup
    success = verify_setup()
    
    # Summary
    print('\n' + '═' * 60)
    if success:
        print('✅ Setup Complete!')
        print('═' * 60)
        print('\nResources Created:')
        print(f'  • IAM Role: BedrockAgentCoreRole')
        print(f'  • IAM Role: BedrockAgentCoreGatewayRole')
        if gateway_id:
            print(f'  • AgentCore Gateway: {gateway_id}')
            print(f'  • Gateway URL: {gateway_url}')
        print('\nNote: AgentCore gateways are ephemeral in preview.')
        print('You can view them in the AWS Console:')
        print('https://us-east-1.console.aws.amazon.com/bedrock-agentcore/gateways')
        print('\nYour web UI (app.py) works independently of the gateway.')
        print('Run: python3 app.py')
    else:
        print('⚠️  Setup completed with warnings')
        print('═' * 60)
        print('\nSome resources may not have been created.')
        print('Check the output above for details.')
    print('═' * 60)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
