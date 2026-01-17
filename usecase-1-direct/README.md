# Use Case 1: Direct HTTP Tools

**Fastest path to demo.** Bedrock Claude calls Azure APIs directly via tool-use, no MCP gateway.

```
User → Flask UI → Bedrock (tool-use) → Azure API /api1-4
```

## Demo in 30 seconds

```bash
./deploy.sh
# Then in browser: http://localhost:5000
# Ask: "Compare security on api2 vs api3"
```

## What Gets Deployed

- Flask web app on `localhost:5000` with chat UI
- Bedrock model: `anthropic.claude-3-haiku-20240307-v1:0`
- 4 tools: `fetchapi1`, `fetchapi2`, `fetchapi3`, `fetchapi4`
- Each tool directly hits Azure: `https://api2.us-insurancesre-dev.azure.lnrsg.io/api{1..4}`

## Cleanup

```bash
./cleanup.sh
# Stops Flask process, no AWS resources created
```

## Talking Points

- ✅ **Simplest:** No gateway, no credential providers, just direct HTTPS
- ✅ **Fast:** ~2 min deploy; Bedrock to Azure in <3s round-trip
- ✅ **Good for:** Proof-of-concept, team experiments, hackathons
- ❌ **Not for:** Multi-team, audit-heavy, or multi-LLM scenarios (see Gateway)

## Architecture

```
┌──────────────────────┐
│    Browser / UI      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────┐
│     Flask Web App                │
│  • POST /api/chat endpoint       │
│  • Session history tracking      │
└──────────┬───────────────────────┘
           │ (tool-use)
           ▼
┌──────────────────────────────────┐
│   AWS Bedrock (Claude)           │
│   • Understands natural language │
│   • Decides which tools to call  │
│   • Processes Azure API response │
└──────────┬───────────────────────┘
           │ (HTTPS)
           ▼
┌──────────────────────────────────┐
│   Azure APIs                     │
│   /api1 /api2 /api3 /api4        │
│   https://api2.us-...-dev...io   │
└──────────────────────────────────┘
```

## Tools Defined in Claude

```json
[
  {
    "name": "fetchapi1",
    "description": "Feature detection from Flask API 1",
    "inputSchema": { "type": "object", "properties": {} }
  },
  {
    "name": "fetchapi2",
    "description": "Security configuration from Flask API 2"
  },
  {
    "name": "fetchapi3",
    "description": "API configuration from Flask API 3"
  },
  {
    "name": "fetchapi4",
    "description": "Additional API from Flask API 4"
  }
]
```

## When to Use This Approach

- 🎯 **Demo to stakeholders** – Shows value in 5 minutes
- 🎯 **Proof of concept** – Validate the idea before committing to infrastructure
- 🎯 **Small teams** – All engineers have access, no RBAC needed
- 🎯 **Changing APIs** – Easy to add/modify tools (just edit `app.py`)

## Limitations

- **No tool registry** – Tools live in code, not in a central service
- **Bedrock-only** – Can't use GPT-4, Claude via API, etc.
- **No credentials vault** – API keys/auth hardcoded (mitigation: use env vars)
- **No audit trail** – Tool calls not logged to CloudWatch automatically

## Upgrade Path

Ready for production? Graduates to **Use Case 2: Gateway** for:
- Tool registry (who can see what?)
- Credential management (rotate keys safely)
- Multi-LLM support (Bedrock, AWS-hosted third-party models)
- Compliance/audit (CloudTrail logs of every tool call)
