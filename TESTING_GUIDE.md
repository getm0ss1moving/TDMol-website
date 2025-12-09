# EDM 系统测试验证指南

## 🎯 快速验证方法

### 方法1: 使用监控面板 (推荐)

访问: `http://your-server/bioinf2/edm_web/monitor.php`

**监控面板功能**:
- ✅ 实时查看系统统计
- ✅ 查看最近的任务列表
- ✅ 实时日志滚动显示
- ✅ 自动刷新 (5秒/10秒/30秒)
- ✅ 系统信息检查

**如何使用**:
1. 在浏览器打开 monitor.php
2. 查看"系统统计"部分，确认上传文件数和完成任务数
3. 查看"最近的任务"表格，每个任务显示状态
4. 查看"实时日志"部分，看到详细的执行过程
5. 如果有问题，日志会显示红色的ERROR消息

---

### 方法2: 使用测试工具

访问: `http://your-server/bioinf2/edm_web/test_workflow.php`

**测试工具功能**:
- ✅ 检查前端文件是否存在
- ✅ 检查目录权限
- ✅ 测试文件写入
- ✅ 检查PHP函数是否可用
- ✅ 测试Python环境
- ✅ 测试Bash脚本权限
- ✅ 查看最近的任务
- ✅ 模拟提交测试

**如何使用**:
1. 访问 test_workflow.php
2. 从上到下检查每个部分
3. 所有绿色✓表示正常，红色✗表示有问题
4. 点击"模拟提交测试"按钮测试完整流程

---

### 方法3: 手动检查文件

**步骤1: 检查上传文件**
```bash
ls -lh upload/
```
如果有任务提交，应该看到 `.txt` 文件

**步骤2: 检查日志文件**
```bash
tail -f logs/edm_debug.log
```
实时查看日志输出

**步骤3: 检查结果文件**
```bash
ls -lh result/
```
任务完成后，应该看到 `*_brief.html` 文件

---

## 📋 完整测试流程

### 测试1: 前端文件检查

```bash
cd /var/www/bioinf2/edm_web/

# 检查必要文件
ls -l index.html
ls -l EDM.php
ls -l py.php
ls -l EDM_frontend.sh
ls -l EDM_server.py

# 检查目录
ls -ld upload/
ls -ld result/
ls -ld logs/

# 检查权限
chmod +x EDM_frontend.sh
chmod +x EDM_server.py
chmod 755 upload result logs
```

### 测试2: 提交测试任务

**通过网页提交**:
1. 访问 `index.html`
2. 点击 "Example" 填充示例文本
3. 填写邮箱 (可选)
4. 点击 "Submit"
5. 等待跳转到等待页面

**预期结果**:
- 看到等待页面，显示任务ID
- `upload/` 目录出现新的 `.txt` 文件
- `logs/edm_debug.log` 开始记录日志

### 测试3: 检查日志

**实时查看日志**:
```bash
tail -f logs/edm_debug.log
```

**预期日志内容**:
```
[2025-11-28 15:30:45] [INFO] ============================================================
[2025-11-28 15:30:45] [INFO] EDM_server.py started
[2025-11-28 15:30:45] [INFO] Arguments: ['EDM_server.py', '', '20251128153045']
[2025-11-28 15:30:45] [INFO] Email:
[2025-11-28 15:30:45] [INFO] Task ID: 20251128153045
[2025-11-28 15:30:45] [INFO] Remote command: bash /data/yfang/EDM_new/web_apps/EDM.sh  20251128153045
[2025-11-28 15:30:45] [INFO] Step 1: Uploading input file to backend
[2025-11-28 15:30:45] [INFO] Local input: /var/www/bioinf2/edm_web/upload/20251128153045.txt
[2025-11-28 15:30:45] [INFO] Remote input: /data/yfang/EDM_new/web_apps/upload/20251128153045.txt
[2025-11-28 15:30:45] [INFO] Input file exists, size: 123 bytes
[2025-11-28 15:30:46] [SUCCESS] Input file uploaded successfully
[2025-11-28 15:30:46] [INFO] Step 2: Executing command on backend server
[2025-11-28 15:30:46] [INFO] Command executed
[2025-11-28 15:32:15] [INFO] Step 3: Downloading result files from backend
[2025-11-28 15:32:15] [SUCCESS] Downloaded brief.html to /var/www/bioinf2/edm_web/result/20251128153045_brief.html
[2025-11-28 15:32:16] [INFO] Found 8 files in remote result directory
[2025-11-28 15:32:16] [INFO] Downloaded: result_1.html
[2025-11-28 15:32:16] [INFO] Downloaded: result_2.html
[2025-11-28 15:32:16] [INFO] Downloaded: result_3.html
[2025-11-28 15:32:16] [SUCCESS] Downloaded 8 files
[2025-11-28 15:32:16] [SUCCESS] Task 20251128153045 completed successfully!
[2025-11-28 15:32:16] [INFO] ============================================================
```

### 测试4: 检查结果文件

```bash
# 检查结果目录
ls -lh result/

# 应该看到:
# 20251128153045_brief.html  (概览页面)
# 20251128153045/            (详细结果目录)
#   ├── brief.html
#   ├── result_1.html
#   ├── result_2.html
#   ├── result_3.html
#   ├── molecule_1.xyz
#   ├── molecule_1.sdf
#   ├── molecule_2.xyz
#   └── ...
```

### 测试5: 访问结果页面

访问: `http://your-server/bioinf2/edm_web/result/TASK_ID_brief.html`

**预期**:
- 看到结果概览页面
- 显示3个生成的分子
- 每个分子有2D结构图
- 点击"查看详情"可以看到3D可视化

---

## 🐛 常见问题排查

### 问题1: 日志文件不存在

**症状**: `logs/edm_debug.log` 不存在

**排查**:
```bash
# 检查logs目录
ls -ld logs/

# 如果不存在，创建它
mkdir -p logs
chmod 755 logs

# 手动运行EDM_server.py测试
python3 EDM_server.py "" "test123"

# 检查日志是否生成
cat logs/edm_debug.log
```

### 问题2: 上传文件不存在

**症状**: 日志显示 "Input file not found"

**排查**:
```bash
# 检查EDM.php是否正确保存文件
ls -lh upload/

# 检查PHP错误日志
tail -f /var/log/apache2/error.log  # 或
tail -f /var/log/nginx/error.log

# 测试PHP写入权限
php -r "file_put_contents('upload/test.txt', 'test');"
ls -l upload/test.txt
```

### 问题3: SSH连接失败

**症状**: 日志显示 "Failed to upload input file" 或连接错误

**排查**:
```bash
# 测试SSH连接
ssh -p 2349 user@backend_server

# 测试Python SSH
python3 -c "
import paramiko
tran = paramiko.Transport(('backend_ip', 2349))
tran.connect(username='user', password='pass')
print('OK')
tran.close()
"
```

### 问题4: 后端脚本未执行

**症状**: 文件上传成功，但后端没有生成结果

**排查**:
```bash
# SSH到后端服务器
ssh -p 2349 user@backend_server

# 检查后端upload目录
ls -lh /data/yfang/EDM_new/web_apps/upload/

# 手动运行后端脚本
cd /data/yfang/EDM_new/web_apps/
bash EDM.sh "" "TASK_ID"

# 检查后端Python环境
which python3
python3 --version
python3 -c "import torch; print('PyTorch OK')"
```

### 问题5: 结果文件下载失败

**症状**: 后端有结果，但前端没有

**排查**:
```bash
# SSH到后端检查结果
ssh -p 2349 user@backend_server
ls -lh /data/yfang/EDM_new/web_apps/result/TASK_ID/

# 手动下载测试
scp -P 2349 user@backend:/path/to/result/file ./
```

---

## 📊 日志级别说明

| 级别 | 颜色 | 含义 |
|------|------|------|
| INFO | 绿色 | 正常信息 |
| SUCCESS | 亮绿 | 成功操作 |
| WARNING | 黄色 | 警告信息 |
| ERROR | 红色 | 错误信息 |

---

## ✅ 成功标志

系统正常运行时，应该看到:

1. **monitor.php 显示**:
   - 上传文件数 > 0
   - 完成任务数 > 0
   - 任务完成率接近100%
   - 最近任务列表显示"✓ 完成"

2. **日志显示**:
   - 大量 [SUCCESS] 消息
   - 没有 [ERROR] 消息
   - 每个步骤都有完整记录

3. **文件系统**:
   - `upload/` 有 .txt 文件
   - `result/` 有 _brief.html 和对应目录
   - `logs/` 有 edm_debug.log

4. **网页访问**:
   - 等待页面正常显示
   - 结果链接可点击
   - 3D分子可视化正常加载

---

## 🚀 快速诊断命令

```bash
# 一键检查脚本
cat > check_system.sh << 'EOF'
#!/bin/bash
echo "=== EDM System Check ==="
echo ""
echo "1. Files:"
ls -l index.html EDM.php py.php EDM_frontend.sh EDM_server.py 2>/dev/null | wc -l
echo ""
echo "2. Directories:"
ls -ld upload result logs 2>/dev/null
echo ""
echo "3. Recent uploads:"
ls -lht upload/*.txt 2>/dev/null | head -5
echo ""
echo "4. Recent results:"
ls -lht result/*_brief.html 2>/dev/null | head -5
echo ""
echo "5. Log file size:"
du -h logs/edm_debug.log 2>/dev/null
echo ""
echo "6. Latest log entries:"
tail -20 logs/edm_debug.log 2>/dev/null
EOF

chmod +x check_system.sh
./check_system.sh
```

---

## 📞 获取帮助

如果测试失败:
1. 查看 `logs/edm_debug.log` 找到具体错误
2. 访问 `monitor.php` 查看系统状态
3. 运行 `test_workflow.php` 定位问题
4. 检查本文档的"常见问题排查"部分
