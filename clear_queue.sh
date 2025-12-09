#!/bin/bash

# ============================================================
# clear_queue.sh - 清空EDM排队系统（紧急使用）
# ============================================================
# 警告：此脚本会清空所有等待中的任务！
# 只在系统出现问题时使用
# ============================================================

WORK_DIR="/var/www/bioinf/TDMol"
cd "$WORK_DIR" || exit 1

echo "========================================"
echo "EDM Queue Clear Utility"
echo "========================================"
echo "WARNING: This will clear all queued tasks!"
echo ""

# 显示当前状态
running_count=$(wc -l < running.queue 2>/dev/null || echo "0")
waiting_count=$(wc -l < waiting.queue 2>/dev/null || echo "0")

echo "Current status:"
echo "  Running tasks: $running_count"
echo "  Waiting tasks: $waiting_count"
echo ""

# 确认
read -p "Are you sure you want to clear the queue? (yes/no): " confirm

if [[ "$confirm" != "yes" ]]; then
    echo "Operation cancelled."
    exit 0
fi

# 备份队列文件
backup_dir="logs/queue_backup"
mkdir -p "$backup_dir"
timestamp=$(date '+%Y%m%d_%H%M%S')

if [[ -f running.queue ]]; then
    cp running.queue "$backup_dir/running.queue.$timestamp"
    echo "Backed up running.queue to $backup_dir/running.queue.$timestamp"
fi

if [[ -f waiting.queue ]]; then
    cp waiting.queue "$backup_dir/waiting.queue.$timestamp"
    echo "Backed up waiting.queue to $backup_dir/waiting.queue.$timestamp"
fi

# 清空队列
> running.queue
> waiting.queue

echo ""
echo "Queue cleared successfully!"
echo "Backup files saved in: $backup_dir/"
echo ""
echo "Cleared $running_count running tasks and $waiting_count waiting tasks"
echo ""
echo "To restore from backup:"
echo "  cp $backup_dir/running.queue.$timestamp running.queue"
echo "  cp $backup_dir/waiting.queue.$timestamp waiting.queue"
