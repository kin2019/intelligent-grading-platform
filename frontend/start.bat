@echo off
title ZYJC Frontend Server

REM 处理命令行参数
set PORT=8080
set OPEN_BROWSER=1
if not "%1"=="" set PORT=%1
if not "%2"=="" if "%2"=="noopen" set OPEN_BROWSER=0

REM 切换到项目根目录（上一级目录）
cd /d "%~dp0.."

echo =================================
echo    ZYJC Frontend Server Startup
echo =================================
echo Current Directory: %CD%
echo Port: %PORT%
echo.

REM 自动打开浏览器标记
set OPEN_BROWSER=1

REM 检查 Node.js
node -v >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo Error: Node.js is not installed!
    echo Please download Node.js from https://nodejs.org
    echo.
    pause
    exit /b 1
)

REM 检查 http-server
call http-server -v >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing http-server...
    call npm install http-server -g
    if %errorlevel% neq 0 (
        color 0C
        echo Error: Failed to install http-server!
        pause
        exit /b 1
    )
)

REM 检查并强制关闭端口占用
netstat -ano | findstr :%PORT% >nul
if %errorlevel% equ 0 (
    color 0E
    echo Warning: Port %PORT% is already in use!
    echo Attempting to free port %PORT%...
    
    REM 获取占用端口的PID并关闭
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
        echo Killing process %%a...
        taskkill /PID %%a /F >nul 2>&1
    )
    
    timeout /t 1 /nobreak >nul
    echo Port %PORT% has been freed.
    echo.
)
set PORT=8080

echo.
echo Starting server on port %PORT%...
echo Server root: %CD%
echo.
echo Available pages:
echo - http://localhost:%PORT%/frontend/login.html
echo - http://localhost:%PORT%/frontend/student-home.html
echo - http://localhost:%PORT%/frontend/parent-home.html
echo - http://localhost:%PORT%/frontend/profile.html
echo.
echo Press Ctrl+C to stop the server
echo.

REM 启动服务器，使用当前目录作为根目录
http-server . -p %PORT%

REM 如果服务器异常退出，询问是否重启
if %errorlevel% neq 0 (
    color 0E
    echo.
    echo Server stopped unexpectedly!
    echo Would you like to restart? [Y/N]
    choice /c YN /n
    if errorlevel 2 (
        echo.
        echo Goodbye!
        timeout /t 2 /nobreak >nul
        exit /b 1
    ) else (
        cls
        goto start_server
    )
) else (
    color 0B
    echo.
    echo Server stopped normally.
)

echo.
echo Thank you for using ZYJC Frontend Server!
pause
    )
) else (
    color 0B
    echo.
    echo Server stopped normally.
)

echo.
echo Thank you for using ZYJC Frontend Server!
pause
