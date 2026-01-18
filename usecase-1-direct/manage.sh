#!/usr/bin/env bash
set -euo pipefail

usage(){
  cat <<EOF
Usage: $0 <command>
Commands:
  create   - Create resources (none for usecase-1) and start local app
  start    - Start the Flask app (foreground via nohup)
  stop     - Stop the Flask app
  destroy  - Stop the Flask app and remove local artifacts
  status   - Show process status and HTTP check
EOF
}

cmd=${1:-}
if [ -z "$cmd" ]; then usage; exit 1; fi

case "$cmd" in
  create)
    echo "Use Case 1 has no AWS resources. Starting the app..."
    $0 start
    ;;

  start)
    echo "Installing Python deps (if any) and starting Flask app..."
    if [ -f requirements.txt ]; then pip3 install -q -r requirements.txt || true; fi
    nohup python3 app.py > /tmp/usecase1_app.log 2>&1 &
    echo $! > /tmp/usecase1.pid
    echo "Started (pid=$(cat /tmp/usecase1.pid)). Logs: /tmp/usecase1_app.log"
    ;;

  stop)
    echo "Stopping Flask app..."
    if [ -f /tmp/usecase1.pid ]; then
      kill "$(cat /tmp/usecase1.pid)" 2>/dev/null || true
      rm -f /tmp/usecase1.pid
    else
      pkill -f "app.py" || true
    fi
    echo "Stopped"
    ;;

  destroy)
    echo "Destroying local artifacts and stopping app"
    $0 stop
    rm -f gateway_id.txt || true
    rm -f /tmp/usecase1.pid || true
    echo "Destroyed"
    ;;

  status)
    echo "Process status:"
    if [ -f /tmp/usecase1.pid ]; then ps -p "$(cat /tmp/usecase1.pid)" -o pid,cmd || true; else ps aux | egrep 'app.py' | egrep -v egrep || echo "no process found"; fi
    echo
    echo "HTTP check (root):"
    curl -sS -I http://127.0.0.1:5000/ || true
    ;;

  *) usage; exit 2 ;;
esac
