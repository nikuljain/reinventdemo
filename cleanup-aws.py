#!/usr/bin/env python3
"""
AWS Resource Cleanup Script
Removes AgentCore gateways and IAM roles from enterprise account
Run this before demo to ensure clean environment
"""

import boto3
import sys

def cleanup_resources():
    """Clean up AWS resources"""
    print('🧹 Cleaning up AWS resources in enterprise account...')
    print('=' * 60)
    
    # Initialize clients
    try:
        agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        iam = boto3.client('iam', region_name='us-east-1')
        
        # Test credentials
        sts = boto3.client('sts', region_name='us-east-1')
        identity = sts.get_caller_identity()
        print(f'\n✓ Authenticated as: {identity["Arn"]}')
        print(f'✓ Account: {identity["Account"]}')
    except Exception as e:
        print(f'\n❌ AWS authentication failed: {str(e)}')
        print('\nPlease refresh your AWS credentials and try again.')
        return False
    
    # 1. List and delete AgentCore gateways
    print('\n1. Checking AgentCore Gateways...')
    try:
        gateways = agentcore.list_gateways()
        if gateways.get('items'):
            for gw in gateways['items']:
                gateway_id = gw.get('gatewayId')
                gateway_name = gw.get('name', 'Unknown')
                print(f'   Found gateway: {gateway_name} ({gateway_id})')
                print(f'   → Deleting gateway...')
                # Use gatewayIdentifier parameter (not gatewayId)
                agentcore.delete_gateway(gatewayIdentifier=gateway_id)
                print(f'   ✓ Gateway deleted')
        else:
            print('   ✓ No gateways found (already clean)')
    except Exception as e:
        print(f'   ⚠️  Error with gateways: {str(e)}')
    
    # 2. Delete IAM roles
    print('\n2. Checking IAM Roles...')
    roles_to_delete = ['BedrockAgentCoreRole', 'BedrockAgentCoreGatewayRole']
    
    for role_name in roles_to_delete:
        try:
            # Check if role exists
            iam.get_role(RoleName=role_name)
            print(f'   Found role: {role_name}')
            
            # Detach all managed policies
            attached_policies = iam.list_attached_role_policies(RoleName=role_name)
            for policy in attached_policies['AttachedPolicies']:
                print(f'   → Detaching policy: {policy["PolicyName"]}')
                iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
            
            # Delete inline policies
            inline_policies = iam.list_role_policies(RoleName=role_name)
            for policy_name in inline_policies['PolicyNames']:
                print(f'   → Deleting inline policy: {policy_name}')
                iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
            
            # Delete the role
            print(f'   → Deleting role...')
            iam.delete_role(RoleName=role_name)
            print(f'   ✓ Role deleted')
        except iam.exceptions.NoSuchEntityException:
            print(f'   ✓ Role {role_name} not found (already clean)')
        except Exception as e:
            print(f'   ⚠️  Error deleting role {role_name}: {str(e)}')
    
    print('\n' + '=' * 60)
    print('✅ Cleanup complete! Environment is ready for fresh demo setup.')
    print('=' * 60)
    return True

if __name__ == '__main__':
    print('\nAWS Resource Cleanup Script')
    print('This will delete:')
    print('  • All AgentCore gateways')
    print('  • BedrockAgentCoreRole')
    print('  • BedrockAgentCoreGatewayRole')
    print()
    
    response = input('Do you want to proceed? (yes/no): ')
    if response.lower() in ['yes', 'y']:
        success = cleanup_resources()
        sys.exit(0 if success else 1)
    else:
        print('Cleanup cancelled.')
        sys.exit(0)
