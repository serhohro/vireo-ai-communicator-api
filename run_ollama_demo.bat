@echo off
title Vireo - Ollama Demo
color 0A

echo.
echo ========================================
echo 🌿 VIREO - OLLAMA DEMO
echo ========================================
echo.

:: Перевіряємо .env
if not exist ".env" (
    echo ⚠️ .env file not found! Creating default...
    echo LLM_PROVIDER=ollama > .env
    echo OLLAMA_MODEL=llama3.1:8b >> .env
    echo ✅ .env created
)

:: Перевіряємо Ollama
ollama --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama not found!
    echo    Please install Ollama: https://ollama.com
    pause
    exit /b 1
)

:: Перевіряємо модель
echo 🔍 Checking for model...
ollama list | find "llama3.1:8b" > nul
if %errorlevel% neq 0 (
    echo 📥 Pulling llama3.1:8b...
    ollama pull llama3.1:8b
)

:: Запускаємо демо
echo.
echo 🚀 Starting demo with Ollama...
echo.
python protocol/examples/llm_agent_demo.py

pause