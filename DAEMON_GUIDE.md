# EDM 队列守护进程使用指南

## 📋 概述

队列守护进程会持续运行在后台，自动监控和调度任务队列，确保系统24/7不间断工作。

---

## 🎯 守护进程的作用

**传统方式（无守护进程）：**
- 用户提交任务 → queue_edm.sh 处理 → 任务完成后调度下一个
- **问题**：如果没有新任务提交，等待队列中的任务不会自动启动

**守护进程方式：**
- 守护进程持续运行，每10秒检查一次队列
- 自动从 waiting.queue 启动任务
- 自动清理僵死任务
- **优势**：完全自动化，无需人工干预

---

## 🚀 快速开始

### 方法1：使用脚本管理（推荐新手）

```bash
cd /var/www/bioinf2/edm_web

# 启动守护进程
bash start_daemon.sh

# 检查状态
bash status_daemon.sh

# 停止守护进程
bash stop_daemon.sh
```

### 方法2：使用 systemd 管理（推荐生产环境）

```bash
# 1. 安装服务
sudo cp edm-queue.service /etc/systemd/system/
sudo systemctl daemon-reload

# 2. 启动服务
sudo systemctl start edm-queue

# 3. 设置开机自启
sudo systemctl enable edm-queue

# 4. 查看状态
sudo systemctl status edm-queue

# 5. 查看日志
sudo journalctl -u edm-queue -f
```

---

## 📖 详细使用方法

### 启动守护进程

```bash
bash start_daemon.sh
```

**输出示例：**
```
Starting EDM Queue Daemon...
Queue daemon started successfully!
  PID: 12345
  Log: logs/queue_daemon.log

To check status: bash status_daemon.sh
To stop daemon: bash stop_daemon.sh
```

**守护进程会：**
- 在后台持续运行
- 每10秒检查一次队列
- 将日志写入 `logs/queue_daemon.log`

---

### 检查守护进程状态

```bash
bash status_daemon.sh
```

**输出示例：**
```
==========================================
EDM Queue Daemon Status
==========================================
Time: 2025-12-01 15:30:45

Status: RUNNING
  PID: 12345
  Uptime: 02:15:30
  Memory: 15.2 MB

==========================================
Queue Status
==========================================
Running tasks: 1
  - Task: 20251201153000 (Email: user@test.com)

Waiting tasks: 2
  - Task: 20251201153100 (Email: user2@test.com)
  - Task: 20251201153200 (Email: user3@test.com)

==========================================
Recent Daemon Activity (last 10 lines)
==========================================
[2025-12-01 15:30:00] Starting task from queue: 20251201153000
[2025-12-01 15:30:10] Task 20251201153000 started in background
...
```

---

### 停止守护进程

```bash
bash stop_daemon.sh
```

**输出示例：**
```
Stopping queue daemon (PID: 12345)...
Queue daemon stopped successfully
```

---

### 查看守护进程日志

```bash
# 实时查看日志
tail -f logs/queue_daemon.log

# 查看最近100行
tail -100 logs/queue_daemon.log

# 搜索特定任务
grep "20251201153000" logs/queue_daemon.log
```

---

## 🔄 工作流程

```
守护进程启动
    ↓
每10秒循环检查
    ↓
┌─────────────────────────────────┐
│ 1. 清理僵死任务                  │
│    - 检查running.queue中的任务   │
│    - 如果进程不存在，从队列删除   │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ 2. 检查是否可以启动新任务         │
│    - 当前运行任务 < MAX_CONCURRENT│
│    - waiting.queue 中有任务      │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ 3. 启动新任务                    │
│    - 从waiting.queue取出第一个   │
│    - 调用 queue_edm.sh 启动      │
└─────────────────────────────────┘
    ↓
等待10秒，重复循环
```

---

## 🛠️ 配置参数

编辑 `queue_daemon.sh` 修改以下参数：

```bash
# 最大并发任务数（默认1）
MAX_CONCURRENT=1

# 检查间隔（秒，默认10）
CHECK_INTERVAL=10
```

**建议值：**
- `MAX_CONCURRENT=1`: 单GPU服务器
- `MAX_CONCURRENT=2`: 双GPU服务器
- `CHECK_INTERVAL=10`: 平衡响应速度和系统负载

---

## 🧪 测试守护进程

### 测试1：启动和停止

```bash
# 1. 启动
bash start_daemon.sh

# 2. 检查是否运行
bash status_daemon.sh

# 3. 查看日志
tail logs/queue_daemon.log

# 4. 停止
bash stop_daemon.sh

# 5. 确认已停止
bash status_daemon.sh
```

### 测试2：任务自动调度

```bash
# 1. 启动守护进程
bash start_daemon.sh

# 2. 提交3个测试任务
echo "Test 1" > upload/DAEMON_TEST_1.txt
echo "Test 2" > upload/DAEMON_TEST_2.txt
echo "Test 3" > upload/DAEMON_TEST_3.txt

echo "test@test.com DAEMON_TEST_1" >> waiting.queue
echo "test@test.com DAEMON_TEST_2" >> waiting.queue
echo "test@test.com DAEMON_TEST_3" >> waiting.queue

# 3. 实时监控（新终端）
watch -n 2 bash status_daemon.sh

# 4. 查看日志（另一个新终端）
tail -f logs/queue_daemon.log

# 期望看到：
# - 守护进程自动从waiting.queue取出任务
# - 任务依次启动
# - running.queue 和 waiting.queue 动态变化
```

### 测试3：崩溃恢复

```bash
# 1. 启动守护进程和一个任务
bash start_daemon.sh
bash queue_edm.sh "test@test.com" "CRASH_TEST" &

# 2. 手动杀死任务进程（模拟崩溃）
pkill -f "EDM.sh.*CRASH_TEST"

# 3. 等待10秒，守护进程会自动清理
sleep 10

# 4. 检查状态
bash status_daemon.sh

# 期望看到：
# - CRASH_TEST 已从 running.queue 删除
# - 日志显示 "Found dead task: CRASH_TEST"
```

---

## 🔧 故障排查

### 问题1：守护进程无法启动

**症状：**
```
ERROR: Daemon already running (PID: 12345)
```

**解决：**
```bash
# 检查进程是否真的在运行
ps aux | grep queue_daemon

# 如果没有运行，删除PID文件
rm logs/queue_daemon.pid

# 重新启动
bash start_daemon.sh
```

### 问题2：守护进程意外停止

**检查日志：**
```bash
tail -50 logs/queue_daemon.log
tail -50 logs/daemon_nohup.log
```

**常见原因：**
- 权限问题
- 磁盘空间满
- 手动kill -9

**解决：**
```bash
# 使用 systemd 自动重启（推荐）
sudo systemctl start edm-queue
sudo systemctl enable edm-queue
```

### 问题3：任务没有自动启动

**检查：**
```bash
# 1. 守护进程是否运行
bash status_daemon.sh

# 2. waiting.queue 格式是否正确
cat waiting.queue
# 正确格式: email taskID

# 3. running.queue 是否已满
cat running.queue
```

**解决：**
```bash
# 如果格式错误，手动修复
echo "test@test.com TASK001" >> waiting.queue

# 如果running.queue卡住，清理
> running.queue
```

---

## 📊 监控和维护

### 日常监控

```bash
# 每天检查一次守护进程状态
bash status_daemon.sh

# 查看今天的活动
grep "$(date +%Y-%m-%d)" logs/queue_daemon.log | tail -20
```

### 定期维护

```bash
# 每周清理旧日志
tail -1000 logs/queue_daemon.log > logs/queue_daemon.log.tmp
mv logs/queue_daemon.log.tmp logs/queue_daemon.log

# 每月检查磁盘空间
df -h /var/www/bioinf2/edm_web
du -sh logs/
```

### 性能监控

```bash
# 查看守护进程资源占用
ps aux | grep queue_daemon

# 查看所有EDM相关进程
ps aux | grep -E "(queue_daemon|queue_edm|EDM.sh)"

# 查看内存使用
free -h
```

---

## 🎛️ systemd 服务管理（推荐）

### 安装服务

```bash
# 1. 复制服务文件
sudo cp edm-queue.service /etc/systemd/system/

# 2. 重新加载 systemd
sudo systemctl daemon-reload

# 3. 启动服务
sudo systemctl start edm-queue

# 4. 设置开机自启
sudo systemctl enable edm-queue
```

### 常用命令

```bash
# 启动服务
sudo systemctl start edm-queue

# 停止服务
sudo systemctl stop edm-queue

# 重启服务
sudo systemctl restart edm-queue

# 查看状态
sudo systemctl status edm-queue

# 查看日志
sudo journalctl -u edm-queue -f

# 查看最近100行日志
sudo journalctl -u edm-queue -n 100

# 禁用开机自启
sudo systemctl disable edm-queue
```

### systemd 优势

✅ **自动重启**：进程崩溃自动重启
✅ **开机启动**：系统重启后自动运行
✅ **统一管理**：使用标准systemd命令
✅ **日志集成**：与系统日志集成
✅ **资源限制**：可以设置CPU、内存限制

---

## 📈 对比

| 特性 | 脚本管理 | systemd管理 |
|------|---------|-------------|
| 启动方式 | bash start_daemon.sh | systemctl start |
| 开机自启 | ❌ 手动 | ✅ 自动 |
| 崩溃重启 | ❌ 需手动 | ✅ 自动 |
| 日志管理 | 文件日志 | journald集成 |
| 易用性 | ⭐⭐⭐⭐⭐ 简单 | ⭐⭐⭐ 需root |
| 适用场景 | 测试、开发 | 生产环境 |

---

## 🎯 最佳实践

### 开发/测试环境

使用脚本管理：
```bash
bash start_daemon.sh    # 手动启动
bash status_daemon.sh   # 定期检查
bash stop_daemon.sh     # 需要时停止
```

### 生产环境

使用 systemd 管理：
```bash
sudo systemctl enable edm-queue   # 设置开机自启
sudo systemctl start edm-queue    # 启动服务
# 系统会自动管理，无需人工干预
```

---

## 📝 文件清单

创建的新文件：

- `queue_daemon.sh` - 守护进程主脚本
- `start_daemon.sh` - 启动脚本
- `stop_daemon.sh` - 停止脚本
- `status_daemon.sh` - 状态检查脚本
- `edm-queue.service` - systemd服务配置

生成的日志文件：

- `logs/queue_daemon.log` - 守护进程日志
- `logs/daemon_nohup.log` - nohup输出
- `logs/queue_daemon_tasks.log` - 任务启动日志
- `logs/daemon_systemd.log` - systemd标准输出
- `logs/daemon_systemd_error.log` - systemd错误输出

---

## 总结

守护进程提供了一个可靠的、自动化的队列管理方案：

✅ **24/7运行**：持续监控队列
✅ **自动调度**：无需人工干预
✅ **故障恢复**：自动清理僵死任务
✅ **易于管理**：简单的启动/停止命令
✅ **生产就绪**：支持systemd集成

**推荐使用流程：**
1. 测试阶段：使用 `bash start_daemon.sh`
2. 生产部署：使用 `systemctl enable edm-queue`
3. 日常维护：定期查看 `bash status_daemon.sh`

---

**最后更新：** 2025-12-01
**版本：** 1.0
