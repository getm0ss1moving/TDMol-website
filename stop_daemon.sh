#!/bin/bash

# ============================================================
# stop_daemon.sh - 停止队列守护进程
# ============================================================

WORK_DIR="/var/www/bioinf/TDMol"
cd "$WORK_DIR" || exit 1

PIDFILE="logs/queue_daemon.pid"

if [[ ! -f "$PIDFILE" ]]; then
    echo "Queue daemon is not running (no PID file found)"
    exit 0
fi

PID=$(cat "$PIDFILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "Queue daemon is not running (stale PID file)"
    rm -f "$PIDFILE"
    exit 0
fi

echo "Stopping queue daemon (PID: $PID)..."
kill "$PID"

# 等待进程结束
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "Queue daemon stopped successfully"
        rm -f "$PIDFILE"
        exit 0
    fi
    sleep 1
done

# 如果还没停止，强制杀死
echo "Daemon not responding, force killing..."
kill -9 "$PID" 2>/dev/null
rm -f "$PIDFILE"
echo "Queue daemon force stopped"
