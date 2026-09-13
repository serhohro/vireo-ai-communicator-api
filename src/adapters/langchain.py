# [file name]: src/adapters/langchain.py
# ============================================================
# VIREO LANGCHAIN ADAPTER
# ============================================================
"""
LangChain integration for Vireo.

Provides a LangChain tool for interacting with Vireo agents.
"""

import json
from typing import Any, Dict, Optional

from protocol.agent import Agent
from protocol.llm_agent import LLMAgent

try:
    from langchain.tools import BaseTool
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback для без LangChain
    class BaseTool:
        pass
    class BaseModel:
        pass
    def Field(*args, **kwargs):
        return None


class VireoTaskInput(BaseModel):
    """Вхідні параметри для Vireo Agent Tool."""
    task: str = Field(description="Detailed task description for Vireo agent")
    recipient: Optional[str] = Field(
        default="agent-training",
        description="Recipient agent ID"
    )
    max_price_tokens: Optional[int] = Field(
        default=500,
        description="Maximum token price for execution"
    )


class VireoAgentTool(BaseTool):
    """LangChain Tool для взаємодії з Vireo агентами."""
    
    name: str = "vireo_agent_protocol"
    description: str = (
        "Use this tool to delegate tasks to autonomous AI agents through the Vireo protocol. "
        "Agents can generate, negotiate, and execute code independently."
    )
    args_schema: type[BaseModel] = VireoTaskInput
    
    def __init__(self, agent_id: str = "langchain-agent", provider: str = "ollama"):
        super().__init__()
        self.agent = LLMAgent(agent_id, provider=provider)
    
    def _run(self, task: str, recipient: str = "agent-training", max_price_tokens: int = 500) -> str:
        """Виконує інструмент."""
        try:
            result = self.agent.propose(recipient, task, max_price_tokens=max_price_tokens)
            
            if result.get("status") == "success":
                return json.dumps({
                    "status": "success",
                    "proposal_id": result.get("proposal_id"),
                    "code": result.get("code", ""),
                    "message": "Task proposed successfully"
                }, ensure_ascii=False, indent=2)
            else:
                return json.dumps({
                    "status": "error",
                    "message": result.get("message", "Unknown error")
                })
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
    async def _arun(self, task: str, recipient: str = "agent-training", max_price_tokens: int = 500) -> str:
        """Асинхронне виконання інструменту."""
        return self._run(task, recipient, max_price_tokens)


def create_vireo_tool(agent_id: str = "langchain-agent", provider: str = "ollama") -> VireoAgentTool:
    """Створює LangChain Tool для Vireo."""
    return VireoAgentTool(agent_id, provider)


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    # Створення інструменту
    tool = create_vireo_tool()
    
    # Використання
    result = tool._run(
        task="Create a neural network for MNIST classification",
        recipient="agent-training"
    )
    print(result)