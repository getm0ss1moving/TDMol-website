# Conda 环境配置说明

## 📋 后端需要的 conda 环境

后端代码必须在名为 `edm_web` 的 conda 环境中运行。

---

## 🔧 环境配置方式

### 方法1: 如果您已有 edm_web 环境

**检查环境是否存在**:
```bash
conda env list | grep edm_web
```

**检查环境中的Python路径**:
```bash
conda activate edm_web
which python
# 输出类似: /data/yfang/anaconda3/envs/edm_web/bin/python
```

**更新 EDM.sh 中的路径**:
如果您的conda路径不是默认的，请告诉我正确的路径，我会更新EDM.sh。

---

### 方法2: 创建新的 edm_web 环境

如果您还没有 `edm_web` 环境，按以下步骤创建:

**步骤1: 创建环境**
```bash
conda create -n edm_web python=3.8 -y
```

**步骤2: 激活环境**
```bash
conda activate edm_web
```

**步骤3: 安装必要的包**
```bash
# PyTorch (根据您的CUDA版本选择)
# CUDA 11.3
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch -y

# 或者 CPU版本
# conda install pytorch torchvision torchaudio cpuonly -c pytorch -y

# RDKit
conda install -c conda-forge rdkit -y

# 其他依赖
pip install paramiko numpy Pillow
```

**步骤4: 验证安装**
```bash
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import rdkit; print('RDKit OK')"
python -c "import paramiko; print('Paramiko OK')"
```

---

## 📂 EDM.sh 环境激活机制

EDM.sh 脚本会自动尝试两种方式激活环境:

### 方式1: 使用 conda activate (推荐)
```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate edm_web
```

### 方式2: 直接使用Python路径
如果conda命令不可用，脚本会尝试以下路径:
- `/data/yfang/anaconda3/envs/edm_web/bin/python`
- `/data/yfang/anaconda/envs/edm_web/bin/python`
- `/home/yfang/anaconda3/envs/edm_web/bin/python`
- `/opt/anaconda3/envs/edm_web/bin/python`

---

## 🔍 验证环境配置

### 测试1: 手动激活环境
```bash
# SSH到后端服务器
ssh -p 2349 user@backend_server

# 激活环境
conda activate edm_web

# 检查Python
which python
python --version

# 测试导入
python -c "import torch; import rdkit; print('Environment OK')"
```

### 测试2: 运行EDM.sh
```bash
cd /data/yfang/EDM_new/web_apps/
bash EDM.sh "" "test123"
```

**预期输出**:
```
Found conda command, activating edm_web environment...
Activated conda environment: edm_web
Python location: /data/yfang/anaconda3/envs/edm_web/bin/python
Python version: Python 3.8.x
Working directory: /data/yfang/EDM_new/web_apps
...
```

---

## 🐛 常见问题

### 问题1: conda: command not found

**原因**: conda 未添加到 PATH

**解决方案**:
```bash
# 找到conda安装路径
find /data /home /opt -name "conda.sh" 2>/dev/null

# 添加到 .bashrc
echo 'source /path/to/anaconda3/etc/profile.d/conda.sh' >> ~/.bashrc
source ~/.bashrc
```

### 问题2: 环境激活失败

**原因**: conda 初始化问题

**解决方案**:
```bash
# 重新初始化conda
conda init bash
source ~/.bashrc

# 或者直接使用绝对路径
/data/yfang/anaconda3/envs/edm_web/bin/python --version
```

### 问题3: ImportError: No module named 'torch'

**原因**: edm_web 环境中缺少 PyTorch

**解决方案**:
```bash
conda activate edm_web
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch -y
```

### 问题4: 路径不匹配

**症状**: EDM.sh 显示 "Cannot find edm_web conda environment"

**解决方案**: 告诉我您的实际conda路径，我会更新EDM.sh中的路径列表

**查找conda路径**:
```bash
conda info --base
# 输出: /data/yfang/anaconda3

# Python路径应该是:
# /data/yfang/anaconda3/envs/edm_web/bin/python
```

---

## 📝 需要告诉我的信息

如果您的conda路径与默认不同，请告诉我:

1. **Conda安装路径**:
   ```bash
   conda info --base
   ```

2. **edm_web环境Python路径**:
   ```bash
   conda activate edm_web
   which python
   ```

3. **后端项目路径**:
   ```bash
   pwd
   # 在您的项目目录下执行
   ```

我会根据您的实际路径更新 `EDM.sh` 文件。

---

## ✅ 配置完成检查清单

- [ ] conda 已安装
- [ ] edm_web 环境已创建
- [ ] PyTorch 已安装在 edm_web 中
- [ ] RDKit 已安装在 edm_web 中
- [ ] paramiko 已安装
- [ ] EDM.sh 中的路径已更新
- [ ] 手动运行 EDM.sh 测试成功

---

## 📦 完整的环境导出/导入

### 导出当前环境
```bash
conda activate edm_web
conda env export > edm_web_environment.yml
```

### 在另一台机器上导入
```bash
conda env create -f edm_web_environment.yml
```

---

## 🎯 最佳实践

1. **使用conda activate (推荐)**
   - 自动设置所有环境变量
   - 避免依赖冲突

2. **使用绝对路径 (备选)**
   - 适用于cron job或非交互式脚本
   - 确保路径正确

3. **定期更新依赖**
   ```bash
   conda activate edm_web
   conda update --all
   ```

4. **创建环境备份**
   ```bash
   conda env export > edm_web_backup_$(date +%Y%m%d).yml
   ```
