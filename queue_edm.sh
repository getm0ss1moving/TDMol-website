#!/bin/bash

# ============================================================
# queue_edm.sh - EDM任务排队管理系统
# ============================================================
# 功能：
#   1. 限制同时运行的EDM任务数量（防止硬件过载）
#   2. 自动排队和调度任务
#   3. 任务完成后自动启动下一个等待的任务
#
# 参数：
#   $1 = email
#   $2 = timeVar (任务ID)
#
# 队列文件：
#   running.queue - 正在运行的任务列表
#   waiting.queue - 等待执行的任务列表
# ============================================================

set -e

# 工作目录（EDM web应用的根目录）
WORK_DIR="/var/www/bioinf/TDMol"
cd "$WORK_DIR"

# 确保队列文件存在
touch running.queue
touch waiting.queue

# 最大并发任务数（建议1-2个，因为EDM模型推理消耗大量GPU/CPU资源）
MAX_CONCURRENT=1

# ============================================================
# 清理和调度函数
# ============================================================
cleanup_and_next() {
    cd "$WORK_DIR"

    local job_id="$1"

    # 从running.queue中删除已完成的任务
    if [[ -z "$job_id" ]]; then
        # 如果job_id为空，删除包含"None"的行
        sed -i '/None/d' running.queue
    else
        # 删除匹配的任务行
        sed -i "/$job_id/d" running.queue
    fi

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task $job_id completed, removed from running queue"

    # 检查waiting.queue中是否还有等待的任务
    rowInfoNew=$(wc -l waiting.queue 2>/dev/null || echo "0")
    rowNew=$(echo $rowInfoNew | awk '{print $1}')

    if [[ $rowNew -gt 0 ]]; then
        # 从等待队列取出第一个任务
        cmdLineNew=$(head -n 1 waiting.queue)
        email_new=$(echo $cmdLineNew | awk '{print $1}')
        timevar_new=$(echo $cmdLineNew | awk '{print $2}')

        # 从waiting.queue中删除该任务
        sed -i '1d' waiting.queue

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting next task from queue: $timevar_new"

        # 启动下一个任务（后台运行）
        bash "$WORK_DIR/queue_edm.sh" "$email_new" "$timevar_new" >> "$WORK_DIR/logs/queue.log" 2>&1 &
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] No more tasks in waiting queue"
    fi
}

# ============================================================
# 主逻辑
# ============================================================

# 获取参数
email="$1"
timeVar="$2"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========================================"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] New task request: $timeVar (email: $email)"

# trap确保任务完成后一定会执行清理和调度
trap "cleanup_and_next '$timeVar'" EXIT

# 检查当前运行的任务数量
rowInfo=$(wc -l running.queue 2>/dev/null || echo "0")
row=$(echo $rowInfo | awk '{print $1}')

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running tasks: $row / $MAX_CONCURRENT"

if [[ $row -lt $MAX_CONCURRENT ]]; then
    # 有空闲槽位，立即执行任务
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Slot available, starting task immediately"
    echo "$email $timeVar" >> running.queue

    # 执行EDM任务
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Executing: bash EDM.sh '$email' '$timeVar'"
    bash "$WORK_DIR/EDM.sh" "$email" "$timeVar"

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task $timeVar finished successfully"
else
    # 没有空闲槽位，加入等待队列
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] All slots occupied, adding to waiting queue"
    echo "$email $timeVar" >> waiting.queue

    # 获取队列位置
    queue_position=$(wc -l waiting.queue | awk '{print $1}')
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task $timeVar queued at position $queue_position"

    # 不执行trap（因为任务还没开始）
    trap - EXIT
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] queue_edm.sh finished for task $timeVar"
