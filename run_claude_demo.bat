@echo off
title Vireo - Claude Demo
color 0A

echo.
echo ========================================
echo 🌿 VIREO - CLAUDE DEMO
echo ========================================
echo.

:: Перевіряємо .env
if not exist ".env" (
    echo ⚠️ .env file not found!
    echo    Please create .env with ANTHROPIC_API_KEY
    pause
    exit /b 1
)

:: Перевіряємо API ключ
find "ANTHROPIC_API_KEY=" .env > nul
if %errorlevel% neq 0 (
    echo ❌ ANTHROPIC_API_KEY not found in .env!
    echo    Add: ANTHROPIC_API_KEY=sk-ant-...
    pause
    exit /b 1
)

:: Запускаємо демо
echo.
echo 🚀 Starting demo with Claude...
echo.
python protocol/examples/llm_agent_demo.py

pause