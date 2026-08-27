# [file name]: protocol/examples/negotiation_demo.py
# ============================================================
# NEGOTIATION PROTOCOL DEMO
# Автономні переговори між агентами з контрактами
# ============================================================

import sys
import os
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from protocol.agents import MasterAgent, create_role_agent, create_analyst_agent, create_executor_agent
from protocol.llm_provider import create_llm_provider
from protocol.config import LLMConfig

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("vireo.negotiation_demo")


def print_separator():
    print("\n" + "=" * 60)


def negotiation_demo():
    """Демонстрація повного циклу переговорів між агентами."""
    
    print_separator()
    print("🤝 NEGOTIATION PROTOCOL DEMO")
    print("   Agent-to-Agent negotiation with contracts")
    print("=" * 60)
    
    # Перевірка Ollama
    if not LLMConfig.is_ollama_available():
        print("⚠️ Ollama is not available. Please install and run Ollama.")
        print("   ollama pull qwen2.5-coder:latest")
        return
    
    # Створюємо Master Agent (координатор)
    master = MasterAgent("master", provider="ollama")
    print("✅ Master Agent created")
    
    # Створюємо агентів з ролями
    weather_agent = create_analyst_agent("weather-agent", provider="ollama")
    compute_agent = create_executor_agent("compute-agent", provider="ollama")
    
    print(f"✅ Weather Agent created (Analyst role)")
    print(f"✅ Compute Agent created (Executor role)")
    
    # Реєструємо агентів у Master
    master.register_agents([weather_agent, compute_agent])
    print(f"\n📋 Total agents registered: {len(master.agents)}")
    
    # Задача з переговорами
    task = """
    Negotiate a weather prediction task between agents:
    
    1. Weather Agent (Analyst) proposes a task:
       - Predict weather for 7 days
       - Using historical data
       - With price negotiation
    
    2. Compute Agent (Executor) reviews the proposal:
       - Checks if it can execute
       - Negotiates price if needed
       - Accepts or rejects
    
    3. If accepted:
       - Execute the prediction
       - Return results
    
    4. If rejected:
       - Try alternative approach
       - Or report failure
    """
    
    print(f"\n📝 Task: {task.strip()}")
    print("\n🔄 Agents negotiating...\n")
    
    # Запускаємо оркестрацію
    result = master.orchestrate(task)
    
    print_separator()
    print("📊 NEGOTIATION RESULT")
    print_separator()
    
    print(f"\n   Status: {result.get('status', 'unknown')}")
    print(f"   Conversation ID: {result.get('conversation_id', 'N/A')}")
    print(f"   Total subtasks: {result.get('summary', {}).get('total_subtasks', 0)}")
    print(f"   Completed: {result.get('summary', {}).get('completed', 0)}")
    print(f"   Failed: {result.get('summary', {}).get('failed', 0)}")
    
    print("\n   Subtask results:")
    for i, r in enumerate(result.get('results', [])):
        status = r.get('result', {}).get('status', 'unknown')
        icon = "✅" if status == "success" else "❌"
        agent = r.get('agent', 'N/A')
        role = r.get('role', 'N/A')
        desc = r.get('description', 'N/A')[:60]
        print(f"      {icon} #{i+1}: {desc}...")
        print(f"         Agent: {agent} ({role})")
        print(f"         Status: {status}")
    
    print_separator()
    
    # Показуємо конверсацію
    if result.get('conversation_id'):
        conv_id = result['conversation_id']
        conv = master.get_conversation(conv_id)
        if conv:
            print("\n💬 Conversation log:")
            for entry in conv:
                print(f"   🎭 {entry.get('role', 'Unknown')} ({entry.get('agent', 'Unknown')}):")
                task_desc = entry.get('task', 'N/A')[:80]
                print(f"      Task: {task_desc}...")
                res = entry.get('result', {})
                print(f"      Status: {res.get('status', 'N/A')}")
                if res.get('decision'):
                    print(f"      Decision: {res.get('decision', {}).get('decision', 'N/A')}")
    
    return result


def simple_negotiation_demo():
    """Спрощена демонстрація переговорів без Master Agent."""
    
    print_separator()
    print("🤝 SIMPLE NEGOTIATION DEMO")
    print("   Two agents negotiate directly")
    print("=" * 60)
    
    if not LLMConfig.is_ollama_available():
        print("⚠️ Ollama is not available")
        return
    
    from protocol.llm_agent import create_llm_agent
    
    # Створюємо двох агентів
    proposer = create_llm_agent("agent-proposer", provider="ollama")
    executor = create_llm_agent("agent-executor", provider="ollama")
    
    # Додаємо можливості
    proposer.register_capability("propose_tasks", "Can propose tasks to other agents")
    executor.register_capability("execute_tasks", "Can execute tasks and provide results")
    executor.register_capability("negotiate", "Can negotiate task parameters")
    
    # Задача для переговорів
    task = """
    Weather prediction task:
    - Predict temperature for 7 days
    - Using historical data from last month
    - Budget: 100 tokens
    - Deadline: 5 seconds
    """
    
    print(f"\n📝 Task: {task}")
    print("\n🔄 Proposer generates proposal...\n")
    
    # 1. Пропонент генерує пропозицію
    proposal = proposer.ask_for_proposal(task, executor.capabilities)
    
    if proposal.get("status") == "error":
        print(f"❌ Error: {proposal.get('message')}")
        return
    
    code = proposal.get("data", {}).get("code", "")
    reasoning = proposal.get("data", {}).get("reasoning", "")
    
    print("📄 Proposal generated:")
    print("-" * 40)
    print(code[:300] + "..." if len(code) > 300 else code)
    print("-" * 40)
    print(f"💡 Reasoning: {reasoning[:100]}...")
    
    # 2. Виконавець приймає рішення
    print("\n🤔 Executor decides...")
    decision = executor.ask_for_decision(code, reasoning)
    
    if decision.get("status") == "error":
        print(f"❌ Error: {decision.get('message')}")
        return
    
    dec = decision.get("data", {}).get("decision", "reject")
    reason = decision.get("data", {}).get("reason", "No reason")
    confidence = decision.get("data", {}).get("confidence", 0.5)
    
    print(f"\n✅ Decision: {dec.upper()}")
    print(f"💡 Reason: {reason}")
    print(f"📊 Confidence: {confidence:.2f}")
    
    # 3. Виконання (якщо commit)
    if dec == "commit":
        print("\n⚡ Executing code...")
        try:
            from vireo_interpreter import execute_vireo_code
            result = execute_vireo_code(code)
            print(f"\n📊 Execution Result:")
            print(f"   Status: {result.get('status')}")
            print(f"   Output: {result.get('output', 'No output')[:200]}...")
        except Exception as e:
            print(f"❌ Execution error: {e}")
    else:
        print("\n❌ Proposal rejected")
    
    print_separator()
    print("✅ Negotiation completed!")


def main():
    """Головна функція."""
    
    print("\n" + "=" * 60)
    print("🌿 VIREO NEGOTIATION PROTOCOL DEMO")
    print("   Autonomous agent-to-agent negotiation")
    print("=" * 60)
    
    print("\nSelect demo:")
    print("  1. Full negotiation with Master Agent")
    print("  2. Simple negotiation (two agents)")
    
    choice = input("\n👉 Choice [1-2]: ").strip() or "1"
    
    if choice == "1":
        negotiation_demo()
    elif choice == "2":
        simple_negotiation_demo()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()