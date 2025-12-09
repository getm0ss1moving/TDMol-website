# Shell 脚本文件检查和守护进程总结

检查日期：2025-12-01

---

## ✅ Shell 脚本检查结果

### 符合要求的文件（8个）

所有以下文件的 shebang 都正确（`#!/bin/bash`），格式符合bash要求：

| 文件名 | 用途 | 状态 |
|--------|------|------|
| `EDM.sh` | 前端执行入口 | ✅ 正确 |
| `EDM_backend.sh` | 后端执行脚本 | ✅ 正确 |
| `EDM_frontend.sh` | 前端执行脚本（备用） | ✅ 正确 |
| `queue_edm.sh` | 排队管理主脚本 | ✅ 正确 |
| `init_queue.sh` | 初始化队列系统 | ✅ 正确 |
| `check_queue.sh` | 查看队列状态 | ✅ 正确 |
| `clear_queue.sh` | 清空队列（紧急用） | ✅ 正确 |
| `test_queue.sh` | 测试脚本 | ✅ 正确 |

### 不相关的文件（1个）

| 文件名 | 问题 | 处理方式 |
|--------|------|----------|
| `queue.sh` | 从FoldExplorer项目复制的旧文件，路径错误 | ⚠️ 不是前端需要的文件，忽略 |

---

## 🆕 新创建的守护进程文件（5个）

为了实现长时间运行的队列系统，创建了以下文件：

| 文件名 | 用途 | 类型 |
|--------|------|------|
| `queue_daemon.sh` | 守护进程主脚本（持续监控队列） | Shell脚本 |
| `start_daemon.sh` | 启动守护进程 | Shell脚本 |
| `stop_daemon.sh` | 停止守护进程 | Shell脚本 |
| `status_daemon.sh` | 检查守护进程状态 | Shell脚本 |
| `edm-queue.service` | systemd服务配置文件 | 服务配置 |

---

## 📚 新创建的文档文件（10个）

| 文件名 | 内容 |
|--------|------|
| `QUEUE_USAGE_GUIDE.md` | 排队系统详细使用指南 |
| `QUICK_TEST.md` | 5分钟快速测试清单 |
| `TEST_CHECKLIST.md` | 详细测试检查清单 |
| `QUEUE_SYSTEM_DIAGRAM.md` | 系统架构和流程图 |
| `DAEMON_GUIDE.md` | 守护进程使用指南 |
| `SHELL_SCRIPTS_CHECK_REPORT.md` | Shell脚本检查报告 |
| `DEPLOY_TEST_SCRIPTS.md` | 部署测试脚本说明 |
| `UPLOAD_INSTRUCTIONS.md` | 文件上传和换行符处理说明 |
| `upload_to_server.bat` | Windows批处理上传脚本 |
| `SHELL_FILES_SUMMARY.md` | 本文件（总结） |

---

## ⚠️ 重要提醒：换行符问题

**所有 .sh 文件在上传到Linux服务器后需要处理换行符问题！**

### 问题原因
Windows使用 CRLF (`\r\n`) 换行符，Linux使用 LF (`\n`) 换行符。

### 解决方案（任选其一）

**方案1：批量转换（推荐）**
```bash
cd /var/www/bioinf2/edm_web

# 使用 dos2unix
find . -maxdepth 1 -name "*.sh" -type f -exec dos2unix {} \;

# 或使用 sed
find . -maxdepth 1 -name "*.sh" -type f -exec sed -i 's/\r$//' {} \;

# 设置执行权限
chmod +x *.sh
```

**方案2：逐个转换**
```bash
# 转换守护进程相关脚本
sed -i 's/\r$//' queue_daemon.sh
sed -i 's/\r$//' start_daemon.sh
sed -i 's/\r$//' stop_daemon.sh
sed -i 's/\r$//' status_daemon.sh
sed -i 's/\r$//' test_queue.sh

# 设置执行权限
chmod +x queue_daemon.sh start_daemon.sh stop_daemon.sh status_daemon.sh test_queue.sh
```

---

## 🚀 快速部署指南

### 步骤1：上传所有文件到服务器

需要上传的 .sh 文件：
- `queue_daemon.sh`
- `start_daemon.sh`
- `stop_daemon.sh`
- `status_daemon.sh`
- `test_queue.sh`
- （其他已有的 .sh 文件）

需要上传的配置文件：
- `edm-queue.service`（如果要使用systemd）

### 步骤2：在服务器上执行

```bash
# 进入工作目录
cd /var/www/bioinf2/edm_web

# 转换换行符
find . -maxdepth 1 -name "*.sh" -type f -exec sed -i 's/\r$//' {} \;

# 设置执行权限
chmod +x *.sh

# 验证文件格式
file queue_daemon.sh
# 应该显示: queue_daemon.sh: Bash script, ASCII text executable

# 初始化队列系统
bash init_queue.sh

# 启动守护进程
bash start_daemon.sh

# 检查状态
bash status_daemon.sh
```

---

## 🧪 测试验证

### 测试1：守护进程基本功能

```bash
# 1. 启动守护进程
bash start_daemon.sh

# 2. 检查状态
bash status_daemon.sh

# 3. 查看日志
tail -f logs/queue_daemon.log

# 4. 停止守护进程
bash stop_daemon.sh
```

### 测试2：任务自动调度

```bash
# 1. 启动守护进程
bash start_daemon.sh

# 2. 添加测试任务到等待队列
echo "test@test.com TEST_DAEMON_1" >> waiting.queue
echo "test@test.com TEST_DAEMON_2" >> waiting.queue

# 3. 创建测试输入文件
echo "Generate benzene" > upload/TEST_DAEMON_1.txt
echo "Generate toluene" > upload/TEST_DAEMON_2.txt

# 4. 监控队列（新终端）
watch -n 2 bash status_daemon.sh

# 期望结果：
# - 10秒内，守护进程自动从waiting.queue取出任务
# - 任务依次启动
# - running.queue 和 waiting.queue 动态更新
```

### 测试3：完整流程测试

```bash
# 使用测试脚本
bash test_queue.sh 3

# 期望结果：
# - 3个任务提交
# - 第1个立即执行
# - 第2、3个进入等待队列
# - 守护进程自动调度后续任务
```

---

## 📊 守护进程 vs 传统方式

| 特性 | 传统方式 (queue_edm.sh) | 守护进程方式 |
|------|------------------------|-------------|
| 启动方式 | 每次任务触发 | 持续后台运行 |
| 队列检查 | 仅在任务完成时 | 每10秒自动检查 |
| 僵死任务清理 | ❌ 不支持 | ✅ 自动清理 |
| 手动干预 | ⚠️ 可能需要 | ❌ 无需干预 |
| 资源占用 | 低（按需运行） | 极低（常驻5-10MB） |
| 适用场景 | 低频任务 | 高频/生产环境 |

---

## 🎯 推荐配置

### 开发/测试环境
```bash
# 使用传统方式即可
# 任务通过 EDM.php → queue_edm.sh 提交
# 无需守护进程
```

### 生产环境（推荐）
```bash
# 方案1：使用脚本守护进程
bash start_daemon.sh

# 方案2：使用 systemd（更可靠）
sudo systemctl enable edm-queue
sudo systemctl start edm-queue
```

---

## 📁 完整文件结构

```
/var/www/bioinf2/edm_web/
│
├── 核心执行脚本
│   ├── EDM.sh                 ← 前端执行入口
│   ├── EDM_backend.sh         ← 后端执行脚本
│   └── EDM_server.py          ← SSH连接脚本
│
├── 排队系统（传统方式）
│   ├── queue_edm.sh           ← 排队管理主脚本
│   ├── init_queue.sh          ← 初始化队列
│   ├── check_queue.sh         ← 查看队列状态
│   ├── clear_queue.sh         ← 清空队列
│   └── test_queue.sh          ← 测试脚本
│
├── 守护进程系统（新增）
│   ├── queue_daemon.sh        ← 守护进程主脚本
│   ├── start_daemon.sh        ← 启动守护进程
│   ├── stop_daemon.sh         ← 停止守护进程
│   ├── status_daemon.sh       ← 查看守护进程状态
│   └── edm-queue.service      ← systemd服务配置
│
├── 队列文件
│   ├── running.queue          ← 正在运行的任务
│   └── waiting.queue          ← 等待中的任务
│
├── Web界面
│   ├── index.html             ← 用户提交表单
│   ├── EDM.php                ← 接收提交
│   └── py.php                 ← 旧版（不再使用）
│
├── 输入输出
│   ├── upload/                ← 用户输入文件
│   └── result/                ← 生成结果目录
│
└── 日志文件
    └── logs/
        ├── queue.log          ← 队列系统日志
        ├── queue_daemon.log   ← 守护进程日志
        ├── daemon_nohup.log   ← nohup输出
        └── edm_debug.log      ← SSH传输日志
```

---

## ✅ 部署检查清单

上传完成后，请确认：

- [ ] 所有 .sh 文件已转换换行符
- [ ] 所有 .sh 文件有执行权限（chmod +x）
- [ ] 验证文件格式（file *.sh 显示 "ASCII text executable"）
- [ ] 测试 init_queue.sh 成功运行
- [ ] 测试 check_queue.sh 能正常显示状态
- [ ] 测试 start_daemon.sh 能启动守护进程
- [ ] 测试 status_daemon.sh 能查看守护进程状态
- [ ] 测试 test_queue.sh 能提交测试任务
- [ ] 守护进程日志正常记录

---

## 📞 快速参考命令

```bash
# 队列管理
bash init_queue.sh           # 初始化队列
bash check_queue.sh          # 查看队列状态
bash clear_queue.sh          # 清空队列（紧急）
bash test_queue.sh 3         # 提交3个测试任务

# 守护进程管理
bash start_daemon.sh         # 启动守护进程
bash status_daemon.sh        # 查看守护进程状态
bash stop_daemon.sh          # 停止守护进程

# systemd管理（需root）
sudo systemctl start edm-queue     # 启动服务
sudo systemctl stop edm-queue      # 停止服务
sudo systemctl status edm-queue    # 查看状态
sudo systemctl enable edm-queue    # 开机自启

# 日志查看
tail -f logs/queue_daemon.log      # 守护进程日志
tail -f logs/queue.log             # 队列系统日志
sudo journalctl -u edm-queue -f    # systemd日志
```

---

## 🎓 文档阅读顺序

**新手用户：**
1. `QUICK_TEST.md` - 快速上手
2. `QUEUE_USAGE_GUIDE.md` - 详细了解排队系统
3. `DAEMON_GUIDE.md` - 学习守护进程

**系统管理员：**
1. `SHELL_SCRIPTS_CHECK_REPORT.md` - 了解文件状态
2. `UPLOAD_INSTRUCTIONS.md` - 正确部署文件
3. `DAEMON_GUIDE.md` - 配置守护进程
4. `TEST_CHECKLIST.md` - 完整测试验证

**开发者：**
1. `QUEUE_SYSTEM_DIAGRAM.md` - 理解系统架构
2. `DAEMON_GUIDE.md` - 了解实现原理
3. 阅读脚本源码 - 深入理解逻辑

---

**最后更新：** 2025-12-01
**检查人员：** Claude
**总文件数：** 23个（13个.sh脚本 + 10个文档）
