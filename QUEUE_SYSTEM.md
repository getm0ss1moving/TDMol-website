# EDM 排队系统文档

## 系统概述

EDM排队系统用于防止同时运行过多的分子生成任务导致硬件过载。系统会自动管理任务队列，确保在资源可用时才启动新任务。

## 系统架构

```
用户提交表单
    ↓
EDM.php 接收请求
    ↓
调用 queue_edm.sh（排队管理）
    ↓
    ├─ 有空闲槽位 → 立即执行 EDM.sh
    │                    ↓
    │              EDM_server.py（SSH到后端）
    │                    ↓
    │              后端执行分子生成
    │                    ↓
    │              任务完成 → 启动下一个等待的任务
    │
    └─ 无空闲槽位 → 加入 waiting.queue
                        ↓
                   等待前面的任务完成
```

## 核心文件

### 1. queue_edm.sh
排队管理主脚本，负责：
- 检查当前运行的任务数
- 决定立即执行还是加入等待队列
- 任务完成后自动启动下一个任务

### 2. running.queue
记录正在运行的任务列表，格式：
```
email1 taskID1
email2 taskID2
```

### 3. waiting.queue
记录等待执行的任务列表，格式：
```
email1 taskID1
email2 taskID2
email3 taskID3
```

### 4. init_queue.sh
初始化脚本，用于：
- 创建队列文件
- 设置正确的权限
- 清空旧的队列数据

## 配置参数

### 最大并发数
在 `queue_edm.sh` 第17行设置：
```bash
MAX_CONCURRENT=1
```

**建议值：**
- **1个任务**：适用于单GPU服务器或资源有限的环境
- **2个任务**：适用于双GPU服务器
- **不建议超过2个**：EDM模型推理消耗大量资源

## 使用指南

### 初始化队列系统

第一次使用前，在前端服务器执行：
```bash
cd /var/www/bioinf2/edm_web
bash init_queue.sh
```

### 查看队列状态

```bash
# 查看正在运行的任务
cat running.queue

# 查看等待中的任务
cat waiting.queue

# 实时查看队列日志
tail -f logs/queue.log
```

### 手动提交任务（测试用）

```bash
bash queue_edm.sh "user@example.com" "202511301234567"
```

### 清空队列

**注意：只在必要时执行，会清空所有等待任务**
```bash
> running.queue
> waiting.queue
```

## 工作流程

### 场景1：系统空闲，立即执行

```
1. 用户提交任务 A
2. queue_edm.sh 检查：running.queue = 0 < MAX_CONCURRENT (1)
3. 任务 A 加入 running.queue
4. 立即执行 EDM.sh
5. 任务完成后从 running.queue 删除
```

### 场景2：系统繁忙，加入队列

```
1. 任务 A 正在运行（running.queue = 1）
2. 用户提交任务 B
3. queue_edm.sh 检查：running.queue = 1 >= MAX_CONCURRENT (1)
4. 任务 B 加入 waiting.queue
5. 任务 A 完成
6. queue_edm.sh 自动从 waiting.queue 取出任务 B
7. 任务 B 开始执行
```

### 场景3：多个任务排队

```
running.queue: [任务 A]
waiting.queue: [任务 B, 任务 C, 任务 D]

任务 A 完成 →
    从 waiting.queue 取出任务 B
    running.queue: [任务 B]
    waiting.queue: [任务 C, 任务 D]

任务 B 完成 →
    从 waiting.queue 取出任务 C
    running.queue: [任务 C]
    waiting.queue: [任务 D]

...以此类推
```

## 日志系统

### 主要日志文件

| 日志文件 | 内容 | 位置 |
|---------|------|------|
| `logs/queue.log` | 排队系统日志 | 任务提交、启动、完成 |
| `logs/edm_php_debug.log` | PHP调试日志 | 任务提交记录 |
| `logs/edm_sh_output.log` | EDM.sh输出 | 后端执行详情 |
| `logs/edm_debug.log` | EDM_server.py日志 | SSH连接和文件传输 |

### 查看日志示例

```bash
# 查看最近的队列活动
tail -50 logs/queue.log

# 实时监控队列
tail -f logs/queue.log

# 查看特定任务的日志
grep "202511301234567" logs/queue.log
```

## 故障排查

### 问题1：任务一直在等待队列

**检查：**
```bash
cat running.queue
cat waiting.queue
```

**可能原因：**
- running.queue 中的任务卡住了
- 权限问题导致无法写入队列文件

**解决：**
```bash
# 检查进程
ps aux | grep EDM.sh

# 如果没有进程但 running.queue 不为空，手动清空
> running.queue

# 重新启动队列
bash init_queue.sh
```

### 问题2：权限错误

**症状：**
```
sed: cannot rename running.queue: Permission denied
```

**解决：**
```bash
cd /var/www/bioinf2/edm_web
chmod 666 running.queue waiting.queue
chmod 755 queue_edm.sh
```

### 问题3：队列文件不存在

**解决：**
```bash
bash init_queue.sh
```

## 监控和维护

### 定期检查

建议每周检查一次队列状态：
```bash
# 检查是否有遗留的任务
cat running.queue
cat waiting.queue

# 检查日志大小
du -sh logs/*.log

# 清理过大的日志（保留最后1000行）
tail -1000 logs/queue.log > logs/queue.log.tmp
mv logs/queue.log.tmp logs/queue.log
```

### 性能监控

```bash
# 查看今天提交的任务数
grep "$(date +%Y-%m-%d)" logs/queue.log | grep "New task request" | wc -l

# 查看平均队列长度
grep "queued at position" logs/queue.log | tail -20

# 查看任务完成情况
grep "finished successfully" logs/queue.log | tail -10
```

## 调优建议

### 1. 调整最大并发数

根据服务器资源调整 `MAX_CONCURRENT`：

**单GPU (12GB显存)**
```bash
MAX_CONCURRENT=1
```

**双GPU (24GB显存)**
```bash
MAX_CONCURRENT=2
```

### 2. 优先级队列（未实现）

如果需要VIP用户优先，可以修改 `queue_edm.sh`：
```bash
# 在waiting.queue中插入到队首而不是队尾
if [[ "$is_vip" == "true" ]]; then
    sed -i "1i $email $timeVar" waiting.queue  # 插入到第一行
else
    echo "$email $timeVar" >> waiting.queue    # 追加到最后
fi
```

### 3. 超时机制（未实现）

如果任务运行时间过长（如超过1小时），自动终止：
```bash
# 在 queue_edm.sh 中添加
timeout 3600 bash "$WORK_DIR/EDM.sh" "$email" "$timeVar"
```

## 安全注意事项

1. **队列文件权限**：确保只有web服务器和管理员能写入
2. **日志大小**：定期清理日志，防止磁盘满
3. **输入验证**：EDM.php已验证用户输入，防止注入攻击
4. **并发限制**：不要将 `MAX_CONCURRENT` 设置过高

## 系统优势

✅ **防止过载**：限制同时运行的任务数，保护硬件
✅ **自动调度**：任务完成后自动启动下一个
✅ **透明性**：用户可以看到任务在排队
✅ **可靠性**：使用 `trap` 确保清理函数一定执行
✅ **日志完整**：详细记录所有队列活动

## 与原系统的对比

| 特性 | 原系统 | 排队系统 |
|------|--------|----------|
| 并发控制 | ❌ 无限制 | ✅ 可配置限制 |
| 资源保护 | ❌ 可能过载 | ✅ 防止过载 |
| 任务调度 | ❌ 手动 | ✅ 自动 |
| 日志记录 | 基本 | 详细 |
| 用户体验 | 可能失败 | 稳定可靠 |

## 总结

EDM排队系统提供了一个简单而有效的方法来管理分子生成任务，确保系统稳定运行，同时为用户提供透明的队列状态。通过合理配置 `MAX_CONCURRENT` 参数，可以在资源利用率和系统稳定性之间找到平衡。
