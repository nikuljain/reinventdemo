"""
Use Case 1: Direct HTTP Tools
Bedrock Claude directly calls Azure APIs via tool-use
"""
from flask import Flask, render_template, request, jsonify
import boto3
import requests
from datetime import datetime
import os
import json
import urllib3

# Disable SSL warnings for staging Let's Encrypt certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

# Initialize Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'

# Azure API endpoints
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
            'description': 'Fetch feature detection data from Azure API 1. Returns mTLS, Traefik, and ingress configuration.',
            'inputSchema': {'json': {'type': 'object', 'properties': {}, 'required': []}}
        }
    },
    {
        'toolSpec': {
            'name': 'fetchapi2',
            'description': 'Fetch security configuration from Azure API 2. Returns TLS, SSL, and mTLS settings.',
            'inputSchema': {'json': {'type': 'object', 'properties': {}, 'required': []}}
        }
    },
    {
        'toolSpec': {
            'name': 'fetchapi3',
            'description': 'Fetch API configuration from Azure API 3.',
            'inputSchema': {'json': {'type': 'object', 'properties': {}, 'required': []}}
        }
    },
    {
        'toolSpec': {
            'name': 'fetchapi4',
            'description': 'Fetch additional data from Azure API 4.',
            'inputSchema': {'json': {'type': 'object', 'properties': {}, 'required': []}}
        }
    },
]

# In-memory conversation storage
conversations = {}


@app.route('/')
def index():
    return render_template('chat.html')


def invoke_claude(messages):
    """Call Bedrock using converse API with tool-use"""
    system_prompt = "You are a helpful API analyst. Use the provided tools to fetch data from Azure APIs and provide insights."
    
    response = bedrock.converse(
        modelId=MODEL_ID,
        system=[{'text': system_prompt}],
        messages=messages,
        toolConfig={'tools': TOOLS},
        inferenceConfig={'maxTokens': 1024}
    )
    
    return response


def process_tool_call(tool_name):
    """Execute tool call by hitting Azure endpoint"""
    url = API_ENDPOINTS.get(tool_name)
    if not url:
        return {'error': f'Tool {tool_name} not found'}
    
    try:
        # Disable SSL verification for staging Let's Encrypt certificates
        resp = requests.get(url, timeout=10, verify=False)
        # Try to decode JSON first; if not JSON, return text body
        try:
            return resp.json()
        except ValueError:
            # Return a structured dict with status, headers, and truncated text
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
    """Quick extraction of key fields from Azure API HTML/text.
    Returns a dict with fields useful to present in UI and for analysis.
    """
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

    # Traefik version
    m = re.search(r"Traefik[- ]?version[:\s]*v?(\d+\.\d+)", text, re.IGNORECASE)
    if m:
        out['traefik_version'] = m.group(1)

    # backend service
    m = re.search(r"X-Backend-Service[:\s]*([A-Za-z0-9_\-]+)", text, re.IGNORECASE)
    if m:
        out['backend_service'] = m.group(1)

    # mTLS detection
    if re.search(r"mTLS|mutual TLS|client certificate", text, re.IGNORECASE):
        out['mtls'] = True

    # custom headers count like '28 detected'
    m = re.search(r"(\d{1,3})\s+custom headers", text, re.IGNORECASE)
    if m:
        out['custom_headers_count'] = int(m.group(1))

    # proxy IPs
    m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3}(?:,\d{1,3}(?:\.\d{1,3}){3})*)", text)
    if m:
        out['proxy_ips'] = m.group(1)

    # short summary (first 240 chars of cleaned text)
    cleaned = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()
    out['summary'] = cleaned[:240] + ('...' if len(cleaned) > 240 else '')

    return out


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        # Initialize conversation if needed
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Add user message in converse format (text in content list)
        conversations[session_id].append({
            'role': 'user',
            'content': [{'text': user_message}]
        })
        
        # Track tool calls
        tools_used = []
        collected_tool_results = []
        
        # Agentic loop (max 5 iterations to prevent infinite loops)
        for iteration in range(5):
            response = invoke_claude(conversations[session_id])
            stop_reason = response['stopReason']
            content = response['output']['message']['content']
            
            # Add assistant response to conversation
            conversations[session_id].append({
                'role': 'assistant',
                'content': content
            })
            
            # Check if Claude wants to call tools
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
                        
                        # Track tool call
                        tools_used.append({
                            'name': tool_name,
                            'url': API_ENDPOINTS.get(tool_name, 'unknown')
                        })
                        
                        # Execute tool
                        tool_result = process_tool_call(tool_name)
                        
                        # Add result for this tool
                        # If we received a text/html content, parse key fields
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

                        # also collect parsed result for UI rendering
                        collected_tool_results.append({'tool': tool_name, 'parsed': parsed, 'raw': tool_result})
                    
                    # Add all tool results as a single user message
                    conversations[session_id].append({
                        'role': 'user',
                        'content': tool_results
                    })
            else:
                # Claude is done (end_turn or other stop reason)
                break
        
        # Extract final text response
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
            '_tool_results': collected_tool_results
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
