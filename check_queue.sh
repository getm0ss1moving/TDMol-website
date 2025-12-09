#!/bin/bash

# ============================================================
# check_queue.sh - 查看EDM排队系统状态
# ============================================================

WORK_DIR="/var/www/bioinf/TDMol"
cd "$WORK_DIR" || exit 1

echo "========================================"
echo "EDM Queue System Status"
echo "========================================"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查队列文件是否存在
if [[ ! -f running.queue ]] || [[ ! -f waiting.queue ]]; then
    echo "ERROR: Queue files not found!"
    echo "Please run: bash init_queue.sh"
    exit 1
fi

# 统计运行中的任务
running_count=$(wc -l < running.queue)
echo "Running tasks: $running_count"
if [[ $running_count -gt 0 ]]; then
    echo "----------------------------------------"
    cat running.queue | while read line; do
        email=$(echo $line | awk '{print $1}')
        task_id=$(echo $line | awk '{print $2}')
        echo "  Task ID: $task_id"
        echo "  Email: $email"
        echo ""
    done
else
    echo "  (No tasks currently running)"
    echo ""
fi

# 统计等待中的任务
waiting_count=$(wc -l < waiting.queue)
echo "Waiting tasks: $waiting_count"
if [[ $waiting_count -gt 0 ]]; then
    echo "----------------------------------------"
    cat waiting.queue | while read line; do
        email=$(echo $line | awk '{print $1}')
        task_id=$(echo $line | awk '{print $2}')
        position=$(($(grep -n "$task_id" waiting.queue | cut -d: -f1)))
        echo "  Position: $position"
        echo "  Task ID: $task_id"
        echo "  Email: $email"
        echo ""
    done
else
    echo "  (No tasks waiting)"
    echo ""
fi

echo "========================================"
echo "Recent queue activity (last 10 events):"
echo "========================================"
if [[ -f logs/queue.log ]]; then
    tail -10 logs/queue.log
else
    echo "(No queue log found)"
fi

echo ""
echo "========================================"
echo "Summary:"
echo "  Total running: $running_count"
echo "  Total waiting: $waiting_count"
echo "  Total tasks: $((running_count + waiting_count))"
echo "========================================"
