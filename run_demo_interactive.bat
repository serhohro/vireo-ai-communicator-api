@echo off
title Vireo - Interactive Demo
color 0A

echo.
echo ========================================
echo 🌿 VIREO - ІНТЕРАКТИВНЕ ДЕМО
echo ========================================
echo.
echo Ви можете вибрати LLM провайдера:
echo.
echo   🆓 БЕЗКОШТОВНІ:
echo   1. Ollama (локальний, повністю безкоштовно)
echo   2. Gemini (безкоштовний рівень, 60 зап/хв)
echo.
echo   💰 ПЛАТНІ (потрібні API ключі):
echo   3. Claude (Anthropic)
echo   4. OpenAI (GPT-4)
echo   5. Mistral AI
echo.
echo   🔄 АВТОМАТИЧНИЙ:
echo   6. Hybrid (сам обере найкращий)
echo.

:: Перевіряємо .env
if not exist ".env" (
    echo ⚠️ .env файл не знайдено!
    echo    Створіть .env з вашими API ключами
    echo    Приклад у .env.example
    pause
    exit /b 1
)

:: Запускаємо демо
echo 🚀 Запуск інтерактивного демо...
echo.
python protocol/examples/llm_agent_demo.py

pause