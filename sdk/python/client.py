# ============================================================
# VIREO PYTHON SDK — CLIENT
# ============================================================
"""
Vireo Python SDK client for agent communication.

Features:
- Agent registration and management
- Message sending and receiving
- Contract creation and validation
- Asynchronous communication
"""

import asyncio
import json
import uuid
import time
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================
# ENUMS
# ============================================================

class Intent(str, Enum):
    PROPOSE = "PROPOSE"
    NEGOTIATE = "NEGOTIATE"
    COMMIT = "COMMIT"
    REJECT = "REJECT"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    INFORM = "INFORM"
    CANCEL = "CANCEL"
    QUERY_CAPABILITIES = "QUERY_CAPABILITIES"
    INFORM_CAPABILITIES = "INFORM_CAPABILITIES"
    ESCALATE = "ESCALATE"


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Contract:
    """Vireo contract with resource limits."""
    max_tokens: Optional[int] = None
    max_cost_usd: Optional[float] = None
    timeout_sec: Optional[int] = None
    verify_timeout_sec: Optional[int] = None
    max_rounds: Optional[int] = None
    max_memory_mb: Optional[int] = None
    allowed_actions: List[str] = field(default_factory=list)
    required_approvals: int = 1
    verify: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_tokens": self.max_tokens,
            "max_cost_usd": self.max_cost_usd,
            "timeout_sec": self.timeout_sec,
            "verify_timeout_sec": self.verify_timeout_sec,
            "max_rounds": self.max_rounds,
            "max_memory_mb": self.max_memory_mb,
            "allowed_actions": self.allowed_actions,
            "required_approvals": self.required_approvals,
            "verify": self.verify
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contract':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AgentInfo:
    """Agent information."""
    id: str
    model: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    role: Optional[str] = None


@dataclass
class Message:
    """Vireo protocol message."""
    protocol: str = "VIREO-A2A"
    version: str = "2.0.2"
    message_id: str = field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    conversation_id: str = field(default_factory=lambda: f"conv-{uuid.uuid4().hex[:8]}")
    sender: str = ""
    recipient: str = ""
    intent: Intent = Intent.PROPOSE
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol": self.protocol,
            "version": self.version,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "intent": self.intent.value if isinstance(self.intent, Intent) else self.intent,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        intent = data.get("intent")
        if isinstance(intent, str):
            try:
                intent = Intent(intent)
            except ValueError:
                pass
        return cls(
            protocol=data.get("protocol", "VIREO-A2A"),
            version=data.get("version", "2.0.2"),
            message_id=data.get("message_id", f"msg-{uuid.uuid4().hex[:8]}"),
            conversation_id=data.get("conversation_id", f"conv-{uuid.uuid4().hex[:8]}"),
            sender=data.get("sender", ""),
            recipient=data.get("recipient", ""),
            intent=intent,
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", time.time()),
            signature=data.get("signature")
        )


# ============================================================
# DEFAULT CONTRACT
# ============================================================

DEFAULT_CONTRACT = Contract(
    max_tokens=1000,
    max_cost_usd=0.05,
    timeout_sec=30,
    verify_timeout_sec=15,
    max_rounds=3,
    max_memory_mb=1024,
    allowed_actions=["train_model", "predict", "evaluate", "generate_code"]
)


def create_contract(**kwargs) -> Contract:
    """Create a contract with default values."""
    default = DEFAULT_CONTRACT
    return Contract(
        max_tokens=kwargs.get("max_tokens", default.max_tokens),
        max_cost_usd=kwargs.get("max_cost_usd", default.max_cost_usd),
        timeout_sec=kwargs.get("timeout_sec", default.timeout_sec),
        verify_timeout_sec=kwargs.get("verify_timeout_sec", default.verify_timeout_sec),
        max_rounds=kwargs.get("max_rounds", default.max_rounds),
        max_memory_mb=kwargs.get("max_memory_mb", default.max_memory_mb),
        allowed_actions=kwargs.get("allowed_actions", default.allowed_actions),
        required_approvals=kwargs.get("required_approvals", default.required_approvals),
        verify=kwargs.get("verify", default.verify)
    )


# ============================================================
# VIREO CLIENT
# ============================================================

class VireoClient:
    """
    Vireo client for agent communication.
    
    Example:
        client = VireoClient("http://localhost:5000")
        agent = client.register_agent("my-agent")
        response = agent.propose("agent-2", "Analyze data")
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self._agents: Dict[str, AgentInfo] = {}
        self._message_handlers: Dict[str, Callable] = {}
    
    async def register_agent(self, agent_id: str, model: str = None) -> AgentInfo:
        """Register an agent."""
        agent_info = AgentInfo(id=agent_id, model=model)
        self._agents[agent_id] = agent_info
        logger.info(f"✅ Agent registered: {agent_id}")
        return agent_info
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information."""
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self._agents.keys())
    
    async def send_message(self, message: Message) -> Message:
        """Send a message to an agent."""
        # In a real implementation, this would make an HTTP request
        # For now, it's a placeholder
        logger.info(f"📤 Sending message: {message.intent} from {message.sender} to {message.recipient}")
        return message
    
    def add_message_handler(self, intent: Intent, handler: Callable):
        """Add a message handler."""
        self._message_handlers[intent] = handler
    
    async def handle_message(self, message: Message):
        """Handle an incoming message."""
        handler = self._message_handlers.get(message.intent)
        if handler:
            return await handler(message)
        logger.warning(f"⚠️ No handler for intent: {message.intent}")
        return None


# ============================================================
# AGENT PROXY
# ============================================================

class AgentProxy:
    """Proxy for interacting with a specific agent."""
    
    def __init__(self, client: VireoClient, agent_id: str):
        self.client = client
        self.agent_id = agent_id
    
    async def propose(self, recipient: str, task: str, contract: Optional[Contract] = None) -> Message:
        """Send a PROPOSE message."""
        message = Message(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.PROPOSE,
            payload={
                "task": task,
                "contract": contract.to_dict() if contract else None
            }
        )
        return await self.client.send_message(message)
    
    async def commit(self, recipient: str, proposal_id: str) -> Message:
        """Send a COMMIT message."""
        message = Message(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.COMMIT,
            payload={"proposal_id": proposal_id}
        )
        return await self.client.send_message(message)
    
    async def reject(self, recipient: str, proposal_id: str, reason: str = "") -> Message:
        """Send a REJECT message."""
        message = Message(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.REJECT,
            payload={"proposal_id": proposal_id, "reason": reason}
        )
        return await self.client.send_message(message)
    
    async def inform(self, recipient: str, proposal_id: str, result: Any) -> Message:
        """Send an INFORM message."""
        message = Message(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.INFORM,
            payload={"proposal_id": proposal_id, "result": result}
        )
        return await self.client.send_message(message)
    
    async def verify(self, recipient: str, proposal_id: str, result: Any, condition: str) -> Message:
        """Send a VERIFY message."""
        message = Message(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.VERIFY,
            payload={
                "proposal_id": proposal_id,
                "result": result,
                "condition": condition
            }
        )
        return await self.client.send_message(message)
    
    async def escalate(self, recipient: str, proposal_id: str, reason: str) -> Message:
        """Send an ESCALATE message."""
        message = Message(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.ESCALATE,
            payload={"proposal_id": proposal_id, "reason": reason}
        )
        return await self.client.send_message(message)
    
    async def negotiate(self, recipient: str, proposal_id: str, counter_offer: Dict[str, Any]) -> Message:
        """Send a NEGOTIATE message."""
        message = Message(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.NEGOTIATE,
            payload={"proposal_id": proposal_id, "counter_offer": counter_offer}
        )
        return await self.client.send_message(message)