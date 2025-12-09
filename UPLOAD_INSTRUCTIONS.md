# 文件上传说明

## 问题说明

Windows和Linux使用不同的换行符：
- Windows: CRLF (`\r\n`)
- Linux: LF (`\n`)

直接上传Windows创建的shell脚本到Linux会导致错误：
```
bash: ./test_queue.sh: /bin/bash^M: bad interpreter: No such file or directory
```

---

## 解决方案

### 方案1：上传后转换（推荐）

上传文件到服务器后，执行以下命令转换换行符：

```bash
# 如果服务器没有 dos2unix，先安装
sudo apt-get install dos2unix

# 转换文件
dos2unix test_queue.sh

# 设置执行权限
chmod +x test_queue.sh

# 运行
./test_queue.sh
```

---

### 方案2：使用sed转换

如果没有dos2unix工具，使用sed命令：

```bash
# 转换换行符
sed -i 's/\r$//' test_queue.sh

# 设置执行权限
chmod +x test_queue.sh

# 运行
./test_queue.sh
```

---

### 方案3：使用正确的上传工具

#### 使用 WinSCP 上传（推荐）

1. 打开 WinSCP
2. 设置 → 编辑器 → 外部编辑器
3. **重要**：勾选 "Transfer → Text (Auto-detect)" 或 "Text"
4. 上传时会自动转换换行符

#### 使用 Git Bash 的 scp

```bash
# Git Bash 会自动处理换行符
scp test_queue.sh user@server:/path/to/destination/
```

#### 使用 WSL (Windows Subsystem for Linux)

```bash
# 在WSL中，先转换文件
dos2unix /mnt/d/研究组课题/project1：Web搭建/web_apps/test_queue.sh

# 然后上传
scp /mnt/d/研究组课题/project1：Web搭建/web_apps/test_queue.sh user@server:/path/
```

---

### 方案4：直接在服务器创建（最简单）

不上传文件，直接在服务器上执行以下命令：

```bash
cd /var/www/bioinf2/edm_web

cat > test_queue.sh << 'EOF'
#!/bin/bash

WORK_DIR="/var/www/bioinf2/edm_web"
cd "$WORK_DIR" || exit 1

echo "=========================================="
echo "EDM Queue System Test"
echo "=========================================="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

NUM_TASKS=${1:-3}
TEST_EMAIL="test@example.com"

echo "Test configuration:"
echo "  Number of tasks to submit: $NUM_TASKS"
echo "  Test email: $TEST_EMAIL"
echo ""

if [[ ! -f running.queue ]] || [[ ! -f waiting.queue ]]; then
    echo "Queue system not initialized. Initializing..."
    bash init_queue.sh
    echo ""
fi

echo "=========================================="
echo "Initial queue status:"
echo "=========================================="
bash check_queue.sh
echo ""

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
EOF

chmod +x test_queue.sh
echo "test_queue.sh created successfully!"
./test_queue.sh
```

---

## 需要上传的文件列表

以下文件都需要使用上述方法之一处理换行符问题：

- `test_queue.sh` - 测试脚本
- `init_queue.sh` - 初始化队列
- `check_queue.sh` - 检查队列状态
- `queue_edm.sh` - 排队管理
- `clear_queue.sh` - 清空队列
- `EDM.sh` - 前端执行脚本
- `EDM_backend.sh` - 后端执行脚本

---

## 验证文件格式

上传后可以用以下命令验证文件格式：

```bash
# 查看文件类型
file test_queue.sh

# 正确的输出应该是：
# test_queue.sh: Bash script, ASCII text executable

# 如果看到 "with CRLF line terminators" 就需要转换
```

---

## 推荐方案

**对于新手用户，推荐使用方案4（直接在服务器创建）**，这样可以完全避免换行符问题。
