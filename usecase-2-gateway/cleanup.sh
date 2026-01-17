#!/bin/bash

echo "Cleaning up Use Case 2..."
pkill -f "python3.*app.py" || true
echo "✓ Stopped Flask process"

# Read gateway ID
if [ -f "gateway_id.txt" ]; then
    GATEWAY_ID=$(cat gateway_id.txt)
    echo "Deleting AWS resources..."
    
    python3 << EOF
import boto3
client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
gateway_id = '$GATEWAY_ID'

# Delete targets
print(f'Deleting targets...')
try:
    targets = client.list_gateway_targets(gatewayIdentifier=gateway_id)
    for target in targets.get('items', []):
        target_id = target['targetId']
        try:
            client.delete_gateway_target(gatewayIdentifier=gateway_id, targetId=target_id)
            print(f'  ✓ Deleted {target_id}')
        except:
            pass
except:
    pass

# Delete credential providers
print(f'Deleting credential providers...')
try:
    providers = client.list_api_key_credential_providers()
    for provider in providers.get('items', []):
        if 'public-endpoints' in provider['displayName'].lower():
            try:
                client.delete_api_key_credential_provider(
                    credentialProviderIdentifier=provider['credentialProviderIdentifier']
                )
                print(f'  ✓ Deleted provider')
            except:
                pass
except:
    pass

# Delete gateway
print(f'Deleting gateway {gateway_id}...')
try:
    client.delete_gateway(gatewayIdentifier=gateway_id)
    print(f'  ✓ Deleted gateway')
except Exception as e:
    print(f'  ⚠️  {str(e)[:60]}')
EOF
    
    rm -f gateway_id.txt
fi

# Delete IAM role if it exists
echo "Checking IAM roles..."
python3 << EOF
import boto3
iam = boto3.client('iam')
role_name = 'GatewayServiceRole'
try:
    policies = iam.list_role_policies(RoleName=role_name)
    for policy_name in policies.get('PolicyNames', []):
        try:
            iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
        except:
            pass
    iam.delete_role(RoleName=role_name)
    print(f'✓ Deleted IAM role {role_name}')
except iam.exceptions.NoSuchEntityException:
    pass
except:
    pass
EOF

echo "✓ Cleanup complete"
