# 最终一致性检查报告

## 📊 检查时间：2025-11-28

---

## ✅ 服务器配置 - 已统一

### 当前配置：

**EDM_server.py** (所有操作已统一):
- 文件上传 (line 41): `202.121.180.146:2346` ✅
- 命令执行 (line 59-60): `202.121.180.146:2346` ✅
- 文件验证 (line 85): `202.121.180.146:2346` ✅
- 结果下载 (line 151): `202.121.180.146:2346` ✅

**结论**: ✅ **服务器和端口已统一！所有操作在同一服务器**

---

## ❌ 路径配置 - 严重不一致

### 问题：两个不同的后端路径

| 文件 | 使用的后端路径 | 状态 |
|------|---------------|------|
| **EDM_server.py** | `/data/yfang/EDM_web/1111/web_apps/` | 路径 A |
| **processhtml.py** | `/data/yfang/EDM_web/1111/web_apps/` | 路径 A |
| **EDM.sh** | `/data/yfang/EDM_new/web_apps/` | 路径 B ❌ |
| **model_runner.py** | `/data/yfang/EDM_new/` | 路径 B ❌ |

---

## 🔴 核心矛盾

### 文件传输流程：

```
1. EDM_server.py 上传文件
   └─ 目标: /data/yfang/EDM_web/1111/web_apps/upload/task.txt

2. EDM_server.py 执行命令
   └─ 命令: bash /data/yfang/EDM_web/1111/web_apps/EDM.sh

3. EDM.sh 启动时设置工作目录
   └─ 使用: /data/yfang/EDM_new/web_apps/  ❌ 不匹配！

4. run_generation.py 查找输入文件
   └─ 查找: $BASE_DIR/upload/task.txt
   └─ 实际: /data/yfang/EDM_new/web_apps/upload/task.txt
   └─ ❌ 但文件在: /data/yfang/EDM_web/1111/web_apps/upload/task.txt

5. 结果保存
   └─ 保存到: /data/yfang/EDM_new/web_apps/result/

6. EDM_server.py 下载结果
   └─ 从这里下载: /data/yfang/EDM_web/1111/web_apps/result/
   └─ ❌ 但结果在: /data/yfang/EDM_new/web_apps/result/
```

---

## 📋 详细路径清单

### 前端路径 (一致性检查)

| 文件 | 前端路径 | 状态 |
|------|---------|------|
| EDM_server.py | `/var/www/bioinf2/edm_web/` | ✅ |
| test_file_transfer.py | `/var/www/bioinf2/edm_web/` | ✅ |

**结论**: ✅ **前端路径统一**

### 后端路径 (不一致！)

#### 使用 `/data/yfang/EDM_web/1111/web_apps/` 的文件：

**EDM_server.py**:
```python
# Line 33
command = 'bash /data/yfang/EDM_web/1111/web_apps/EDM.sh {} {}'

# Line 70
remote_path_input = '/data/yfang/EDM_web/1111/web_apps/upload/' + timeVar + '.txt'

# Line 135-136
remote_path_brief = '/data/yfang/EDM_web/1111/web_apps/result/' + timeVar + '/brief.html'
remote_path_results = '/data/yfang/EDM_web/1111/web_apps/result/' + timeVar + '/'
```

**processhtml.py**:
```python
# Line 223
result_dir = f"/data/yfang/EDM_web/1111/web_apps/result/{task_id}/"
```

#### 使用 `/data/yfang/EDM_new/web_apps/` 的文件：

**EDM.sh**:
```bash
# Line 11
target_dir="/data/yfang/EDM_new/web_apps/result/${2}/"

# Line 67-68
if [ -d "/data/yfang/EDM_new/web_apps" ]; then
    BASE_DIR="/data/yfang/EDM_new/web_apps"
```

**model_runner.py**:
```python
# Line 32-33 (模型路径)
model_path = '/data/yfang/EDM_new/outputs/edm_geom_drugs/'
cl_model_path = "/data/yfang/EDM_new/model_GCN/..."
```

---

## 🔧 解决方案

### 方案 1: 统一到 `/data/yfang/EDM_new/web_apps/` (推荐)

**理由**：
- ✅ 模型文件在 `/data/yfang/EDM_new/`
- ✅ EDM.sh 已经配置为使用此路径
- ✅ 符合项目原始结构

**需要修改**：
1. ✗ EDM_server.py (3处路径)
2. ✗ processhtml.py (1处路径)

### 方案 2: 统一到 `/data/yfang/EDM_web/1111/web_apps/`

**需要修改**：
1. ✗ EDM.sh (2处路径)
2. ⚠️ model_runner.py (需要确认模型文件位置)

**注意**：如果选择此方案，需要确认：
- 模型文件是否需要移动或创建软链接
- `/data/yfang/EDM_web/1111/` 目录是否有足够空间

---

## ⚡ 立即修复 (推荐方案1)

### 修改 EDM_server.py

```python
# Line 33 - 修改命令路径
command = 'bash /data/yfang/EDM_new/web_apps/EDM.sh {} {}'.format(
    email, timeVar
)

# Line 70 - 修改上传路径
remote_path_input = '/data/yfang/EDM_new/web_apps/upload/' + timeVar + '.txt'

# Line 135-136 - 修改结果路径
remote_path_brief = '/data/yfang/EDM_new/web_apps/result/' + timeVar + '/brief.html'
remote_path_results = '/data/yfang/EDM_new/web_apps/result/' + timeVar + '/'
```

### 修改 processhtml.py

```python
# Line 223 - 修改结果目录
result_dir = f"/data/yfang/EDM_new/web_apps/result/{task_id}/"
```

### 修改 diagnose_transfer.py (可选)

```python
# Line 21, 28, 35
"upload_dir": "/data/yfang/EDM_new/web_apps/upload/"
```

---

## 🔍 验证步骤

修改完成后，请运行：

### 1. 检查目录是否存在

```bash
# 在后端服务器上
ssh -p 2346 yfang@202.121.180.146

# 检查关键目录
ls -ld /data/yfang/EDM_new/web_apps/
ls -ld /data/yfang/EDM_new/web_apps/upload/
ls -ld /data/yfang/EDM_new/web_apps/result/
ls -l /data/yfang/EDM_new/web_apps/EDM.sh
ls -l /data/yfang/EDM_new/web_apps/run_generation.py
```

### 2. 创建缺失的目录

```bash
# 如果目录不存在
mkdir -p /data/yfang/EDM_new/web_apps/upload
mkdir -p /data/yfang/EDM_new/web_apps/result
chmod 755 /data/yfang/EDM_new/web_apps/upload
chmod 755 /data/yfang/EDM_new/web_apps/result
```

### 3. 测试文件传输

```bash
# 在前端服务器
python3 test_file_transfer.py
```

### 4. 提交测试任务

```bash
# 通过Web界面提交一个测试任务
# 查看日志
tail -f logs/edm_debug.log
```

---

## 📝 修改检查清单

- [ ] 修改 EDM_server.py (line 33, 70, 135, 136)
- [ ] 修改 processhtml.py (line 223)
- [ ] 修改 diagnose_transfer.py (line 21, 28, 35) - 可选
- [ ] 在后端服务器创建必要目录
- [ ] 设置目录权限 (755)
- [ ] 运行 test_file_transfer.py 测试
- [ ] 提交一个真实任务测试
- [ ] 检查日志确认成功

---

## ✅ 修改后的一致性

修改完成后，整个系统将使用：

### 统一配置

```
前端服务器：
  路径: /var/www/bioinf2/edm_web/

后端服务器：
  地址: 202.121.180.146:2346
  用户: yfang
  路径: /data/yfang/EDM_new/web_apps/

目录结构：
  /data/yfang/EDM_new/web_apps/
  ├── EDM.sh
  ├── run_generation.py
  ├── processhtml.py
  ├── send_email.py
  ├── model_runner.py
  ├── upload/
  └── result/
```

---

## 🎯 总结

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 服务器地址 | ✅ 已统一 | 202.121.180.146:2346 |
| 用户账号 | ✅ 已统一 | yfang |
| 前端路径 | ✅ 已统一 | /var/www/bioinf2/edm_web/ |
| 后端路径 | ❌ 不一致 | 需要统一到 /data/yfang/EDM_new/web_apps/ |

**关键问题**：只剩后端路径不一致，修复后系统即可正常工作！

---

**检查完成时间**: 2025-11-28
**需要修改**: 2个文件 (EDM_server.py, processhtml.py)
**预计修复时间**: 5分钟
**修复优先级**: 🔴 最高 - 必须立即修复
