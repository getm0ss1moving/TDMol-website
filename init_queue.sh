#!/bin/bash

# ============================================================
# init_queue.sh - 初始化EDM排队系统
# ============================================================
# 功能：
#   1. 创建队列文件
#   2. 设置正确的权限
#   3. 清空旧的队列数据
# ============================================================

WORK_DIR="/var/www/bioinf/TDMol"

echo "Initializing EDM queue system..."

# 进入工作目录
cd "$WORK_DIR" || exit 1

# 创建logs目录（如果不存在）
mkdir -p logs

# 创建或清空队列文件
> running.queue
> waiting.queue

# 设置权限（允许web服务器写入）
chmod 666 running.queue
chmod 666 waiting.queue
chmod 755 queue_edm.sh
chmod 755 EDM.sh

echo "Queue files created:"
echo "  - running.queue (current running tasks)"
echo "  - waiting.queue (queued tasks)"
echo ""
echo "Permissions set:"
ls -l running.queue waiting.queue queue_edm.sh EDM.sh
echo ""
echo "Queue system initialized successfully!"
echo ""
echo "Usage:"
echo "  bash queue_edm.sh <email> <timeVar>"
echo ""
echo "To check queue status:"
echo "  cat running.queue  # Currently running tasks"
echo "  cat waiting.queue  # Waiting tasks"
