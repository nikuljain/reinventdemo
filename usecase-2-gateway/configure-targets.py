#!/usr/bin/env python3
"""Register MCP targets on the gateway"""
import boto3
import json

client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Read gateway ID from file
try:
    with open('gateway_id.txt', 'r') as f:
        gateway_id = f.read().strip()
except:
    print('❌ gateway_id.txt not found. Run setup-gateway.py first.')
    exit(1)

AZURE_BASE_URL = 'https://api2.us-insurancesre-dev.azure.lnrsg.io'
CREDENTIAL_PROVIDER_NAME = 'public-endpoints-noauth'

print(f'Configuring targets on gateway {gateway_id}...')

# 1. Create or get credential provider
print('\n1. Setting up credential provider...')
try:
    providers = client.list_api_key_credential_providers()
    provider_id = None
    for provider in providers.get('items', []):
        if provider['displayName'] == CREDENTIAL_PROVIDER_NAME:
            provider_id = provider['credentialProviderIdentifier']
            print(f'✓ Credential provider exists: {provider_id}')
            break
    
    if not provider_id:
        response = client.create_api_key_credential_provider(
            displayName=CREDENTIAL_PROVIDER_NAME,
            apiKeyIdentifier='x-api-key'
        )
        provider_id = response['credentialProviderIdentifier']
        print(f'✓ Created credential provider: {provider_id}')
except Exception as e:
    print(f'⚠️  Credential provider error: {e}')
    provider_id = None

# 2. Register targets
print('\n2. Registering MCP targets...')
api_targets = [
    ('fetchapi1', f'{AZURE_BASE_URL}/api1', 'Feature detection from Azure API 1'),
    ('fetchapi2', f'{AZURE_BASE_URL}/api2', 'Security configuration from Azure API 2'),
    ('fetchapi3', f'{AZURE_BASE_URL}/api3', 'Configuration from Azure API 3'),
    ('fetchapi4', f'{AZURE_BASE_URL}/api4', 'Data from Azure API 4'),
]

for target_name, endpoint, description in api_targets:
    try:
        # Build inline OpenAPI schema
        openapi_schema = {
            'openapi': '3.0.0',
            'info': {
                'title': target_name,
                'version': '1.0.0',
                'description': description
            },
            'servers': [{'url': endpoint}],
            'paths': {
                '/': {
                    'get': {
                        'summary': f'Fetch data from {target_name}',
                        'operationId': 'getData',
                        'responses': {
                            '200': {
                                'description': 'Success',
                                'content': {
                                    'application/json': {
                                        'schema': {'type': 'object'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Check if target exists
        targets = client.list_gateway_targets(gatewayIdentifier=gateway_id)
        target_exists = any(t['displayName'] == target_name for t in targets.get('items', []))
        
        if target_exists:
            print(f'  ✓ {target_name} (already registered)')
        else:
            response = client.create_gateway_target(
                gatewayIdentifier=gateway_id,
                displayName=target_name,
                targetConfiguration={
                    'mcp': {
                        'openApiSchema': {
                            'inlinePayload': json.dumps(openapi_schema)
                        }
                    }
                },
                credentialProviderConfigurations=[
                    {
                        'role': 'TARGET_ENDPOINT_PROVIDER',
                        'credentialProviderIdentifier': provider_id
                    }
                ] if provider_id else []
            )
            print(f'  ✓ {target_name} registered')
    except Exception as e:
        print(f'  ❌ {target_name} error: {str(e)[:80]}')

print('\n✓ Configuration complete')
