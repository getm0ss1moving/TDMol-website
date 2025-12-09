# ⚠️ 严重配置问题 - 必须立即修复

## 🔴 发现的问题

您的 `EDM_server.py` 中存在**服务器地址不一致**的严重问题！

### 当前配置：

```python
# file_transfer 函数 (第41行)
tran = paramiko.Transport(('202.120.37.150', 2349))  # 服务器A

# exec_command 函数 (第59-60行)
client.connect(hostname='202.121.180.146', port=2345, ...)  # 服务器B

# 验证部分 (第85行)
tran = paramiko.Transport(('202.121.180.146', 2346))  # 服务器B (不同端口)
```

### 问题分析：

```
步骤1: 文件上传
   ├─ 上传到 → 202.120.37.150:2349 (服务器A)
   └─ 文件保存在 → /data/yfang/EDM_web/1111/web_apps/upload/

步骤2: 执行命令
   ├─ 连接到 → 202.121.180.146:2345 (服务器B) ❌
   └─ 在服务器B上执行 EDM.sh

步骤3: EDM.sh 寻找文件
   └─ 在服务器B上查找 /data/yfang/EDM_web/1111/web_apps/upload/
   └─ ❌ 找不到！因为文件在服务器A上！
```

## 🔧 解决方案

### 方案1: 统一使用服务器A (202.120.37.150:2349)

如果您的 EDM.sh 部署在 202.120.37.150 上：

```python
# EDM_server.py

def file_transfer(local_path, remote_path, way="upload"):
    tran = paramiko.Transport(('202.120.37.150', 2349))
    tran.connect(username='server', password='che22ySJTUse2ve2')
    # ...

def exec_command(command):
    client.connect(
        hostname='202.120.37.150',  # 修改这里
        port=2349,                   # 修改这里
        username='server',           # 修改这里
        password='che22ySJTUse2ve2'  # 修改这里
    )
    # ...

# 验证部分 (第85行)
tran = paramiko.Transport(('202.120.37.150', 2349))  # 修改这里
tran.connect(username='server', password='che22ySJTUse2ve2')  # 修改这里
```

### 方案2: 统一使用服务器B (202.121.180.146)

如果您的 EDM.sh 部署在 202.121.180.146 上：

**但是端口问题**: 2345 和 2346 是不同的端口，需要确认正确的端口！

```python
# EDM_server.py

# 假设正确端口是 2345

def file_transfer(local_path, remote_path, way="upload"):
    tran = paramiko.Transport(('202.121.180.146', 2345))  # 修改这里
    tran.connect(username='yfang', password='20250912')    # 修改这里
    # ...

def exec_command(command):
    client.connect(
        hostname='202.121.180.146',
        port=2345,
        username='yfang',
        password='20250912'
    )
    # ...

# 验证部分
tran = paramiko.Transport(('202.121.180.146', 2345))  # 统一端口
tran.connect(username='yfang', password='20250912')
```

## 📋 诊断步骤

### 1. 运行诊断工具

```bash
python3 diagnose_transfer.py
```

这会告诉您：
- 哪些服务器可以连接
- upload 目录是否存在
- 是否有文件在各个服务器上

### 2. 确认后端服务器

请回答以下问题：

#### 问题 A: EDM.sh 部署在哪个服务器？

```bash
# 在服务器A上检查
ssh -p 2349 server@202.120.37.150 "ls -l /data/yfang/EDM_web/1111/web_apps/EDM.sh"

# 在服务器B上检查
ssh -p 2345 yfang@202.121.180.146 "ls -l /data/yfang/EDM_web/1111/web_apps/EDM.sh"
```

#### 问题 B: conda 环境在哪个服务器？

```bash
# 在服务器A上检查
ssh -p 2349 server@202.120.37.150 "conda env list | grep edm_web"

# 在服务器B上检查
ssh -p 2345 yfang@202.121.180.146 "conda env list | grep edm_web"
```

#### 问题 C: 查看现有文件位置

```bash
# 在服务器A上查找
ssh -p 2349 server@202.120.37.150 "ls -lh /data/yfang/EDM_web/1111/web_apps/upload/"

# 在服务器B上查找
ssh -p 2345 yfang@202.121.180.146 "ls -lh /data/yfang/EDM_web/1111/web_apps/upload/"
```

### 3. 检查日志

```bash
tail -50 logs/edm_debug.log
```

查找类似的错误：
- `FileNotFoundError`
- `No such file or directory`
- `Connection refused`

## 🎯 快速修复模板

确认正确服务器后，使用这个模板：

```python
# ============================================================
# 统一服务器配置
# ============================================================
BACKEND_HOST = '您的后端服务器IP'      # 例如：202.120.37.150
BACKEND_PORT = 您的后端SSH端口         # 例如：2349
SSH_USERNAME = '您的SSH用户名'         # 例如：server
SSH_PASSWORD = '您的SSH密码'           # 例如：che22ySJTUse2ve2
BACKEND_PATH = '/data/yfang/EDM_web/1111/web_apps/'

# ============================================================
# 使用统一配置
# ============================================================

def file_transfer(local_path, remote_path, way="upload"):
    tran = paramiko.Transport((BACKEND_HOST, BACKEND_PORT))
    tran.connect(username=SSH_USERNAME, password=SSH_PASSWORD)
    # ...

def exec_command(command):
    client.connect(
        hostname=BACKEND_HOST,
        port=BACKEND_PORT,
        username=SSH_USERNAME,
        password=SSH_PASSWORD
    )
    # ...

# 验证部分
tran = paramiko.Transport((BACKEND_HOST, BACKEND_PORT))
tran.connect(username=SSH_USERNAME, password=SSH_PASSWORD)
```

## ⚡ 紧急检查清单

- [ ] 确认 EDM.sh 在哪个服务器上
- [ ] 确认 conda 环境在哪个服务器上
- [ ] 运行 diagnose_transfer.py 查看连接状态
- [ ] 修改 EDM_server.py 统一服务器配置
- [ ] 测试文件传输：`python3 test_file_transfer.py`
- [ ] 提交测试任务验证修复

## 📞 需要帮助？

请告诉我：
1. EDM.sh 实际部署在哪个服务器？
2. `diagnose_transfer.py` 的输出结果是什么？
3. 您想使用哪个服务器作为后端？

我会帮您生成正确的配置文件。

---

**创建时间**: 2025-11-28
**优先级**: 🔴 最高 - 必须立即修复
