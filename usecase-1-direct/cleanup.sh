#!/bin/bash

echo "Cleaning up Use Case 1..."
pkill -f "python3.*app.py" || true
echo "✓ Stopped Flask process"
echo "✓ No AWS resources to delete (local only)"
