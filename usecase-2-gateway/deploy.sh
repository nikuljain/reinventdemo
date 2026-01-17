#!/bin/bash
set -e

echo "🚀 Deploying Use Case 2: AgentCore Gateway + MCP Targets"
echo "========================================================"

# Check Python
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION"

# Install dependencies
echo "Installing dependencies..."
pip3 install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check AWS credentials
if aws sts get-caller-identity &>/dev/null; then
    ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    echo "✓ AWS Account: $ACCOUNT"
else
    echo "❌ AWS credentials not found. Run: aws sso login --profile <profile>"
    exit 1
fi

# Setup gateway
echo ""
echo "Creating AgentCore Gateway..."
python3 setup-gateway.py

# Configure targets
echo ""
echo "Registering MCP targets..."
python3 configure-targets.py

# Start Flask
echo ""
echo "✓ Starting Flask on http://localhost:5000"
echo ""
echo "The gateway is now handling your tool calls:"
echo "  User → Flask → Bedrock → AgentCore Gateway → Azure APIs"
echo ""
echo "Try asking:"
echo "  'Compare security on api2 vs api3'"
echo "  'What features does api1 detect?'"
echo ""
python3 -u app.py
