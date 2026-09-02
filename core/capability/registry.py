"""Capability Registry for Vireo v2.0.1"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class CapabilityInfo:
    """Information about a capability"""
    name: str
    description: str
    inputs: Dict[str, str]  # name -> type
    output: Optional[str] = None
    cost: float = 0.0
    estimated_tokens: int = 0
    timeout_sec: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


class CapabilityRegistry:
    """Registry for capabilities across agents"""
    
    def __init__(self):
        self._capabilities: Dict[str, CapabilityInfo] = {}
        self._agent_capabilities: Dict[str, List[str]] = {}  # agent_id -> capability names
        self._handlers: Dict[str, Dict[str, Callable]] = {}  # agent_id -> capability name -> handler
        self._logger = logging.getLogger(__name__)
    
    def register(
        self, 
        agent_id: str,
        capability: CapabilityInfo,
        handler: Callable
    ) -> None:
        """Register a capability for an agent"""
        self._capabilities[capability.name] = capability
        
        if agent_id not in self._agent_capabilities:
            self._agent_capabilities[agent_id] = []
        self._agent_capabilities[agent_id].append(capability.name)
        
        if agent_id not in self._handlers:
            self._handlers[agent_id] = {}
        self._handlers[agent_id][capability.name] = handler
        
        self._logger.info(f"Registered capability '{capability.name}' for agent {agent_id}")
    
    def unregister(self, agent_id: str, capability_name: str) -> bool:
        """Unregister a capability"""
        if agent_id not in self._agent_capabilities:
            return False
        
        if capability_name not in self._agent_capabilities[agent_id]:
            return False
        
        # Remove from agent capabilities
        self._agent_capabilities[agent_id].remove(capability_name)
        
        # Remove handler
        if agent_id in self._handlers:
            self._handlers[agent_id].pop(capability_name, None)
        
        # Remove from global capabilities if no agent has it
        has_other = any(
            capability_name in caps 
            for caps in self._agent_capabilities.values()
        )
        if not has_other:
            self._capabilities.pop(capability_name, None)
        
        self._logger.info(f"Unregistered capability '{capability_name}' for agent {agent_id}")
        return True
    
    def get_capability(self, name: str) -> Optional[CapabilityInfo]:
        """Get capability info by name"""
        return self._capabilities.get(name)
    
    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get all capabilities for an agent"""
        return self._agent_capabilities.get(agent_id, [])
    
    def get_agents_with_capability(self, name: str) -> List[str]:
        """Get all agents that have a capability"""
        return [
            agent_id for agent_id, caps in self._agent_capabilities.items()
            if name in caps
        ]
    
    def get_handler(self, agent_id: str, capability_name: str) -> Optional[Callable]:
        """Get handler for a capability"""
        if agent_id in self._handlers:
            return self._handlers[agent_id].get(capability_name)
        return None
    
    def execute(self, agent_id: str, capability_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a capability"""
        handler = self.get_handler(agent_id, capability_name)
        if handler is None:
            return {"success": False, "error": f"Handler not found for {capability_name}"}
        
        try:
            result = handler(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            self._logger.error(f"Execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def list_capabilities(self) -> List[CapabilityInfo]:
        """List all registered capabilities"""
        return list(self._capabilities.values())
    
    def search_capabilities(self, query: str) -> List[CapabilityInfo]:
        """Search capabilities by name or description"""
        query_lower = query.lower()
        return [
            cap for cap in self._capabilities.values()
            if query_lower in cap.name.lower() or 
               query_lower in cap.description.lower()
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Export registry to dict"""
        return {
            "capabilities": {
                name: {
                    "name": info.name,
                    "description": info.description,
                    "inputs": info.inputs,
                    "output": info.output,
                    "cost": info.cost,
                    "estimated_tokens": info.estimated_tokens,
                    "agents": self.get_agents_with_capability(name)
                }
                for name, info in self._capabilities.items()
            }
        }
    
    def to_json(self) -> str:
        """Export registry to JSON"""
        return json.dumps(self.to_dict(), indent=2)