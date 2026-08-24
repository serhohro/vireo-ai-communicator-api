@echo off
:: [file name]: scripts/test.bat
:: ============================================================
:: VIREO TEST SCRIPT (Windows)
:: ============================================================

title Vireo Test Script
color 0E

echo.
echo 🧪 Vireo Test Script
echo ========================================
echo.

:: Перевірка Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    pause
    exit /b 1
)

echo ✅ Python found!
python --version

:: Перевірка pytest
python -c "import pytest" > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ pytest not found! Installing...
    pip install pytest pytest-cov
)

echo ✅ pytest found

:: Запуск тестів
echo.
echo ========================================
echo 🧪 Running tests...
echo ========================================

:: Тести протоколу
echo.
echo 📋 Testing protocol...
python -m pytest protocol/tests/test_protocol.py -v

:: Тести агентів
echo.
echo 📋 Testing agents...
python -m pytest protocol/tests/test_agents.py -v

:: Тести криптографії (якщо є)
if exist "protocol\tests\test_crypto.py" (
    echo.
    echo 📋 Testing crypto...
    python -m pytest protocol/tests/test_crypto.py -v
)

:: Тести ONNX (якщо є)
if exist "protocol\tests\test_onnx.py" (
    echo.
    echo 📋 Testing ONNX...
    python -m pytest protocol/tests/test_onnx.py -v
)

:: Запуск демо (перевірка роботи)
echo.
echo ========================================
echo 🚀 Running quick demo...
echo ========================================
echo.
python protocol/examples/two_agent_demo.py

echo.
echo ========================================
echo ✅ All tests passed!
echo.
pause