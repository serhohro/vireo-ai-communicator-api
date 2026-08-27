# [file name]: protocol/examples/mcp_demo.py
# ============================================================
# MCP SERVER DEMO
# Демонстрація MCP інтеграції
# ============================================================

import sys
import os
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.adapters.mcp_server import create_mcp_server
from protocol.config import LLMConfig

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("vireo.mcp_demo")


def print_separator():
    print("\n" + "=" * 60)


async def mcp_demo():
    """Демонстрація MCP сервера."""
    
    print_separator()
    print("🔌 VIREO MCP SERVER DEMO")
    print("   Model Context Protocol Integration")
    print("=" * 60)
    
    # Перевірка Ollama
    if not LLMConfig.is_ollama_available():
        print("⚠️ Ollama is not available. Please install and run Ollama.")
        return
    
    # Створення MCP сервера
    server = create_mcp_server("mcp-agent", "ollama")
    print("✅ MCP Server created")
    
    # Показати доступні інструменти
    print("\n🔧 Available MCP Tools:")
    for tool in server.get_tools():
        print(f"   - {tool['name']}: {tool['description']}")
    
    print("\n" + "-" * 40)
    
    # Тест: Пропозиція задачі
    print("\n📝 Testing: Propose Task")
    result = await server.call_tool(
        "vireo_propose",
        {"task": "Create a neural network for MNIST classification with 2 layers"}
    )
    print(f"   Result: {result[0]['text'][:200]}...")
    
    # Тест: Статус
    print("\n📊 Testing: Agent Status")
    result = await server.call_tool(
        "vireo_status",
        {"conversation_id": "conv-test"}
    )
    print(f"   Result: {result[0]['text']}")
    
    print_separator()
    print("✅ MCP Demo completed!")


def main():
    import asyncio
    asyncio.run(mcp_demo())


if __name__ == "__main__":
    main()