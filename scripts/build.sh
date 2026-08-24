#!/bin/bash
# [file name]: scripts/build.sh
# ============================================================
# VIREO BUILD SCRIPT (Linux/macOS)
# ============================================================

set -e

echo "🌿 Vireo Build Script"
echo "========================================"
echo ""

# Перевірка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Перевірка pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found!"
    exit 1
fi

echo "✅ pip found: $(pip3 --version)"

# Встановлення залежностей
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Перевірка Ollama (опціонально)
echo ""
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found: $(ollama --version)"
    echo "   Run: ollama pull qwen2.5-coder:latest"
else
    echo "⚠️ Ollama not found (optional)"
    echo "   Install from: https://ollama.com"
fi

# Перевірка Docker (опціонально)
echo ""
if command -v docker &> /dev/null; then
    echo "✅ Docker found: $(docker --version)"
else
    echo "⚠️ Docker not found (optional)"
fi

echo ""
echo "========================================"
echo "✅ Build complete!"
echo ""
echo "Next steps:"
echo "  1. Run API server: python3 api_server.py"
echo "  2. Open web interface: http://localhost:5000"
echo "  3. Run tests: ./scripts/test.sh"