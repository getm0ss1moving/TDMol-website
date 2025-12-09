# Shell脚本检查报告

检查时间: 2025-12-01
检查范围: web_apps/*.sh

---

## ✅ 通过检查的文件

以下文件shebang正确，格式符合要求：

| 文件名 | Shebang | 状态 |
|--------|---------|------|
| EDM.sh | #!/bin/bash | ✅ 正确 |
| EDM_backend.sh | #!/bin/bash | ✅ 正确 |
| EDM_frontend.sh | #!/bin/bash | ✅ 正确 |
| queue_edm.sh | #!/bin/bash | ✅ 正确 |
| init_queue.sh | #!/bin/bash | ✅ 正确 |
| check_queue.sh | #!/bin/bash | ✅ 正确 |
| clear_queue.sh | #!/bin/bash | ✅ 正确 |
| test_queue.sh | #!/bin/bash | ✅ 正确 |

---

## ⚠️ 发现问题的文件

### queue.sh

**问题：**
- 路径错误：使用了 `/data/liuyuan/FoldExplorer` 而不是 EDM 的路径
- 这个文件看起来是从另一个项目（FoldExplorer）复制来的

**当前代码片段：**
```bash
#!/bin/bash

set -e
# 定义清理和调度的函数
cleanup_and_next() {
    cd /data/liuyuan/FoldExplorer  # ❌ 错误的路径
    if [[ -z "$1" ]]; then
        sed -i '/None/d' running.queue
```

**建议：**
- 这个文件可能是旧文件，已被 `queue_edm.sh` 替代
- 建议删除或更新为正确的 EDM 路径

---

## 📋 换行符问题

**所有.sh文件都需要注意：**

由于这些文件是在Windows系统创建的，上传到Linux服务器后可能会出现换行符问题 (CRLF vs LF)。

**解决方案（任选其一）：**

### 方案1：批量转换所有.sh文件
```bash
# 在服务器上执行
cd /var/www/bioinf2/edm_web

# 如果有 dos2unix
find . -name "*.sh" -type f -exec dos2unix {} \;

# 如果没有 dos2unix，使用 sed
find . -name "*.sh" -type f -exec sed -i 's/\r$//' {} \;

# 设置执行权限
find . -name "*.sh" -type f -exec chmod +x {} \;
```

### 方案2：逐个转换
```bash
dos2unix EDM.sh
dos2unix EDM_backend.sh
dos2unix queue_edm.sh
dos2unix init_queue.sh
dos2unix check_queue.sh
dos2unix clear_queue.sh
dos2unix test_queue.sh

chmod +x *.sh
```

---

## 🔧 修复建议

### 1. 删除或修复 queue.sh

**选项A：删除（推荐）**
```bash
rm queue.sh
```
理由：已被 `queue_edm.sh` 替代

**选项B：修复路径**
需要将所有 `/data/liuyuan/FoldExplorer` 替换为正确的 EDM 路径

### 2. 验证所有脚本

上传后在服务器执行：
```bash
# 检查文件格式
file *.sh

# 正确的输出应该是：
# xxx.sh: Bash script, ASCII text executable

# 如果看到 "with CRLF line terminators"，需要转换
```

### 3. 测试关键脚本

```bash
# 测试语法
bash -n EDM.sh
bash -n queue_edm.sh
bash -n init_queue.sh
bash -n check_queue.sh

# 没有输出表示语法正确
```

---

## 📝 文件用途说明

| 文件 | 用途 | 是否必需 |
|------|------|----------|
| EDM.sh | 前端执行入口 | ✅ 必需 |
| EDM_backend.sh | 后端执行脚本 | ✅ 必需 |
| EDM_frontend.sh | 前端执行脚本（备用） | ⚠️ 可选 |
| queue_edm.sh | 排队管理主脚本 | ✅ 必需 |
| init_queue.sh | 初始化队列系统 | ✅ 必需 |
| check_queue.sh | 查看队列状态 | ✅ 必需 |
| clear_queue.sh | 清空队列（紧急用） | ⚠️ 可选 |
| test_queue.sh | 测试脚本 | ⚠️ 测试用 |
| queue.sh | 旧版排队脚本？ | ❌ 建议删除 |

---

## ✅ 部署检查清单

上传所有.sh文件到服务器后，执行以下检查：

- [ ] 转换换行符 (`dos2unix *.sh` 或 `sed -i 's/\r$//' *.sh`)
- [ ] 设置执行权限 (`chmod +x *.sh`)
- [ ] 验证文件格式 (`file *.sh`)
- [ ] 测试语法 (`bash -n *.sh`)
- [ ] 删除或修复 `queue.sh`
- [ ] 测试初始化 (`bash init_queue.sh`)
- [ ] 测试队列检查 (`bash check_queue.sh`)
- [ ] 运行完整测试 (`bash test_queue.sh`)

---

## 🎯 推荐的部署步骤

```bash
# 1. 进入工作目录
cd /var/www/bioinf2/edm_web

# 2. 备份旧文件（如果存在）
mkdir -p backup_$(date +%Y%m%d)
cp *.sh backup_$(date +%Y%m%d)/ 2>/dev/null || true

# 3. 上传新文件（从本地）
# （使用 scp、WinSCP 或其他工具）

# 4. 转换换行符
find . -maxdepth 1 -name "*.sh" -type f -exec sed -i 's/\r$//' {} \;

# 5. 设置权限
chmod +x *.sh

# 6. 删除旧的 queue.sh（如果存在）
rm -f queue.sh

# 7. 验证
file *.sh
bash -n EDM.sh
bash -n queue_edm.sh
bash -n init_queue.sh

# 8. 测试
bash init_queue.sh
bash check_queue.sh

echo "部署完成！"
```

---

**总结：**
- 8个文件格式正确 ✅
- 1个文件需要处理（queue.sh）⚠️
- 所有文件需要转换换行符 ⚠️
- 所有文件需要设置执行权限 ⚠️
