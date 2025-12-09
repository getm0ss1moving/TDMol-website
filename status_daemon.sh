#!/bin/bash

# ============================================================
# status_daemon.sh - 检查队列守护进程状态
# ============================================================

WORK_DIR="/var/www/bioinf/TDMol"
cd "$WORK_DIR" || exit 1

echo "=========================================="
echo "EDM Queue Daemon Status"
echo "=========================================="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

PIDFILE="logs/queue_daemon.pid"

# 检查守护进程状态
if [[ ! -f "$PIDFILE" ]]; then
    echo "Status: NOT RUNNING"
    echo ""
    echo "To start daemon: bash start_daemon.sh"
else
    PID=$(cat "$PIDFILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Status: RUNNING"
        echo "  PID: $PID"
        echo "  Uptime: $(ps -p $PID -o etime= | xargs)"
        echo "  Memory: $(ps -p $PID -o rss= | awk '{printf "%.1f MB", $1/1024}')"
    else
        echo "Status: NOT RUNNING (stale PID file)"
        rm -f "$PIDFILE"
    fi
fi

echo ""
echo "=========================================="
echo "Queue Status"
echo "=========================================="

# 检查运行中的任务
running_count=$(wc -l < running.queue 2>/dev/null || echo 0)
echo "Running tasks: $running_count"
if [[ $running_count -gt 0 ]]; then
    cat running.queue | while read line; do
        email=$(echo $line | awk '{print $1}')
        task_id=$(echo $line | awk '{print $2}')
        echo "  - Task: $task_id (Email: $email)"
    done
fi

echo ""

# 检查等待中的任务
waiting_count=$(wc -l < waiting.queue 2>/dev/null || echo 0)
echo "Waiting tasks: $waiting_count"
if [[ $waiting_count -gt 0 ]]; then
    head -5 waiting.queue | while read line; do
        email=$(echo $line | awk '{print $1}')
        task_id=$(echo $line | awk '{print $2}')
        echo "  - Task: $task_id (Email: $email)"
    done
    if [[ $waiting_count -gt 5 ]]; then
        echo "  ... and $((waiting_count - 5)) more"
    fi
fi

echo ""
echo "=========================================="
echo "Recent Daemon Activity (last 10 lines)"
echo "=========================================="
if [[ -f logs/queue_daemon.log ]]; then
    tail -10 logs/queue_daemon.log
else
    echo "(No daemon log found)"
fi

echo ""
echo "=========================================="
echo "Commands:"
echo "  Start daemon:  bash start_daemon.sh"
echo "  Stop daemon:   bash stop_daemon.sh"
echo "  View logs:     tail -f logs/queue_daemon.log"
echo "=========================================="
