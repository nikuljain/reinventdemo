#!/usr/bin/env python3
"""
Azure API Agent Client
Simulates AgentCore Gateway functionality by directly calling Azure APIs
Uses Claude to intelligently route queries to appropriate APIs
"""

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import json
import requests
from typing import Dict, List
import sys

# Configuration
REGION = "us-east-1"
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
AZURE_BASE_URL = "https://api2.us-insurancesre-dev.azure.lnrsg.io"
API_ENDPOINTS = {
    "api1": f"{AZURE_BASE_URL}/api1",
    "api2": f"{AZURE_BASE_URL}/api2",
    "api3": f"{AZURE_BASE_URL}/api3",
    "api4": f"{AZURE_BASE_URL}/api4"
}

# Tool definitions for Claude
TOOLS = [
    {
        "name": "fetch_api1",
        "description": "Fetches information from Azure Flask API 1",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "fetch_api2",
        "description": "Fetches information from Azure Flask API 2",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "fetch_api3",
        "description": "Fetches information from Azure Flask API 3",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "fetch_api4",
        "description": "Fetches information from Azure Flask API 4",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

class AzureAPIAgent:
    def __init__(self, profile='default', region=REGION):
        # Validate AWS credentials first
        if not self._validate_credentials(profile, region):
            raise RuntimeError("AWS credentials validation failed. Cannot initialize agent.")
        
        self.session = boto3.Session(profile_name=profile, region_name=region)
        self.bedrock = self.session.client('bedrock-runtime', region_name=region)
        self.conversation_history = []
    
    def _validate_credentials(self, profile, region):
        """Validate AWS credentials are configured and accessible"""
        try:
            session = boto3.Session(profile_name=profile, region_name=region)
            sts = session.client('sts', region_name=region)
            identity = sts.get_caller_identity()
            print(f"✓ AWS credentials validated")
            print(f"  Account: {identity['Account']}")
            print(f"  User/Role: {identity['Arn']}")
            return True
        except NoCredentialsError:
            print("❌ ERROR: AWS credentials not found!")
            print("\nPlease configure AWS credentials using one of these methods:")
            print(f"  1. Run: aws configure --profile {profile}")
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
    
    def fetch_api_data(self, api_name: str) -> str:
        """Fetch data from specified Azure API"""
        url = API_ENDPOINTS.get(api_name)
        if not url:
            return f"Error: Unknown API '{api_name}'"
        
        try:
            print(f"  → Calling {api_name}: {url}")
            # Disable SSL verification for mTLS endpoints (use verify=False)
            # In production, you would provide client certificates
            response = requests.get(url, timeout=10, verify=False)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error calling {api_name}: {str(e)}"
    
    def process_tool_call(self, tool_name: str, tool_input: Dict) -> str:
        """Execute a tool call"""
        # Map tool name to API endpoint
        api_mapping = {
            "fetch_api1": "api1",
            "fetch_api2": "api2",
            "fetch_api3": "api3",
            "fetch_api4": "api4"
        }
        
        api_name = api_mapping.get(tool_name)
        if api_name:
            return self.fetch_api_data(api_name)
        else:
            return f"Unknown tool: {tool_name}"
    
    def chat(self, user_message: str) -> str:
        """Send a message to the agent and get a response"""
        print(f"\n🤔 User: {user_message}")
        
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Call Claude with tools
        response = self.invoke_claude(self.conversation_history)
        
        # Process response
        return self.handle_response(response)
    
    def invoke_claude(self, messages: List[Dict]) -> Dict:
        """Invoke Claude with tool use capability"""
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "system": "You are an intelligent agent that can query Azure Flask APIs to provide information. When users ask about APIs, use the available tools to fetch real-time data.",
            "messages": messages,
            "tools": TOOLS
        }
        
        response = self.bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )
        
        return json.loads(response['body'].read())
    
    def handle_response(self, response: Dict) -> str:
        """Handle Claude's response, including tool calls"""
        stop_reason = response.get('stop_reason')
        content = response.get('content', [])
        
        # Add assistant response to conversation
        self.conversation_history.append({
            "role": "assistant",
            "content": content
        })
        
        if stop_reason == 'tool_use':
            print("🔧 Agent is using tools...")
            
            # Process tool calls
            tool_results = []
            for block in content:
                if block.get('type') == 'tool_use':
                    tool_name = block.get('name')
                    tool_input = block.get('input', {})
                    tool_use_id = block.get('id')
                    
                    # Execute the tool
                    result = self.process_tool_call(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result
                    })
            
            # Send tool results back to Claude
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            
            # Get final response
            final_response = self.invoke_claude(self.conversation_history)
            return self.handle_response(final_response)
        
        else:
            # Extract text response
            response_text = ""
            for block in content:
                if block.get('type') == 'text':
                    response_text += block.get('text', '')
            
            print(f"🤖 Agent: {response_text}")
            return response_text

def main():
    print("=" * 70)
    print("Azure API Agent - Interactive Client")
    print("=" * 70)
    print("This agent can query your Azure Flask APIs:")
    for api, url in API_ENDPOINTS.items():
        print(f"  • {api}: {url}")
    print("\nType 'quit' to exit\n")
    
    # Create agent
    agent = AzureAPIAgent()
    
    # Test queries
    test_queries = [
        "What information is available from API1?",
        "Can you fetch data from all four APIs?",
        "Show me the response from API3"
    ]
    
    print("🧪 Running test queries...")
    for query in test_queries:
        print("\n" + "-" * 70)
        agent.chat(query)
        print("-" * 70)
    
    print("\n\n💬 Interactive mode (type your questions or 'quit'):")
    print("=" * 70)
    
    # Interactive loop
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input:
                agent.chat(user_input)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
