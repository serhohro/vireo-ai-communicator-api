# [file name]: src/adapters/mcp_server.py
# ============================================================
# VIREO MCP SERVER — Integration with Model Context Protocol
# ============================================================
"""
MCP (Model Context Protocol) server for Vireo.

Allows Claude and other MCP clients to:
- Propose tasks to Vireo agents
- Commit to tasks
- Check agent status
"""

import json
import logging
from typing import Dict, Any, Optional, Callable

from protocol.agent import Agent
from protocol.llm_agent import LLMAgent

logger = logging.getLogger("vireo.adapters.mcp")


class VireoMCPServer:
    """MCP сервер для Vireo агентів."""
    
    def __init__(self, agent_id: str = "mcp-agent", provider: str = "ollama"):
        self.agent = LLMAgent(agent_id, provider=provider)
        self._handlers = {}
    
    def register_handler(self, name: str, handler: Callable):
        """Реєструє обробник для MCP інструменту."""
        self._handlers[name] = handler
        logger.info(f"✅ Registered MCP handler: {name}")
    
    async def call_tool(self, name: str, arguments: dict) -> list:
        """
        Викликає MCP інструмент.
        
        Args:
            name: Назва інструменту
            arguments: Аргументи
            
        Returns:
            list: Результат у форматі MCP
        """
        if name in self._handlers:
            result = self._handlers[name](arguments)
        else:
            # Стандартні інструменти
            if name == "vireo_propose":
                result = await self._propose(arguments)
            elif name == "vireo_commit":
                result = await self._commit(arguments)
            elif name == "vireo_status":
                result = await self._status(arguments)
            else:
                return [{"type": "text", "text": f"Unknown tool: {name}"}]
        
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
    
    async def _propose(self, arguments: dict) -> Dict[str, Any]:
        """Пропонує задачу через Vireo протокол."""
        task = arguments.get("task", "")
        recipient = arguments.get("recipient", "agent-training")
        
        if not task:
            return {"status": "error", "message": "Task is required"}
        
        try:
            result = await self.agent.propose_async(recipient, task)
            return {
                "status": "success",
                "proposal_id": result.get("proposal_id"),
                "conversation_id": result.get("conversation_id"),
                "code": result.get("code", "")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _commit(self, arguments: dict) -> Dict[str, Any]:
        """Приймає та виконує задачу."""
        proposal_id = arguments.get("proposal_id", "")
        
        if not proposal_id:
            return {"status": "error", "message": "proposal_id is required"}
        
        try:
            result = await self.agent.commit_async(proposal_id)
            return {
                "status": "success",
                "result": result
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _status(self, arguments: dict) -> Dict[str, Any]:
        """Перевіряє статус агента."""
        conversation_id = arguments.get("conversation_id", "")
        
        try:
            state = self.agent.state.get(conversation_id)
            return {
                "status": "success",
                "state": state.value if state else "NEW",
                "agent_id": self.agent.id
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_tools(self) -> list:
        """Повертає список доступних MCP інструментів."""
        return [
            {
                "name": "vireo_propose",
                "description": "Propose a task to a Vireo agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Task description"},
                        "recipient": {"type": "string", "description": "Agent ID"}
                    },
                    "required": ["task"]
                }
            },
            {
                "name": "vireo_commit",
                "description": "Commit to and execute a proposed task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "proposal_id": {"type": "string", "description": "Proposal ID"}
                    },
                    "required": ["proposal_id"]
                }
            },
            {
                "name": "vireo_status",
                "description": "Check agent status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {"type": "string", "description": "Conversation ID"}
                    }
                }
            }
        ]


def create_mcp_server(agent_id: str = "mcp-agent", provider: str = "ollama") -> VireoMCPServer:
    """Створює MCP сервер для Vireo."""
    return VireoMCPServer(agent_id, provider)


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    # Створення MCP сервера
    server = create_mcp_server()
    
    # Показати доступні інструменти
    print("🔧 Available MCP Tools:")
    for tool in server.get_tools():
        print(f"   - {tool['name']}: {tool['description']}")