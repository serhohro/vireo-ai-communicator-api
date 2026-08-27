@echo off
title Vireo AI Communicator
color 0A

echo ========================================
echo VIREO AI COMMUNICATOR v1.4.2
echo ========================================

cd /d "C:\Users\Startklar\Desktop\vireo-ai-communicator-3"

echo [1] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found!
    pause
    exit /b
)
echo [OK] Python found

echo [2] Checking api_server.py...
if not exist "api_server.py" (
    echo [X] api_server.py not found!
    pause
    exit /b
)
echo [OK] api_server.py found

echo [3] Installing dependencies...
pip install flask flask-cors cryptography -q
echo [OK] Dependencies ready

echo [4] Starting server...
start "Vireo Server" python api_server.py

echo [5] Waiting for server...
timeout /t 5 >nul

echo [6] Opening browser...
start http://localhost:5000/web
start http://localhost:5000

echo.
echo ========================================
echo [OK] SERVER RUNNING!
echo ========================================
echo Web: http://localhost:5000/web
echo API: http://localhost:5000
echo Docs: http://localhost:5000/docs
echo.
echo Close this window to stop server
echo ========================================
pause >nul

taskkill /F /IM python.exe 2>nul
echo Done.
pause