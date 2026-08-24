#!/bin/bash
# [file name]: scripts/test.sh
# ============================================================
# VIREO TEST SCRIPT (Linux/macOS)
# ============================================================

set -e

echo "🧪 Vireo Test Script"
echo "========================================"
echo ""

# Перевірка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Перевірка pytest
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "⚠️ pytest not found! Installing..."
    pip3 install pytest pytest-cov
fi

echo "✅ pytest found"

# Запуск тестів
echo ""
echo "========================================"
echo "🧪 Running tests..."
echo "========================================"

# Тести протоколу
echo ""
echo "📋 Testing protocol..."
python3 -m pytest protocol/tests/test_protocol.py -v

# Тести агентів
echo ""
echo "📋 Testing agents..."
python3 -m pytest protocol/tests/test_agents.py -v

# Тести криптографії (якщо є)
if [ -f "protocol/tests/test_crypto.py" ]; then
    echo ""
    echo "📋 Testing crypto..."
    python3 -m pytest protocol/tests/test_crypto.py -v
fi

# Тести ONNX (якщо є)
if [ -f "protocol/tests/test_onnx.py" ]; then
    echo ""
    echo "📋 Testing ONNX..."
    python3 -m pytest protocol/tests/test_onnx.py -v
fi

# Запуск демо (перевірка роботи)
echo ""
echo "========================================"
echo "🚀 Running quick demo..."
echo "========================================"
echo ""
python3 protocol/examples/two_agent_demo.py

echo ""
echo "========================================"
echo "✅ All tests passed!"