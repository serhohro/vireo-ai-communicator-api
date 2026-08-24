#!/bin/bash
# [file name]: docker/entrypoint.sh
# ============================================================
# VIREO DOCKER ENTRYPOINT
# ============================================================

set -e

echo "🌿 Vireo Docker Container"
echo "========================================"
echo ""

# Запуск Ollama у фоновому режимі (якщо встановлено)
if command -v ollama &> /dev/null; then
    echo "🚀 Starting Ollama..."
    ollama serve &
    
    # Очікування запуску Ollama
    echo "⏳ Waiting for Ollama..."
    sleep 5
    
    # Перевірка наявності моделі
    if ! ollama list | grep -q "qwen2.5-coder"; then
        echo "📥 Pulling qwen2.5-coder:latest..."
        ollama pull qwen2.5-coder:latest
    fi
    
    echo "✅ Ollama ready!"
fi

# Запуск основної команди
echo "🚀 Starting Vireo..."
exec "$@"