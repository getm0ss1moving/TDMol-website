# EDM_server.py 配置一致性分析报告

## 📊 当前配置总览

### 服务器配置对比表

| 操作 | 服务器地址 | 端口 | 用户名 | 代码位置 |
|------|-----------|------|--------|---------|
| **文件上传** | 202.120.37.150 | 2349 | server | line 41 |
| **命令执行** | 202.121.180.146 | 2345 | yfang | line 59 |
| **文件验证** | 202.121.180.146 | 2346 | yfang | line 85 |
| **结果下载** | 202.121.180.146 | 2346 | yfang | line 151 |

---

## ❌ 发现的严重问题

### 问题 1: 文件上传与命令执行不在同一服务器

```python
# Line 41: 文件上传到
202.120.37.150:2349  (服务器 A)

# Line 59: 但命令执行在
202.121.180.146:2345  (服务器 B)
```

**影响**:
- 文件上传到服务器 A: `/data/yfang/EDM_web/1111/web_apps/upload/`
- 命令在服务器 B 上执行
- 服务器 B 找不到文件！

---

### 问题 2: 同一服务器使用不同端口

```python
# Line 59: 命令执行使用
202.121.180.146:2345

# Line 85, 151: 文件验证和下载使用
202.121.180.146:2346
```

**影响**:
- 端口 2345 和 2346 可能是不同的服务或实例
- 可能导致文件访问不一致

---

### 问题 3: 使用不同的用户账号

```python
# 服务器 A 使用:
username='server', password='che22ySJTUse2ve2'

# 服务器 B 使用:
username='yfang', password='20250912'
```

---

## 🔍 详细代码分析

### 1. 文件上传 (Line 41-42)

```python
def file_transfer(local_path, remote_path, way="upload"):
    tran = paramiko.Transport(('202.120.37.150', 2349))
    tran.connect(username="server", password='che22ySJTUse2ve2')
```

- ✅ 上传功能本身正常
- ❌ 但目标服务器与执行服务器不同

---

### 2. 命令执行 (Line 59-63)

```python
def exec_command(command):
    client.connect(
        hostname='202.121.180.146',
        port=2345,
        username='yfang',
        password='20250912'
    )
```

- ✅ 连接功能正常
- ❌ 服务器与文件上传不同
- ⚠️ 端口与验证/下载不同

---

### 3. 文件验证 (Line 85-86)

```python
tran = paramiko.Transport(('202.121.180.146', 2346))
tran.connect(username='yfang', password='20250912')
```

- ❌ 验证的是服务器 B，但文件在服务器 A
- ⚠️ 端口 2346 与命令执行端口 2345 不同

---

### 4. 结果下载 (Line 151-153)

```python
tran = paramiko.Transport(('202.121.180.146', 2346))
tran.connect(username="yfang", password='20250912')
```

- ✅ 与验证使用相同配置
- ❌ 但如果命令在端口 2345 执行，结果可能在 2345，而不是 2346

---

## 🎯 执行流程分析

### 当前流程（有问题）:

```
步骤1: 上传文件
   └─ 202.120.37.150:2349 → /data/yfang/EDM_web/1111/web_apps/upload/task.txt

步骤2: 执行命令
   └─ 202.121.180.146:2345 执行: bash /data/yfang/EDM_web/1111/web_apps/EDM.sh
   └─ EDM.sh 尝试读取: /data/yfang/EDM_web/1111/web_apps/upload/task.txt
   └─ ❌ 找不到文件！（文件在 202.120.37.150 上）

步骤3: 验证文件
   └─ 202.121.180.146:2346 检查文件
   └─ ❌ 文件不在这个服务器上

步骤4: 下载结果
   └─ 202.121.180.146:2346 下载结果
   └─ ❌ 没有结果（因为命令执行失败）
```

---

## ✅ 正确的配置方案

### 方案 A: 使用 202.120.37.150:2349

如果 EDM.sh 和 conda 环境在这个服务器：

```python
# ============================================================
# 统一配置
# ============================================================
BACKEND_HOST = '202.120.37.150'
BACKEND_PORT = 2349
SSH_USERNAME = 'server'
SSH_PASSWORD = 'che22ySJTUse2ve2'

# ============================================================
# 所有函数使用统一配置
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

# 下载部分
tran = paramiko.Transport((BACKEND_HOST, BACKEND_PORT))
tran.connect(username=SSH_USERNAME, password=SSH_PASSWORD)
```

### 方案 B: 使用 202.121.180.146

**需要先确认正确的端口！**

选项 1: 如果端口是 2345
```python
BACKEND_HOST = '202.121.180.146'
BACKEND_PORT = 2345
SSH_USERNAME = 'yfang'
SSH_PASSWORD = '20250912'
```

选项 2: 如果端口是 2346
```python
BACKEND_HOST = '202.121.180.146'
BACKEND_PORT = 2346
SSH_USERNAME = 'yfang'
SSH_PASSWORD = '20250912'
```

---

## 🔧 验证步骤

### 1. 确认 EDM.sh 在哪个服务器

```bash
# 测试服务器 A
ssh -p 2349 server@202.120.37.150 "ls -l /data/yfang/EDM_web/1111/web_apps/EDM.sh"

# 测试服务器 B (端口 2345)
ssh -p 2345 yfang@202.121.180.146 "ls -l /data/yfang/EDM_web/1111/web_apps/EDM.sh"

# 测试服务器 B (端口 2346)
ssh -p 2346 yfang@202.121.180.146 "ls -l /data/yfang/EDM_web/1111/web_apps/EDM.sh"
```

### 2. 确认 conda 环境在哪里

```bash
# 测试服务器 A
ssh -p 2349 server@202.120.37.150 "conda env list | grep edm_web"

# 测试服务器 B (端口 2345)
ssh -p 2345 yfang@202.121.180.146 "conda env list | grep edm_web"

# 测试服务器 B (端口 2346)
ssh -p 2346 yfang@202.121.180.146 "conda env list | grep edm_web"
```

### 3. 测试连接

```bash
# 测试各服务器连接
ssh -p 2349 server@202.120.37.150 "echo 'Server A OK'"
ssh -p 2345 yfang@202.121.180.146 "echo 'Server B:2345 OK'"
ssh -p 2346 yfang@202.121.180.146 "echo 'Server B:2346 OK'"
```

---

## 📋 配置检查清单

请回答以下问题：

- [ ] EDM.sh 部署在哪个服务器？
  - [ ] 202.120.37.150:2349
  - [ ] 202.121.180.146:2345
  - [ ] 202.121.180.146:2346

- [ ] edm_web conda 环境在哪个服务器？
  - [ ] 202.120.37.150:2349
  - [ ] 202.121.180.146:2345
  - [ ] 202.121.180.146:2346

- [ ] 您主要使用哪个账号？
  - [ ] server@202.120.37.150
  - [ ] yfang@202.121.180.146

- [ ] 202.121.180.146 的正确端口是？
  - [ ] 2345
  - [ ] 2346
  - [ ] 两个端口都可以用，但作用不同

---

## ⚠️ 立即行动

**优先级**: 🔴 最高

1. **运行验证命令**（上面的"验证步骤"）
2. **告诉我结果**
3. **我会生成正确的配置文件**

---

**分析时间**: 2025-11-28
**问题级别**: 严重 - 系统无法正常工作
**修复时间**: 5分钟（在确认正确配置后）
