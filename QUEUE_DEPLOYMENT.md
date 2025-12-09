# EDM排队系统部署指南

## 部署概述

本文档介绍如何在前端服务器（www.csbio.sjtu.edu.cn）上部署EDM排队系统。

## 前置条件

- 已部署EDM web应用
- 具有服务器SSH访问权限
- 熟悉基本的Linux命令

## 部署步骤

### 1. 上传文件到前端服务器

将以下文件上传到 `/var/www/bioinf2/edm_web/`：

```bash
# 在本地Windows系统
# 使用SFTP工具（如FileZilla、WinSCP）上传以下文件：

queue_edm.sh          # 排队管理主脚本
init_queue.sh         # 初始化脚本
check_queue.sh        # 队列状态查看工具
clear_queue.sh        # 队列清空工具（紧急使用）
EDM.php               # 修改后的PHP文件（已集成排队系统）
```

### 2. 连接到前端服务器

```bash
ssh your_username@www.csbio.sjtu.edu.cn
```

### 3. 进入工作目录

```bash
cd /var/www/bioinf2/edm_web
```

### 4. 设置文件权限

```bash
# 给脚本添加执行权限
chmod 755 queue_edm.sh
chmod 755 init_queue.sh
chmod 755 check_queue.sh
chmod 755 clear_queue.sh
chmod 755 EDM.sh
```

### 5. 初始化排队系统

```bash
bash init_queue.sh
```

**预期输出：**
```
Initializing EDM queue system...
Queue files created:
  - running.queue (current running tasks)
  - waiting.queue (queued tasks)

Permissions set:
-rw-rw-rw- 1 www-data www-data 0 Nov 30 12:00 running.queue
-rw-rw-rw- 1 www-data www-data 0 Nov 30 12:00 waiting.queue
-rwxr-xr-x 1 user user 2345 Nov 30 12:00 queue_edm.sh
-rwxr-xr-x 1 user user 1234 Nov 30 12:00 EDM.sh

Queue system initialized successfully!
```

### 6. 验证部署

#### 6.1 检查队列状态
```bash
bash check_queue.sh
```

**预期输出：**
```
========================================
EDM Queue System Status
========================================
Time: 2025-11-30 12:00:00

Running tasks: 0
  (No tasks currently running)

Waiting tasks: 0
  (No tasks waiting)

========================================
Summary:
  Total running: 0
  Total waiting: 0
  Total tasks: 0
========================================
```

#### 6.2 测试提交任务
```bash
# 测试提交一个任务
bash queue_edm.sh "test@example.com" "TEST_$(date +%Y%m%d%H%M%S)"

# 查看日志
tail -20 logs/queue.log
```

#### 6.3 通过Web界面测试

1. 打开浏览器访问：`http://www.csbio.sjtu.edu.cn/bioinf2/edm_web/index.html`
2. 输入分子描述提交任务
3. 观察等待页面，应该显示："Note: Your task is now in the queue system."
4. SSH到服务器，运行 `bash check_queue.sh` 查看任务是否在队列中

### 7. 配置最大并发数

根据服务器资源编辑 `queue_edm.sh`：

```bash
# 使用vim或nano编辑
vim queue_edm.sh

# 找到第17行
MAX_CONCURRENT=1

# 根据服务器资源修改：
# 单GPU服务器：MAX_CONCURRENT=1
# 双GPU服务器：MAX_CONCURRENT=2
```

保存后无需重启，下一个任务会使用新配置。

## 日常管理

### 查看队列状态

```bash
bash check_queue.sh
```

### 实时监控队列

```bash
tail -f logs/queue.log
```

### 查看特定任务

```bash
# 查看任务 202511301234567 的日志
grep "202511301234567" logs/queue.log
```

### 手动清空队列（紧急情况）

```bash
bash clear_queue.sh
```

## 故障排查

### 问题1：队列文件不存在

**症状：**
```
ERROR: Queue files not found!
```

**解决：**
```bash
bash init_queue.sh
```

### 问题2：权限错误

**症状：**
```
sed: cannot rename running.queue: Permission denied
```

**解决：**
```bash
chmod 666 running.queue waiting.queue
chown www-data:www-data running.queue waiting.queue
```

### 问题3：任务卡住

**症状：**
- `running.queue` 不为空但没有进程在运行
- 新任务无法启动

**检查：**
```bash
# 查看是否有EDM相关进程
ps aux | grep EDM

# 查看running.queue
cat running.queue
```

**解决：**
```bash
# 如果确认没有进程在运行，手动清空running.queue
> running.queue

# 或使用清空工具
bash clear_queue.sh
```

### 问题4：日志文件过大

**症状：**
```bash
du -sh logs/queue.log
# 输出：500M logs/queue.log
```

**解决：**
```bash
# 保留最后1000行
tail -1000 logs/queue.log > logs/queue.log.tmp
mv logs/queue.log.tmp logs/queue.log

# 或直接清空
> logs/queue.log
```

## 监控建议

### 设置定期检查（可选）

创建cron任务每小时检查队列状态：

```bash
# 编辑crontab
crontab -e

# 添加以下行（每小时记录队列状态）
0 * * * * cd /var/www/bioinf2/edm_web && bash check_queue.sh >> logs/queue_hourly.log 2>&1
```

### 设置告警（可选）

如果队列长度超过阈值，发送邮件告警：

```bash
# 创建 monitor_queue.sh
#!/bin/bash
THRESHOLD=10
waiting_count=$(wc -l < /var/www/bioinf2/edm_web/waiting.queue)

if [[ $waiting_count -gt $THRESHOLD ]]; then
    echo "Warning: Queue has $waiting_count waiting tasks" | \
    mail -s "EDM Queue Alert" admin@example.com
fi

# 添加到crontab（每30分钟检查）
*/30 * * * * /var/www/bioinf2/edm_web/monitor_queue.sh
```

## 性能优化建议

### 1. 根据硬件调整并发数

**单GPU (12GB显存)**
```bash
MAX_CONCURRENT=1
```

**双GPU (24GB显存)**
```bash
MAX_CONCURRENT=2
```

### 2. 日志轮转

定期清理日志文件：
```bash
# 每周日凌晨2点清理旧日志（保留最近1000行）
0 2 * * 0 tail -1000 /var/www/bioinf2/edm_web/logs/queue.log > /var/www/bioinf2/edm_web/logs/queue.log.tmp && mv /var/www/bioinf2/edm_web/logs/queue.log.tmp /var/www/bioinf2/edm_web/logs/queue.log
```

## 升级和维护

### 更新排队脚本

如果需要更新 `queue_edm.sh`：

1. 上传新版本文件
2. 设置权限：`chmod 755 queue_edm.sh`
3. 无需重启，下一个任务会使用新版本

### 备份队列数据

```bash
# 备份队列文件
mkdir -p backups
cp running.queue backups/running.queue.$(date +%Y%m%d)
cp waiting.queue backups/waiting.queue.$(date +%Y%m%d)
```

### 恢复队列数据

```bash
# 从备份恢复
cp backups/running.queue.20251130 running.queue
cp backups/waiting.queue.20251130 waiting.queue
```

## 卸载排队系统

如果需要移除排队系统，恢复原始行为：

1. 编辑 `EDM.php` 第44行：
```php
// 修改前（排队系统）
$command = "bash queue_edm.sh '".$email."' '".$timeVar."' >> logs/queue.log 2>&1 &";

// 修改后（直接调用）
$command = "bash EDM.sh '".$email."' '".$timeVar."' >> logs/edm_sh_output.log 2>&1 &";
```

2. 删除队列文件（可选）：
```bash
rm running.queue waiting.queue
```

## 总结

✅ 部署完成后，系统会自动管理任务队列
✅ 用户提交任务时会看到排队提示
✅ 资源有限时任务会自动排队
✅ 任务完成后自动启动下一个等待的任务

**关键文件清单：**
- `queue_edm.sh` - 核心排队逻辑
- `running.queue` - 运行中任务
- `waiting.queue` - 等待任务
- `logs/queue.log` - 队列日志

**常用命令：**
```bash
bash check_queue.sh    # 查看队列状态
tail -f logs/queue.log # 实时监控
bash clear_queue.sh    # 清空队列（紧急）
```

如有问题，请参考 `QUEUE_SYSTEM.md` 文档或查看日志文件。
