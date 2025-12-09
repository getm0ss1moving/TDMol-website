# 文件传输检测工具使用指南

## 📋 工具说明

`test_file_transfer.py` 是一个独立的文件传输测试工具，用于验证前端服务器到后端服务器的文件传输功能是否正常。

---

## 🎯 主要功能

1. ✅ 测试SSH连接到后端服务器
2. ✅ 创建测试文件并上传到后端
3. ✅ 验证文件是否存在于后端
4. ✅ 验证文件大小是否正确
5. ✅ 验证文件内容是否完整
6. ✅ 自动清理测试文件

---

## 🔧 配置步骤

### 步骤1: 修改配置参数

编辑 `test_file_transfer.py` 文件，修改以下配置：

```python
# 后端服务器配置
BACKEND_IP = '192.168.1.100'          # 改成您的后端服务器IP
BACKEND_PORT = 2349                    # 后端SSH端口
SSH_USERNAME = 'your_username'         # SSH用户名
SSH_PASSWORD = 'your_password'         # SSH密码

# 路径配置
FRONTEND_UPLOAD_DIR = '/var/www/bioinf2/edm_web/upload/'
BACKEND_UPLOAD_DIR = '/data/yfang/EDM_new/web_apps/upload/'
```

### 步骤2: 确保依赖已安装

```bash
pip3 install paramiko
```

---

## 🚀 使用方法

### 方法1: 直接运行（推荐）

在前端服务器上运行：

```bash
cd /var/www/bioinf2/edm_web/
python3 test_file_transfer.py
```

### 方法2: 添加执行权限后运行

```bash
chmod +x test_file_transfer.py
./test_file_transfer.py
```

---

## 📊 输出示例

### 成功的输出：

```
============================================================
EDM 文件传输测试工具
============================================================

ℹ 测试时间: 2023-11-28 14:30:15
ℹ 后端服务器: 192.168.1.100:2349
ℹ 测试文件: test_transfer_20231128143015.txt

ℹ 预检查: 测试SSH连接
✓ SSH连接正常: 192.168.1.100:2349

ℹ 步骤1: 创建测试文件
✓ 测试文件已创建: /var/www/bioinf2/edm_web/upload/test_transfer_20231128143015.txt
ℹ   文件大小: 89 bytes

ℹ 步骤2: 上传文件到后端服务器
ℹ   连接到后端服务器: 192.168.1.100:2349
ℹ   上传文件: /var/www/bioinf2/edm_web/upload/test_transfer_20231128143015.txt -> /data/yfang/EDM_new/web_apps/upload/test_transfer_20231128143015.txt
✓ 文件上传成功

ℹ 步骤3: 验证后端文件
✓ 文件存在于后端: /data/yfang/EDM_new/web_apps/upload/test_transfer_20231128143015.txt
ℹ   远程文件大小: 89 bytes
ℹ   本地文件大小: 89 bytes
✓ 文件大小匹配 ✓
✓ 文件内容匹配 ✓

ℹ 步骤4: 清理测试文件
✓ 本地测试文件已删除: /var/www/bioinf2/edm_web/upload/test_transfer_20231128143015.txt
✓ 远程测试文件已删除: /data/yfang/EDM_new/web_apps/upload/test_transfer_20231128143015.txt

============================================================
测试结果
============================================================

✓ 所有测试通过！文件传输功能正常。
```

### 失败的输出示例：

```
============================================================
EDM 文件传输测试工具
============================================================

ℹ 测试时间: 2023-11-28 14:30:15
ℹ 后端服务器: 192.168.1.100:2349
ℹ 测试文件: test_transfer_20231128143015.txt

ℹ 预检查: 测试SSH连接
✗ SSH连接失败: [Errno 111] Connection refused

✗ 测试失败：无法连接到后端服务器
ℹ 请检查以下配置：
ℹ   - BACKEND_IP: 192.168.1.100
ℹ   - BACKEND_PORT: 2349
ℹ   - SSH_USERNAME: your_username
ℹ   - SSH_PASSWORD: ********
```

---

## 🐛 故障排查

### 问题1: SSH连接失败

**错误信息**：
```
✗ SSH连接失败: [Errno 111] Connection refused
```

**解决方案**：
1. 检查后端服务器IP和端口是否正确
2. 确认后端SSH服务是否运行：
   ```bash
   ssh -p 2349 user@backend-ip
   ```
3. 检查防火墙设置

### 问题2: 权限被拒绝

**错误信息**：
```
✗ 上传文件时出错: Permission denied
```

**解决方案**：
1. 检查后端upload目录权限：
   ```bash
   ssh -p 2349 user@backend-ip "ls -ld /data/yfang/EDM_new/web_apps/upload/"
   ```
2. 修改权限（如果需要）：
   ```bash
   ssh -p 2349 user@backend-ip "chmod 755 /data/yfang/EDM_new/web_apps/upload/"
   ```

### 问题3: 文件大小不匹配

**错误信息**：
```
✗ 文件大小不匹配！预期 89，实际 0
```

**可能原因**：
- 磁盘空间不足
- 文件传输中断
- 网络不稳定

**解决方案**：
1. 检查后端磁盘空间：
   ```bash
   ssh -p 2349 user@backend-ip "df -h"
   ```
2. 重新运行测试
3. 检查网络连接

### 问题4: 文件内容不匹配

**错误信息**：
```
✗ 文件内容不匹配！
```

**可能原因**：
- 文件编码问题
- 文件传输损坏

**解决方案**：
1. 检查文件编码设置
2. 尝试使用二进制模式传输
3. 检查网络质量

---

## 🔄 与现有系统集成

### 在EDM.php中调用测试

您可以在实际文件上传前先运行测试：

```php
// 在 EDM.php 中
$test_result = shell_exec('python3 test_file_transfer.py 2>&1');
if (strpos($test_result, '所有测试通过') !== false) {
    // 继续正常流程
    echo "文件传输测试通过，开始处理任务...\n";
} else {
    // 报告错误
    echo "文件传输测试失败，请检查系统配置\n";
    exit(1);
}
```

### 定期自动测试

添加到crontab进行定期测试：

```bash
# 每小时测试一次文件传输
0 * * * * cd /var/www/bioinf2/edm_web && python3 test_file_transfer.py >> logs/transfer_test.log 2>&1
```

---

## 📝 测试检查清单

运行测试前确认：

- [ ] 后端服务器IP和端口配置正确
- [ ] SSH用户名和密码正确
- [ ] paramiko已安装
- [ ] 前端upload目录存在且可写
- [ ] 后端upload目录存在且可写
- [ ] 网络连接正常
- [ ] SSH端口未被防火墙阻挡

---

## 💡 高级用法

### 自定义测试文件大小

修改 `TEST_CONTENT` 变量来测试大文件传输：

```python
# 生成1MB的测试内容
TEST_CONTENT = "X" * (1024 * 1024)
```

### 测试多个文件

修改脚本循环上传多个文件：

```python
for i in range(10):
    TEST_FILENAME = f"test_{i}.txt"
    # ... 执行测试
```

### 记录测试日志

将输出重定向到日志文件：

```bash
python3 test_file_transfer.py >> logs/transfer_test.log 2>&1
```

---

## 📊 与monitor.php集成

测试结果可以在monitor.php中显示。在monitor.php中添加：

```php
// 运行文件传输测试
$transfer_test = shell_exec('cd /var/www/bioinf2/edm_web && python3 test_file_transfer.py 2>&1');

// 检查结果
if (strpos($transfer_test, '所有测试通过') !== false) {
    echo '<div class="alert alert-success">✓ 文件传输功能正常</div>';
} else {
    echo '<div class="alert alert-danger">✗ 文件传输测试失败</div>';
    echo '<pre>' . htmlspecialchars($transfer_test) . '</pre>';
}
```

---

## ⚠️ 注意事项

1. **安全性**：脚本中包含SSH密码，请确保文件权限设置为600
   ```bash
   chmod 600 test_file_transfer.py
   ```

2. **测试文件自动清理**：脚本会自动删除测试文件，但如果脚本异常终止，可能需要手动清理

3. **网络延迟**：如果网络较慢，可以增加 `time.sleep()` 的等待时间

4. **并发测试**：避免同时运行多个测试实例，可能导致冲突

---

## 版本信息

- 创建日期：2025-11-28
- 版本：1.0
- 依赖：Python 3.6+, paramiko
