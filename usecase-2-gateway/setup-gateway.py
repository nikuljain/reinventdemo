#!/usr/bin/env python3
"""Create AgentCore Gateway for Azure APIs"""
import boto3
import json

client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

GATEWAY_NAME = 'demo-azure-gateway'

print(f'Creating AgentCore Gateway: {GATEWAY_NAME}...')

try:
    response = client.create_gateway(
        gatewayName=GATEWAY_NAME,
        description='Demo gateway for Azure APIs (api1-4)'
    )
    gateway_id = response['gatewayId']
    print(f'✓ Gateway created: {gateway_id}')
    print(f'\nSave this Gateway ID: {gateway_id}')
    
    # Write to file for cleanup
    with open('gateway_id.txt', 'w') as f:
        f.write(gateway_id)
    print('✓ Saved to gateway_id.txt')
    
except Exception as e:
    if 'already exists' in str(e):
        # Find existing gateway
        gateways = client.list_gateways()
        for gw in gateways.get('items', []):
            if gw['name'] == GATEWAY_NAME:
                gateway_id = gw['gatewayId']
                print(f'✓ Gateway already exists: {gateway_id}')
                with open('gateway_id.txt', 'w') as f:
                    f.write(gateway_id)
                exit(0)
    
    print(f'❌ Error: {e}')
    exit(1)
