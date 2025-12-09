# EDM Web Application 部署指南

## 📁 文件分类

### 前端服务器文件 (部署在22端口)

```
/var/www/bioinf2/edm_web/
├── index.html              ✅ 用户界面
├── EDM.php                 ✅ 表单处理和等待页面
├── py.php                  ✅ AJAX调用的PHP脚本
├── EDM_frontend.sh         ✅ 前端执行脚本(调用EDM_server.py)
├── EDM_server.py           ✅ SSH连接到后端的Python脚本
├── upload/                 📁 用户输入文件目录
├── result/                 📁 结果文件目录
├── js/                     📁 JavaScript库
│   ├── jquery-3.4.1.min.js
│   ├── jquery.min.js
│   └── bootstrap.min.js
├── css/                    📁 CSS样式文件
│   ├── bootstrap.css
│   └── css.css
└── jsmol-16.3.33/         📁 JSmol 3D可视化库(可选)
```

### 后端服务器文件 (部署在2349端口)

```
/data/yfang/EDM_new/web_apps/
├── EDM.sh                  ✅ 后端执行脚本(真正的分子生成)
├── run_generation.py       ✅ 分子生成核心
├── processhtml.py          ✅ HTML结果生成
├── send_email.py           ✅ 邮件发送(可选)
├── model_runner.py         ✅ 模型运行器
├── app.py                  ✅ 原始应用(保留)
├── upload/                 📁 接收的用户文件
├── result/                 📁 生成的结果文件
└── [其他EDM模型相关文件]
```

---

## 🔧 配置修改清单

### 需要修改的文件和位置：

#### 1. **EDM_server.py** (前端服务器)
修改SSH连接参数：

```python
# 第10行 - 后端EDM.sh的路径
command = 'bash /data/yfang/EDM_new/web_apps/EDM.sh {} {}'.format(...)

# 第18、67行 - 后端服务器IP和端口
tran = paramiko.Transport(('YOUR_BACKEND_IP', YOUR_BACKEND_PORT))

# 第19、68行 - SSH用户名和密码
tran.connect(username="YOUR_USERNAME", password='YOUR_PASSWORD')

# 第36行 - 后端服务器IP
hostname='YOUR_BACKEND_IP'

# 第37行 - 后端服务器端口
port=YOUR_BACKEND_PORT

# 第38-39行 - SSH用户名和密码
username='YOUR_USERNAME'
password='YOUR_PASSWORD'

# 第45行 - 前端上传目录
local_path_input = '/var/www/bioinf2/edm_web/upload/' + timeVar + '.txt'

# 第46行 - 后端上传目录
remote_path_input = '/data/yfang/EDM_new/web_apps/upload/' + timeVar + '.txt'

# 第54-57行 - 前端和后端结果目录
local_path_brief = '/var/www/bioinf2/edm_web/result/' + timeVar + '_brief.html'
local_path_results_dir = '/var/www/bioinf2/edm_web/result/' + timeVar + '/'
remote_path_brief = '/data/yfang/EDM_new/web_apps/result/' + timeVar + '/brief.html'
remote_path_results = '/data/yfang/EDM_new/web_apps/result/' + timeVar + '/'
```

#### 2. **EDM.php** (前端服务器)
修改结果URL：

```php
# 第71、77、108行 - 结果页面URL
"http://YOUR_FRONTEND_URL/bioinf2/edm_web/result/" + timeVar + "_brief.html"
```

#### 3. **EDM.sh** (后端服务器)
修改Python路径和项目路径：

```bash
# 第18-24行 - Python解释器路径检测
if [ -f "/data/yfang/anaconda/EDM/bin/python" ]; then
    PYTHON_CMD="/data/yfang/anaconda/EDM/bin/python"
# 根据实际路径修改

# 第26-32行 - 项目路径检测
if [ -d "/data/yfang/EDM_new/web_apps" ]; then
    BASE_DIR="/data/yfang/EDM_new/web_apps"
# 根据实际路径修改
```

#### 4. **processhtml.py** (后端服务器)
修改后端结果目录：

```python
# 第108行
result_dir = f"/data/yfang/EDM_new/web_apps/result/{task_id}/"
```

#### 5. **send_email.py** (后端服务器)
修改结果URL：

```python
# 第35行
<a href="http://YOUR_FRONTEND_URL/bioinf2/edm_web/result/...">
```

---

## 📝 部署步骤

### 步骤1: 前端服务器部署

```bash
# 1. 创建目录
ssh user@frontend_server
mkdir -p /var/www/bioinf2/edm_web/upload
mkdir -p /var/www/bioinf2/edm_web/result

# 2. 上传前端文件
scp index.html user@frontend_server:/var/www/bioinf2/edm_web/
scp EDM.php user@frontend_server:/var/www/bioinf2/edm_web/
scp py.php user@frontend_server:/var/www/bioinf2/edm_web/
scp EDM_frontend.sh user@frontend_server:/var/www/bioinf2/edm_web/
scp EDM_server.py user@frontend_server:/var/www/bioinf2/edm_web/

# 3. 设置执行权限
chmod +x /var/www/bioinf2/edm_web/EDM_frontend.sh
chmod +x /var/www/bioinf2/edm_web/EDM_server.py

# 4. 设置目录权限
chmod 755 /var/www/bioinf2/edm_web/upload
chmod 755 /var/www/bioinf2/edm_web/result

# 5. 安装Python依赖
pip3 install paramiko
```

### 步骤2: 后端服务器部署

```bash
# 1. 创建目录
ssh user@backend_server -p 2349
mkdir -p /data/yfang/EDM_new/web_apps/upload
mkdir -p /data/yfang/EDM_new/web_apps/result

# 2. 上传后端文件
scp -P 2349 EDM.sh user@backend_server:/data/yfang/EDM_new/web_apps/
scp -P 2349 run_generation.py user@backend_server:/data/yfang/EDM_new/web_apps/
scp -P 2349 processhtml.py user@backend_server:/data/yfang/EDM_new/web_apps/
scp -P 2349 send_email.py user@backend_server:/data/yfang/EDM_new/web_apps/
scp -P 2349 model_runner.py user@backend_server:/data/yfang/EDM_new/web_apps/

# 3. 设置执行权限
chmod +x /data/yfang/EDM_new/web_apps/EDM.sh

# 4. 配置 Conda 环境 (重要!)
# 后端代码必须在 edm_web conda 环境中运行
conda activate edm_web

# 如果 edm_web 环境不存在，创建它:
conda create -n edm_web python=3.8 -y
conda activate edm_web

# 5. 安装Python依赖到 edm_web 环境
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch -y
conda install -c conda-forge rdkit -y
pip install paramiko numpy Pillow

# 6. 验证环境
python -c "import torch; import rdkit; print('Environment OK')"

# 详细的conda环境配置请查看 CONDA_ENV_SETUP.md
```

---

## 🔍 测试流程

### 1. 测试SSH连接
```bash
# 在前端服务器测试
ssh -p 2349 user@backend_server "echo 'SSH OK'"
```

### 2. 测试文件传输
```bash
# 在前端服务器测试
python3 -c "
import paramiko
tran = paramiko.Transport(('backend_ip', 2349))
tran.connect(username='user', password='pass')
print('Connection OK')
tran.close()
"
```

### 3. 测试完整流程
```bash
# 访问前端网页
http://YOUR_FRONTEND_URL/bioinf2/edm_web/index.html

# 输入测试文本
"A small aromatic molecule containing benzene rings"

# 提交并等待结果
```

---

## 🚨 故障排查

### 问题1: PHP无法执行bash脚本
**解决方案**:
```bash
# 检查PHP配置
php -i | grep disable_functions
# 确保exec, shell_exec没有被禁用

# 检查SELinux
getenforce
# 如果是Enforcing，可能需要设置权限
```

### 问题2: SSH连接失败
**解决方案**:
```bash
# 检查防火墙
firewall-cmd --list-ports
# 确保2349端口开放

# 检查SSH服务
systemctl status sshd
```

### 问题3: 文件权限错误
**解决方案**:
```bash
# 前端
chown -R www-data:www-data /var/www/bioinf2/edm_web/

# 后端
chown -R yfang:yfang /data/yfang/EDM_new/web_apps/
```

### 问题4: Python依赖缺失
**解决方案**:
```bash
# 后端安装完整依赖
pip install rdkit torch numpy paramiko Pillow
```

---

## 📊 文件流转图

```
用户输入 (文本)
    ↓
index.html
    ↓
EDM.php (保存到 upload/task_id.txt)
    ↓ (AJAX)
py.php
    ↓
EDM_frontend.sh (前端)
    ↓
EDM_server.py (SSH连接)
    ↓ [上传文件到后端]
    ↓ [执行后端EDM.sh]
    ↓
EDM.sh (后端)
    ↓
run_generation.py → 生成分子 → XYZ/SDF文件
    ↓
processhtml.py → 生成HTML
    ↓
send_email.py → 发送邮件(可选)
    ↓ [下载所有结果]
EDM_server.py
    ↓
用户查看 result/task_id_brief.html
```

---

## 📋 配置检查表

### 前端服务器
- [ ] index.html 正确部署
- [ ] EDM.php URL配置正确
- [ ] py.php 可执行
- [ ] EDM_frontend.sh 有执行权限
- [ ] EDM_server.py 连接参数正确
- [ ] upload/ 目录可写
- [ ] result/ 目录可写
- [ ] paramiko已安装

### 后端服务器
- [ ] EDM.sh 有执行权限
- [ ] Python环境完整
- [ ] 所有依赖已安装
- [ ] model_runner.py 可用
- [ ] upload/ 目录可写
- [ ] result/ 目录可写

### 网络配置
- [ ] 前端可SSH到后端
- [ ] 2349端口开放
- [ ] SFTP文件传输正常
- [ ] SMTP服务器可访问(邮件功能)

---

## 🎯 快速配置模板

将以下信息填写后，替换所有文件中的对应配置：

```ini
[Frontend]
frontend_url = http://YOUR_DOMAIN/bioinf2/edm_web/
frontend_path = /var/www/bioinf2/edm_web/

[Backend]
backend_ip = YOUR_BACKEND_IP
backend_port = YOUR_BACKEND_PORT
ssh_username = YOUR_USERNAME
ssh_password = YOUR_PASSWORD
backend_path = /data/yfang/EDM_new/web_apps/
python_path = /data/yfang/anaconda/EDM/bin/python

[Email]
smtp_server = smtp.163.com
smtp_user = YOUR_EMAIL@163.com
smtp_password = YOUR_SMTP_PASSWORD
```

---

## 版本信息
- 创建日期: 2025-11-28
- 最后更新: 2025-11-28
- 版本: 1.0
