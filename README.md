# EDM Web Application - 完整说明

## 📖 项目概述

这是一个基于EDM (Equivariant Diffusion Model) 的分子生成Web应用，完全仿照RNAJog的架构实现。用户可以通过文本描述生成新的分子结构，并查看3D/2D可视化结果。

---

## 🏗️ 系统架构

```
前端服务器 (22端口)          后端服务器 (2349端口)
     |                              |
index.html                          |
     ↓                              |
  EDM.php                           |
     ↓ (AJAX)                       |
  py.php                            |
     ↓                              |
EDM_frontend.sh                     |
     ↓                              |
EDM_server.py -----(SSH/SFTP)----> EDM.sh (激活 edm_web conda环境)
                                    ↓
                            run_generation.py
                                    ↓
                            processhtml.py
                                    ↓
                            send_email.py (可选)
                                    ↓
                    (结果传回前端服务器)
                                    ↓
                    brief.html & result_X.html
```

---

## 📁 文件清单

### 前端文件 (部署在前端22服务器)
- `index.html` - 用户界面
- `EDM.php` - 表单处理和等待页面
- `py.php` - AJAX调用入口
- `EDM_frontend.sh` - 前端执行脚本
- `EDM_server.py` - SSH连接到后端
- `monitor.php` - 实时监控面板 (新增)
- `test_workflow.php` - 系统测试工具 (新增)

### 后端文件 (部署在后端2349服务器)
- `EDM.sh` - 后端执行脚本 (**需要激活 edm_web conda环境**)
- `run_generation.py` - 分子生成核心
- `processhtml.py` - HTML结果生成
- `send_email.py` - 邮件发送
- `model_runner.py` - 模型运行器
- `app.py` - 原始应用 (保留)

### 文档文件
- `README.md` - 本文件
- `DEPLOYMENT_GUIDE.md` - 部署指南
- `CONDA_ENV_SETUP.md` - Conda环境配置 (**重要**)
- `TESTING_GUIDE.md` - 测试验证指南
- `README_WORKFLOW.md` - 工作流程详解
- `FILES_SUMMARY.md` - 文件清单

---

## ⚙️ 重要配置要求

### 🔴 Conda 环境 (必须)

后端代码**必须**在名为 `edm_web` 的 conda 环境中运行！

**快速配置**:
```bash
# 1. 创建环境
conda create -n edm_web python=3.8 -y

# 2. 激活环境
conda activate edm_web

# 3. 安装依赖
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch -y
conda install -c conda-forge rdkit -y
pip install paramiko numpy Pillow

# 4. 验证
python -c "import torch; import rdkit; print('OK')"
```

**详细说明**: 请查看 `CONDA_ENV_SETUP.md`

---

## 🚀 快速开始

### 1. 部署前端
```bash
# 上传文件到前端服务器
scp index.html EDM.php py.php EDM_frontend.sh EDM_server.py \
    user@frontend:/var/www/bioinf2/edm_web/

# 设置权限
chmod +x EDM_frontend.sh EDM_server.py
mkdir -p upload result logs
chmod 755 upload result logs
```

### 2. 部署后端
```bash
# 上传文件到后端服务器
scp -P 2349 EDM.sh run_generation.py processhtml.py send_email.py model_runner.py \
    user@backend:/data/yfang/EDM_new/web_apps/

# 设置权限
chmod +x EDM.sh
mkdir -p upload result
chmod 755 upload result

# 激活conda环境 (重要!)
conda activate edm_web
```

### 3. 配置参数
修改以下文件中的服务器配置:
- `EDM_server.py` - 后端IP、端口、SSH账号密码
- `EDM.php` - 结果URL
- `EDM.sh` - conda路径 (如果默认路径不匹配)

详细配置说明请查看 `DEPLOYMENT_GUIDE.md`

### 4. 测试系统
访问: `http://your-server/bioinf2/edm_web/test_workflow.php`

---

## 📊 监控和验证

### 实时监控面板
访问: `http://your-server/bioinf2/edm_web/monitor.php`

功能:
- 📈 系统统计 (上传数、完成数、完成率)
- 📝 最近任务列表
- 📜 实时日志 (自动刷新)
- ℹ️ 系统信息

### 查看日志
```bash
# 实时查看
tail -f logs/edm_debug.log

# 查看最后50行
tail -50 logs/edm_debug.log
```

### 手动测试
```bash
# 前端测试
python3 EDM_server.py "" "test123"

# 后端测试 (在后端服务器上)
conda activate edm_web
bash EDM.sh "" "test123"
```

详细测试说明请查看 `TESTING_GUIDE.md`

---

## 🔧 需要配置的参数

告诉我以下信息，我可以帮您批量修改配置:

### 网络配置
1. **前端服务器URL**: `http://YOUR_DOMAIN/bioinf2/edm_web/`
2. **后端服务器IP**: `YOUR_BACKEND_IP`
3. **后端服务器端口**: `YOUR_BACKEND_PORT` (例如: 2349)
4. **SSH用户名**: `YOUR_USERNAME`
5. **SSH密码**: `YOUR_PASSWORD`

### 路径配置
6. **前端项目路径**: `/var/www/bioinf2/edm_web/`
7. **后端项目路径**: `/data/yfang/EDM_new/web_apps/`
8. **Conda环境路径**: 运行 `conda info --base` 获取

### Conda环境
9. **edm_web环境Python路径**: 运行 `conda activate edm_web && which python` 获取

---

## 📝 使用流程

### 用户视角
1. 访问 `index.html`
2. 输入分子描述 (英文)
3. 填写邮箱 (可选)
4. 点击 Submit
5. 等待页面显示结果链接
6. 点击链接查看结果

### 系统执行流程
1. EDM.php 保存用户输入到 `upload/task_id.txt`
2. py.php 调用 EDM_frontend.sh
3. EDM_frontend.sh 调用 EDM_server.py
4. EDM_server.py 上传文件到后端并执行 EDM.sh
5. 后端 EDM.sh 激活 edm_web 环境
6. run_generation.py 生成3个分子
7. processhtml.py 生成HTML页面
8. send_email.py 发送邮件 (如果有邮箱)
9. EDM_server.py 下载所有结果回前端
10. 用户查看结果

---

## 🎯 生成的结果

每个任务生成:
- `brief.html` - 结果概览页面
- `result_1.html` - 分子1详情 (含3D可视化)
- `result_2.html` - 分子2详情
- `result_3.html` - 分子3详情
- `molecule_X.xyz` - XYZ坐标文件
- `molecule_X.sdf` - SDF结构文件
- `summary.json` - 任务摘要

---

## 🐛 常见问题

### 1. conda: command not found
**解决**: 查看 `CONDA_ENV_SETUP.md` 中的"问题1"

### 2. 文件上传失败
**解决**: 检查 `upload/` 目录权限，查看日志

### 3. SSH连接失败
**解决**: 检查网络、端口、防火墙配置

### 4. Python依赖缺失
**解决**: 确保在 `edm_web` 环境中安装了所有依赖

### 5. 结果文件未生成
**解决**:
- 查看 `logs/edm_debug.log`
- 在后端手动运行 `EDM.sh`
- 检查 conda 环境是否激活

详细排查请查看 `TESTING_GUIDE.md`

---

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| README.md | 项目概述 (本文件) |
| DEPLOYMENT_GUIDE.md | 详细部署步骤 |
| CONDA_ENV_SETUP.md | Conda环境配置 (**重要**) |
| TESTING_GUIDE.md | 测试验证方法 |
| README_WORKFLOW.md | 工作流程详解 |
| FILES_SUMMARY.md | 文件清单总结 |

---

## ✅ 部署检查清单

### 前端
- [ ] 所有文件已上传
- [ ] 目录权限正确 (upload, result, logs)
- [ ] EDM_frontend.sh 可执行
- [ ] EDM_server.py 连接参数已配置
- [ ] paramiko 已安装

### 后端
- [ ] 所有文件已上传
- [ ] EDM.sh 可执行
- [ ] **edm_web conda 环境已创建**
- [ ] **所有依赖已安装在 edm_web 环境**
- [ ] conda路径已配置 (如果非默认)
- [ ] 目录权限正确

### 网络
- [ ] 前端可SSH到后端
- [ ] SFTP文件传输正常
- [ ] 防火墙端口开放

### 测试
- [ ] test_workflow.php 全部通过
- [ ] monitor.php 可访问
- [ ] 提交测试任务成功
- [ ] 日志文件正常生成

---

## 📞 支持

- 查看日志: `logs/edm_debug.log`
- 监控面板: `monitor.php`
- 测试工具: `test_workflow.php`
- 详细文档: 见上方文档索引

---

## 🎉 成功标志

系统正常运行时:
- ✅ monitor.php 显示任务完成率接近100%
- ✅ logs/edm_debug.log 显示 [SUCCESS] 消息
- ✅ result/ 目录有HTML文件
- ✅ 3D分子可视化正常加载

---

**版本**: 1.0
**最后更新**: 2025-11-28
**重要**: 后端必须使用 `edm_web` conda 环境！
