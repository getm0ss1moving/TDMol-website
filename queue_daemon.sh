#!/bin/bash

# ============================================================
# queue_daemon.sh - EDM队列守护进程
# ============================================================
# 功能：
#   1. 持续运行，监控队列状态
#   2. 自动从waiting.queue启动任务
#   3. 检测僵死任务并清理
# ============================================================

WORK_DIR="/var/www/bioinf/TDMol"
cd "$WORK_DIR" || exit 1

# 最大并发任务数
MAX_CONCURRENT=1

# 检查间隔（秒）
CHECK_INTERVAL=10

# 任务超时时间（秒） - 150分钟 = 9000秒
TASK_TIMEOUT=9000

# 日志文件
DAEMON_LOG="logs/queue_daemon.log"
mkdir -p logs

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$DAEMON_LOG"
}

# 检查守护进程是否已在运行
check_already_running() {
    PIDFILE="logs/queue_daemon.pid"
    if [[ -f "$PIDFILE" ]]; then
        OLD_PID=$(cat "$PIDFILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            log "ERROR: Queue daemon already running (PID: $OLD_PID)"
            log "To stop it, run: kill $OLD_PID"
            exit 1
        else
            log "Removing stale PID file"
            rm -f "$PIDFILE"
        fi
    fi
    echo $$ > "$PIDFILE"
}

# 清理函数（退出时执行）
cleanup() {
    log "Queue daemon stopping..."
    rm -f logs/queue_daemon.pid
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 启动任务的函数
start_next_task() {
    # 检查是否有等待的任务
    if [[ ! -f waiting.queue ]]; then
        return
    fi

    waiting_count=$(wc -l < waiting.queue 2>/dev/null || echo 0)
    if [[ $waiting_count -eq 0 ]]; then
        return
    fi

    # 检查当前运行任务数
    running_count=$(wc -l < running.queue 2>/dev/null || echo 0)

    if [[ $running_count -ge $MAX_CONCURRENT ]]; then
        return
    fi

    # 取出第一个等待任务
    task_line=$(head -n 1 waiting.queue)
    email=$(echo "$task_line" | awk '{print $1}')
    task_id=$(echo "$task_line" | awk '{print $2}')

    # 从waiting.queue删除
    sed -i '1d' waiting.queue

    log "Starting task from queue: $task_id (email: $email)"

    # 启动任务（后台运行）
    bash queue_edm.sh "$email" "$task_id" >> logs/queue_daemon_tasks.log 2>&1 &

    log "Task $task_id started in background"
}

# 转换时间为秒数的函数
# 输入格式: [[dd-]hh:]mm:ss
# 输出: 总秒数
parse_elapsed_time() {
    local time_str="$1"
    local total_seconds=0

    # 检查是否包含天数（格式: dd-hh:mm:ss）
    if [[ "$time_str" =~ ([0-9]+)-(.+) ]]; then
        local days="${BASH_REMATCH[1]}"
        time_str="${BASH_REMATCH[2]}"
        total_seconds=$((days * 86400))
    fi

    # 分割时:分:秒
    IFS=':' read -ra parts <<< "$time_str"
    local len=${#parts[@]}

    if [[ $len -eq 3 ]]; then
        # hh:mm:ss
        total_seconds=$((total_seconds + parts[0] * 3600 + parts[1] * 60 + parts[2]))
    elif [[ $len -eq 2 ]]; then
        # mm:ss
        total_seconds=$((total_seconds + parts[0] * 60 + parts[1]))
    elif [[ $len -eq 1 ]]; then
        # ss
        total_seconds=$((total_seconds + parts[0]))
    fi

    echo "$total_seconds"
}

# 清理僵死任务和超时任务的函数
cleanup_dead_tasks() {
    if [[ ! -f running.queue ]]; then
        return
    fi

    while IFS= read -r line; do
        task_id=$(echo "$line" | awk '{print $2}')

        # 查找对应的进程
        pid=$(pgrep -f "EDM.sh.*$task_id" | head -1)

        if [[ -z "$pid" ]]; then
            # 进程不存在 - 僵死任务
            log "WARNING: Found dead task: $task_id, removing from running.queue"
            sed -i "/$task_id/d" running.queue
        else
            # 进程存在 - 检查是否超时
            elapsed=$(ps -p "$pid" -o etime= 2>/dev/null | xargs)

            if [[ -n "$elapsed" ]]; then
                elapsed_seconds=$(parse_elapsed_time "$elapsed")

                if [[ $elapsed_seconds -gt $TASK_TIMEOUT ]]; then
                    log "WARNING: Task $task_id timeout (running for ${elapsed_seconds}s > ${TASK_TIMEOUT}s)"
                    log "Killing task $task_id (PID: $pid)"

                    # 杀死进程树（包括子进程）
                    pkill -P "$pid" 2>/dev/null || true
                    kill "$pid" 2>/dev/null || true

                    # 等待2秒让进程结束
                    sleep 2

                    # 如果还没死，强制杀死
                    if ps -p "$pid" > /dev/null 2>&1; then
                        kill -9 "$pid" 2>/dev/null || true
                    fi

                    # 从队列删除
                    sed -i "/$task_id/d" running.queue
                    log "Task $task_id killed and removed from queue"
                fi
            fi
        fi
    done < running.queue
}

# 主循环
main_loop() {
    log "=========================================="
    log "Queue Daemon Started"
    log "=========================================="
    log "Working directory: $WORK_DIR"
    log "Max concurrent tasks: $MAX_CONCURRENT"
    log "Check interval: ${CHECK_INTERVAL}s"
    log "Task timeout: ${TASK_TIMEOUT}s ($(($TASK_TIMEOUT / 60)) minutes)"
    log "PID: $$"
    log ""
    log "Press Ctrl+C to stop"
    log "=========================================="

    while true; do
        # 清理僵死任务
        cleanup_dead_tasks

        # 尝试启动等待的任务
        start_next_task

        # 等待一段时间再检查
        sleep $CHECK_INTERVAL
    done
}

# 主程序
check_already_running
main_loop
