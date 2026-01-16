"""
Flask Web Application for Azure API AI Agent
Provides a professional web UI for interacting with the agent
"""

from flask import Flask, render_template, request, jsonify, Response
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import json
import requests
from datetime import datetime
import sys

app = Flask(__name__)

def validate_aws_credentials():
    """Validate AWS credentials are configured and accessible"""
    try:
        # Create a test client to verify credentials
        sts = boto3.client('sts', region_name='us-east-1')
        identity = sts.get_caller_identity()
        print(f"✓ AWS credentials validated")
        print(f"  Account: {identity['Account']}")
        print(f"  User/Role: {identity['Arn']}")
        return True
    except NoCredentialsError:
        print("❌ ERROR: AWS credentials not found!")
        print("\nPlease configure AWS credentials using one of these methods:")
        print("  1. Run: aws configure")
        print("  2. Set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("  3. Use IAM role (if running on EC2/ECS/Lambda)")
        return False
    except PartialCredentialsError:
        print("❌ ERROR: AWS credentials are incomplete!")
        print("\nPlease ensure both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set.")
        return False
    except ClientError as e:
        print(f"❌ ERROR: AWS credentials validation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error validating AWS credentials: {e}")
        return False

# Validate credentials before initializing Bedrock client
if not validate_aws_credentials():
    print("\n⚠️  Application cannot start without valid AWS credentials.")
    print("Please configure your credentials and restart the application.")
    sys.exit(1)

# Initialize Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Tool definitions for Claude (Converse API format)
TOOLS = [
    {
        "toolSpec": {
            "name": "fetch_api1",
            "description": "Fetches feature detection information from Flask API 1. Returns details about mTLS configuration, custom headers, and Traefik ingress settings.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "fetch_api2",
            "description": "Fetches security configuration from Flask API 2. Returns information about SSL/TLS settings and security features.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "fetch_api3",
            "description": "Fetches Azure Key Vault demo data from Spring Cloud API. Returns information about secrets stored in Azure Key Vault.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "fetch_api4",
            "description": "Fetches version and environment information from .NET Core API. Returns details about the application runtime.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    }
]

# API endpoint mapping
API_ENDPOINTS = {
    "fetch_api1": "https://api2.us-insurancesre-dev.azure.lnrsg.io/api1",
    "fetch_api2": "https://api2.us-insurancesre-dev.azure.lnrsg.io/api2",
    "fetch_api3": "https://api2.us-insurancesre-dev.azure.lnrsg.io/api3",
    "fetch_api4": "https://api2.us-insurancesre-dev.azure.lnrsg.io/api4"
}

# Conversation history per session (in-memory, for demo)
conversations = {}

def fetch_api_data(url):
    """Fetch data from Azure API endpoint"""
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def invoke_claude(messages, tools):
    """Invoke Claude via Bedrock"""
    
    # Add system prompt to encourage tool use and structured formatting
    system_prompts = [
        {
            "text": """You are an intelligent Azure API assistant with direct access to four Azure API endpoints through tools.

IMPORTANT INSTRUCTIONS:
1. When users ask about API data, ALWAYS use the appropriate tools to fetch real-time data
2. NEVER say you don't have access - you have direct tool access to all APIs
3. Format your responses with clear structure using markdown:
   - Use **bold** for important terms
   - Use bullet points (•) for lists
   - Use headings (##) to organize sections
   - Use code blocks for technical data
   - Keep responses concise but informative

EXAMPLE GOOD RESPONSE:
## Security Features
• **mTLS Authentication**: Enabled with client certificates
• **Custom Headers**: 26 security headers detected
• **SSL/TLS**: Active with Let's Encrypt certificates
• **Ingress**: Traefik controller managing traffic

Always structure your responses this way for clarity and professionalism."""
        }
    ]
    
    response = bedrock.converse(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        messages=messages,
        system=system_prompts,
        toolConfig={"tools": tools}
    )
    return response

def process_tool_call(tool_name):
    """Execute the tool call by fetching API data"""
    if tool_name in API_ENDPOINTS:
        url = API_ENDPOINTS[tool_name]
        return fetch_api_data(url)
    return {"error": f"Unknown tool: {tool_name}"}

@app.route('/')
def index():
    """Serve the web UI"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests from the UI"""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Initialize or retrieve conversation history
    if session_id not in conversations:
        conversations[session_id] = []
    
    # Add user message to history
    conversations[session_id].append({
        "role": "user",
        "content": [{"text": user_message}]
    })
    
    tools_used = []
    max_iterations = 5
    iteration = 0
    
    try:
        while iteration < max_iterations:
            iteration += 1
            
            # Invoke Claude
            response = invoke_claude(conversations[session_id], TOOLS)
            
            # Extract stop reason and content
            stop_reason = response['stopReason']
            output_message = response['output']['message']
            
            # Add assistant response to conversation
            conversations[session_id].append(output_message)
            
            if stop_reason == 'tool_use':
                # Process tool calls
                for content_block in output_message['content']:
                    if 'toolUse' in content_block:
                        tool_use = content_block['toolUse']
                        tool_name = tool_use['name']
                        tool_use_id = tool_use['toolUseId']
                        
                        # Track which tool was used
                        tools_used.append({
                            "name": tool_name,
                            "url": API_ENDPOINTS.get(tool_name, "")
                        })
                        
                        # Execute the tool
                        tool_result = process_tool_call(tool_name)
                        
                        # Add tool result to conversation
                        conversations[session_id].append({
                            "role": "user",
                            "content": [
                                {
                                    "toolResult": {
                                        "toolUseId": tool_use_id,
                                        "content": [{"json": tool_result}]
                                    }
                                }
                            ]
                        })
            
            elif stop_reason == 'end_turn':
                # Extract final response text
                final_response = ""
                for content_block in output_message['content']:
                    if 'text' in content_block:
                        final_response += content_block['text']
                
                return jsonify({
                    "response": final_response,
                    "tools_used": tools_used,
                    "timestamp": datetime.now().isoformat()
                })
            
            else:
                return jsonify({"error": f"Unexpected stop reason: {stop_reason}"}), 500
        
        return jsonify({"error": "Max iterations reached"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history for a session"""
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in conversations:
        conversations[session_id] = []
    
    return jsonify({"status": "cleared"})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(conversations)
    })

if __name__ == '__main__':
    # Disable SSL warnings for staging certificates
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("🚀 Azure API AI Agent Web UI")
    print("=" * 50)
    print("✓ Server starting on http://localhost:5000")
    print("✓ Open your browser and navigate to the URL above")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
