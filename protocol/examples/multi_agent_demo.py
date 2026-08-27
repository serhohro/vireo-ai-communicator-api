# [file name]: protocol/examples/multi_agent_demo.py
# ============================================================
# ДЕМО: МУЛЬТИАГЕНТНА СИСТЕМА З РОЛЯМИ
# ============================================================

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from protocol.agents import (
    MasterAgent,
    create_vision_agent,
    create_nlp_agent,
    create_analyst_agent,
    create_researcher_agent,
    create_executor_agent,
    create_guardian_agent,
    create_teacher_agent,
    create_quantum_agent,
)
from protocol.config import LLMConfig


def create_agent_system(provider: str = "ollama"):
    """Створює повну систему агентів."""
    
    print("\n" + "=" * 60)
    print("🤖 CREATING MULTI-AGENT SYSTEM")
    print("=" * 60)
    
    master = MasterAgent("master", provider=provider)
    
    agents = [
        create_vision_agent(provider=provider),
        create_nlp_agent(provider=provider),
        create_analyst_agent(provider=provider),
        create_researcher_agent(provider=provider),
        create_executor_agent(provider=provider),
        create_guardian_agent(provider=provider),
        create_teacher_agent(provider=provider),
        create_quantum_agent(provider=provider),
    ]
    
    master.register_agents(agents)
    
    print(f"\n📋 Total agents: {len(master.agents)}")
    for agent in master.agents.values():
        caps = ", ".join(agent.capabilities[:3])
        if len(agent.capabilities) > 3:
            caps += f" + {len(agent.capabilities) - 3} more"
        print(f"   🎭 {agent.role.name}: {caps}")
    
    return master


def main():
    if not LLMConfig.is_ollama_available():
        print("⚠️ Ollama not available. Please install and run Ollama.")
        return
    
    master = create_agent_system()
    
    task = """
    Create a complete AI solution for medical image analysis:
    1. Analyze medical images (Vision)
    2. Process doctor notes (NLP)
    3. Analyze patient data (Analyst)
    4. Research best approaches (Researcher)
    5. Validate safety (Guardian)
    """
    
    print(f"\n📝 Task: {task.strip()}")
    result = master.orchestrate(task)
    
    print("\n📊 Result:")
    print(f"   Completed: {result['summary']['completed']}/{result['summary']['total_subtasks']}")
    
    return result


if __name__ == "__main__":
    main()