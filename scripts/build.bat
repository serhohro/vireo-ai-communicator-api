@echo off
:: [file name]: scripts/build.bat
:: ============================================================
:: VIREO BUILD SCRIPT (Windows)
:: ============================================================

title Vireo Build Script
color 0A

echo.
echo 🌿 Vireo Build Script
echo ========================================
echo.

:: Перевірка Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found!
python --version

:: Перевірка pip
pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip not found!
    pause
    exit /b 1
)

echo ✅ pip found!

:: Встановлення залежностей
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

:: Перевірка Ollama (опціонально)
echo.
ollama --version > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama found!
    ollama --version
    echo    Run: ollama pull qwen2.5-coder:latest
) else (
    echo ⚠️ Ollama not found (optional)
    echo    Install from: https://ollama.com
)

:: Перевірка Docker (опціонально)
echo.
docker --version > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker found!
    docker --version
) else (
    echo ⚠️ Docker not found (optional)
)

echo.
echo ========================================
echo ✅ Build complete!
echo.
echo Next steps:
echo   1. Run API server: python api_server.py
echo   2. Open web interface: http://localhost:5000
echo   3. Run tests: scripts\test.bat
echo.
pause