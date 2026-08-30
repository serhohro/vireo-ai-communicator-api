# ============================================================
# VIREO API MODELS
# Pydantic-подібні моделі для API
# ============================================================

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentRequest:
    """Запит на реєстрацію агента."""
    id: str
    model: str = "qwen2.5-coder:latest"
    capabilities: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class AgentResponse:
    """Відповідь реєстрації агента."""
    status: str
    agent_id: str
    model: str
    message: str
    agents: List[str]


@dataclass
class ProposeRequest:
    """Запит на пропозицію."""
    sender: str
    recipient: str
    task: str
    code: Optional[str] = None
    contract: Optional[Dict[str, Any]] = None


@dataclass
class ProposeResponse:
    """Відповідь на пропозицію."""
    status: str
    proposal_id: str
    conversation_id: str
    sender: str
    recipient: str
    proposal: Dict[str, Any]


@dataclass
class ExecuteRequest:
    """Запит на виконання."""
    code: str
    agent_id: Optional[str] = None
    conversation_id: Optional[str] = None


@dataclass
class ExecuteResponse:
    """Відповідь виконання."""
    status: str
    output: str
    variables: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Any] = field(default_factory=dict)
    models: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NegotiateRequest:
    """Запит на переговори."""
    sender: str
    recipient: str
    task: str
    max_rounds: int = 3
    timeout_sec: int = 30


@dataclass
class NegotiateResponse:
    """Відповідь переговорів."""
    status: str
    conversation_id: str
    sender: str
    recipient: str
    decision: str
    result: Dict[str, Any]


@dataclass
class ProviderStatus:
    """Статус LLM провайдера."""
    name: str
    available: bool
    model: str
    free: bool
    cost: str


@dataclass
class HealthResponse:
    """Health check відповідь."""
    status: str = "healthy"
    service: str = "Vireo AI Communicator"
    version: str = "1.4.3"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "service": self.service,
            "version": self.version,
            "timestamp": self.timestamp
        }


@dataclass
class ModelDefinition:
    """Визначення нейромережі."""
    name: str
    layers: List[str]
    activations: List[str]
    loss: Optional[str] = None
    optimizer: Optional[str] = None
    parameters: int = 0


@dataclass
class AgentDefinition:
    """Визначення агента."""
    id: str
    model: str
    capabilities: List[str]
    role: Optional[str] = None
    identity: Optional[str] = None


@dataclass
class ContractDefinition:
    """Визначення контракту."""
    name: str
    max_tokens: int = 1000
    max_cost_usd: float = 0.05
    timeout_sec: int = 30
    max_rounds: int = 3
    allowed_actions: List[str] = field(default_factory=list)


@dataclass
class NegotiationDefinition:
    """Визначення переговорів."""
    name: str
    parties: List[Dict[str, str]]
    timeout: int = 10
    max_rounds: int = 5
    on_offer: Optional[str] = None