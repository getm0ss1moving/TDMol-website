#!/bin/bash

# ============================================================
# start_daemon.sh - 启动队列守护进程
# ============================================================

WORK_DIR="/var/www/bioinf/TDMol"
cd "$WORK_DIR" || exit 1

echo "Starting EDM Queue Daemon..."

# 检查是否已在运行
if [[ -f logs/queue_daemon.pid ]]; then
    PID=$(cat logs/queue_daemon.pid)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "ERROR: Daemon already running (PID: $PID)"
        echo "To stop it, run: bash stop_daemon.sh"
        exit 1
    fi
fi

# 确保队列文件存在
if [[ ! -f running.queue ]] || [[ ! -f waiting.queue ]]; then
    echo "Initializing queue system..."
    bash init_queue.sh
fi

# 启动守护进程（后台运行）
nohup bash queue_daemon.sh > logs/daemon_nohup.log 2>&1 &

# 等待PID文件创建
sleep 1

if [[ -f logs/queue_daemon.pid ]]; then
    PID=$(cat logs/queue_daemon.pid)
    echo "Queue daemon started successfully!"
    echo "  PID: $PID"
    echo "  Log: logs/queue_daemon.log"
    echo ""
    echo "To check status: bash status_daemon.sh"
    echo "To stop daemon: bash stop_daemon.sh"
else
    echo "ERROR: Failed to start daemon"
    echo "Check logs/daemon_nohup.log for errors"
    exit 1
fi
