@echo off
chcp 65001 >nul
echo ============================================
echo 数据库代理客户端启动中...
echo ============================================
echo.

if not exist ".env" (
    echo 正在创建配置文件...
    copy ".env.example" ".env"
    echo.
    echo [!] 请编辑 .env 文件配置您的数据库和中继服务
    echo.
    pause
    exit /b 1
)

python client.py

pause
