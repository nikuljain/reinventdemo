# Demo Quick Reference Card

## Pre-Demo Checklist

```bash
☐ Terminal window maximized
☐ Font size increased for visibility
☐ AWS credentials configured
☐ Navigate to: cd /Users/jainni01/personallocaltest/icsdevbedrock
☐ Test run: python3 azure-api-agent.py <<< "quit"
☐ Have ARCHITECTURE_COMPLETE.md open in another tab
☐ Have backup terminal output ready
```

## Demo Commands

### Start Agent
```bash
cd /Users/jainni01/personallocaltest/icsdevbedrock
python3 azure-api-agent.py
```

### Demo Queries (Copy-Paste Ready)

**Query 1: Single API Intelligence**
```
What information is available from API1?
```
*Expected: Agent calls fetch_api1, returns feature detection info*

**Query 2: Multi-API Coordination**
```
Can you fetch data from all four APIs?
```
*Expected: Agent calls all 4 APIs, provides aggregated summary*

**Query 3: Contextual Understanding**
```
Tell me more about the Key Vault one
```
*Expected: Agent recalls API3 from previous query, no new API call*

**Query 4: Natural Language Variation**
```
What security features are enabled?
```
*Expected: Agent calls API1 and API2 (both have security info)*

**Query 5: Comparison**
```
Compare the Flask APIs with the .NET one
```
*Expected: Agent intelligently compares API1/2/3 vs API4*

### Exit Demo
```
quit
```

## Key Talking Points by Query

### Query 1: "What information is available from API1?"

**Point to Highlight:**
- "Notice I didn't specify an endpoint like `/api1`"
- "The agent understood 'API1' and selected the right tool"
- "Watch the '🔧 Agent is using tools' indicator"

**Expected Output:**
```
🔧 Agent is using tools...
  → Calling api1: https://api2.us-insurancesre-dev.azure.lnrsg.io/api1
🤖 Agent: API1 provides feature detection showing mTLS enabled,
26 custom headers detected, Traefik configuration...
```

---

### Query 2: "Can you fetch data from all four APIs?"

**Point to Highlight:**
- "Agent autonomously decided to call ALL four APIs"
- "No explicit instructions needed - it understood 'all four'"
- "Watch it coordinate multiple API calls"

**Expected Output:**
```
🔧 Agent is using tools...
  → Calling api1
🔧 Agent is using tools...
  → Calling api2
🔧 Agent is using tools...
  → Calling api3
🔧 Agent is using tools...
  → Calling api4
🤖 Agent: Summary across all APIs...
```

---

### Query 3: "Tell me more about the Key Vault one"

**Point to Highlight:**
- "Notice there's NO '🔧 Agent is using tools' this time"
- "It remembered API3 from the previous query"
- "Conversation memory in action!"

**Expected Output:**
```
🤖 Agent: API3 demonstrates Azure Key Vault integration...
```
(No API call indicator)

---

## Troubleshooting

### If Agent Fails to Start
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check Python version
python3 --version  # Should be 3.12+

# Reinstall dependencies
pip3 install boto3 requests --upgrade
```

### If API Calls Fail
- Show it's expected (SSL certificates)
- Explain staging environment
- Point out error handling in code

### If Demo Freezes
```
Ctrl+C to exit
```
Then explain asynchronous nature and retry

## Architecture Diagram URLs

Show these during presentation:

1. **System Architecture** → Open ARCHITECTURE_COMPLETE.md, scroll to "System Architecture"
2. **Data Flow** → Scroll to "Data Flow Diagram"
3. **Component Details** → Scroll to "Component Details"

## Code Highlights

### Show in azure-api-agent.py

**Line ~40-60: Tool Definitions**
```python
TOOLS = [
    {
        "name": "fetch_api1",
        "description": "Fetches information from Azure Flask API 1",
        ...
    }
]
```
*"This is how Claude knows what tools are available"*

**Line ~85-95: API Client**
```python
def fetch_api_data(self, api_name: str) -> str:
    url = API_ENDPOINTS.get(api_name)
    response = requests.get(url, timeout=10, verify=False)
    return response.text
```
*"Simple HTTP GET - agent handles the complexity"*

**Line ~135-160: Claude Invocation**
```python
request_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 2048,
    "system": "You are an intelligent agent...",
    "messages": messages,
    "tools": TOOLS  # ← This is the magic
}
```
*"We pass tool definitions to Claude, it decides when to use them"*

## Backup Slides

If technical issues arise, show:

1. **Pre-recorded Output** (have a text file ready)
2. **Architecture Diagrams** (ARCHITECTURE_COMPLETE.md)
3. **Code Walkthrough** (azure-api-agent.py)
4. **Cost Analysis** (COST_ANALYSIS.md)

## Time Management

| Section | Duration | Notes |
|---------|----------|-------|
| Intro | 2 min | Problem statement |
| Architecture | 5 min | Show diagrams |
| **Demo** | 10 min | **This section** |
| Comparison | 8 min | Alternatives |
| Q&A | 10 min | Open discussion |
| **Total** | 35 min | |

## Q&A Prep

### Expected Questions

**"How does it handle errors?"**
→ Show error handling in code, explain graceful degradation

**"What if API changes?"**
→ Just update tool description, no code changes needed

**"Can we use GPT-4?"**
→ Yes! Replace Bedrock client with OpenAI API

**"Cost at scale?"**
→ Reference COST_ANALYSIS.md, show linear scaling

**"Security concerns?"**
→ IAM controls, existing mTLS, no new surface

**"Production readiness?"**
→ Add monitoring, logging, rate limiting - otherwise ready

## Post-Demo Actions

```bash
☐ Share GitHub repo link
☐ Send ARCHITECTURE_COMPLETE.md
☐ Send PRESENTATION_GUIDE.md
☐ Schedule follow-up demos
☐ Create Confluence page
☐ Propose pilot project
```

## Emergency Contacts

- **AWS Support**: If Bedrock issues
- **Code Owner**: jainni01@risk.regn.net
- **Backup Presenter**: [Name if applicable]

## Final Pre-Demo Command

```bash
# Run this 5 minutes before demo to verify everything works
cd /Users/jainni01/personallocaltest/icsdevbedrock
python3 azure-api-agent.py <<< "What information is available from API1?
quit"
```

Should see:
```
✓ Agent starts
✓ Calls API1
✓ Returns response
✓ Exits cleanly
```

## Presentation Flow

1. **Start** → Problem statement (2 min)
2. **Show** → Architecture diagram (3 min)
3. **Demo** → Run queries (10 min) ← YOU ARE HERE
4. **Compare** → Show alternatives (5 min)
5. **Discuss** → Q&A (10 min)
6. **Close** → Next steps (2 min)

---

## The Money Slide

```
┌──────────────────────────────────────────────────────┐
│  Traditional API Access                               │
│  "Go to docs, find endpoint, craft curl, parse JSON" │
│  Time: 2 minutes per query                            │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│  AI Agent                                             │
│  "Show me security configurations"                    │
│  Time: 10 seconds                                     │
│                                                        │
│  92% time reduction                                   │
│  $22/month cost                                       │
│  ROI: 136x                                            │
└──────────────────────────────────────────────────────┘
```

**Use this slide for executive summary!**

---

## Success Criteria

Demo is successful if audience:
- ✅ Understands natural language interface
- ✅ Sees autonomous tool selection in action
- ✅ Recognizes value proposition
- ✅ Asks about applying to their use cases
- ✅ Requests follow-up demos

---

Good luck! 🚀
