# 路径一致性检查报告

## ❌ 发现严重不一致！

---

## 🔴 核心问题：两个不同的后端路径

### 路径 A: `/data/yfang/EDM_web/1111/web_apps/`
**使用此路径的文件**:
- ✗ EDM_server.py (line 33, 70, 135, 136)
- ✗ processhtml.py (line 223)
- ✗ diagnose_transfer.py (line 21, 28, 35)

### 路径 B: `/data/yfang/EDM_new/web_apps/`
**使用此路径的文件**:
- ✗ EDM.sh (line 11, 67, 68)
- ✗ model_runner.py (line 14, 32, 33)
- ✗ sample.py (line 3)
- ✗ en_diffusion.py (line 11)

---

## 📊 详细路径对比表

| 文件 | 前端路径 | 后端路径 | 问题 |
|------|---------|---------|------|
| EDM_server.py | /var/www/bioinf2/edm_web/ | /data/yfang/EDM_web/1111/web_apps/ | ❌ 后端路径不同 |
| EDM.sh | N/A | /data/yfang/EDM_new/web_apps/ | ❌ 后端路径不同 |
| processhtml.py | N/A | /data/yfang/EDM_web/1111/web_apps/ | ❌ 后端路径不同 |
| model_runner.py | N/A | /data/yfang/EDM_new/ | ❌ 后端路径不同 |

---

## 🎯 问题说明

### 执行流程中的路径冲突：

```
步骤1: EDM_server.py 上传文件
   └─ 上传到: /data/yfang/EDM_web/1111/web_apps/upload/task.txt

步骤2: EDM_server.py 执行命令
   └─ 执行: bash /data/yfang/EDM_web/1111/web_apps/EDM.sh

步骤3: EDM.sh 设置工作目录
   └─ 使用: /data/yfang/EDM_new/web_apps/
   └─ ❌ 与上传路径不同！

步骤4: EDM.sh 调用 run_generation.py
   └─ 查找文件: /data/yfang/EDM_new/web_apps/upload/task.txt
   └─ ❌ 文件不在这里！文件在 /data/yfang/EDM_web/1111/web_apps/upload/

步骤5: 生成结果
   └─ 保存到: /data/yfang/EDM_new/web_apps/result/

步骤6: EDM_server.py 下载结果
   └─ 从这里下载: /data/yfang/EDM_web/1111/web_apps/result/
   └─ ❌ 结果不在这里！结果在 /data/yfang/EDM_new/web_apps/result/
```

---

## 📋 所有路径清单

### EDM_server.py 路径配置

```python
# Line 33: 命令路径
bash /data/yfang/EDM_web/1111/web_apps/EDM.sh

# Line 69-70: 上传路径
local_path_input  = '/var/www/bioinf2/edm_web/upload/' + timeVar + '.txt'
remote_path_input = '/data/yfang/EDM_web/1111/web_apps/upload/' + timeVar + '.txt'

# Line 133-136: 结果路径
local_path_brief      = '/var/www/bioinf2/edm_web/result/' + timeVar + '_brief.html'
local_path_results_dir = '/var/www/bioinf2/edm_web/result/' + timeVar + '/'
remote_path_brief     = '/data/yfang/EDM_web/1111/web_apps/result/' + timeVar + '/brief.html'
remote_path_results   = '/data/yfang/EDM_web/1111/web_apps/result/' + timeVar + '/'
```

### EDM.sh 路径配置

```bash
# Line 11: 结果目录
target_dir="/data/yfang/EDM_new/web_apps/result/${2}/"

# Line 67-68: 工作目录
if [ -d "/data/yfang/EDM_new/web_apps" ]; then
    BASE_DIR="/data/yfang/EDM_new/web_apps"
```

### processhtml.py 路径配置

```python
# Line 223: 结果目录
result_dir = f"/data/yfang/EDM_web/1111/web_apps/result/{task_id}/"
```

### model_runner.py 路径配置

```python
# Line 32-33: 模型路径
model_path = '/data/yfang/EDM_new/outputs/edm_geom_drugs/'
cl_model_path = "/data/yfang/EDM_new/model_GCN/model_GCN_1111_fixed_full200_epoch20_guidance_epoch26.pt"
```

---

## ✅ 解决方案：需要统一为一个路径

### 关键问题：您的实际后端项目在哪里？

**选项 A: 如果在 `/data/yfang/EDM_web/1111/web_apps/`**

需要修改：
- ❌ EDM.sh
- ❌ model_runner.py (如果模型也在此路径)

**选项 B: 如果在 `/data/yfang/EDM_new/web_apps/`**

需要修改：
- ❌ EDM_server.py
- ❌ processhtml.py
- ❌ diagnose_transfer.py

---

## 🔍 确认实际路径

请运行以下命令确认：

### 1. 检查 EDM.sh 在哪里

```bash
# 检查路径 A
ls -l /data/yfang/EDM_web/1111/web_apps/EDM.sh

# 检查路径 B
ls -l /data/yfang/EDM_new/web_apps/EDM.sh
```

### 2. 检查 upload 目录在哪里

```bash
# 检查路径 A
ls -ld /data/yfang/EDM_web/1111/web_apps/upload/

# 检查路径 B
ls -ld /data/yfang/EDM_new/web_apps/upload/
```

### 3. 检查模型文件在哪里

```bash
# 检查模型路径
ls -l /data/yfang/EDM_new/outputs/edm_geom_drugs/

# 检查是否有备份在另一个路径
ls -l /data/yfang/EDM_web/1111/outputs/edm_geom_drugs/
```

### 4. 检查 run_generation.py 在哪里

```bash
# 检查路径 A
ls -l /data/yfang/EDM_web/1111/web_apps/run_generation.py

# 检查路径 B
ls -l /data/yfang/EDM_new/web_apps/run_generation.py
```

---

## 🎯 推荐的统一配置

### 如果使用 `/data/yfang/EDM_new/web_apps/` (推荐)

**理由**：
- ✅ EDM.sh 已经在使用这个路径
- ✅ 模型文件在 `/data/yfang/EDM_new/`
- ✅ 符合 EDM_new 项目结构

**需要修改的文件**：

#### 1. EDM_server.py

```python
# Line 33
command = 'bash /data/yfang/EDM_new/web_apps/EDM.sh {} {}'.format(email, timeVar)

# Line 70
remote_path_input = '/data/yfang/EDM_new/web_apps/upload/' + timeVar + '.txt'

# Line 135-136
remote_path_brief = '/data/yfang/EDM_new/web_apps/result/' + timeVar + '/brief.html'
remote_path_results = '/data/yfang/EDM_new/web_apps/result/' + timeVar + '/'
```

#### 2. processhtml.py

```python
# Line 223
result_dir = f"/data/yfang/EDM_new/web_apps/result/{task_id}/"
```

#### 3. diagnose_transfer.py

```python
# Line 21, 28, 35
"upload_dir": "/data/yfang/EDM_new/web_apps/upload/"
```

---

### 如果使用 `/data/yfang/EDM_web/1111/web_apps/`

**需要修改的文件**：

#### 1. EDM.sh

```bash
# Line 11
target_dir="/data/yfang/EDM_web/1111/web_apps/result/${2}/"

# Line 67-68
if [ -d "/data/yfang/EDM_web/1111/web_apps" ]; then
    BASE_DIR="/data/yfang/EDM_web/1111/web_apps"
elif [ -d "/data/yfang/EDM_new/web_apps" ]; then
    BASE_DIR="/data/yfang/EDM_new/web_apps"
```

#### 2. model_runner.py

**注意**：如果模型文件在 `/data/yfang/EDM_new/`，可能需要：
- 移动模型文件，或
- 使用软链接，或
- 保持 model_runner.py 使用 `/data/yfang/EDM_new/`

---

## ⚡ 快速检查命令

```bash
# 一键检查所有关键路径
echo "=== 检查 EDM.sh ==="
ls -l /data/yfang/EDM_web/1111/web_apps/EDM.sh 2>&1
ls -l /data/yfang/EDM_new/web_apps/EDM.sh 2>&1

echo "=== 检查 upload 目录 ==="
ls -ld /data/yfang/EDM_web/1111/web_apps/upload/ 2>&1
ls -ld /data/yfang/EDM_new/web_apps/upload/ 2>&1

echo "=== 检查 result 目录 ==="
ls -ld /data/yfang/EDM_web/1111/web_apps/result/ 2>&1
ls -ld /data/yfang/EDM_new/web_apps/result/ 2>&1

echo "=== 检查模型文件 ==="
ls -ld /data/yfang/EDM_new/outputs/ 2>&1
ls -ld /data/yfang/EDM_web/1111/outputs/ 2>&1
```

---

## 📌 待确认

请告诉我：

1. **实际的后端项目路径是哪个？**
   - [ ] /data/yfang/EDM_web/1111/web_apps/
   - [ ] /data/yfang/EDM_new/web_apps/
   - [ ] 其他: _______________

2. **模型文件在哪里？**
   - [ ] /data/yfang/EDM_new/outputs/
   - [ ] /data/yfang/EDM_web/1111/outputs/

3. **您想统一使用哪个路径？**
   - [ ] 统一到 /data/yfang/EDM_new/web_apps/ (推荐)
   - [ ] 统一到 /data/yfang/EDM_web/1111/web_apps/

**一旦您确认，我会立即生成所有需要修改的文件！**

---

**检查时间**: 2025-11-28
**问题严重性**: 🔴 严重 - 导致文件传输和结果获取失败
**修复时间**: 10分钟（确认路径后）
