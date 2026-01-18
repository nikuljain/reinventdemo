"""
Use Case 2: Gateway + MCP Targets
Same Flask UI, but with Bedrock connected to AgentCore Gateway
"""
from flask import Flask, render_template, request, jsonify
import boto3
import requests
from datetime import datetime
import os
import json
import urllib3

app = Flask(__name__)

# Disable SSL warnings for staging Let's Encrypt certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read gateway ID from file
try:
    with open('gateway_id.txt', 'r') as f:
        GATEWAY_ID = f.read().strip()
    GATEWAY_ENDPOINT = f'https://{GATEWAY_ID}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp'
except:
    GATEWAY_ENDPOINT = None

# Initialize Bedrock (pointing to gateway)
bedrock = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1',
    endpoint_url=GATEWAY_ENDPOINT if GATEWAY_ENDPOINT else None
)
MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'

# Azure API endpoints (for fallback if gateway doesn't work)
AZURE_ENDPOINT_BASE = 'https://api2.us-insurancesre-dev.azure.lnrsg.io'
API_ENDPOINTS = {
    'fetchapi1': f'{AZURE_ENDPOINT_BASE}/api1',
    'fetchapi2': f'{AZURE_ENDPOINT_BASE}/api2',
    'fetchapi3': f'{AZURE_ENDPOINT_BASE}/api3',
    'fetchapi4': f'{AZURE_ENDPOINT_BASE}/api4',
}

# Tool definitions for Bedrock converse API
TOOLS = [
    {
        'toolSpec': {
            'name': 'fetchapi1',
            'description': 'Feature detection from Azure API 1',
            'inputSchema': {'json': {'type': 'object', 'properties': {}, 'required': []}}
        }
    },
    {
        'toolSpec': {
            'name': 'fetchapi2',
            'description': 'Security configuration from Azure API 2',
            'inputSchema': {'json': {'type': 'object', 'properties': {}, 'required': []}}
        }
    },
    {
        'toolSpec': {
            'name': 'fetchapi3',
            'description': 'Configuration from Azure API 3',
            'inputSchema': {'json': {'type': 'object', 'properties': {}, 'required': []}}
        }
    },
    {
        'toolSpec': {
            'name': 'fetchapi4',
            'description': 'Data from Azure API 4',
            'inputSchema': {'json': {'type': 'object', 'properties': {}, 'required': []}}
        }
    },
]

conversations = {}


@app.route('/')
def index():
    if GATEWAY_ENDPOINT:
        mode = f'Gateway Mode ({GATEWAY_ID})'
    else:
        mode = 'Direct Mode (fallback)'
    return render_template('chat.html', mode=mode)


def invoke_claude(messages):
    """Call Bedrock via AgentCore gateway when configured,
    otherwise fall back to direct mode.
    """
    system_prompt = "You are a helpful API analyst. Use the provided tools to fetch data from Azure APIs and provide insights."

    # If gateway endpoint is configured, use bedrock-agentcore InvokeAgentRuntime
    if GATEWAY_ENDPOINT and GATEWAY_ID:
        try:
            import boto3
            
            # Use bedrock-agentcore client for gateway invocation
            agentcore_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
            
            # Build MCP JSON-RPC payload for converse
            mcp_payload = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'bedrock/converse',
                'params': {
                    'modelId': MODEL_ID,
                    'system': [{'text': system_prompt}],
                    'messages': messages,
                    'toolConfig': {'tools': TOOLS},
                    'inferenceConfig': {'maxTokens': 1024}
                }
            }
            
            # Construct gateway ARN from ID
            gateway_arn = f'arn:aws:bedrock-agentcore:us-east-1:846069303018:gateway/{GATEWAY_ID}'
            
            # Invoke gateway with MCP protocol
            response = agentcore_client.invoke_agent_runtime(
                agentRuntimeArn=gateway_arn,
                mcpProtocolVersion='2025-11-25',
                contentType='application/json',
                accept='application/json',
                payload=json.dumps(mcp_payload).encode('utf-8')
            )
            
            # Parse response body
            response_body = response['payload'].read().decode('utf-8')
            result = json.loads(response_body)
            
            # Check for JSON-RPC error
            if 'error' in result:
                return {
                    'stopReason': 'completed',
                    'output': {'message': {'content': [{'text': f"Gateway error: {json.dumps(result['error'])}"}]}}
                }
            
            # Extract result and map to expected format
            mcp_result = result.get('result', {})
            if 'stopReason' in mcp_result and 'output' in mcp_result:
                return mcp_result
            
            # Return raw result if format unexpected
            return {
                'stopReason': 'completed',
                'output': {'message': {'content': [{'text': json.dumps(result)}]}}
            }
            
        except Exception as e:
            import traceback
            return {
                'stopReason': 'completed',
                'output': {'message': {'content': [{'text': f'Gateway invocation failed: {e}\n{traceback.format_exc()[:800]}'}]}}
            }

    # Fallback: make a runtime invoke_model call (local/demo mode)
    text_input = system_prompt + '\n' + '\n'.join([m.get('content', [{}])[0].get('text', '') for m in messages])
    payload = {
        'modelId': MODEL_ID,
        'body': text_input.encode('utf-8'),
        'contentType': 'text/plain'
    }

    try:
        resp = bedrock.invoke_model(**payload)
        out = {
            'stopReason': 'completed',
            'output': {'message': {'content': []}}
        }
        try:
            body = resp.get('body')
            if hasattr(body, 'read'):
                txt = body.read().decode('utf-8')
            else:
                txt = str(body)
        except Exception:
            txt = str(resp)
        out['output']['message']['content'].append({'text': txt})
        return out
    except Exception as e:
        return {
            'stopReason': 'completed',
            'output': {'message': {'content': [{'text': f'Runtime invoke failed: {e}'}]}}
        }
    


def sanitize_messages(messages):
    """Remove ContentBlock entries with empty text to satisfy Bedrock validation."""
    out = []
    for msg in messages:
        new_content = []
        for block in msg.get('content', []):
            # keep toolUse/toolResult blocks as-is
            if isinstance(block, dict) and ('toolUse' in block or 'toolResult' in block):
                new_content.append(block)
                continue

            # keep blocks without 'text' (defensive), or with non-empty text
            if not isinstance(block, dict):
                continue
            text = block.get('text')
            if text is None:
                new_content.append(block)
                continue
            if isinstance(text, str) and text.strip() == '':
                # skip empty text blocks
                continue
            new_content.append(block)

        if new_content:
            out.append({'role': msg.get('role'), 'content': new_content})
    return out


def process_tool_call(tool_name):
    """Execute tool call by hitting Azure endpoint directly"""
    url = API_ENDPOINTS.get(tool_name)
    if not url:
        return {'error': f'Tool {tool_name} not found'}
    
    try:
        # Disable SSL verification for staging Let's Encrypt certificates
        resp = requests.get(url, timeout=10, verify=False)
        try:
            return resp.json()
        except ValueError:
            text = resp.text
            truncated = text[:5000] if len(text) > 5000 else text
            return {
                'status_code': resp.status_code,
                'headers': dict(resp.headers),
                'text': truncated
            }
    except Exception as e:
        return {'error': str(e), 'endpoint': url}


def parse_azure_html(tool_result_text):
    import re
    text = tool_result_text if isinstance(tool_result_text, str) else ''
    out = {
        'traefik_version': None,
        'backend_service': None,
        'mtls': False,
        'custom_headers_count': None,
        'proxy_ips': None,
        'summary': None
    }
    m = re.search(r"Traefik[- ]?version[:\s]*v?(\d+\.\d+)", text, re.IGNORECASE)
    if m:
        out['traefik_version'] = m.group(1)
    m = re.search(r"X-Backend-Service[:\s]*([A-Za-z0-9_\-]+)", text, re.IGNORECASE)
    if m:
        out['backend_service'] = m.group(1)
    if re.search(r"mTLS|mutual TLS|client certificate", text, re.IGNORECASE):
        out['mtls'] = True
    m = re.search(r"(\d{1,3})\s+custom headers", text, re.IGNORECASE)
    if m:
        out['custom_headers_count'] = int(m.group(1))
    m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3}(?:,\d{1,3}(?:\.\d{1,3}){3})*)", text)
    if m:
        out['proxy_ips'] = m.group(1)
    cleaned = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()
    out['summary'] = cleaned[:240] + ('...' if len(cleaned) > 240 else '')
    return out


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Add user message in converse format
        conversations[session_id].append({
            'role': 'user',
            'content': [{'text': user_message}]
        })
        
        tools_used = []
        collected_tool_results = []
        
        for iteration in range(5):
            # Sanitize messages to remove empty text blocks, then dump for debug
            sanitized = sanitize_messages(conversations[session_id])
            try:
                with open('/tmp/conv_debug.json', 'w') as _f:
                    json.dump(sanitized, _f, indent=2)
            except Exception as _ex:
                print('Failed to write conv debug:', _ex)

            response = invoke_claude(sanitized)
            
            # Handle gateway response - may not have stopReason if error occurred
            if not isinstance(response, dict):
                response = {'stopReason': 'completed', 'output': {'message': {'content': [{'text': str(response)}]}}}
            
            stop_reason = response.get('stopReason', 'completed')
            output = response.get('output', {})
            message = output.get('message', {})
            content = message.get('content', [{'text': 'No content returned'}])
            
            conversations[session_id].append({
                'role': 'assistant',
                'content': content
            })
            
            if stop_reason == 'tool_use':
                # Collect ALL tool uses from the response
                tool_use_blocks = [block for block in content if 'toolUse' in block]
                
                if tool_use_blocks:
                    # Build tool results for each tool use
                    tool_results = []
                    for tool_use_block in tool_use_blocks:
                        tool_use = tool_use_block['toolUse']
                        tool_name = tool_use['name']
                        tool_use_id = tool_use['toolUseId']
                        
                        tools_used.append({
                            'name': tool_name,
                            'url': API_ENDPOINTS.get(tool_name, 'unknown')
                        })
                        
                        tool_result = process_tool_call(tool_name)
                        
                        parsed = None
                        try:
                            if isinstance(tool_result, dict) and 'text' in tool_result:
                                parsed = parse_azure_html(tool_result.get('text', ''))
                        except Exception:
                            parsed = None

                        tool_results.append({
                            'toolResult': {
                                'toolUseId': tool_use_id,
                                'content': [{'text': json.dumps(tool_result)}]
                            }
                        })

                        collected_tool_results.append({'tool': tool_name, 'parsed': parsed, 'raw': tool_result})
                    
                    conversations[session_id].append({
                        'role': 'user',
                        'content': tool_results
                    })
            else:
                break
        
        final_response = ''
        if conversations[session_id]:
            last_message = conversations[session_id][-1]
            if last_message['role'] == 'assistant':
                for block in last_message.get('content', []):
                    if 'text' in block:
                        final_response = block['text']
                        break
        
        return jsonify({
            'response': final_response,
            'timestamp': datetime.utcnow().isoformat(),
            'tools_used': tools_used,
            'session_id': session_id,
            'gateway': GATEWAY_ENDPOINT if GATEWAY_ENDPOINT else 'Not configured',
            '_tool_results': collected_tool_results
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    print(f'Gateway Endpoint: {GATEWAY_ENDPOINT or "Not set (using direct mode)"}')
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
