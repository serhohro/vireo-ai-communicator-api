"""Agent Registry for Vireo v2.0.1"""

from typing import Dict, List, Optional, Any
import logging
import json

from .base import BaseAgent, AgentInfo

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing agents"""
    
    _instance: Optional['AgentRegistry'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._agents: Dict[str, BaseAgent] = {}
        self._capabilities_index: Dict[str, List[str]] = {}
        self._initialized = True
        logger.info("AgentRegistry initialized")
    
    def register(self, agent: BaseAgent) -> None:
        """Register an agent"""
        self._agents[agent.agent_id] = agent
        
        # Index capabilities
        for capability in agent.capabilities:
            if capability not in self._capabilities_index:
                self._capabilities_index[capability] = []
            self._capabilities_index[capability].append(agent.agent_id)
        
        logger.info(f"Registered agent: {agent.agent_id}")
    
    def unregister(self, agent_id: str) -> None:
        """Unregister an agent"""
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            for capability in agent.capabilities:
                if capability in self._capabilities_index:
                    self._capabilities_index[capability].remove(agent_id)
            del self._agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self._agents.get(agent_id)
    
    def get_agents(self) -> List[BaseAgent]:
        """Get all agents"""
        return list(self._agents.values())
    
    def get_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """Get agents with a specific capability"""
        agent_ids = self._capabilities_index.get(capability, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    def get_agents_by_role(self, role: str) -> List[BaseAgent]:
        """Get agents with a specific role"""
        return [a for a in self._agents.values() if a.role.value == role]
    
    def find_agent(self, **criteria) -> Optional[BaseAgent]:
        """Find an agent matching criteria"""
        for agent in self._agents.values():
            matches = True
            for key, value in criteria.items():
                if key == "capability":
                    if value not in agent.capabilities:
                        matches = False
                        break
                elif key == "role":
                    if agent.role.value != value:
                        matches = False
                        break
                elif hasattr(agent, key):
                    if getattr(agent, key) != value:
                        matches = False
                        break
            if matches:
                return agent
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Export registry to dict"""
        return {
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "role": agent.role.value,
                    "capabilities": agent.capabilities
                }
                for agent in self._agents.values()
            ]
        }
    
    def to_json(self) -> str:
        """Export registry to JSON"""
        return json.dumps(self.to_dict(), indent=2)