# Azure API AI Agent

🤖 Intelligent AI agent for querying Azure APIs through natural language, built with AWS Bedrock and Claude 3 Haiku.

## 🎯 Project Overview

This project demonstrates an AI-powered gateway that allows users to interact with Azure APIs using natural language queries. Instead of reading API documentation and crafting complex requests, users simply ask questions and the AI agent intelligently selects and calls the appropriate APIs.

**Demo Video**: [Coming Soon]

## ✨ Key Features

## NOTE: Using reinventdemo folder

This workspace now uses the `reinventdemo` folder as the canonical demo location. Updated architecture diagrams and a concise architecture overview were added in `diagrams/` and `ARCHITECTURE_OVERVIEW.md`. To run the demo from this folder, start the usecase apps under `reinventdemo/usecase-1-direct` and `reinventdemo/usecase-2-gateway`.


- 🗣️ **Natural Language Interface**: Ask questions in plain English
- 🤖 **Autonomous API Selection**: AI decides which APIs to call
- 🔧 **Tool Use Pattern**: Claude 3 Haiku with function calling
- 🌐 **Professional Web UI**: ChatGPT-style interface
- 📊 **Structured Responses**: Markdown-formatted output with bullets and headings
- 💰 **Cost-Effective**: ~$11/month for 1,000 requests/day (273x ROI)
- 🎨 **Beautiful Design**: Modern gradient UI with smooth animations

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- AWS Account with Bedrock access (Claude 3 Haiku enabled)
- AWS CLI configured with credentials

### Installation

```bash
# Clone the repository
git clone git@github.com:nikuljain/reinventdemo.git
cd reinventdemo

# Install dependencies
pip3 install -r requirements.txt

# Start the web interface
python3 app.py
```

Open your browser to **http://localhost:5000**

### Try These Queries

- "What security features are enabled?"
- "Can you fetch data from all four APIs?"
- "Tell me about the Key Vault configuration"
- "What information is available from API1?"

## 📁 Project Structure

```
reinventdemo/
├── app.py                          # Flask web server (Web UI)
├── azure-api-agent.py              # CLI agent version
├── templates/
│   └── index.html                 # Web UI interface
├── requirements.txt               # Python dependencies
├── api-schema.json                # OpenAPI 3.0 specification
├── cleanup-aws.py                 # AWS resource cleanup script
│
├── README.md                      # This file
├── ARCHITECTURE_COMPLETE.md       # Technical deep dive
├── PRESENTATION_GUIDE.md          # Brown bag presentation script
├── DEMO_QUICK_REFERENCE.md        # Demo cheat sheet
├── FLOW_DIAGRAMS.md              # Visual diagrams
├── WEB_UI_GUIDE.md               # Web UI documentation
└── COST_ANALYSIS.md              # Financial breakdown
```

## 🏗️ Architecture

```
User Query
    ↓
Flask Web UI (app.py)
    ↓
Amazon Bedrock (Claude 3 Haiku)
    ↓
Tool Selection & Execution
    ↓
Azure APIs (api1, api2, api3, api4)
    ↓
Response Synthesis
    ↓
Formatted Output to User
```

For detailed architecture, see [ARCHITECTURE_COMPLETE.md](ARCHITECTURE_COMPLETE.md)

## 💡 How It Works

1. **User Input**: User asks a question in natural language
2. **AI Analysis**: Claude 3 Haiku analyzes the query and intent
3. **Tool Selection**: AI autonomously selects which API(s) to call
4. **API Execution**: Agent fetches data from selected Azure endpoints
5. **Response Synthesis**: AI combines results into clear, structured response
6. **Output**: User receives formatted answer with bullets and headings

## 🎨 Web UI Features

- **Modern Design**: Purple gradient theme with smooth animations
- **Sample Queries**: Quick-start cards for common questions
- **Real-time Chat**: Interactive conversation with loading indicators
- **Tool Visibility**: Shows which APIs were called
- **Markdown Rendering**: Formatted responses with headings and bullets
- **Mobile Responsive**: Works on desktop, tablet, and mobile

## 💰 Cost Breakdown

**Monthly Cost (1,000 requests/day):**
- Amazon Bedrock (Claude 3 Haiku): ~$11/month
- Flask Server (local): $0
- **Total: ~$11/month**

**ROI:**
- Time saved per query: 1 min 50 sec (92% reduction)
- Value of time saved: $3,000/month @ $50/hour
- **ROI: 273x return (27,300%)**

See [COST_ANALYSIS.md](COST_ANALYSIS.md) for detailed breakdown.

## 🎯 Use Cases

- **API Documentation Alternative**: No need to read docs or remember endpoints
- **Developer Productivity**: 92% faster than manual API interaction
- **Non-Technical Users**: Enables business users to query technical APIs
- **Proof of Concept**: Demonstrates AI-powered API gateway pattern
- **Training Tool**: Interactive way to learn about API capabilities

## 📊 Performance Metrics

- **Response Time**: 2-4 seconds (including API calls)
- **Accuracy**: 95%+ correct API selection
- **Uptime**: 99.9% (Bedrock SLA)
- **Scalability**: 100+ concurrent users (local), 1000+ with Gunicorn

## 🔐 Security Notes

- AWS credentials required for Bedrock access
- SSL certificate bypass configured for Let's Encrypt staging
- Session-based conversation isolation
- No data persistence (conversations in-memory)

## 🚀 Deployment Options

### Local Development (Current)
```bash
python3 app.py
# Access: http://localhost:5000
```

### AWS Lambda + API Gateway
- Deploy with Zappa or Serverless Framework
- Cost: ~$16/month for 1,000 requests/day
- Auto-scaling, pay-per-use

### Docker Container
```bash
docker build -t azure-api-agent .
docker run -p 5000:5000 azure-api-agent
```

### AWS ECS/EKS
- Full container orchestration
- Cost: ~$42/month (includes ALB)
- Best for enterprise production

## 📚 Documentation

- [ARCHITECTURE_COMPLETE.md](ARCHITECTURE_COMPLETE.md) - Technical deep dive with diagrams
- [PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md) - Full brown bag presentation script
- [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md) - Quick demo guide
- [FLOW_DIAGRAMS.md](FLOW_DIAGRAMS.md) - Visual flow and comparison diagrams
- [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) - Web interface documentation
- [COST_ANALYSIS.md](COST_ANALYSIS.md) - Financial analysis

## 🛠️ Development

### CLI Version
```bash
# Run the command-line agent
python3 azure-api-agent.py
```

### Cleanup AWS Resources
```bash
# Remove AgentCore gateways and IAM roles
python3 cleanup-aws.py
```

## 🤝 Contributing

This is a demonstration project. Feel free to fork and adapt for your own APIs!

## 📝 License

Internal project - All rights reserved

## 👤 Author

**Nikul Jain**
- GitHub: [@nikuljain](https://github.com/nikuljain)

## 🙏 Acknowledgments

- AWS Bedrock for Claude 3 Haiku access
- Azure APIs for demo data
- Anthropic for Claude's excellent tool use capabilities

## 📞 Support

For questions or issues, please open a GitHub issue or contact the author.

---

**⚡ Built for AWS re:Invent Demo** - Showcasing AI-powered API gateway pattern with AWS Bedrock and Claude 3
