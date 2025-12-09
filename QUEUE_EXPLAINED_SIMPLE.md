# 排队系统简单解释 - 传统方式 vs 守护进程

## 🎯 核心问题：这两种方式有什么区别？

---

## 📖 方式1：传统排队方式（已经在用）

### 它是怎么工作的？

```
用户提交表单
    ↓
EDM.php 调用 queue_edm.sh
    ↓
queue_edm.sh 检查队列
    ↓
如果有空位 → 启动任务 → 任务完成时调用 cleanup_and_next
                              ↓
                        cleanup_and_next 检查 waiting.queue
                              ↓
                        如果有等待任务 → 启动下一个任务
```

### 实际例子

**场景：3个用户几乎同时提交任务**

```bash
时间 0秒：用户A提交 → queue_edm.sh 启动任务A
时间 5秒：用户B提交 → queue_edm.sh 发现队列满，任务B进入 waiting.queue
时间 10秒：用户C提交 → queue_edm.sh 发现队列满，任务C进入 waiting.queue

...等待任务A完成（约145秒）...

时间 145秒：任务A完成
           → cleanup_and_next 被调用
           → 从 waiting.queue 取出任务B
           → 启动任务B

...等待任务B完成（约145秒）...

时间 290秒：任务B完成
           → cleanup_and_next 被调用
           → 从 waiting.queue 取出任务C
           → 启动任务C
```

### ✅ 优点
- 简单，无需额外进程
- 资源占用低

### ❌ 缺点
- **依赖任务完成时的调用**：如果任务异常退出，cleanup_and_next 可能不执行
- **没有主动监控**：如果 running.queue 里有僵死任务，系统不会自动发现

---

## 📖 方式2：守护进程方式（新增）

### 它是怎么工作的？

```
启动守护进程（只需要启动一次）
    ↓
守护进程持续运行，每10秒循环：
    1. 检查 running.queue 中的任务是否还活着
       - 如果进程死了，从 running.queue 删除
    2. 检查是否可以启动新任务
       - running.queue 未满 && waiting.queue 有任务
    3. 如果可以，从 waiting.queue 取出任务并启动
    ↓
等待10秒，重复循环
```

### 实际例子

**同样场景：3个用户提交任务**

```bash
时间 -10秒：管理员执行 bash start_daemon.sh
           → 守护进程启动，开始监控

时间 0秒：用户A提交 → 任务A进入 waiting.queue
          守护进程每10秒检查一次，在下一次检查时发现：
          - running.queue 为空（有空位）
          - waiting.queue 有任务A
          → 守护进程启动任务A

时间 5秒：用户B提交 → 任务B进入 waiting.queue

时间 10秒：守护进程检查
          - running.queue 有1个任务（任务A）
          - waiting.queue 有1个任务（任务B）
          - 队列已满，不启动新任务

时间 15秒：用户C提交 → 任务C进入 waiting.queue

时间 20秒：守护进程检查
          - running.queue 仍然有任务A
          - waiting.queue 有2个任务（B、C）
          - 队列已满，不启动新任务

...任务A运行中...

时间 145秒：任务A完成并退出

时间 150秒：守护进程检查
          - 发现任务A进程已不存在
          - 从 running.queue 删除任务A
          - 发现 waiting.queue 有任务B
          - 启动任务B

...任务B运行中...

时间 295秒：任务B完成

时间 300秒：守护进程检查
          - 发现任务B进程已不存在
          - 从 running.queue 删除任务B
          - 发现 waiting.queue 有任务C
          - 启动任务C
```

### ✅ 优点
- **主动监控**：每10秒检查一次，不依赖任务完成时的回调
- **自动清理**：发现僵死任务自动清理
- **更可靠**：即使任务异常退出也能继续调度

### ❌ 缺点
- 需要额外的守护进程（占用约5-10MB内存）
- 有10秒延迟（检查间隔）

---

## 🔄 两种方式对比

### 传统方式

```
EDM.php → queue_edm.sh → 检查队列 → 启动任务
                            ↓
                      任务运行 (145秒)
                            ↓
                       任务完成时
                            ↓
                    cleanup_and_next
                            ↓
                      启动下一个任务
```

**关键点：** 下一个任务的启动**依赖**前一个任务的完成回调

---

### 守护进程方式

```
守护进程持续运行 ──┐
                  │
                  ↓
            每10秒检查一次 ←─────────┐
                  │                  │
                  ↓                  │
            发现可启动任务？          │
            /           \            │
          是             否           │
          ↓              ↓           │
      启动任务        什么都不做      │
          │              │           │
          └──────────────┴───────────┘
              等待10秒后继续检查
```

**关键点：** 守护进程**主动**定期检查队列，不依赖任务完成

---

## 🎓 回答你的问题：只需要运行一次吗？

### 情况1：只用传统方式（不需要守护进程）

```bash
# 第一次部署时执行一次
bash init_queue.sh

# 之后不需要做任何事情
# 用户提交表单时，EDM.php 会自动调用 queue_edm.sh
```

**适用场景：**
- 测试环境
- 任务提交频率低
- 不在乎偶尔的调度失败

---

### 情况2：使用守护进程（推荐生产环境）

```bash
# 第一次部署时执行一次
bash init_queue.sh

# 启动守护进程（只需启动一次）
bash start_daemon.sh

# 之后守护进程会一直运行
# 用户提交表单 → EDM.php 把任务加到 waiting.queue
# 守护进程会自动从 waiting.queue 启动任务
```

**守护进程什么时候会停止？**
- 手动执行 `bash stop_daemon.sh`
- 服务器重启

**服务器重启后需要重新启动吗？**
- 如果用脚本方式：需要手动执行 `bash start_daemon.sh`
- 如果用 systemd 方式：设置开机自启后自动启动

---

## 📊 实际使用建议

### 方案A：传统方式（简单）

```bash
# 部署时执行一次
bash init_queue.sh

# 完成！无需其他操作
# 用户通过网页提交任务即可
```

**优点：** 简单，不需要额外管理
**缺点：** 如果任务异常退出，等待队列可能卡住

---

### 方案B：守护进程方式（推荐）

#### 临时使用（测试）
```bash
# 部署时
bash init_queue.sh
bash start_daemon.sh

# 每次服务器重启后
bash start_daemon.sh
```

#### 永久使用（生产环境，推荐）
```bash
# 部署时执行一次
bash init_queue.sh

# 安装 systemd 服务（只需一次）
sudo cp edm-queue.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable edm-queue  # 设置开机自启
sudo systemctl start edm-queue   # 立即启动

# 完成！之后服务器重启也会自动启动守护进程
```

**优点：** 可靠，自动化，服务器重启后自动恢复
**缺点：** 需要 root 权限配置 systemd

---

## 🎯 推荐配置流程

### 第一次部署

```bash
# 1. 上传所有文件到服务器
# 2. 转换换行符
cd /var/www/bioinf2/edm_web
find . -maxdepth 1 -name "*.sh" -exec sed -i 's/\r$//' {} \;
chmod +x *.sh

# 3. 初始化队列（只需一次）
bash init_queue.sh

# 4. 选择一种方式：

# 方式A：不使用守护进程（简单，适合测试）
# 什么都不做，直接可以用

# 方式B：使用守护进程脚本（需要记得重启后再次启动）
bash start_daemon.sh

# 方式C：使用 systemd（最可靠，推荐生产）
sudo cp edm-queue.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable edm-queue
sudo systemctl start edm-queue
```

### 日常使用

**方式A（传统）：** 无需任何操作

**方式B（守护进程脚本）：**
```bash
# 检查守护进程是否运行
bash status_daemon.sh

# 如果停止了，重新启动
bash start_daemon.sh
```

**方式C（systemd）：**
```bash
# 检查状态
sudo systemctl status edm-queue

# 如果停止了，启动
sudo systemctl start edm-queue
```

---

## 💡 简单决策树

```
你希望系统自动化程度如何？
    │
    ├─ 简单即可，偶尔手动干预没问题
    │  → 使用方式A（传统方式）
    │  → 只需执行一次 init_queue.sh
    │
    ├─ 希望可靠但不想配置 systemd
    │  → 使用方式B（守护进程脚本）
    │  → 执行一次 init_queue.sh
    │  → 执行一次 start_daemon.sh
    │  → 服务器重启后需要手动再次 start_daemon.sh
    │
    └─ 希望完全自动化，无需人工干预
       → 使用方式C（systemd）
       → 执行一次 init_queue.sh
       → 配置一次 systemd（需要root权限）
       → 之后完全自动，服务器重启也自动恢复
```

---

## 🔍 如何验证当前状态？

### 检查队列系统是否初始化

```bash
ls -l running.queue waiting.queue

# 如果文件存在 → 已初始化
# 如果文件不存在 → 需要执行 bash init_queue.sh
```

### 检查守护进程是否运行

```bash
bash status_daemon.sh

# 输出 "Status: RUNNING" → 守护进程在运行
# 输出 "Status: NOT RUNNING" → 守护进程未运行
```

### 检查 systemd 服务是否运行

```bash
sudo systemctl status edm-queue

# Active: active (running) → 服务在运行
# Active: inactive (dead) → 服务未运行
```

---

## ✅ 总结

**你的问题：只需要运行一次 init_queue 和一次 start_daemon 吗？**

**答案：是的！**

```bash
# 第一次部署时
bash init_queue.sh      # ✅ 只需一次
bash start_daemon.sh    # ✅ 只需一次（如果用守护进程）

# 之后
# - init_queue.sh 不需要再运行
# - start_daemon.sh 只在以下情况重新运行：
#   1. 服务器重启后（如果没用systemd）
#   2. 守护进程意外停止后
#   3. 手动停止后想重新启动
```

**推荐：使用 systemd 方式，一次配置，永久自动运行。**

---

**最后更新：** 2025-12-01
**难度级别：** ⭐ 入门级
