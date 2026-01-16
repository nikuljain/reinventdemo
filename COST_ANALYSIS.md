# Cost Breakdown: Enterprise Bedrock Agent Setup
## Account: 846069303018 (risk-insus-ics-dev)

---

## Architecture Comparison

### Current Setup (Lambda + API Gateway)
```
User → API Gateway → Lambda → Bedrock Runtime → Claude
                       ↓
                  Azure APIs
```

### AgentCore Gateway Option
```
User → Bedrock Agent → AgentCore Gateway → Azure APIs
```

---

## Monthly Cost Estimate - Current Setup

### Infrastructure Costs (Fixed)

| Component | Pricing | Monthly Cost |
|-----------|---------|--------------|
| **IAM Role & Policies** | Free | $0.00 |
| **Lambda Storage** | Free (within free tier) | $0.00 |
| **API Gateway (first 333M)** | $3.50 per million requests | Variable |
| **CloudWatch Logs** | $0.50 per GB ingested | ~$0.50 - $2.00 |

---

## Usage-Based Costs

### 1. **API Gateway** 
```
First 333 million requests: $3.50 per million
Next 667 million requests: $2.80 per million

Examples:
- 1,000 requests/day   = 30K/month  = ~$0.11/month
- 10,000 requests/day  = 300K/month = ~$1.05/month
- 100,000 requests/day = 3M/month   = ~$10.50/month
```

### 2. **AWS Lambda**
```
Pricing:
- First 1M requests: FREE
- After that: $0.20 per 1M requests
- Compute: $0.0000166667 per GB-second

With 256 MB RAM, 3-5 second avg execution:
- 1,000 requests/day   = ~$0.00 (free tier)
- 10,000 requests/day  = ~$0.00 (free tier)
- 100,000 requests/day = ~$0.50/month
```

### 3. **AWS Bedrock - Claude 3 Haiku** ⚠️ **Main Cost Driver**
```
Input tokens:  $0.25 per 1 million tokens
Output tokens: $1.25 per 1 million tokens

Average prompt: ~200 tokens input
Average response: ~500 tokens output

Per request cost: ~$0.000675

Examples:
┌──────────────────┬────────────┬──────────────┬──────────────┐
│ Daily Requests   │ Monthly    │ Token Usage  │ Monthly Cost │
├──────────────────┼────────────┼──────────────┼──────────────┤
│ 100              │ 3,000      │ 2.1M tokens  │ $2.00        │
│ 500              │ 15,000     │ 10.5M tokens │ $10.00       │
│ 1,000            │ 30,000     │ 21M tokens   │ $20.00       │
│ 5,000            │ 150,000    │ 105M tokens  │ $100.00      │
│ 10,000           │ 300,000    │ 210M tokens  │ $200.00      │
└──────────────────┴────────────┴──────────────┴──────────────┘
```

### 4. **External API Calls** (Azure)
```
Your Azure API: No AWS charges
(Costs depend on your Azure infrastructure)
```

---

## AgentCore Gateway Pricing

### If Using Bedrock AgentCore Gateway Instead:

**NEW Costs:**
```
Bedrock Agent Gateway Pricing:
- Gateway creation: FREE
- Gateway management: FREE  
- API calls through gateway: $0.25 per 1,000 requests

Per Request: $0.00025
```

**Comparison Table:**

| Component | Current Setup | AgentCore Gateway |
|-----------|--------------|-------------------|
| **API Gateway** | $3.50 per 1M requests | Not needed ($0) |
| **Lambda** | $0.20 per 1M requests + compute | Not needed ($0) |
| **AgentCore Gateway** | Not used ($0) | $0.25 per 1,000 requests |
| **Bedrock Claude** | $0.25/$1.25 per 1M tokens | Same |
| **Management** | Manual code updates | Bedrock console managed |

**Monthly Cost Examples with AgentCore:**

```
┌──────────────────┬─────────────┬──────────────────┬──────────────────┐
│ Daily Requests   │ Monthly     │ Current Setup    │ AgentCore Setup  │
├──────────────────┼─────────────┼──────────────────┼──────────────────┤
│ 100              │ 3,000       │ $3.00            │ $2.75            │
│ 1,000            │ 30,000      │ $22.00           │ $28.00           │
│ 5,000            │ 150,000     │ $107.00          │ $137.50          │
│ 10,000           │ 300,000     │ $214.00          │ $275.00          │
└──────────────────┴─────────────┴──────────────────┴──────────────────┘

Breakdown for 1,000 req/day (AgentCore):
- AgentCore Gateway: $7.50  (30K × $0.00025)
- Bedrock Claude:    $20.00
- CloudWatch:        $0.50
─────────────────────────────
TOTAL:               $28/month
```

---

## Which is Cheaper?

**Current Setup (Lambda + API Gateway) is cheaper for:**
- ✅ Low to medium usage (< 2,000 requests/day)
- ✅ Cost: ~$22/month at 1,000 req/day

**AgentCore Gateway is better for:**
- ✅ High-level abstraction (easier management)
- ✅ Built-in Bedrock features
- ⚠️ But costs ~25% more at moderate usage

**Break-even point:** ~50-100 requests/day
- Below: Current setup cheaper
- Above: AgentCore slightly more expensive but easier to manage

---

## Updated Recommendation

**For your use case (enterprise team):**

**Stick with Current Setup if:**
- Cost-sensitive
- 1,000-5,000 requests/day
- Comfortable with Lambda/API Gateway
- **Savings: ~$6/month at 1,000 req/day**

**Switch to AgentCore if:**
- Want managed solution
- Don't want to maintain Lambda code
- Need Bedrock console integration
- **Extra cost: ~$6/month at 1,000 req/day**

---

## Total Cost Scenarios - Updated

### 💰 **Low Usage** (100 requests/day)
```
API Gateway:    $0.11
Lambda:         $0.00 (free tier)
Bedrock:        $2.00
CloudWatch:     $0.50
─────────────────────
TOTAL:          ~$3/month
```

### 💰 **Medium Usage** (1,000 requests/day)
```
API Gateway:    $1.05
Lambda:         $0.00 (free tier)
Bedrock:        $20.00
CloudWatch:     $1.00
─────────────────────
TOTAL:          ~$22/month
```

### 💰 **High Usage** (5,000 requests/day)
```
API Gateway:    $5.25
Lambda:         $0.30
Bedrock:        $100.00
CloudWatch:     $2.00
─────────────────────
TOTAL:          ~$107/month
```

### 💰 **Very High Usage** (10,000 requests/day)
```
API Gateway:    $10.50
Lambda:         $0.50
Bedrock:        $200.00
CloudWatch:     $3.00
─────────────────────
TOTAL:          ~$214/month
```

---

## Cost Optimization Tips

### 1. **Enable Response Caching**
```python
# Cache common queries in Lambda
cache = {}
if prompt in cache:
    return cache[prompt]
```
**Savings: 50-70% for repeated queries**

### 2. **Use Shorter System Prompts**
- Keep tool descriptions concise
- Reduce token count by 20-30%
**Savings: $4-6 per 1,000 daily requests**

### 3. **Implement Rate Limiting**
```python
# Already in API Gateway throttling settings
# 100 req/sec, 200 burst
```
**Prevents cost spikes from abuse**

### 4. **Set CloudWatch Alarms**
```bash
# Alert at different thresholds
$50  - Warning
$100 - Alert
$200 - Critical
```

### 5. **Use Request Filtering**
```python
# Block simple queries that don't need Bedrock
if len(prompt) < 5:
    return quick_response
```
**Savings: 10-20% of Bedrock calls**

---

## Comparison: Personal vs Enterprise Account

| Aspect | Personal (345527981530) | Enterprise (846069303018) |
|--------|------------------------|---------------------------|
| **Model Access** | ❌ Nova Lite (no tools) | ✅ Claude Haiku (TRUE agent) |
| **Agent Type** | Manual keyword routing | Autonomous tool use |
| **Cost per 1M tokens** | $0.30 input / $1.20 output | $0.25 input / $1.25 output |
| **Payment Required** | ✅ Yes (blocked) | ✅ Yes (likely active) |
| **Use Case** | Demo/Learning | Production-ready |
| **Typical Monthly** | $15-30 (if worked) | $20-100 (real usage) |

---

## Cost Controls in Deploy Script

The setup includes:
- ✅ API Gateway throttling (100 req/sec, 200 burst)
- ✅ Lambda timeout (30 seconds - prevents runaway costs)
- ✅ Lambda memory cap (256 MB)
- ⚠️ **Missing:** CloudWatch billing alarms (add after deployment)

---

## Recommended Starting Point

**For Testing:**
- Budget: $20-50/month
- Expected: 500-1,000 requests/day
- ~$20-30 actual spend

**For Production:**
- Budget: $100-200/month
- Expected: 3,000-5,000 requests/day
- ~$70-110 actual spend

---

## Hidden Costs to Watch

1. **Failed Requests** - Still consume Lambda + Bedrock tokens
2. **Retries** - Automatic retry logic doubles costs
3. **Large Responses** - Complex queries = more output tokens
4. **Tool Chaining** - Claude calling multiple tools = 2-3x cost per request

---

## Real-World Example

**Scenario:** Internal team of 20 people, 50 queries each/day

```
Daily requests: 1,000
Monthly requests: 30,000

Costs:
- API Gateway: $1.05
- Lambda: $0.00
- Bedrock: $20.00
- CloudWatch: $1.00
───────────────────
Total: ~$22/month

Cost per person: $1.10/month
Cost per query: $0.00073
```

---

## Bottom Line

**Minimum to start:** $3-5/month (testing/demo)
**Realistic production:** $20-100/month (team usage)
**High volume:** $200-500/month (department-wide)

**Main driver:** Bedrock token costs (85-90% of total)
**Most efficient:** 1,000-2,000 requests/day sweet spot

---

## Next Steps After Deployment

1. **Day 1-7:** Monitor actual usage patterns
2. **Week 2:** Adjust Lambda memory/timeout based on metrics
3. **Month 1:** Set up billing alarms at $50, $100, $200
4. **Ongoing:** Review CloudWatch metrics weekly

**Pro Tip:** Enable AWS Cost Explorer for detailed breakdown
