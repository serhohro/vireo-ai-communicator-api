@echo off
title Vireo AI Communicator v1.4.3
color 0A

echo.
echo ========================================
echo  🌿 VIREO AI COMMUNICATOR v1.4.3
echo  The World's First AI-to-AI Communication Language
echo ========================================
echo.

cd /d "C:\Users\Startklar\Desktop\vireo-ai-communicator-3"

echo [1] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found!
    pause
    exit /b
)
echo [OK] Python found

echo [2] Checking server file...
if exist "api_server.py" (
    echo [OK] api_server.py found
    set SERVER_FILE=api_server.py
) else if exist "server.py" (
    echo [OK] server.py found
    set SERVER_FILE=server.py
) else if exist "api/server.py" (
    echo [OK] api/server.py found
    set SERVER_FILE=api/server.py
) else (
    echo [X] No server file found!
    pause
    exit /b
)

echo [3] Installing dependencies...
pip install flask flask-cors python-dotenv cryptography -q 2>nul
echo [OK] Dependencies ready

echo [4] Stopping old server...
taskkill /F /IM python.exe 2>nul
timeout /t 1 >nul
echo [OK] Stopped

echo [5] Starting server...
start "Vireo Server" python %SERVER_FILE%

echo [6] Waiting for server...
timeout /t 5 /nobreak >nul

echo [7] Opening browser...
start http://localhost:5000/web
timeout /t 1 >nul
start http://localhost:5000
timeout /t 1 >nul
start http://localhost:5000/docs
timeout /t 1 >nul
start http://localhost:5000/api/health

echo.
echo ========================================
echo  [OK] SERVER RUNNING!
echo ========================================
echo  🌐 Web: http://localhost:5000/web
echo  📡 API: http://localhost:5000
echo  📚 Docs: http://localhost:5000/docs
echo  🔐 Security: http://localhost:5000/api/health
echo.
echo  🤖 Vireo v1.4.3 — Language-First
echo  Close this window to stop server
echo ========================================
pause >nul

echo Stopping server...
taskkill /F /IM python.exe 2>nul
echo Done.
pause