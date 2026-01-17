# Azure API AI Agent - Architecture & Presentation Guide

## Executive Summary

Intelligent AI agent that autonomously queries external Azure Flask APIs using Amazon Bedrock's Claude 3 Haiku with native tool use capability. The agent understands natural language queries and automatically selects and calls the appropriate APIs to fetch real-time information.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                                  │
│                    (Interactive CLI or Web UI)                           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     AZURE API AI AGENT                                   │
│                    (azure-api-agent.py)                                  │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Conversation Manager                                            │   │
│  │  • Maintains conversation history                                │   │
│  │  • Handles multi-turn interactions                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                     │                                     │
│                                     ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Amazon Bedrock Runtime API                                      │   │
│  │  • Model: Claude 3 Haiku                                         │   │
│  │  • Capability: Native Tool Use                                   │   │
│  │  • Region: us-east-1                                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                     │                                     │
│                                     ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Tool Orchestration Engine                                       │   │
│  │  • Tool definitions for 4 APIs                                   │   │
│  │  • Autonomous tool selection                                     │   │
│  │  • Multi-tool coordination                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                     │                                     │
│                                     ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  API Client Layer                                                │   │
│  │  • HTTPS requests                                                │   │
│  │  • SSL/TLS handling (staging cert bypass)                        │   │
│  │  • Error handling & retry logic                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   EXTERNAL AZURE INFRASTRUCTURE                          │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Traefik Ingress Controller (mTLS, Routing, Security)            │  │
│  └───────────┬──────────────┬──────────────┬──────────────┬─────────┘  │
│              │              │              │              │              │
│              ▼              ▼              ▼              ▼              │
│  ┌────────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐    │
│  │   Flask API 1  │ │Flask API 2 │ │Flask API 3 │ │.NET Core API4│    │
│  │                │ │            │ │            │ │              │    │
│  │  Feature       │ │ Security   │ │ Azure Key  │ │ Version Info │    │
│  │  Detection     │ │ Config     │ │ Vault Demo │ │ & Timestamp  │    │
│  └────────────────┘ └────────────┘ └────────────┘ └──────────────┘    │
│                                                                           │
│  Base URL: https://api2.us-insurancesre-dev.azure.lnrsg.io              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────┐
│   User   │
│  Query   │
└────┬─────┘
     │ "What info is in API1?"
     ▼
┌────────────────────────────────────────────────────────────┐
│ Step 1: Query Received                                      │
│ Agent receives natural language query                       │
└────┬───────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────────┐
│ Step 2: Claude Analysis                                     │
│ • Send query + tool definitions to Claude                   │
│ • Claude analyzes intent                                    │
│ • Decides which tool(s) to use                              │
└────┬───────────────────────────────────────────────────────┘
     │
     │ Claude Response: {
     │   "stop_reason": "tool_use",
     │   "content": [{
     │     "type": "tool_use",
     │     "name": "fetch_api1",
     │     "id": "toolu_123",
     │     "input": {}
     │   }]
     │ }
     │
     ▼
┌────────────────────────────────────────────────────────────┐
│ Step 3: Tool Execution                                      │
│ • Agent extracts tool call: fetch_api1                      │
│ • Makes HTTPS GET request to:                               │
│   https://api2.us-insurancesre-dev.azure.lnrsg.io/api1     │
└────┬───────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────────┐
│ Step 4: API Response                                        │
│ Returns HTML with:                                          │
│ • mTLS status                                               │
│ • 26 custom headers                                         │
│ • Traefik configuration                                     │
│ • Feature detection results                                 │
└────┬───────────────────────────────────────────────────────┘
     │
     │ Tool Result: "<html>API1 Features:..."
     │
     ▼
┌────────────────────────────────────────────────────────────┐
│ Step 5: Result Processing                                   │
│ • Agent sends tool result back to Claude                    │
│ • Claude synthesizes human-readable response                │
└────┬───────────────────────────────────────────────────────┘
     │
     │ Claude Final Response:
     │ "API1 provides feature detection showing
     │  mTLS enabled, 26 custom headers, and
     │  Traefik ingress configuration..."
     │
     ▼
┌────────────────────────────────────────────────────────────┐
│ Step 6: User Response                                       │
│ Display formatted answer to user                            │
└────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Azure API AI Agent (`azure-api-agent.py`)

**Core Components:**
- **AzureAPIAgent Class**: Main orchestrator
- **Conversation History**: Maintains context across turns
- **Tool Processor**: Executes API calls based on Claude's decisions
- **Response Handler**: Processes Claude's tool use responses

**Key Features:**
- Autonomous tool selection (Claude decides which API to call)
- Multi-turn conversations with context
- Concurrent multi-API calls when needed
- Error handling for network/API failures
- SSL certificate bypass for staging environments

### 2. Tool Definitions

Each Azure API is exposed as a tool:

```python
{
    "name": "fetch_api1",
    "description": "Fetches information from Azure Flask API 1",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

Claude uses these definitions to understand:
- What tools are available
- When to use each tool
- What parameters they accept

### 3. Amazon Bedrock Integration

**Model**: Claude 3 Haiku (`anthropic.claude-3-haiku-20240307-v1:0`)

**Why Claude 3 Haiku:**
- Native tool use capability (function calling)
- Fast response times (< 1 second)
- Cost-effective ($0.25/$1.25 per million tokens)
- Excellent at understanding context and intent
- Can coordinate multiple tool calls intelligently

**API Call Structure:**
```python
{
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 2048,
    "system": "You are an intelligent agent...",
    "messages": [conversation_history],
    "tools": [tool_definitions]
}
```

### 4. External Azure APIs

**Base URL**: `https://api2.us-insurancesre-dev.azure.lnrsg.io`

| API | Purpose | Key Features |
|-----|---------|--------------|
| `/api1` | Feature Detection | mTLS status, Traefik config, 26 custom headers |
| `/api2` | Security Config | Security features, SSL/TLS info, custom headers |
| `/api3` | Key Vault Demo | Spring Cloud Azure integration, managed identity |
| `/api4` | Version Info | .NET Core version, timestamp |

**Infrastructure:**
- **Traefik Ingress**: Load balancing, mTLS, routing
- **mTLS Authentication**: Mutual TLS for security
- **Let's Encrypt**: Staging certificates (bypassed for testing)

## Current Deployment

### AWS Resources

**Account**: `846069303018` (risk-insus-ics-dev)  
**Region**: `us-east-1`

**Created Resources:**
- ✅ IAM Role: `BedrockAgentCoreRole` (for agent deployment)
- ✅ IAM Role: `BedrockAgentCoreGatewayRole` (for gateway)
- ✅ AgentCore Gateway: Created but ephemeral in preview
- ✅ Working Agent: Local Python script

**Files:**
```
icsdevbedrock/
├── azure-api-agent.py          # Main agent implementation
├── api-schema.json             # OpenAPI schema for APIs
├── agent-permissions.json      # Bedrock permissions
├── agent-trust-policy.json     # IAM trust policy
├── trust-policy.json           # Lambda trust policy
├── deploy.sh                   # Lambda deployment (legacy)
├── bedrock_agent.py            # Lambda version (alternative)
├── COST_ANALYSIS.md            # Cost breakdown
└── ENTERPRISE_ARCHITECTURE.md  # Technical documentation
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| AI Model | Claude 3 Haiku (Bedrock) | Natural language understanding, tool orchestration |
| Runtime | Python 3.12 | Agent execution environment |
| AWS SDK | boto3 1.42+ | Bedrock API integration |
| HTTP Client | requests | External API calls |
| Authentication | AWS IAM | Bedrock access control |
| Hosting | Local / Lambda (optional) | Agent deployment |

## Agent Capabilities

### What It Can Do

1. **Natural Language Understanding**
   - "What information is in API1?"
   - "Can you fetch data from all four APIs?"
   - "Show me the Key Vault configuration"

2. **Autonomous Decision Making**
   - Determines which API(s) to call
   - Decides if multiple APIs are needed
   - Handles sequential or parallel calls

3. **Context Retention**
   - Remembers previous queries in conversation
   - Can reference earlier API responses
   - Builds on previous knowledge

4. **Multi-API Coordination**
   - Calls multiple APIs in single query
   - Aggregates and compares responses
   - Provides unified summary

5. **Error Handling**
   - Gracefully handles API failures
   - Explains connection issues to user
   - Suggests alternatives when APIs unavailable

### Example Interactions

**Single API Query:**
```
User: "What information is available from API1?"
Agent: [Calls fetch_api1]
Response: "API1 provides feature detection showing mTLS 
enabled, 26 custom headers detected, Traefik ingress 
configuration, and endpoints for /, /health, /api/info..."
```

**Multi-API Query:**
```
User: "Can you fetch data from all four APIs?"
Agent: [Calls fetch_api1, fetch_api2, fetch_api3, fetch_api4]
Response: "Summary across all APIs:
- API1: Flask with mTLS and Traefik
- API2: Security features and SSL/TLS config
- API3: Spring Cloud Azure Key Vault demo
- API4: .NET Core version 2.1.0"
```

**Contextual Follow-up:**
```
User: "Tell me more about the Key Vault one"
Agent: [Recalls API3 from previous query, no new call needed]
Response: "API3 demonstrates Azure Key Vault integration 
using Spring Cloud Azure and Managed Identity. It successfully 
retrieves 3 secrets: Application Secret, API Key, and Database 
URL without storing credentials..."
```

## File Summary

### Active Files

1. **azure-api-agent.py** (Primary Implementation)
   - 200+ lines of Python
   - Interactive CLI interface
   - Full conversation management
   - Works immediately with `python3 azure-api-agent.py`

2. **api-schema.json** (API Documentation)
   - OpenAPI 3.0 specification
   - Documents all 4 Azure APIs
   - Used for agent configuration

3. **COST_ANALYSIS.md** (Financial Planning)
   - Detailed cost breakdown
   - Lambda vs AgentCore comparison
   - Usage projections

4. **ENTERPRISE_ARCHITECTURE.md** (Technical Docs)
   - Architecture details
   - Deployment guide
   - Integration patterns

### Legacy/Alternative Files

5. **bedrock_agent.py** (Lambda Alternative)
   - Lambda function handler
   - Same tool use logic
   - For serverless deployment

6. **deploy.sh** (Lambda Deployment)
   - Automated Lambda setup
   - IAM role creation
   - API Gateway integration

## How to Run

### Prerequisites
```bash
# AWS credentials configured
aws configure

# Python 3.12+ with boto3
pip3 install boto3 requests
```

### Execute Agent
```bash
cd /Users/jainni01/personallocaltest/icsdevbedrock
python3 azure-api-agent.py
```

### Sample Session
```
🧪 Running test queries...
----------------------------------------------------------------------
🤔 User: What information is available from API1?
🔧 Agent is using tools...
  → Calling api1: https://api2.us-insurancesre-dev.azure.lnrsg.io/api1
🤖 Agent: API1 provides feature detection showing mTLS enabled, 
26 custom headers, Traefik configuration...
----------------------------------------------------------------------

💬 Interactive mode (type your questions or 'quit'):
======================================================================
👤 You: |
```

## Project Directory Structure

```
/Users/jainni01/personallocaltest/
│
├── personalaws/              # Personal AWS experiments (Nova Lite)
│   ├── nova_agent.py
│   ├── bedrock-ui.html
│   └── ARCHITECTURE.md
│
└── icsdevbedrock/            # Enterprise production setup
    ├── azure-api-agent.py    ← PRIMARY IMPLEMENTATION
    ├── api-schema.json
    ├── agent-permissions.json
    ├── agent-trust-policy.json
    ├── trust-policy.json
    ├── deploy.sh
    ├── bedrock_agent.py
    ├── COST_ANALYSIS.md
    └── ENTERPRISE_ARCHITECTURE.md
```

## Summary

✅ **Working**: Local Python agent with full autonomous tool use  
✅ **Tested**: Successfully queries all 4 Azure Flask APIs  
✅ **Scalable**: Can deploy as Lambda for production  
✅ **Cost-Effective**: ~$22/month for 1,000 requests/day  
✅ **Documented**: Comprehensive architecture and cost analysis  

The agent demonstrates true agentic AI capability - it understands intent, selects appropriate tools, executes API calls, and synthesizes responses without manual intervention.
