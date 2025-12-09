# 部署测试脚本到服务器

## 方法1：直接在服务器上创建（推荐）

在服务器终端执行以下命令（复制整个代码块）：

```bash
cd /var/www/bioinf2/edm_web

# 创建 test_queue.sh
cat > test_queue.sh << 'EOFTEST'
#!/bin/bash

# ============================================================
# test_queue.sh - EDM排队系统测试脚本
# ============================================================

WORK_DIR="/var/www/bioinf2/edm_web"
cd "$WORK_DIR" || exit 1

echo "=========================================="
echo "EDM Queue System Test"
echo "=========================================="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 测试参数
NUM_TASKS=${1:-3}  # 默认提交3个测试任务
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
    # 生成测试任务ID
    TASK_ID="TEST_$(date +%Y%m%d%H%M%S)_${i}"

    # 创建测试输入文件
    TEST_INPUT="upload/${TASK_ID}.txt"
    echo "Generate molecules with benzene ring and amine group" > "$TEST_INPUT"

    echo "[$i/$NUM_TASKS] Submitting task: $TASK_ID"

    # 提交到队列（后台运行，避免阻塞）
    bash queue_edm.sh "$TEST_EMAIL" "$TASK_ID" >> logs/test_queue.log 2>&1 &

    # 稍微延迟，避免任务ID冲突
    sleep 1
done

echo ""
echo "All tasks submitted!"
echo ""

# 等待2秒让任务开始
sleep 2

# 显示当前状态
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
EOFTEST

# 设置执行权限
chmod +x test_queue.sh

# 验证创建成功
echo "test_queue.sh 创建成功！"
ls -l test_queue.sh

# 运行测试
echo ""
echo "现在运行测试..."
./test_queue.sh
```

---

## 方法2：使用 SCP 上传（从Windows本地）

如果您在Windows本地有文件，可以使用以下命令上传：

### 使用 Git Bash 或 WSL：
```bash
# 上传到前端服务器
scp D:/研究组课题/project1：Web搭建/web_apps/test_queue.sh www-data@前端服务器IP:/var/www/bioinf2/edm_web/

# 然后SSH到服务器
ssh www-data@前端服务器IP

# 设置权限
cd /var/www/bioinf2/edm_web
chmod +x test_queue.sh
```

### 使用 WinSCP（图形界面）：
1. 打开 WinSCP
2. 连接到前端服务器
3. 导航到 `/var/www/bioinf2/edm_web/`
4. 上传 `test_queue.sh`
5. 右键文件 → Properties → 勾选 Execute 权限

---

## 方法3：手动复制粘贴

1. 在服务器上执行：
```bash
cd /var/www/bioinf2/edm_web
nano test_queue.sh
```

2. 复制以下内容粘贴到 nano 编辑器：
```bash
#!/bin/bash

# ============================================================
# test_queue.sh - EDM排队系统测试脚本
# ============================================================

WORK_DIR="/var/www/bioinf2/edm_web"
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
```

3. 按 `Ctrl+X`，然后按 `Y`，再按 `Enter` 保存

4. 设置权限并运行：
```bash
chmod +x test_queue.sh
./test_queue.sh
```

---

## 推荐使用方法1

**最简单的方式是直接在服务器上执行方法1的命令**，这样无需文件传输，直接创建并运行。
