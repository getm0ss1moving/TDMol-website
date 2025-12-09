#!/usr/bin/env python3
"""
diagnose_transfer.py - 诊断文件传输问题
"""

import paramiko
import os
import sys

print("="*60)
print("文件传输诊断工具")
print("="*60)

# 从EDM_server.py读取的配置
configs = {
    "file_transfer": {
        "host": "202.121.180.146",
        "port": 2346,
        "username": "yfang",
        "password": "20250912",
        "upload_dir": "/data/yfang/EDM_web/1111/web_apps/upload/"
    },
    "exec_command": {
        "host": "202.121.180.146",
        "port": 2346,
        "username": "yfang",
        "password": "20250912",
        "upload_dir": "/data/yfang/EDM_web/1111/web_apps/upload/"
    },
    "verification": {
        "host": "202.121.180.146",
        "port": 2346,
        "username": "yfang",
        "password": "20250912",
        "upload_dir": "/data/yfang/EDM_web/1111/web_apps/upload/"
    }
}

print("\n✓ 配置已统一到同一服务器\n")
print("当前配置：")
print(f"  后端服务器:   {configs['file_transfer']['host']}:{configs['file_transfer']['port']}")
print(f"  工作目录:     /data/yfang/EDM_web/1111/web_apps/")
print(f"  用户名:       {configs['file_transfer']['username']}")

print("\n" + "="*60)
print("开始测试各服务器连接和目录...")
print("="*60)

def test_server(name, config):
    print(f"\n测试 {name}:")
    print(f"  服务器: {config['host']}:{config['port']}")
    print(f"  用户名: {config['username']}")
    print(f"  密码: {'*' * len(config['password'])}")

    try:
        # 测试SSH连接
        transport = paramiko.Transport((config['host'], config['port']))
        transport.connect(username=config['username'], password=config['password'])

        print(f"  ✓ SSH连接成功")

        # 测试SFTP
        sftp = paramiko.SFTPClient.from_transport(transport)

        # 检查upload目录
        upload_dir = config['upload_dir']
        try:
            files = sftp.listdir(upload_dir)
            print(f"  ✓ upload目录存在: {upload_dir}")
            print(f"  ✓ 目录中有 {len(files)} 个文件")

            # 显示最近的文件
            if files:
                print(f"  最近的文件:")
                for f in files[-5:]:  # 显示最后5个
                    stat = sftp.stat(upload_dir + f)
                    print(f"    - {f} ({stat.st_size} bytes)")
        except Exception as e:
            print(f"  ✗ upload目录不存在或无法访问: {e}")

        sftp.close()
        transport.close()
        return True

    except Exception as e:
        print(f"  ✗ 连接失败: {e}")
        return False

# 测试所有服务器
results = {}
for name, config in configs.items():
    results[name] = test_server(name, config)

# 总结
print("\n" + "="*60)
print("诊断总结")
print("="*60)

if results['file_transfer'] and not results['exec_command']:
    print("\n✓ 文件传输服务器可以连接")
    print("✗ 命令执行服务器无法连接")
    print("\n建议: 检查命令执行服务器的连接参数")

elif not results['file_transfer'] and results['exec_command']:
    print("\n✗ 文件传输服务器无法连接")
    print("✓ 命令执行服务器可以连接")
    print("\n建议: 检查文件传输服务器的连接参数")

elif results['file_transfer'] and results['exec_command']:
    print("\n✓ 服务器地址一致")
    print("✓ 所有连接正常")
    print(f"✓ 统一使用: {configs['file_transfer']['host']}:{configs['file_transfer']['port']}")
    print("\n如果仍然看不到文件，可能的原因：")
    print("  1. 文件上传路径与命令执行路径不同")
    print("  2. 权限问题")
    print("  3. 文件名不匹配")
    print("\n建议运行：")
    print(f"  ssh -p {configs['file_transfer']['port']} {configs['file_transfer']['username']}@{configs['file_transfer']['host']}")
    print(f"  ls -lh /data/yfang/EDM_web/1111/web_apps/upload/")
else:
    print("\n✗ 所有服务器都无法连接")
    print("\n建议: 检查网络连接和防火墙设置")

print("\n" + "="*60)
