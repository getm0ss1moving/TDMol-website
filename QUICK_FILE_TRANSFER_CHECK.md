# 快速文件传输检查指南

## 🚀 三种检查方式

### 1️⃣ 独立测试工具（推荐用于系统测试）

```bash
# 运行完整的文件传输测试
python3 test_file_transfer.py
```

**何时使用**：
- 初次部署系统时
- 系统出现问题需要诊断时
- 定期系统检查时

**优点**：
- 完整的测试流程
- 详细的输出信息
- 自动清理测试文件

---

### 2️⃣ 实时运行检查（EDM_server.py内置）

**自动运行**：每次任务提交时自动验证

**日志位置**：`logs/edm_debug.log`

**查看方式**：
```bash
tail -f logs/edm_debug.log
```

**日志内容**：
```
[2023-11-28 14:30:15] [INFO] Input file exists, size: 234 bytes
[2023-11-28 14:30:16] [INFO] Input file uploaded
[2023-11-28 14:30:16] [INFO] Verifying file transfer...
[2023-11-28 14:30:17] [INFO] Remote file size: 234 bytes
[2023-11-28 14:30:17] [SUCCESS] File transfer verified: size matches ✓
```

**何时使用**：
- 每次实际任务运行时
- 不需要额外操作，自动检查

---

### 3️⃣ 手动命令检查

```bash
# 在前端服务器
LOCAL_FILE="/var/www/bioinf2/edm_web/upload/task_123.txt"
LOCAL_SIZE=$(stat -f%z "$LOCAL_FILE")  # macOS
# 或
LOCAL_SIZE=$(stat -c%s "$LOCAL_FILE")  # Linux

echo "Local file size: $LOCAL_SIZE bytes"

# 在后端服务器（或通过SSH）
ssh -p 2349 user@backend-server "stat -c%s /data/yfang/EDM_new/web_apps/upload/task_123.txt"
```

**何时使用**：
- 快速检查特定文件
- 调试单个任务
- 不想运行完整测试

---

## 📊 检查内容对比

| 检查方式 | 验证SSH连接 | 验证文件存在 | 验证文件大小 | 验证文件内容 | 自动清理 |
|---------|------------|-------------|-------------|-------------|---------|
| test_file_transfer.py | ✅ | ✅ | ✅ | ✅ | ✅ |
| EDM_server.py内置 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 手动命令 | ❌ | ✅ | ✅ | ❌ | ❌ |

---

## 🔍 快速诊断

### 问题：不知道文件是否传输成功

**解决方案**：
```bash
# 查看最近的传输日志
tail -20 logs/edm_debug.log | grep -i "transfer"
```

### 问题：想测试传输功能但不想提交真实任务

**解决方案**：
```bash
# 运行独立测试
python3 test_file_transfer.py
```

### 问题：特定任务的文件传输失败

**解决方案**：
```bash
# 查看该任务的日志
grep "task_20231128001" logs/edm_debug.log
```

---

## ⚡ 一行命令快速检查

```bash
# 检查最近的文件传输状态
tail -100 logs/edm_debug.log | grep -E "SUCCESS|ERROR|File transfer"
```

**输出示例**：
```
[2023-11-28 14:30:17] [SUCCESS] File transfer verified: size matches ✓
[2023-11-28 14:35:22] [SUCCESS] File transfer verified: size matches ✓
[2023-11-28 14:40:18] [ERROR] File transfer verification FAILED: size mismatch
```

---

## 📝 总结

| 场景 | 推荐方法 | 命令 |
|------|---------|------|
| 系统初次部署 | 独立测试工具 | `python3 test_file_transfer.py` |
| 日常任务运行 | 内置自动检查 | 查看 `logs/edm_debug.log` |
| 快速验证某个文件 | 手动命令 | `ssh ... stat ...` |
| 定期系统检查 | 独立测试工具 | `python3 test_file_transfer.py` |
| 排查问题 | 查看日志 | `tail -f logs/edm_debug.log` |

---

## 🎯 最佳实践

1. **初次部署时**：
   ```bash
   # 配置好参数后运行
   python3 test_file_transfer.py
   ```

2. **正常运行时**：
   - 系统自动检查（EDM_server.py内置）
   - 定期查看日志：`tail -f logs/edm_debug.log`

3. **遇到问题时**：
   ```bash
   # 1. 查看最近日志
   tail -50 logs/edm_debug.log

   # 2. 运行完整测试
   python3 test_file_transfer.py

   # 3. 手动验证特定文件
   ssh -p 2349 user@backend "ls -lh /data/yfang/EDM_new/web_apps/upload/"
   ```

---

## 版本：1.0 | 更新：2025-11-28
