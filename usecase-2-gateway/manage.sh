#!/usr/bin/env bash
set -euo pipefail

usage(){
  cat <<EOF
Usage: $0 <command>
Commands:
  create   - Create AgentCore gateway, configure targets, and start local app
  start    - Start the Flask app (foreground via nohup)
  stop     - Stop the Flask app
  destroy  - Run cleanup to delete gateway, IAM role, and stop app
  status   - Show process status and list gateways (AWS)
EOF
}

cmd=${1:-}
if [ -z "$cmd" ]; then usage; exit 1; fi

case "$cmd" in
  create)
    echo "Creating AgentCore Gateway and registering targets..."
    if ! aws sts get-caller-identity &>/dev/null; then
      echo "AWS credentials not found. Run: aws sso login --profile <profile>"; exit 1
    fi
    python3 setup-gateway.py
    python3 configure-targets.py
    $0 start
    ;;

  start)
    echo "Installing deps (if any) and starting Flask app..."
    if [ -f requirements.txt ]; then pip3 install -q -r requirements.txt || true; fi
    nohup python3 app.py > /tmp/usecase2_app.log 2>&1 &
    echo $! > /tmp/usecase2.pid
    echo "Started (pid=$(cat /tmp/usecase2.pid)). Logs: /tmp/usecase2_app.log"
    ;;

  stop)
    echo "Stopping Flask app..."
    if [ -f /tmp/usecase2.pid ]; then
      kill "$(cat /tmp/usecase2.pid)" 2>/dev/null || true
      rm -f /tmp/usecase2.pid
    else
      pkill -f "app.py" || true
    fi
    echo "Stopped"
    ;;

  destroy)
    echo "Destroying AWS resources (gateway, targets, IAM role) and stopping app..."
    set +e
    ./cleanup.sh || true
    $0 stop || true
    rm -f gateway_id.txt || true
    rm -f /tmp/usecase2.pid || true
    set -e
    echo "Destroy complete"
    ;;

  status)
    echo "Process status:"
    if [ -f /tmp/usecase2.pid ]; then ps -p "$(cat /tmp/usecase2.pid)" -o pid,cmd || true; else ps aux | egrep 'app.py' | egrep -v egrep || echo "no process found"; fi
    echo
    echo "Listing AgentCore gateways (us-east-1):"
    python3 - <<PY
import boto3, json
client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
try:
    print(json.dumps(client.list_gateways(), indent=2))
except Exception as e:
    print('ERROR:', e)
PY
    ;;

  *) usage; exit 2 ;;
esac
