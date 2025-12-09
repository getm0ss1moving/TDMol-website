@echo off
REM ============================================================
REM 上传测试脚本到服务器
REM ============================================================

echo 正在上传测试脚本到服务器...

REM 使用 scp 上传文件（需要安装 OpenSSH 或 Git Bash）
scp -P 2346 test_queue.sh yfang@202.121.180.146:/data/yfang/EDM_web/1111/web_apps/

echo.
echo 上传完成！
echo.
echo 现在在服务器上执行以下命令：
echo   ssh -p 2346 yfang@202.121.180.146
echo   cd /data/yfang/EDM_web/1111/web_apps/
echo   chmod +x test_queue.sh
echo   ./test_queue.sh
echo.

pause
