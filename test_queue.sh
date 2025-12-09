#!/bin/bash

# ============================================================
# test_queue.sh - EDM排队系统测试脚本
# ============================================================

WORK_DIR="/var/www/bioinf/TDMol"
cd "$WORK_DIR" || exit 1

echo "=========================================="
echo "EDM Queue System Test"
echo "=========================================="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 测试参数
NUM_TASKS=${1:-3}
TEST_EMAIL="test@example.com"

echo "Test configuration:"
echo "  Number of tasks to submit: $NUM_TASKS"
echo "  Test email: $TEST_EMAIL"
echo ""

# 检查队列系统是否已初始化
if [[ ! -f running.queue ]] || [[ ! -f waiting.queue ]]; then
    echo "Queue system not initialized. Initializing..."
    bash init_queue.sh
    echo ""
fi

# 显示初始状态
echo "=========================================="
echo "Initial queue status:"
echo "=========================================="
bash check_queue.sh
echo ""

# 提交测试任务
echo "=========================================="
echo "Submitting $NUM_TASKS test tasks..."
echo "=========================================="

for i in $(seq 1 $NUM_TASKS); do
    TASK_ID="TEST_$(date +%Y%m%d%H%M%S)_${i}"
    TEST_INPUT="upload/${TASK_ID}.txt"
    echo "Generate molecules with benzene ring and amine group" > "$TEST_INPUT"
    echo "[$i/$NUM_TASKS] Submitting task: $TASK_ID"
    bash queue_edm.sh "$TEST_EMAIL" "$TASK_ID" >> logs/test_queue.log 2>&1 &
    sleep 1
done

echo ""
echo "All tasks submitted!"
echo ""
sleep 2

echo "=========================================="
echo "Current queue status:"
echo "=========================================="
bash check_queue.sh

echo ""
echo "=========================================="
echo "Monitor commands:"
echo "=========================================="
echo "  Watch queue status:  watch -n 2 bash check_queue.sh"
echo "  View queue logs:     tail -f logs/queue.log"
echo "  Check running tasks: cat running.queue"
echo "  Check waiting tasks: cat waiting.queue"
echo ""
