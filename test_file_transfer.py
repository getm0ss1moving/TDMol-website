#!/usr/bin/env python3
"""
test_file_transfer.py - 文件传输检测工具

功能：
1. 测试上传文件到后端服务器
2. 验证文件是否存在
3. 验证文件内容是否正确
4. 清理测试文件

使用方法：
    python3 test_file_transfer.py
"""

import os
import sys
import time
import paramiko
import datetime

# ============================================================
# 配置参数 (请根据实际情况修改)
# ============================================================

# 后端服务器配置
BACKEND_IP = '202.121.180.146'         # 后端服务器IP
BACKEND_PORT = 2346                    # 后端SSH端口
SSH_USERNAME = 'yfang'                 # SSH用户名
SSH_PASSWORD = '20250912'              # SSH密码

# 路径配置
FRONTEND_UPLOAD_DIR = '/var/www/bioinf/TDMol/upload/'
BACKEND_UPLOAD_DIR = '/data/yfang/EDM_web/1111/web_apps/upload/'

# 测试文件名
TEST_FILENAME = f"test_transfer_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
TEST_CONTENT = "This is a test file for EDM file transfer verification.\n测试文件用于验证文件传输功能。\n"

# ============================================================
# 颜色输出
# ============================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

# ============================================================
# 文件传输测试
# ============================================================

def create_test_file():
    """创建测试文件"""
    print_info("步骤1: 创建测试文件")

    local_path = os.path.join(FRONTEND_UPLOAD_DIR, TEST_FILENAME)

    try:
        # 创建目录（如果不存在）
        os.makedirs(FRONTEND_UPLOAD_DIR, exist_ok=True)

        # 写入测试文件
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(TEST_CONTENT)

        # 验证文件
        if os.path.exists(local_path):
            file_size = os.path.getsize(local_path)
            print_success(f"测试文件已创建: {local_path}")
            print_info(f"  文件大小: {file_size} bytes")
            return local_path, file_size
        else:
            print_error("测试文件创建失败")
            return None, 0

    except Exception as e:
        print_error(f"创建测试文件时出错: {e}")
        return None, 0

def upload_file_to_backend(local_path):
    """上传文件到后端服务器"""
    print_info("步骤2: 上传文件到后端服务器")

    remote_path = os.path.join(BACKEND_UPLOAD_DIR, TEST_FILENAME)

    try:
        # 建立SSH连接
        print_info(f"  连接到后端服务器: {BACKEND_IP}:{BACKEND_PORT}")
        transport = paramiko.Transport((BACKEND_IP, BACKEND_PORT))
        transport.connect(username=SSH_USERNAME, password=SSH_PASSWORD)

        # 创建SFTP客户端
        sftp = paramiko.SFTPClient.from_transport(transport)

        # 确保远程目录存在
        try:
            sftp.stat(BACKEND_UPLOAD_DIR)
        except FileNotFoundError:
            print_warning(f"  远程目录不存在，尝试创建: {BACKEND_UPLOAD_DIR}")
            sftp.mkdir(BACKEND_UPLOAD_DIR)

        # 上传文件
        print_info(f"  上传文件: {local_path} -> {remote_path}")
        sftp.put(local_path, remote_path)

        print_success("文件上传成功")

        sftp.close()
        transport.close()

        return remote_path

    except Exception as e:
        print_error(f"上传文件时出错: {e}")
        return None

def verify_file_on_backend(remote_path, expected_size):
    """验证文件在后端服务器上是否存在且正确"""
    print_info("步骤3: 验证后端文件")

    try:
        # 建立SSH连接
        transport = paramiko.Transport((BACKEND_IP, BACKEND_PORT))
        transport.connect(username=SSH_USERNAME, password=SSH_PASSWORD)

        # 创建SFTP客户端
        sftp = paramiko.SFTPClient.from_transport(transport)

        # 检查文件是否存在
        try:
            file_stat = sftp.stat(remote_path)
            remote_size = file_stat.st_size

            print_success(f"文件存在于后端: {remote_path}")
            print_info(f"  远程文件大小: {remote_size} bytes")
            print_info(f"  本地文件大小: {expected_size} bytes")

            # 验证文件大小
            if remote_size == expected_size:
                print_success("文件大小匹配 ✓")
            else:
                print_error(f"文件大小不匹配！预期 {expected_size}，实际 {remote_size}")
                sftp.close()
                transport.close()
                return False

            # 读取远程文件内容
            with sftp.open(remote_path, 'r') as f:
                remote_content = f.read().decode('utf-8')

            # 验证内容
            if remote_content == TEST_CONTENT:
                print_success("文件内容匹配 ✓")
            else:
                print_error("文件内容不匹配！")
                print_info(f"  预期内容: {TEST_CONTENT[:50]}...")
                print_info(f"  实际内容: {remote_content[:50]}...")
                sftp.close()
                transport.close()
                return False

            sftp.close()
            transport.close()
            return True

        except FileNotFoundError:
            print_error(f"文件不存在于后端: {remote_path}")
            sftp.close()
            transport.close()
            return False

    except Exception as e:
        print_error(f"验证文件时出错: {e}")
        return False

def cleanup_test_files(local_path, remote_path):
    """清理测试文件"""
    print_info("步骤4: 清理测试文件")

    # 清理本地文件
    try:
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
            print_success(f"本地测试文件已删除: {local_path}")
    except Exception as e:
        print_warning(f"删除本地文件失败: {e}")

    # 清理远程文件
    try:
        transport = paramiko.Transport((BACKEND_IP, BACKEND_PORT))
        transport.connect(username=SSH_USERNAME, password=SSH_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        if remote_path:
            try:
                sftp.remove(remote_path)
                print_success(f"远程测试文件已删除: {remote_path}")
            except FileNotFoundError:
                print_warning("远程文件不存在，无需删除")

        sftp.close()
        transport.close()
    except Exception as e:
        print_warning(f"删除远程文件失败: {e}")

# ============================================================
# 主测试流程
# ============================================================

def test_ssh_connection():
    """测试SSH连接"""
    print_info("预检查: 测试SSH连接")

    try:
        transport = paramiko.Transport((BACKEND_IP, BACKEND_PORT))
        transport.connect(username=SSH_USERNAME, password=SSH_PASSWORD)

        # 执行简单命令测试
        ssh = paramiko.SSHClient()
        ssh._transport = transport
        stdin, stdout, stderr = ssh.exec_command('echo "SSH OK"')
        output = stdout.read().decode('utf-8').strip()

        if output == "SSH OK":
            print_success(f"SSH连接正常: {BACKEND_IP}:{BACKEND_PORT}")
            transport.close()
            return True
        else:
            print_error("SSH连接异常")
            transport.close()
            return False

    except Exception as e:
        print_error(f"SSH连接失败: {e}")
        return False

def main():
    print_header("EDM 文件传输测试工具")

    print_info(f"测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"后端服务器: {BACKEND_IP}:{BACKEND_PORT}")
    print_info(f"测试文件: {TEST_FILENAME}\n")

    # 预检查
    if not test_ssh_connection():
        print_error("\n测试失败：无法连接到后端服务器")
        print_info("请检查以下配置：")
        print_info(f"  - BACKEND_IP: {BACKEND_IP}")
        print_info(f"  - BACKEND_PORT: {BACKEND_PORT}")
        print_info(f"  - SSH_USERNAME: {SSH_USERNAME}")
        print_info(f"  - SSH_PASSWORD: {'*' * len(SSH_PASSWORD)}")
        sys.exit(1)

    print()

    # 步骤1: 创建测试文件
    local_path, file_size = create_test_file()
    if not local_path:
        print_error("\n测试失败：无法创建测试文件")
        sys.exit(1)

    print()

    # 步骤2: 上传文件
    remote_path = upload_file_to_backend(local_path)
    if not remote_path:
        print_error("\n测试失败：无法上传文件到后端")
        cleanup_test_files(local_path, None)
        sys.exit(1)

    print()

    # 等待一下确保文件系统同步
    time.sleep(1)

    # 步骤3: 验证文件
    verification_passed = verify_file_on_backend(remote_path, file_size)

    print()

    # 步骤4: 清理
    cleanup_test_files(local_path, remote_path)

    # 最终结果
    print_header("测试结果")

    if verification_passed:
        print_success("✓ 所有测试通过！文件传输功能正常。\n")
        sys.exit(0)
    else:
        print_error("✗ 测试失败！文件传输存在问题。\n")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
