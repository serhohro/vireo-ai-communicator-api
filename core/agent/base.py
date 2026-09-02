"""Base Agent implementation for Vireo v2.0.1"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in the Vireo ecosystem"""
    MASTER = "master"
    WORKER = "worker"
    EXECUTOR = "executor"
    GUARDIAN = "guardian"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    TEACHER = "teacher"
    CUSTOM = "custom"


@dataclass
class AgentInfo:
    """Agent metadata"""
    agent_id: str
    name: str
    role: AgentRole
    capabilities: List[str] = field(default_factory=list)
    description: str = ""
    public_key: Optional[bytes] = None


class BaseAgent(ABC):
    """Base class for all Vireo agents"""
    
    def __init__(
        self,
        name: str,
        role: AgentRole = AgentRole.WORKER,
        capabilities: Optional[List[str]] = None,
        description: str = ""
    ):
        self.agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        self.name = name
        self.role = role
        self.capabilities = capabilities or []
        self.description = description
        self._handlers: Dict[str, Callable] = {}
        self._state: Dict[str, Any] = {}
        self._logger = logging.getLogger(f"{__name__}.{name}")
        
        # Initialize key manager
        from ..identity.key_manager import KeyManager
        self.key_manager = KeyManager(self.agent_id)
        
        self._logger.info(f"Agent {self.agent_id} initialized")
    
    @property
    def info(self) -> AgentInfo:
        """Get agent information"""
        return AgentInfo(
            agent_id=self.agent_id,
            name=self.name,
            role=self.role,
            capabilities=self.capabilities,
            description=self.description,
            public_key=self.key_manager.get_public_key()
        )
    
    def register_capability(self, name: str, handler: Callable) -> None:
        """Register a capability handler"""
        if name not in self.capabilities:
            self.capabilities.append(name)
        self._handlers[name] = handler
        self._logger.info(f"Registered capability: {name}")
    
    def has_capability(self, name: str) -> bool:
        """Check if agent has a capability"""
        return name in self.capabilities
    
    def execute(self, action: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a capability"""
        if action not in self._handlers:
            self._logger.error(f"Unknown capability: {action}")
            raise ValueError(f"Unknown capability: {action}")
        
        self._logger.info(f"Executing capability: {action}")
        try:
            result = self._handlers[action](**inputs)
            return {"success": True, "result": result}
        except Exception as e:
            self._logger.error(f"Execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_state(self, key: str) -> Optional[Any]:
        """Get agent state"""
        return self._state.get(key)
    
    def set_state(self, key: str, value: Any) -> None:
        """Set agent state"""
        self._state[key] = value
    
    @abstractmethod
    def start(self) -> None:
        """Start the agent"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the agent"""
        pass
    
    def __repr__(self) -> str:
        return f"Agent({self.agent_id}, {self.name}, role={self.role.value})"