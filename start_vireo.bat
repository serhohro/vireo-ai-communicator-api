@echo off
title Vireo AI Communicator - Launcher v1.4.0
color 0A

echo.
echo 🌿 ========================================
echo VIREO AI COMMUNICATOR v1.4.0
echo A Language Designed for AI-to-AI Communication
echo ========================================
echo.
echo 📂 Project: vireo-ai-communicator-3
echo.

:: Перевіряємо Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python found!

:: Перевіряємо, чи є файл api_server.py
if not exist "api_server.py" (
    echo ❌ ERROR: api_server.py not found!
    echo    Please make sure you're in the right folder.
    pause
    exit /b 1
)
echo ✅ API server found!

:: Перевіряємо залежності
echo.
echo 📦 Checking dependencies...
pip show Flask > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Flask not found! Installing...
    pip install Flask flask-cors
)
echo ✅ Dependencies OK!

:: Запускаємо сервер
echo.
echo 🚀 Starting API server...
start "Vireo Server" cmd /k "python api_server.py"

:: Чекаємо запуску
echo ⏳ Waiting for server to start...
timeout /t 5 /nobreak > nul

:: Відкриваємо ВЕБ-ІНТЕРФЕЙС
echo 🌐 Opening web interface...
start http://localhost:5000/web

:: Відкриваємо ДОКУМЕНТАЦІЮ
echo 📚 Opening documentation...
start http://localhost:5000/docs

echo.
echo ========================================
echo ✅ Vireo AI Communicator is running!
echo ========================================
echo.
echo 📡 API Server:    http://localhost:5000
echo 🌐 Web Interface: http://localhost:5000/web
echo 📚 Documentation: http://localhost:5000/docs
echo.
echo 🔴 Close this window to stop the server

pause > nul

:: Закриваємо Python процес
echo.
echo 🛑 Stopping server...
taskkill /F /IM python.exe 2>nul
echo ✅ Server stopped.

echo.
echo Press any key to exit...
pause > nul