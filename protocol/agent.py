import uuid
from typing import Dict, Any, Optional
from .message import Message
from .intent import Intent
from .state import DialogueState, StateMachine
from .capabilities import CapabilityRegistry

class Agent:
    def __init__(self, agent_id: str, bus, model: str = None, executor=None):
        self.agent_id = agent_id
        self.bus = bus
        self.model = model
        self.executor = executor
        self.capabilities = CapabilityRegistry()
        self.state = StateMachine()
        self._pending_proposals = {}
        
        # Підписуємося на повідомлення
        bus.subscribe(agent_id, self._handle_message)
    
    def register_capability(self, name: str, description: str = ""):
        self.capabilities.register(name, description)
    
    def propose(self, recipient: str, payload: Dict[str, Any]) -> Message:
        msg = Message(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.PROPOSE,
            payload=payload
        )
        self._pending_proposals[msg.message_id] = msg
        self.state.transition(msg.conversation_id, DialogueState.PROPOSED)
        self.bus.publish(recipient, msg)
        return msg
    
    def commit(self, proposal: Message) -> None:
        self.state.transition(proposal.conversation_id, DialogueState.COMMITTED)
        self.bus.publish(proposal.sender, Message(
            sender=self.agent_id,
            recipient=proposal.sender,
            intent=Intent.COMMIT,
            payload={"proposal_id": proposal.message_id}
        ))
    
    def reject(self, proposal: Message, reason: str = "") -> None:
        self.state.transition(proposal.conversation_id, DialogueState.REJECTED)
        self.bus.publish(proposal.sender, Message(
            sender=self.agent_id,
            recipient=proposal.sender,
            intent=Intent.REJECT,
            payload={"proposal_id": proposal.message_id, "reason": reason}
        ))
    
    def _handle_message(self, message: Message):
        print(f"Agent {self.agent_id} received: {message.intent}")