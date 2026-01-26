@echo off
echo ========================================
echo        MyWeb 项目启动脚本
echo ========================================
echo.

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ❌ 虚拟环境不存在，正在创建...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境创建完成
)

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

REM 检查MongoDB连接
echo.
echo 检查MongoDB连接...
python -c "import pymongo; client=pymongo.MongoClient('mongodb://127.0.0.1:27017/', serverSelectionTimeoutMS=3000); client.admin.command('ping'); print('✅ MongoDB连接成功'); client.close()" 2>nul
if errorlevel 1 (
    echo ❌ MongoDB连接失败
    echo 请确保MongoDB服务已启动
    echo 运行命令: net start MongoDB
    echo.
    pause
    exit /b 1
)

REM 创建必要目录
if not exist "static\uploads" (
    mkdir static\uploads
    echo ✅ 创建上传目录
)

REM 启动应用
echo.
echo 启动Flask应用...
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止应用
echo.
python app.py

pause