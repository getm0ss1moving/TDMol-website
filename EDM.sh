#!/bin/bash

# EDM_backend.sh - 后端执行脚本 (部署在后端服务器 202.121.180.146:2346)
# 路径: /data/yfang/EDM_web/1111/web_apps/EDM.sh
# 参数:
# $1 = email
# $2 = timeVar (任务ID)
# $3 = num_molecules (可选，默认100)
# $4 = guidance_scale (可选，默认5.0)

# ============================================================
# 日志函数
# ============================================================

LOG_DIR="/data/yfang/EDM_web/1111/web_apps/logs"
LOG_FILE="$LOG_DIR/edm_backend.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log "INFO" "============================================================"
log "INFO" "EDM_backend.sh started"
log "INFO" "Script location: $(readlink -f $0)"
log "INFO" "Working directory: $(pwd)"
log "INFO" "Parameters: email='$1', timeVar='$2', num_molecules='$3', guidance_scale='$4'"

# ============================================================
# 创建后端结果目录
# ============================================================

email="$1"
timeVar="$2"

if [ -z "$timeVar" ]; then
    log "ERROR" "timeVar is empty! Cannot proceed."
    exit 1
fi

target_dir="/data/yfang/EDM_web/1111/web_apps/result/${timeVar}/"
log "INFO" "Creating result directory: $target_dir"

if [ ! -d "$target_dir" ]; then
    mkdir -p "$target_dir"
    log "INFO" "Result directory created"
else
    log "WARNING" "Result directory already exists: $target_dir"
fi

# ============================================================
# 激活 conda 环境 edm_web
# ============================================================

log "INFO" "Activating conda environment: edm_web"

# 方法1: 尝试使用conda命令激活
if command -v conda &> /dev/null; then
    log "INFO" "Found conda command, activating edm_web environment..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate edm_web
    PYTHON_CMD="python"
    log "INFO" "Activated conda environment: edm_web"
    log "INFO" "Python location: $(which python)"
    log "INFO" "Python version: $(python --version 2>&1)"
else
    # 方法2: 直接使用conda环境中的python
    log "INFO" "Conda command not found, trying direct python path..."

    # 尝试多个可能的conda路径
    CONDA_PATHS=(
        "/data/yfang/anaconda3/envs/edm_web/bin/python"
        "/data/yfang/anaconda3/envs/edm_web/bin/python3"
        "/data/yfang/anaconda/envs/edm_web/bin/python"
        "/data/yfang/anaconda/envs/edm_web/bin/python3"
        "/home/yfang/anaconda3/envs/edm_web/bin/python"
        "/opt/anaconda3/envs/edm_web/bin/python"
    )

    for path in "${CONDA_PATHS[@]}"; do
        if [ -f "$path" ]; then
            PYTHON_CMD="$path"
            log "INFO" "Found Python at: $PYTHON_CMD"
            log "INFO" "Python version: $($PYTHON_CMD --version 2>&1)"
            break
        fi
    done

    # 如果都找不到，报错
    if [ -z "$PYTHON_CMD" ]; then
        log "ERROR" "Cannot find edm_web conda environment!"
        log "ERROR" "Please check conda installation path"
        exit 1
    fi
fi

# ============================================================
# 确定工作目录
# ============================================================

if [ -d "/data/yfang/EDM_web/1111/web_apps" ]; then
    BASE_DIR="/data/yfang/EDM_web/1111/web_apps"
elif [ -d "/home/yfang/EDM_web/1111/web_apps" ]; then
    BASE_DIR="/home/yfang/EDM_web/1111/web_apps"
else
    BASE_DIR="/workspace/EDM_web/1111/web_apps"
fi

log "INFO" "Base directory: $BASE_DIR"
cd "$BASE_DIR"
log "INFO" "Changed to working directory: $(pwd)"

# ============================================================
# 检查输入文件
# ============================================================

input_file="$BASE_DIR/upload/${timeVar}.txt"
log "INFO" "Checking input file: $input_file"

if [ -f "$input_file" ]; then
    file_size=$(stat -c%s "$input_file" 2>/dev/null || stat -f%z "$input_file" 2>/dev/null)
    log "INFO" "Input file found, size: $file_size bytes"
    log "INFO" "Input file content (first 200 chars):"
    head -c 200 "$input_file" | tee -a "$LOG_FILE"
    echo "" >> "$LOG_FILE"
else
    log "ERROR" "Input file not found: $input_file"
    exit 1
fi

# ============================================================
# 执行分子生成
# ============================================================

# 设置默认参数
NUM_MOLECULES=${3:-3}  # 默认100个分子
GUIDANCE_SCALE=${4:-5.0}  # 默认guidance scale为5.0

log "INFO" "Starting molecule generation..."
log "INFO" "  Task ID: $timeVar"
log "INFO" "  Email: $email"
log "INFO" "  Number of molecules: $NUM_MOLECULES"
log "INFO" "  Guidance scale: $GUIDANCE_SCALE"

# 检查 run_generation.py 是否存在
if [ ! -f "$BASE_DIR/run_generation.py" ]; then
    log "ERROR" "run_generation.py not found at $BASE_DIR/run_generation.py"
    exit 1
fi

log "INFO" "Executing run_generation.py..."

$PYTHON_CMD ./run_generation.py \
    --task_id "$timeVar" \
    --input_file "$BASE_DIR/upload/${timeVar}.txt" \
    --output_dir "$BASE_DIR/result/${timeVar}/" \
    --num_molecules "$NUM_MOLECULES" \
    --guidance_scale "$GUIDANCE_SCALE" 2>&1 | tee -a "$LOG_FILE"

exit_code=${PIPESTATUS[0]}

if [ $exit_code -ne 0 ]; then
    log "ERROR" "run_generation.py failed with exit code: $exit_code"
    exit 1
fi

log "INFO" "Molecule generation completed successfully"

# ============================================================
# 生成HTML结果页面
# ============================================================

log "INFO" "Generating HTML result pages..."

# 检查 processhtml.py 是否存在
if [ ! -f "$BASE_DIR/processhtml.py" ]; then
    log "ERROR" "processhtml.py not found at $BASE_DIR/processhtml.py"
    exit 1
fi

$PYTHON_CMD ./processhtml.py "$timeVar" "$email" 2>&1 | tee -a "$LOG_FILE"

exit_code=${PIPESTATUS[0]}

if [ $exit_code -ne 0 ]; then
    log "ERROR" "processhtml.py failed with exit code: $exit_code"
    exit 1
fi

log "INFO" "HTML generation completed successfully"

# ============================================================
# 发送邮件 (可选)
# ============================================================

if [ -n "$email" ] && [ "$email" != "" ]; then
    log "INFO" "Sending email notification to: $email"

    if [ -f "$BASE_DIR/send_email.py" ]; then
        $PYTHON_CMD ./send_email.py "$email" "$timeVar" 2>&1 | tee -a "$LOG_FILE"

        if [ $? -eq 0 ]; then
            log "INFO" "Email sent successfully"
        else
            log "WARNING" "Email sending failed"
        fi
    else
        log "WARNING" "send_email.py not found, skipping email notification"
    fi
else
    log "INFO" "No email provided, skipping email notification"
fi

# ============================================================
# 完成
# ============================================================

log "INFO" "Task $timeVar completed successfully!"
log "INFO" "Results saved to: $BASE_DIR/result/${timeVar}/"
log "INFO" "============================================================"

exit 0
