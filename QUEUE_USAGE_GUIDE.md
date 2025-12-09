# EDM 排队系统使用指南

## 📚 目录
1. [快速开始](#快速开始)
2. [系统架构](#系统架构)
3. [详细使用方法](#详细使用方法)
4. [测试步骤](#测试步骤)
5. [监控和维护](#监控和维护)
6. [常见问题](#常见问题)

---

## 🚀 快速开始

### 第一步：初始化队列系统

在前端服务器执行（**仅首次使用需要**）：

```bash
cd /var/www/bioinf2/edm_web
bash init_queue.sh
```

**期望输出：**
```
Initializing EDM queue system...
Queue files created:
  - running.queue (current running tasks)
  - waiting.queue (queued tasks)

Permissions set:
-rw-rw-rw- 1 www-data www-data 0 Nov 30 10:00 running.queue
-rw-rw-rw- 1 www-data www-data 0 Nov 30 10:00 waiting.queue
-rwxr-xr-x 1 www-data www-data 3456 Nov 30 10:00 queue_edm.sh
-rwxr-xr-x 1 www-data www-data 1234 Nov 30 10:00 EDM.sh
```

### 第二步：查看队列状态

```bash
bash check_queue.sh
```

### 第三步：提交任务（通过Web界面）

用户访问：`http://your-server/bioinf2/edm_web/index.html`

填写分子描述 → 点击提交 → 自动进入排队系统

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     用户Web界面                          │
│                    (index.html)                         │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                      EDM.php                            │
│  1. 接收用户输入                                         │
│  2. 保存到 upload/TASKID.txt                            │
│  3. 调用 queue_edm.sh                                   │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   queue_edm.sh                          │
│              (排队管理核心逻辑)                          │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│ 有空闲槽位？      │          │  所有槽位占用？   │
│ (running < MAX)  │          │  (running >= MAX) │
└────────┬─────────┘          └────────┬─────────┘
         │                             │
         ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│  立即执行任务     │          │ 加入等待队列      │
│  ↓               │          │  (waiting.queue) │
│  EDM.sh          │          │                  │
│  ↓               │          │  等待前面任务完成 │
│  SSH到后端       │          └──────────────────┘
│  ↓               │
│  分子生成         │
│  ↓               │
│  生成HTML         │
│  ↓               │
│  下载结果         │
│  ↓               │
│  任务完成         │
│  ↓               │
│  cleanup_and_next│───────┐
└──────────────────┘        │
                            │
         ┌──────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  从 waiting.queue 取出下一个 │
│  自动启动新任务               │
└──────────────────────────────┘
```

---

## 📖 详细使用方法

### 1. 初始化队列系统

**命令：**
```bash
bash init_queue.sh
```

**功能：**
- 创建 `running.queue` 和 `waiting.queue` 文件
- 设置正确的文件权限（666，允许Web服务器写入）
- 清空旧的队列数据

**何时执行：**
- 首次部署系统时
- 队列文件损坏或丢失时
- 需要清空所有队列时

---

### 2. 查看队列状态

**命令：**
```bash
bash check_queue.sh
```

**输出示例：**
```
========================================
EDM Queue System Status
========================================
Time: 2025-11-30 15:30:45

Running tasks: 1
----------------------------------------
  Task ID: 20251130153012_1
  Email: user1@example.com

Waiting tasks: 2
----------------------------------------
  Position: 1
  Task ID: 20251130153025_2
  Email: user2@example.com

  Position: 2
  Task ID: 20251130153038_3
  Email: user3@example.com

========================================
Summary:
  Total running: 1
  Total waiting: 2
  Total tasks: 3
========================================
```

---

### 3. 手动提交任务（测试用）

**命令：**
```bash
bash queue_edm.sh "user@example.com" "TASK_ID"
```

**示例：**
```bash
bash queue_edm.sh "test@test.com" "20251130153000"
```

**注意：**
- 正常使用时，任务由 `EDM.php` 自动提交
- 手动提交仅用于测试和调试

---

### 4. 实时监控队列

**方法1：实时查看队列状态**
```bash
watch -n 2 bash check_queue.sh
```
- 每2秒刷新一次队列状态
- 按 `Ctrl+C` 退出

**方法2：查看队列日志**
```bash
tail -f logs/queue.log
```
- 实时显示队列活动日志
- 按 `Ctrl+C` 退出

**方法3：查看队列文件**
```bash
# 查看正在运行的任务
cat running.queue

# 查看等待中的任务
cat waiting.queue
```

---

## 🧪 测试步骤

### 测试1：单任务测试（验证基本功能）

**步骤：**

1. **初始化队列**
   ```bash
   cd /var/www/bioinf2/edm_web
   bash init_queue.sh
   ```

2. **查看初始状态**
   ```bash
   bash check_queue.sh
   ```
   应该看到：
   ```
   Running tasks: 0
   Waiting tasks: 0
   ```

3. **创建测试输入文件**
   ```bash
   echo "Generate molecules with benzene ring" > upload/TEST001.txt
   ```

4. **提交测试任务**
   ```bash
   bash queue_edm.sh "test@example.com" "TEST001"
   ```

5. **立即查看状态**
   ```bash
   bash check_queue.sh
   ```
   应该看到：
   ```
   Running tasks: 1
     Task ID: TEST001
   ```

6. **监控任务执行**
   ```bash
   tail -f logs/queue.log
   ```

7. **等待任务完成**
   任务完成后，再次查看状态：
   ```bash
   bash check_queue.sh
   ```
   应该恢复为：
   ```
   Running tasks: 0
   Waiting tasks: 0
   ```

---

### 测试2：多任务排队测试（验证队列功能）

**使用自动化测试脚本：**

```bash
# 提交3个测试任务
bash test_queue.sh 3
```

**期望行为：**
1. 第1个任务立即开始执行（加入 `running.queue`）
2. 第2、3个任务进入等待队列（加入 `waiting.queue`）
3. 第1个任务完成后，第2个任务自动开始
4. 第2个任务完成后，第3个任务自动开始

**验证步骤：**

1. **提交后立即查看状态**
   ```bash
   bash check_queue.sh
   ```
   应该看到：
   ```
   Running tasks: 1
   Waiting tasks: 2
   ```

2. **实时监控**
   ```bash
   watch -n 2 bash check_queue.sh
   ```
   观察任务从 `waiting.queue` 移动到 `running.queue`

3. **查看日志**
   ```bash
   tail -f logs/queue.log
   ```
   应该看到：
   ```
   [2025-11-30 15:30:00] New task request: TEST_20251130153000_1
   [2025-11-30 15:30:00] Slot available, starting task immediately
   [2025-11-30 15:30:01] New task request: TEST_20251130153001_2
   [2025-11-30 15:30:01] All slots occupied, adding to waiting queue
   [2025-11-30 15:30:01] Task TEST_20251130153001_2 queued at position 1
   ...
   [2025-11-30 15:35:00] Task TEST_20251130153000_1 finished successfully
   [2025-11-30 15:35:00] Starting next task from queue: TEST_20251130153001_2
   ```

---

### 测试3：通过Web界面测试（完整流程）

**步骤：**

1. **访问Web界面**
   ```
   http://your-server/bioinf2/edm_web/index.html
   ```

2. **填写表单**
   - Molecule Description: `Generate molecules with benzene ring and hydroxyl group`
   - Email: `your-email@example.com`
   - Number of Molecules: `3`（测试用，生产环境用100）

3. **点击提交**
   页面跳转到 `EDM.php` 显示：
   ```
   Thank you for using EDM Molecule Generator!
   Your task is now in the queue system.
   This page will automatically check for results every 15 seconds.
   ```

4. **在服务器端查看队列**
   ```bash
   bash check_queue.sh
   ```

5. **等待结果**
   - 页面会自动检测 `result/TASKID/brief.html`
   - 当文件生成后，链接变为可点击

6. **查看结果**
   点击 "View Results" 查看生成的分子

---

## 📊 监控和维护

### 日常监控

**1. 检查队列状态**
```bash
# 每天检查一次
bash check_queue.sh
```

**2. 检查日志大小**
```bash
du -sh logs/*.log
```

**3. 查看今天的任务统计**
```bash
grep "$(date +%Y-%m-%d)" logs/queue.log | grep "New task request" | wc -l
```

### 定期维护

**1. 清理旧日志（每月执行）**
```bash
# 保留最后1000行
tail -1000 logs/queue.log > logs/queue.log.tmp
mv logs/queue.log.tmp logs/queue.log

tail -1000 logs/edm_php_debug.log > logs/edm_php_debug.log.tmp
mv logs/edm_php_debug.log.tmp logs/edm_php_debug.log
```

**2. 清理旧结果文件（每月执行）**
```bash
# 删除30天前的结果
find result/ -type d -mtime +30 -exec rm -rf {} +
find upload/ -type f -mtime +30 -delete
```

**3. 检查权限**
```bash
ls -l running.queue waiting.queue
# 应该显示 -rw-rw-rw-
```

---

## ❓ 常见问题

### Q1: 任务一直在等待队列，不执行

**检查：**
```bash
cat running.queue
ps aux | grep EDM.sh
```

**可能原因：**
- `running.queue` 中有卡住的任务，但实际进程已结束

**解决：**
```bash
# 手动清空 running.queue
> running.queue

# 重新初始化
bash init_queue.sh
```

---

### Q2: 权限错误

**错误信息：**
```
sed: cannot rename running.queue: Permission denied
```

**解决：**
```bash
chmod 666 running.queue waiting.queue
chmod 755 queue_edm.sh EDM.sh
```

---

### Q3: 如何增加并发任务数？

**编辑 `queue_edm.sh`：**
```bash
nano queue_edm.sh
```

**修改第31行：**
```bash
MAX_CONCURRENT=2  # 从1改为2
```

**注意：**
- 单GPU服务器建议 `MAX_CONCURRENT=1`
- 双GPU服务器可以设置 `MAX_CONCURRENT=2`
- 不建议超过2，EDM模型很消耗资源

---

### Q4: 如何强制清空所有队列？

**警告：这会清空所有等待任务！**

```bash
> running.queue
> waiting.queue
```

---

### Q5: 如何查看特定任务的状态？

```bash
# 在队列日志中搜索
grep "TASK_ID" logs/queue.log

# 检查任务是否在运行
grep "TASK_ID" running.queue

# 检查任务是否在等待
grep "TASK_ID" waiting.queue
```

---

## 🎯 最佳实践

### 1. 资源配置建议

| 服务器配置 | MAX_CONCURRENT | 预期性能 |
|-----------|----------------|----------|
| 单GPU (12GB) | 1 | 稳定，无过载风险 |
| 双GPU (24GB) | 2 | 资源利用率高 |
| CPU only | 1 | 速度慢，但可用 |

### 2. 监控建议

- **每天**：检查队列状态
- **每周**：清理日志
- **每月**：清理旧结果文件

### 3. 用户体验建议

- 在网页上显示队列位置（当前已实现"任务在队列中"提示）
- 发送邮件通知（当前已实现）
- 设置合理的超时时间（当前为60分钟）

---

## 📈 系统优势

✅ **防止过载**：限制同时运行的任务数
✅ **自动调度**：任务完成后自动启动下一个
✅ **透明性**：用户可以看到队列状态
✅ **可靠性**：使用 `trap` 确保清理
✅ **日志完整**：详细记录所有活动

---

## 📞 技术支持

如有问题，请查看：
1. `logs/queue.log` - 队列系统日志
2. `logs/edm_php_debug.log` - PHP调试日志
3. `logs/edm_debug.log` - 后端执行日志

---

**最后更新：** 2025-11-30
**版本：** 1.0
