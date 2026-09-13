@echo off
title Vireo AI Communicator v3.1
color 0A

echo.
echo ========================================
echo   VIREO v3.1 - Interoperability Release
echo   Experimental protocol for AI-to-AI
echo   communication, negotiation, coordination
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found!
    pause
    exit /b
)
echo [OK] Python found

echo [2] Checking server file...
if exist "api\server.py" (
    echo [OK] api/server.py found
) else (
    echo [X] api/server.py not found!
    pause
    exit /b
)

echo [3] Installing dependencies...
pip install -r requirements.txt -q 2>nul
echo [OK] Dependencies ready

echo [4] Stopping old server (if any)...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul
echo [OK] Stopped

echo [5] Starting server...
start "Vireo v3.1 Server" python -m api.server

echo [6] Waiting for server...
timeout /t 5 /nobreak >nul

echo [7] Opening browser...
start http://localhost:5000/web
timeout /t 1 >nul
start http://localhost:5000/docs

echo.
echo ========================================
echo  [OK] SERVER RUNNING!
echo ========================================
echo  Web:    http://localhost:5000/web
echo  Docs:   http://localhost:5000/docs
echo  API:    http://localhost:5000
echo  Health: http://localhost:5000/api/health
echo.
echo  Vireo v3.1 - Wire: 0x0301 - Crypto: Ed25519 + BLAKE2b-256
echo.
echo  Close this window to stop server
echo ========================================
pause >nul

echo Stopping server...
taskkill /F /IM python.exe 2>nul
echo Done.
pause