#!/bin/bash

# EDM.sh - 前端执行脚本 (部署在前端服务器)
# 这个脚本在前端服务器执行，调用EDM_server.py来SSH到后端
# 参数:
# $1 = email
# $2 = timeVar (任务ID)

# ============================================================
# 激活 conda base 环境 (包含 paramiko)
# ============================================================

# 方法1: 尝试使用conda命令激活base环境
if command -v conda &> /dev/null; then
    echo "Found conda command, activating base environment..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate base
    PYTHON_CMD="python"
    echo "Activated conda environment: base"
    echo "Python location: $(which python)"
    echo "Python version: $(python --version)"
else
    # 方法2: 直接使用conda base环境中的python
    echo "Conda command not found, trying direct python path..."

    # 尝试多个可能的conda路径
    CONDA_PATHS=(
        "/root/anaconda3/bin/python"
        "/root/anaconda3/bin/python3"
        "/home/anaconda3/bin/python"
        "/opt/anaconda3/bin/python"
        "/usr/local/anaconda3/bin/python"
        "$(which python3)"
    )

    for path in "${CONDA_PATHS[@]}"; do
        if [ -f "$path" ]; then
            # 测试这个python是否有paramiko
            if $path -c "import paramiko" 2>/dev/null; then
                PYTHON_CMD="$path"
                echo "Found Python with paramiko at: $PYTHON_CMD"
                echo "Python version: $($PYTHON_CMD --version)"
                break
            fi
        fi
    done

    # 如果都找不到，报错
    if [ -z "$PYTHON_CMD" ]; then
        echo "ERROR: Cannot find Python with paramiko installed!"
        echo "Please check conda installation or install paramiko"
        exit 1
    fi
fi

# ============================================================
# 调用EDM_server.py，它会SSH到后端服务器执行后端的EDM.sh
# ============================================================

echo "Calling EDM_server.py with email=$1, timeVar=$2"
$PYTHON_CMD EDM_server.py "$1" "$2"

exit_code=$?
echo "EDM_server.py finished with exit code: $exit_code"
exit $exit_code
