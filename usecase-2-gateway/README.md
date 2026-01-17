# Use Case 2: AgentCore Gateway with MCP Targets

**Enterprise approach.** Central gateway indexes tools, manages credentials, integrates with compliance/audit.

```
User → Flask UI → Bedrock (tool-use) → AgentCore Gateway → MCP Targets → Azure API /api1-4
```

## Demo in 2 minutes

```bash
./deploy.sh    # Creates gateway, registers targets, starts Flask
# Then in browser: http://localhost:5000
# Ask: "What's the difference in security between api2 and api3?"
./cleanup.sh   # Deletes gateway, targets, IAM roles
```

## What Gets Deployed

**AWS Resources:**
- AgentCore Gateway (name: `demo-azure-gateway`)
- 4 MCP Targets (fetchapi1-4) mapped to Azure APIs
- API Key Credential Provider (for future auth)
- IAM role: `GatewayServiceRole` (grants Bedrock access)

**Local:**
- Flask web app on `localhost:5000`
- Same chat UI as Use Case 1

## Cleanup

```bash
./cleanup.sh
# Deletes:
#   - Gateway
#   - MCP targets
#   - Credential provider
#   - IAM role
# Stops Flask process
```

## Talking Points

- ✅ **Tool Registry:** Gateway indexes 4 tools; easy to see what's available
- ✅ **Credential Management:** API keys/auth secrets in one place (future expansion)
- ✅ **Audit Trail:** Every tool call logged to CloudTrail
- ✅ **Multi-LLM:** Same tools work with Anthropic, Cohere, Mistral (if you host them on Bedrock)
- ❌ **Overhead:** Extra control-plane setup (but one-time cost)

## Architecture

```
┌──────────────────┐
│  Browser / UI    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────┐
│     Flask Web App                │
│  • POST /api/chat endpoint       │
│  • Session history tracking      │
└────────┬─────────────────────────┘
         │ (tool-use)
         ▼
┌──────────────────────────────────┐
│   AWS Bedrock (Claude)           │
│   • Receives tool definitions    │
│   • Calls tools via gateway      │
│   • Processes responses          │
└────────┬─────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│   AgentCore Gateway                         │
│   • gatewayId: demo-azure-gateway           │
│   • Hosts MCP target registry               │
│   • Manages credentials                     │
│   • Audit log integration                   │
└────────┬────────────────────────────────────┘
         │
         ├─────────┬──────────┬──────────┐
         ▼         ▼          ▼          ▼
      Target1   Target2   Target3    Target4
      (api1)    (api2)    (api3)     (api4)
         │         │          │          │
         └────────┬──────────┬──────────┘
                  ▼
         ┌──────────────────────┐
         │  Azure APIs (HTTPS)  │
         │  /api1 /api2 /api3   │
         └──────────────────────┘
```

## MCP Targets in Gateway

Each target:
- **Name:** fetchapi{1..4}
- **Type:** OpenAPI (inline schema)
- **Protocol:** HTTPS
- **Endpoint:** `https://api2.us-insurancesre-dev.azure.lnrsg.io/api{1..4}`
- **Credentials:** API Key Credential Provider (name: `public-endpoints-noauth`)

## Scripts Included

1. **`setup-gateway.py`** – Create the AgentCore gateway
2. **`configure-targets.py`** – Register 4 MCP targets
3. **`app.py`** – Flask UI (same as Use Case 1, points to gateway endpoint)
4. **`deploy.sh`** – Orchestrates all steps + runs Flask
5. **`cleanup.sh`** – Destroys everything

## When to Use This Approach

- 🎯 **Multi-team environments** – Teams can discover tools in the registry
- 🎯 **Compliance-heavy** – Audit trail, credential vault, RBAC (future)
- 🎯 **Planned expansion** – Adding more tools? Easy to register them
- 🎯 **Multi-LLM strategy** – Same tools for Claude, Cohere, custom models

## Upgrade Path

Ready for production? Add:
- **API Authentication:** Update `app.py` to pass auth tokens to gateway
- **Credential Rotation:** Use Secrets Manager for API keys
- **Rate Limiting:** Add DynamoDB-based quota management
- **Custom Transformations:** Extend targets to normalize API responses

## Costs

- Gateway: ~$0.05/request (first 100K/month free)
- Targets: no additional cost
- IAM: included in Bedrock pricing

Total for demo: ~free (under free tier limits)
