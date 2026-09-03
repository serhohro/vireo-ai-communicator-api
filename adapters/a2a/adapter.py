# ============================================================
# VIREO A2A ADAPTER
# ============================================================
"""
A2A (Agent-to-Agent) protocol adapter for Vireo.

Maps Vireo protocol to A2A and vice versa.
"""

import json
import uuid
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class A2AAgent:
    """A2A agent representation."""
    id: str
    name: str
    capabilities: List[str] = field(default_factory=list)
    endpoint: Optional[str] = None


@dataclass
class A2AMessage:
    """A2A message format."""
    type: str  # 'propose', 'commit', 'reject', 'inform'
    sender: str
    recipient: str
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: f"a2a-{uuid.uuid4().hex[:8]}")


class A2AAdapter:
    """
    Adapter between Vireo and A2A protocols.
    
    Maps:
    - Vireo PROPOSE → A2A propose
    - Vireo COMMIT → A2A commit
    - Vireo REJECT → A2A reject
    - Vireo INFORM → A2A inform
    - Vireo capabilities → A2A Agent Card
    """
    
    def __init__(self):
        self._agents: Dict[str, A2AAgent] = {}
        self._messages: Dict[str, A2AMessage] = {}
    
    def register_agent(self, agent_id: str, name: str, 
                       capabilities: List[str] = None,
                       endpoint: Optional[str] = None) -> A2AAgent:
        """Register an agent with A2A."""
        agent = A2AAgent(
            id=agent_id,
            name=name,
            capabilities=capabilities or [],
            endpoint=endpoint
        )
        self._agents[agent_id] = agent
        logger.info(f"✅ A2A agent registered: {agent_id}")
        return agent
    
    def get_agent_card(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get A2A Agent Card for an agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            return None
        
        return {
            "id": agent.id,
            "name": agent.name,
            "capabilities": agent.capabilities,
            "endpoint": agent.endpoint,
            "protocol": "A2A",
            "version": "1.0"
        }
    
    def vireo_to_a2a(self, vireo_message: Dict[str, Any]) -> A2AMessage:
        """Convert Vireo message to A2A message."""
        intent = vireo_message.get("intent", "PROPOSE")
        
        type_map = {
            "PROPOSE": "propose",
            "COMMIT": "commit",
            "REJECT": "reject",
            "INFORM": "inform",
            "NEGOTIATE": "negotiate",
            "CANCEL": "cancel",
            "VERIFY": "verify",
            "ESCALATE": "escalate"
        }
        
        message = A2AMessage(
            type=type_map.get(intent, "propose"),
            sender=vireo_message.get("sender", {}).get("id", ""),
            recipient=vireo_message.get("recipient", {}).get("id", ""),
            payload=vireo_message.get("payload", {})
        )
        
        self._messages[message.message_id] = message
        return message
    
    def a2a_to_vireo(self, a2a_message: A2AMessage) -> Dict[str, Any]:
        """Convert A2A message to Vireo message."""
        intent_map = {
            "propose": "PROPOSE",
            "commit": "COMMIT",
            "reject": "REJECT",
            "inform": "INFORM",
            "negotiate": "NEGOTIATE",
            "cancel": "CANCEL",
            "verify": "VERIFY",
            "escalate": "ESCALATE"
        }
        
        return {
            "protocol": "VIREO-A2A",
            "version": "2.0.2",
            "message_id": a2a_message.message_id,
            "conversation_id": f"conv-{uuid.uuid4().hex[:8]}",
            "sender": {"id": a2a_message.sender},
            "recipient": {"id": a2a_message.recipient},
            "intent": intent_map.get(a2a_message.type, "PROPOSE"),
            "payload": a2a_message.payload,
            "timestamp": 0
        }
    
    def discover_agents(self) -> List[Dict[str, Any]]:
        """Discover all registered A2A agents."""
        return [self.get_agent_card(agent_id) for agent_id in self._agents]
    
    def send_message(self, message: A2AMessage) -> bool:
        """Send an A2A message."""
        logger.info(f"📤 A2A message sent: {message.type} from {message.sender} to {message.recipient}")
        return True
    
    def receive_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Receive and process an A2A message."""
        logger.info(f"📥 A2A message received: {message.type} from {message.sender}")
        return self.a2a_to_vireo(message)