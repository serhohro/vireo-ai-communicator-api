# [file name]: src/adapters/crewai.py
# ============================================================
# VIREO CREWAI ADAPTER
# ============================================================
"""
CrewAI integration for Vireo.

Allows Vireo agents to work within CrewAI workflows.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from protocol.agent import Agent
from protocol.llm_agent import LLMAgent

logger = logging.getLogger("vireo.adapters.crewai")


class VireoCrewAIAgent:
    """
    Vireo агент для CrewAI.

    Може використовуватися як CrewAI агент для:
    - Пропозиції задач
    - Прийняття рішень
    - Виконання коду
    """
    
    def __init__(self, agent_id: str = "crewai-agent", provider: str = "ollama"):
        self.agent = LLMAgent(agent_id, provider=provider)
        self.agent.register_capability("crewai_integration", "Works with CrewAI")
    
    def propose(self, task: str, recipient: str = "agent-training") -> Dict[str, Any]:
        """Пропонує задачу в рамках CrewAI."""
        return self.agent.propose(recipient, task)
    
    def decide(self, proposal_code: str, reasoning: str) -> Dict[str, Any]:
        """Приймає рішення про commit/reject."""
        return self.agent.ask_for_decision(proposal_code, reasoning)
    
    def execute(self, code: str) -> Dict[str, Any]:
        """Виконує Vireo код."""
        try:
            from vireo_interpreter import execute_vireo_code
            return execute_vireo_code(code)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_status(self, conversation_id: str) -> Dict[str, Any]:
        """Отримує статус конверсації."""
        state = self.agent.state.get(conversation_id)
        return {
            "conversation_id": conversation_id,
            "state": state.value if state else "NEW",
            "agent_id": self.agent.id
        }
    
    def orchestrate_crew(self, tasks: List[str]) -> List[Dict[str, Any]]:
        """
        Оркеструє виконання кількох задач через CrewAI.
        
        Args:
            tasks: Список задач
            
        Returns:
            List[Dict]: Результати кожної задачі
        """
        results = []
        
        for task in tasks:
            logger.info(f"📝 Processing task: {task[:50]}...")
            
            # Крок 1: Пропозиція
            proposal = self.propose(task)
            if proposal.get("status") == "error":
                results.append({"task": task, "status": "error", "message": proposal.get("message")})
                continue
            
            # Крок 2: Рішення
            code = proposal.get("code", "")
            reasoning = proposal.get("reasoning", "")
            decision = self.decide(code, reasoning)
            
            if decision.get("status") == "error":
                results.append({"task": task, "status": "error", "message": decision.get("message")})
                continue
            
            # Крок 3: Виконання (якщо commit)
            dec = decision.get("data", {}).get("decision", "reject")
            if dec == "commit":
                execution = self.execute(code)
                results.append({
                    "task": task,
                    "status": "success",
                    "decision": dec,
                    "execution": execution
                })
            else:
                results.append({
                    "task": task,
                    "status": "rejected",
                    "decision": dec,
                    "reason": decision.get("data", {}).get("reason", "No reason")
                })
        
        return results


def create_crewai_agent(agent_id: str = "crewai-agent", provider: str = "ollama") -> VireoCrewAIAgent:
    """Створює Vireo агента для CrewAI."""
    return VireoCrewAIAgent(agent_id, provider)


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    # Створення агента
    agent = create_crewai_agent()
    
    # Список задач
    tasks = [
        "Create a neural network for MNIST classification",
        "Train the model on MNIST dataset",
        "Evaluate model accuracy"
    ]
    
    # Оркестрація
    results = agent.orchestrate_crew(tasks)
    
    for i, result in enumerate(results):
        print(f"Task {i+1}: {result.get('status')}")