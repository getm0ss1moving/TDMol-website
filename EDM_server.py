import paramiko
import sys
import os
import datetime

# 日志函数
def log(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = "[{0}] [{1}] {2}\n".format(timestamp, level, message)
    print(log_message.strip())

    # 写入日志文件
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "edm_debug.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message)

# 获取命令行参数 - 只有 email 和 timeVar
log("=" * 60)
log("EDM_server.py started")
log("Arguments: {0}".format(sys.argv))

email = sys.argv[1] if len(sys.argv) > 1 else ""
timeVar = sys.argv[2] if len(sys.argv) > 2 else ""

log("Email: {0}".format(email))
log("Task ID: {0}".format(timeVar))

# 构建远程执行命令 (类似RNAJog.sh)
# 使用引号包裹参数，确保空字符串也能正确传递
command = "bash /data/yfang/EDM_web/1111/web_apps/EDM.sh '{0}' '{1}'".format(
    email, timeVar
)
log("Remote command: {0}".format(command))

# 文件传输函数
def file_transfer(local_path, remote_path, way="upload"):
    """上传或下载文件到/从远程服务器 (2349端口)"""
    tran = paramiko.Transport(('202.121.180.146', 2346))
    tran.connect(username="yfang", password='20250912')
    sftp = paramiko.SFTPClient.from_transport(tran)

    if way == "upload":
        sftp.put(local_path, remote_path)
    elif way == "download":
        sftp.get(remote_path, local_path)
    else:
        raise Exception("wrong way!")

    tran.close()

def exec_command(command):
    """在远程服务器上执行命令"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname='202.121.180.146',
        port=2346,
        username='yfang',
        password='20250912'
    )
    stdin, stdout, stderr = client.exec_command(command)
    return stdout.read(), stderr.read()

# 1. 上传输入文件到2349服务器
log("Step 1: Uploading input file to backend")
local_path_input = '/var/www/bioinf/TDMol/upload/' + timeVar + '.txt'
remote_path_input = '/data/yfang/EDM_web/1111/web_apps/upload/' + timeVar + '.txt'

log("Local input: {0}".format(local_path_input))
log("Remote input: {0}".format(remote_path_input))

if os.path.exists(local_path_input):
    local_size = os.path.getsize(local_path_input)
    log("Input file exists, size: {0} bytes".format(local_size))
    try:
        file_transfer(local_path_input, remote_path_input, way="upload")
        log("Input file uploaded", "INFO")

        # 验证文件是否成功传输到后端
        log("Verifying file transfer...")
        try:
            tran = paramiko.Transport(('202.121.180.146', 2346))
            tran.connect(username='yfang', password='20250912')
            sftp = paramiko.SFTPClient.from_transport(tran)

            # 检查远程文件是否存在
            remote_stat = sftp.stat(remote_path_input)
            remote_size = remote_stat.st_size

            log("Remote file size: {0} bytes".format(remote_size))

            # 验证文件大小
            if remote_size == local_size:
                log("File transfer verified: size matches ✓", "SUCCESS")
            else:
                log("File transfer verification FAILED: size mismatch (local: {0}, remote: {1})".format(local_size, remote_size), "ERROR")
                sftp.close()
                tran.close()
                sys.exit(1)

            sftp.close()
            tran.close()

        except Exception as ve:
            log("File transfer verification failed: {0}".format(ve), "ERROR")
            log("Warning: Cannot verify file transfer, but continuing...", "WARNING")

    except Exception as e:
        log("Failed to upload input file: {0}".format(e), "ERROR")
        sys.exit(1)
else:
    log("Input file not found: {0}".format(local_path_input), "ERROR")
    sys.exit(1)

# 2. 在后端服务器上执行命令
log("Step 2: Executing command on backend server")
log("This may take several minutes, please wait...")
try:
    stdout, stderr = exec_command(command)
    log("Command finished execution")

    # 记录详细的输出
    if stdout:
        stdout_text = stdout.decode('utf-8')
        log("STDOUT (length: {0} bytes):".format(len(stdout)))
        # 记录最后1000个字符，避免日志过大
        if len(stdout_text) > 1000:
            log("STDOUT (last 1000 chars): ...{0}".format(stdout_text[-1000:]))
        else:
            log("STDOUT: {0}".format(stdout_text))
    else:
        log("STDOUT: (empty)")

    if stderr:
        stderr_text = stderr.decode('utf-8')
        log("STDERR (length: {0} bytes):".format(len(stderr)), "WARNING")
        # 记录最后1000个字符
        if len(stderr_text) > 1000:
            log("STDERR (last 1000 chars): ...{0}".format(stderr_text[-1000:]), "WARNING")
        else:
            log("STDERR: {0}".format(stderr_text), "WARNING")
    else:
        log("STDERR: (empty)")

    log("Backend task completed successfully", "SUCCESS")
except Exception as e:
    log("Failed to execute command: {0}".format(e), "ERROR")
    import traceback
    log("Traceback: {0}".format(traceback.format_exc()), "ERROR")
    sys.exit(1)

# 3. 下载结果文件
log("Step 3: Downloading result files from backend")
# 修复：本地路径应该也是子目录结构，不是 _brief.html
local_path_results_dir = '/var/www/bioinf/TDMol/result/' + timeVar + '/'
local_path_brief = local_path_results_dir + 'brief.html'
remote_path_brief = '/data/yfang/EDM_web/1111/web_apps/result/' + timeVar + '/brief.html'
remote_path_results = '/data/yfang/EDM_web/1111/web_apps/result/' + timeVar + '/'

# 创建本地结果目录
os.makedirs(local_path_results_dir, exist_ok=True)
log("Created local result directory: {0}".format(local_path_results_dir))

# 下载brief.html
try:
    file_transfer(local_path_brief, remote_path_brief, way="download")
    log("Downloaded brief.html to {0}".format(local_path_brief), "SUCCESS")
except Exception as e:
    log("Failed to download brief.html: {0}".format(e), "ERROR")

# 下载所有result_X.html文件和分子数据
try:
    tran = paramiko.Transport(('202.121.180.146', 2346))
    tran.connect(username="yfang", password='20250912')
    sftp = paramiko.SFTPClient.from_transport(tran)

    # 列出远程目录中的所有文件
    remote_files = sftp.listdir(remote_path_results)
    log("Found {0} files in remote result directory".format(len(remote_files)))

    downloaded_count = 0
    for filename in remote_files:
        if filename.endswith('.html') or filename.endswith('.xyz') or filename.endswith('.sdf') or filename.endswith('.json'):
            remote_file = remote_path_results + filename
            local_file = local_path_results_dir + filename
            sftp.get(remote_file, local_file)
            log("Downloaded: {0}".format(filename))
            downloaded_count += 1

    log("Downloaded {0} files".format(downloaded_count), "SUCCESS")
    tran.close()
except Exception as e:
    log("Error downloading result files: {0}".format(e), "ERROR")

log("Task {0} completed successfully!".format(timeVar), "SUCCESS")
log("=" * 60)
