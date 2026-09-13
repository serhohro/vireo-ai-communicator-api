# [file name]: protocol/examples/llm_agent_demo.py
# ============================================================
# ДЕМО: LLM АГЕНТИ (Ollama / Claude)
# Автономна AI-to-AI комунікація
# ============================================================

import sys
import os
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from protocol.llm_agent import LLMAgent
from protocol.llm_provider import create_llm_provider
from protocol.config import LLMConfig

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("vireo.llm_demo")


def print_separator():
    print("\n" + "=" * 60)


def run_demo_with_provider(provider_name: str):
    """Запуск демо з вказаним провайдером."""
    
    print_separator()
    print(f"🤖 VIREO LLM AGENT DEMO - {provider_name.upper()}")
    print_separator()
    
    # Перевірка доступності
    if provider_name == "claude" and not LLMConfig.is_claude_available():
        print("❌ Claude API key not set!")
        print("   Set ANTHROPIC_API_KEY in .env file")
        return False
    
    if provider_name == "ollama" and not LLMConfig.is_ollama_available():
        print("❌ Ollama not available!")
        print("   Make sure Ollama is running: ollama serve")
        print("   And model is pulled: ollama pull llama3.1:8b")
        return False
    
    # Створюємо провайдера
    provider = create_llm_provider(provider_name)
    
    vision = LLMAgent(
        id="agent-vision",
        provider=provider,
        model=LLMConfig.OLLAMA_MODEL if provider_name == "ollama" else LLMConfig.CLAUDE_MODEL
    )
    
    training = LLMAgent(
        id="agent-training",
        provider=provider,
        model=LLMConfig.OLLAMA_MODEL if provider_name == "ollama" else LLMConfig.CLAUDE_MODEL
    )
    
    # Реєстрація можливостей
    training.register_capability(
        "train_model",
        description="Executes Vireo DSL code: model definition and training",
        input_schema={"code": "string"},
        output_schema={"status": "string"}
    )
    
    # Задача
    task = (
        "Create a simple neural network for MNIST classification: "
        "two Dense layers with ReLU and Softmax activation."
    )
    
    print(f"\n📝 Task: {task}\n")
    print(f"🤖 Agent: {vision.id} (using {provider_name})")
    print(f"🤖 Agent: {training.id} (using {provider_name})")
    print("\n" + "-" * 40)
    
    # Автономна комунікація
    print("\n🚀 Starting autonomous negotiation...\n")
    
    result = vision.auto_negotiate(training.id, task)
    
    print_separator()
    
    if result.get("status") == "error":
        print(f"❌ Error: {result.get('message')}")
        return False
    
    # Вивід результату
    print("\n📊 RESULT:\n")
    print(f"   Status: {result.get('status')}")
    print(f"   Sender: {result.get('sender')}")
    print(f"   Recipient: {result.get('recipient')}")
    print(f"   Decision: {result.get('decision', {}).get('decision', 'N/A').upper()}")
    print(f"   Reason: {result.get('decision', {}).get('reason', 'N/A')}")
    
    if result.get("execution"):
        print(f"\n   Execution result: {json.dumps(result.get('execution'), ensure_ascii=False, indent=2)[:200]}...")
    
    print("\n" + "-" * 40)
    print("\n✅ Autonomous negotiation completed!")
    print(f"   Human intervention: {'❌ NONE' if result.get('human_intervention') is False else '✅ YES'}")
    print(f"   LLM provider used: {provider_name}")
    
    print_separator()
    
    return True


def main():
    """Головна функція демо."""
    
    print("\n" + "=" * 60)
    print("🟢 VIREO LLM AGENT DEMO")
    print("=" * 60)
    print("\nSelect LLM provider:")
    print("  1. Ollama (local, free)")
    print("  2. Claude API (requires API key)")
    print("  3. Hybrid (simple → Ollama, complex → Claude)")
    print("  4. Test both")
    
    choice = input("\nChoice [1-4]: ").strip() or "1"
    
    if choice == "1":
        success = run_demo_with_provider("ollama")
    elif choice == "2":
        success = run_demo_with_provider("claude")
    elif choice == "3":
        success = run_demo_with_provider("hybrid")
    elif choice == "4":
        print("\n🔍 Testing Ollama...")
        run_demo_with_provider("ollama")
        print("\n🔍 Testing Claude...")
        run_demo_with_provider("claude")
        success = True
    else:
        print("❌ Invalid choice")
        return
    
    if success:
        print("\n🎉 Demo completed successfully!")
    else:
        print("\n❌ Demo failed. See error messages above.")


if __name__ == "__main__":
    main()