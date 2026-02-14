@echo off
echo 设置Python环境和执行自动清理任务
echo.

REM 激活虚拟环境（如果有）
call venv\Scripts\activate.bat

REM 执行清理任务
python auto_cleanup.py

REM 暂停查看结果
pause