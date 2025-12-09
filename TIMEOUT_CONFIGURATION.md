# 任务超时配置说明

## 📋 概述

守护进程现在支持自动检测和终止超时任务。如果任务运行时间超过设定值，守护进程会自动：
1. 记录超时日志
2. 杀死超时进程
3. 从 running.queue 中删除
4. 自动启动下一个等待任务

---

## ⏱️ 当前配置

**默认超时时间：150分钟（9000秒）**

这意味着：
- 如果任务运行超过150分钟，守护进程会自动杀死该任务
- 适用于分子生成任务可能卡住或出现问题的情况

---

## 🔧 如何修改超时时间

### 方法1：编辑脚本（推荐）

编辑 `queue_daemon.sh` 文件：

```bash
nano queue_daemon.sh
```

找到第22行附近：

```bash
# 任务超时时间（秒） - 150分钟 = 9000秒
TASK_TIMEOUT=9000
```

修改为你想要的值：

```bash
# 示例：修改为180分钟
TASK_TIMEOUT=10800  # 180分钟 × 60秒 = 10800秒

# 示例：修改为2小时
TASK_TIMEOUT=7200   # 2小时 × 60分钟 × 60秒 = 7200秒

# 示例：修改为30分钟
TASK_TIMEOUT=1800   # 30分钟 × 60秒 = 1800秒
```

保存后重启守护进程：

```bash
bash stop_daemon.sh
bash start_daemon.sh
```

---

### 方法2：通过环境变量（高级）

在启动守护进程前设置环境变量：

```bash
# 设置为180分钟
export TASK_TIMEOUT=10800
bash start_daemon.sh
```

或修改 `start_daemon.sh` 脚本，在启动前设置：

```bash
# 在 start_daemon.sh 中添加
export TASK_TIMEOUT=10800
nohup bash queue_daemon.sh > logs/daemon_nohup.log 2>&1 &
```

---

## 📊 推荐超时值

根据不同场景推荐：

| 场景 | 推荐超时时间 | 秒数 | 说明 |
|------|-------------|------|------|
| 测试环境（3个分子） | 10分钟 | 600 | 正常3-5分钟，10分钟足够 |
| 开发环境（10个分子） | 30分钟 | 1800 | 正常10-20分钟 |
| 生产环境（100个分子） | 150分钟 | 9000 | 正常100-120分钟，留足余量 |
| 大批量（1000个分子） | 24小时 | 86400 | 超长任务 |

**计算公式：**
```
超时时间（秒） = 分钟数 × 60
```

**示例：**
- 60分钟 = 60 × 60 = 3600秒
- 120分钟 = 120 × 60 = 7200秒
- 150分钟 = 150 × 60 = 9000秒

---

## 🔍 如何验证超时设置

### 查看当前配置

启动守护进程后，查看日志：

```bash
tail logs/queue_daemon.log
```

你应该看到：

```
[2025-12-01 10:00:00] ==========================================
[2025-12-01 10:00:00] Queue Daemon Started
[2025-12-01 10:00:00] ==========================================
[2025-12-01 10:00:00] Working directory: /var/www/bioinf2/edm_web
[2025-12-01 10:00:00] Max concurrent tasks: 1
[2025-12-01 10:00:00] Check interval: 10s
[2025-12-01 10:00:00] Task timeout: 9000s (150 minutes)  ← 这里显示超时设置
[2025-12-01 10:00:00] PID: 12345
```

---

## 🧪 测试超时功能

### 测试1：正常任务（不超时）

```bash
# 1. 设置短超时（测试用）
# 编辑 queue_daemon.sh，设置 TASK_TIMEOUT=300（5分钟）

# 2. 重启守护进程
bash stop_daemon.sh
bash start_daemon.sh

# 3. 提交测试任务（3个分子，正常3-5分钟完成）
echo "Generate benzene" > upload/TIMEOUT_TEST.txt
bash queue_edm.sh "test@test.com" "TIMEOUT_TEST"

# 4. 监控（应该正常完成，不触发超时）
tail -f logs/queue_daemon.log
```

### 测试2：模拟超时任务

```bash
# 1. 创建一个会长时间运行的测试脚本
cat > test_long_task.sh << 'EOF'
#!/bin/bash
echo "Starting long task..."
sleep 600  # 睡眠10分钟
echo "Long task finished"
EOF
chmod +x test_long_task.sh

# 2. 设置超时为2分钟（测试用）
# 编辑 queue_daemon.sh，设置 TASK_TIMEOUT=120

# 3. 重启守护进程
bash stop_daemon.sh
bash start_daemon.sh

# 4. 手动添加任务到队列并启动脚本
echo "test@test.com LONG_TEST" >> running.queue
./test_long_task.sh &

# 5. 等待2分钟，观察日志
tail -f logs/queue_daemon.log

# 期望看到：
# [时间] WARNING: Task LONG_TEST timeout (running for 120s > 120s)
# [时间] Killing task LONG_TEST (PID: xxxxx)
# [时间] Task LONG_TEST killed and removed from queue
```

---

## 📝 超时日志示例

### 正常任务完成

```
[2025-12-01 10:00:00] Starting task from queue: 20251201100000
[2025-12-01 10:00:10] Task 20251201100000 started in background
...
[2025-12-01 10:05:00] WARNING: Found dead task: 20251201100000, removing from running.queue
```
（任务正常完成，进程退出，被检测为"dead"并清理）

### 超时任务被杀死

```
[2025-12-01 10:00:00] Starting task from queue: 20251201100000
[2025-12-01 10:00:10] Task 20251201100000 started in background
...
[2025-12-01 12:30:10] WARNING: Task 20251201100000 timeout (running for 9010s > 9000s)
[2025-12-01 12:30:10] Killing task 20251201100000 (PID: 12345)
[2025-12-01 12:30:12] Task 20251201100000 killed and removed from queue
[2025-12-01 12:30:20] Starting next task from queue: 20251201100100
```
（任务运行超过150分钟，被强制终止，下一个任务自动启动）

---

## ⚠️ 重要注意事项

### 1. 超时检测频率

超时检测每 `CHECK_INTERVAL` 秒执行一次（默认10秒）。

这意味着：
- 如果设置超时为9000秒
- 实际超时可能在 9000-9010秒 之间
- 误差 = ±CHECK_INTERVAL

**不影响使用，但需要知道有这个误差。**

### 2. 进程杀死顺序

守护进程杀死超时任务时：
1. 先杀子进程（`pkill -P`）
2. 再杀主进程（`kill`）
3. 等待2秒
4. 如果还没死，强制杀死（`kill -9`）

这确保进程树被完全清理。

### 3. 数据保存

**超时任务被杀死后：**
- ✅ 已生成的部分结果会保留（如果有）
- ❌ 未完成的生成会丢失
- ❌ 不会生成 brief.html 和 result_X.html

**建议：**
- 设置合理的超时时间，留足余量
- 定期检查日志，了解任务实际运行时间
- 如果频繁超时，可能需要优化代码或增加超时时间

---

## 🔍 故障排查

### 问题1：任务总是超时

**可能原因：**
1. 超时时间设置太短
2. 模型推理速度慢（GPU资源不足）
3. 生成分子数量太多

**解决方案：**
```bash
# 1. 增加超时时间
# 编辑 queue_daemon.sh
TASK_TIMEOUT=18000  # 增加到300分钟

# 2. 检查实际运行时间
grep "timeout" logs/queue_daemon.log

# 3. 减少生成分子数量（临时）
# 在 EDM_backend.sh 中修改默认值
NUM_MOLECULES=${3:-50}  # 从100改为50
```

### 问题2：超时不生效

**检查：**
```bash
# 1. 确认守护进程在运行
bash status_daemon.sh

# 2. 查看守护进程启动日志
head -20 logs/queue_daemon.log

# 3. 确认超时配置显示正确
grep "Task timeout" logs/queue_daemon.log
```

---

## 📊 性能影响

超时检测对系统性能的影响：

| 项目 | 影响 |
|------|------|
| CPU占用 | 极低（每10秒一次ps命令） |
| 内存占用 | 无影响 |
| 响应延迟 | ±10秒（CHECK_INTERVAL） |
| 准确性 | 高（基于进程实际运行时间） |

**结论：** 超时检测几乎不影响系统性能。

---

## 🎯 最佳实践

### 1. 根据环境设置超时

```bash
# 开发环境（快速失败）
TASK_TIMEOUT=1800  # 30分钟

# 测试环境（适中）
TASK_TIMEOUT=3600  # 60分钟

# 生产环境（保守）
TASK_TIMEOUT=9000  # 150分钟
```

### 2. 定期检查超时日志

```bash
# 查看最近的超时事件
grep "timeout" logs/queue_daemon.log | tail -10

# 统计超时次数
grep "timeout" logs/queue_daemon.log | wc -l
```

### 3. 根据实际情况调整

```bash
# 1. 记录正常任务的运行时间
grep "started in background" logs/queue_daemon.log

# 2. 找出最长的任务时间
# （需要手动分析日志）

# 3. 设置超时 = 最长任务时间 × 1.5
# 例如：最长任务120分钟，设置超时为180分钟
TASK_TIMEOUT=10800
```

---

## 总结

✅ **默认超时：150分钟（9000秒）**

✅ **修改方法：编辑 `queue_daemon.sh` 第22行**

✅ **验证方法：查看守护进程启动日志**

✅ **测试方法：使用短超时测试长任务**

✅ **监控方法：定期检查日志中的超时事件**

**当前配置适合生成100个分子的生产环境，如有需要可随时调整。**

---

**最后更新：** 2025-12-01
**当前默认超时：** 150分钟（9000秒）
