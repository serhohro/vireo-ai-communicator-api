@echo off
title Vireo Protocol Tests
color 0E

echo.
echo 🧪 ========================================
echo VIREO PROTOCOL TESTS
echo ========================================
echo.
echo 📂 Project: vireo-ai-communicator-3
echo.

if not exist "protocol\tests\test_protocol.py" (
    echo ❌ ERROR: test_protocol.py not found!
    echo    Please make sure the protocol folder exists.
    echo.
    echo    Expected path: protocol\tests\test_protocol.py
    pause
    exit /b 1
)

echo ✅ Protocol tests found!
echo.

:: Перевіряємо, чи встановлено Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found!
    echo    Please install Python 3.8 or higher.
    echo    https://python.org/downloads
    pause
    exit /b 1
)

echo ✅ Python found!
echo.

:: Перевіряємо, чи встановлено pytest
pip show pytest > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ pytest not found! Installing...
    pip install pytest
    echo ✅ pytest installed!
)

echo.
echo 🧪 Running protocol tests...
echo ========================================
echo.
echo Tests include:
echo   ✅ Message roundtrip JSON
echo   ✅ State machine valid path
echo   ✅ State machine invalid transition
echo   ✅ Context store conflict detection
echo   ✅ Context store last write wins
echo   ✅ Message signature valid and tampered
echo   ✅ Wrong secret fails verification
echo.
echo ========================================
echo.

python protocol\tests\test_protocol.py

echo.
echo ========================================
echo ✅ Tests completed!
echo.
echo Press any key to exit...
pause > nul