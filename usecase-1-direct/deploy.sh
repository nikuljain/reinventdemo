#!/bin/bash
set -e

echo "🚀 Deploying Use Case 1: Direct HTTP Tools"
echo "==========================================="

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

# Start Flask
echo ""
echo "✓ Starting Flask on http://localhost:5000"
echo ""
echo "Try asking:"
echo "  'Compare security on api2 vs api3'"
echo "  'What features does api1 detect?'"
echo "  'List all security settings across the APIs'"
echo ""
python3 -u app.py
