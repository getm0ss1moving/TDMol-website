# EDM 队列系统快速参考

## ⚡ 一分钟快速上手

### 首次部署

```bash
cd /var/www/bioinf2/edm_web

# 1. 转换换行符
find . -maxdepth 1 -name "*.sh" -exec sed -i 's/\r$//' {} \;
chmod +x *.sh

# 2. 初始化队列（只需一次）
bash init_queue.sh

# 3. 启动守护进程（只需一次）
bash start_daemon.sh
```

### 日常检查

```bash
# 查看队列状态
bash status_daemon.sh

# 查看日志
tail -f logs/queue_daemon.log
```

---

## 📋 核心配置参数

在 `queue_daemon.sh` 文件中：

| 参数 | 默认值 | 说明 | 修改行号 |
|------|-------|------|---------|
| `MAX_CONCURRENT` | 1 | 最大并发任务数 | 第16行 |
| `CHECK_INTERVAL` | 10 | 检查间隔（秒） | 第19行 |
| `TASK_TIMEOUT` | 9000 | 任务超时（秒）= 150分钟 | 第22行 |

### 常用超时值速查

```bash
# 30分钟
TASK_TIMEOUT=1800

# 60分钟（1小时）
TASK_TIMEOUT=3600

# 120分钟（2小时）
TASK_TIMEOUT=7200

# 150分钟（2.5小时）- 当前默认
TASK_TIMEOUT=9000

# 180分钟（3小时）
TASK_TIMEOUT=10800

# 240分钟（4小时）
TASK_TIMEOUT=14400
```

---

## 🔄 守护进程管理命令

```bash
# 启动
bash start_daemon.sh

# 停止
bash stop_daemon.sh

# 查看状态
bash status_daemon.sh

# 查看日志
tail -f logs/queue_daemon.log

# 重启（修改配置后）
bash stop_daemon.sh && bash start_daemon.sh
```

---

## 📊 队列管理命令

```bash
# 查看队列状态
bash check_queue.sh

# 查看运行中的任务
cat running.queue

# 查看等待中的任务
cat waiting.queue

# 清空所有队列（紧急）
bash clear_queue.sh

# 测试队列系统
bash test_queue.sh 3
```

---

## 🔍 常用监控命令

```bash
# 实时监控队列状态（2秒刷新）
watch -n 2 bash check_queue.sh

# 实时查看守护进程日志
tail -f logs/queue_daemon.log

# 实时查看队列系统日志
tail -f logs/queue.log

# 查看今天的超时事件
grep "$(date +%Y-%m-%d)" logs/queue_daemon.log | grep "timeout"

# 统计超时次数
grep "timeout" logs/queue_daemon.log | wc -l

# 查看所有EDM相关进程
ps aux | grep -E "(queue_daemon|queue_edm|EDM.sh)"
```

---

## ⚙️ 修改配置后的步骤

修改 `queue_daemon.sh` 中的任何配置后：

```bash
# 1. 停止守护进程
bash stop_daemon.sh

# 2. 验证修改（可选）
grep "TASK_TIMEOUT" queue_daemon.sh

# 3. 重新启动
bash start_daemon.sh

# 4. 验证新配置
tail -20 logs/queue_daemon.log | grep "timeout"
# 应该显示: Task timeout: XXXXs (YYY minutes)
```

---

## 🎯 systemd 服务管理（生产环境）

### 首次安装

```bash
# 1. 复制服务文件
sudo cp edm-queue.service /etc/systemd/system/

# 2. 重新加载systemd
sudo systemctl daemon-reload

# 3. 启动服务
sudo systemctl start edm-queue

# 4. 设置开机自启
sudo systemctl enable edm-queue
```

### 日常使用

```bash
# 启动服务
sudo systemctl start edm-queue

# 停止服务
sudo systemctl stop edm-queue

# 重启服务（修改配置后）
sudo systemctl restart edm-queue

# 查看状态
sudo systemctl status edm-queue

# 查看日志
sudo journalctl -u edm-queue -f

# 查看最近100行日志
sudo journalctl -u edm-queue -n 100
```

---

## 📝 日志文件位置

| 日志文件 | 内容 | 查看命令 |
|---------|------|---------|
| `logs/queue_daemon.log` | 守护进程日志 | `tail -f logs/queue_daemon.log` |
| `logs/queue.log` | 队列系统日志 | `tail -f logs/queue.log` |
| `logs/daemon_nohup.log` | nohup输出 | `tail -f logs/daemon_nohup.log` |
| `logs/edm_debug.log` | SSH传输日志 | `tail -f logs/edm_debug.log` |
| `logs/edm_php_debug.log` | PHP调试日志 | `tail -f logs/edm_php_debug.log` |

---

## 🐛 快速故障排查

### 守护进程无法启动

```bash
# 检查是否已在运行
bash status_daemon.sh

# 如果显示已运行但实际没有，删除PID文件
rm logs/queue_daemon.pid

# 重新启动
bash start_daemon.sh
```

### 任务一直不启动

```bash
# 1. 检查守护进程是否运行
bash status_daemon.sh

# 2. 检查等待队列
cat waiting.queue

# 3. 检查running.queue是否卡住
cat running.queue

# 4. 如果有僵死任务，清空
> running.queue

# 5. 守护进程会在下次检查时启动等待任务（最多10秒）
```

### 任务频繁超时

```bash
# 1. 查看实际超时时间
grep "timeout" logs/queue_daemon.log

# 2. 增加超时时间
nano queue_daemon.sh
# 修改第22行: TASK_TIMEOUT=18000  # 300分钟

# 3. 重启守护进程
bash stop_daemon.sh
bash start_daemon.sh
```

---

## 💡 最佳实践

### 生产环境配置

```bash
# queue_daemon.sh 配置
MAX_CONCURRENT=1        # 单GPU服务器
CHECK_INTERVAL=10       # 10秒检查一次
TASK_TIMEOUT=9000       # 150分钟超时

# 使用 systemd 管理
sudo systemctl enable edm-queue
sudo systemctl start edm-queue
```

### 定期维护

```bash
# 每周执行一次
# 1. 检查守护进程状态
bash status_daemon.sh

# 2. 清理旧日志（保留最近1000行）
tail -1000 logs/queue_daemon.log > logs/queue_daemon.log.tmp
mv logs/queue_daemon.log.tmp logs/queue_daemon.log

# 3. 检查磁盘空间
du -sh result/
df -h /var/www/bioinf2/edm_web
```

### 监控建议

```bash
# 添加到 crontab（每6小时检查一次）
0 */6 * * * bash /var/www/bioinf2/edm_web/status_daemon.sh >> /var/www/bioinf2/edm_web/logs/daemon_check.log 2>&1

# 或使用 systemd timer（推荐）
```

---

## 📞 紧急情况处理

### 清空所有队列并重启

```bash
# 1. 停止守护进程
bash stop_daemon.sh

# 2. 清空队列
> running.queue
> waiting.queue

# 3. 重新初始化
bash init_queue.sh

# 4. 启动守护进程
bash start_daemon.sh
```

### 杀死所有相关进程

```bash
# 杀死守护进程
pkill -f queue_daemon

# 杀死所有任务
pkill -f queue_edm
pkill -f EDM.sh

# 清理队列
> running.queue
> waiting.queue

# 重新启动
bash init_queue.sh
bash start_daemon.sh
```

---

## 🎓 文档索引

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| `QUEUE_EXPLAINED_SIMPLE.md` | 简单解释两种排队方式 | 新手 |
| `QUICK_REFERENCE.md` | 本文档 | 所有人 |
| `TIMEOUT_CONFIGURATION.md` | 超时配置详细说明 | 管理员 |
| `DAEMON_GUIDE.md` | 守护进程完整指南 | 运维人员 |
| `QUEUE_USAGE_GUIDE.md` | 队列系统使用指南 | 开发者 |
| `TEST_CHECKLIST.md` | 测试检查清单 | 测试人员 |

---

**最后更新：** 2025-12-01
**版本：** 2.0（新增超时功能）
