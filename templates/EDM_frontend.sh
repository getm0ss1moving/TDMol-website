#!/bin/bash

# EDM_frontend.sh - 前端执行脚本 (部署在前端22服务器)
# 这个脚本在前端服务器执行，调用EDM_server.py来SSH到后端
# 参数:
# $1 = email
# $2 = timeVar (任务ID)

# 调用EDM_server.py，它会SSH到后端服务器执行后端的EDM.sh
python3 EDM_server.py "$1" "$2"
