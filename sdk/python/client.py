# Vireo v3.0.0 — Python Client

from typing import Optional, Dict, Any, Callable
import asyncio

from core.protocol.message import Message, Intent
from core.protocol.state import StateMachine
from core.identity.key_manager import KeyManager


class VireoClient:
    """Vireo client for Python."""
    
    def __init__(
        self,
        agent_id: str,
        private_key: bytes,
        public_key: bytes,
    ):
        self.agent_id = agent_id
        self.key_manager = KeyManager()
        self.state_machine = StateMachine(agent_id=agent_id)
        self._callbacks: Dict[str, Callable] = {}
    
    @classmethod
    def create(cls, agent_id: str) -> "VireoClient":
        from core.crypto.ed25519 import generate_keypair
        private_key, public_key = generate_keypair()
        return cls(agent_id, private_key, public_key)
    
    def propose(self, recipient: str, contract: Dict[str, Any]) -> Message:
        msg = Message.create(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.PROPOSE,
            proposal_id=f"prop_{self.agent_id}_{int(asyncio.get_event_loop().time())}",
            payload=contract,
        )
        msg.sign(self.key_manager.get_active_key().private_key)
        self.state_machine.transition(Intent.PROPOSE, {"counterparty": recipient})
        return msg
    
    def commit(self, recipient: str, proposal_id: str) -> Message:
        msg = Message.create(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.COMMIT,
            proposal_id=proposal_id,
            payload={"status": "committed"},
        )
        msg.sign(self.key_manager.get_active_key().private_key)
        self.state_machine.transition(Intent.COMMIT)
        return msg
    
    def execute(self, recipient: str, proposal_id: str) -> Message:
        msg = Message.create(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.EXECUTE,
            proposal_id=proposal_id,
            payload={"status": "executing"},
        )
        msg.sign(self.key_manager.get_active_key().private_key)
        self.state_machine.transition(Intent.EXECUTE)
        return msg
    
    def verify(self, recipient: str, proposal_id: str, result: Dict[str, Any]) -> Message:
        msg = Message.create(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.VERIFY,
            proposal_id=proposal_id,
            payload=result,
        )
        msg.sign(self.key_manager.get_active_key().private_key)
        self.state_machine.transition(Intent.VERIFY)
        return msg
    
    def done(self, recipient: str, proposal_id: str) -> Message:
        msg = Message.create(
            sender=self.agent_id,
            recipient=recipient,
            intent=Intent.DONE,
            proposal_id=proposal_id,
            payload={"status": "done"},
        )
        msg.sign(self.key_manager.get_active_key().private_key)
        self.state_machine.transition(Intent.DONE)
        return msg
    
    def receive(self, message: Message) -> Optional[Message]:
        if not message.verify(self.key_manager.get_active_key().public_key):
            raise ValueError("Invalid signature")
        
        if message.intent == Intent.PROPOSE:
            self.state_machine.transition(Intent.PROPOSE)
            return self._handle_propose(message)
        elif message.intent == Intent.COMMIT:
            self.state_machine.transition(Intent.COMMIT)
            return self._handle_commit(message)
        elif message.intent == Intent.EXECUTE:
            self.state_machine.transition(Intent.EXECUTE)
            return self._handle_execute(message)
        elif message.intent == Intent.VERIFY:
            self.state_machine.transition(Intent.VERIFY)
            return self._handle_verify(message)
        elif message.intent == Intent.DONE:
            self.state_machine.transition(Intent.DONE)
            return self._handle_done(message)
        
        return None
    
    def _handle_propose(self, message: Message) -> Message:
        return Message.create(
            sender=self.agent_id,
            recipient=message.sender,
            intent=Intent.COMMIT,
            proposal_id=message.proposal_id,
            payload={"status": "accepted"},
        )
    
    def _handle_commit(self, message: Message) -> Message:
        return Message.create(
            sender=self.agent_id,
            recipient=message.sender,
            intent=Intent.EXECUTE,
            proposal_id=message.proposal_id,
            payload={"status": "executing"},
        )
    
    def _handle_execute(self, message: Message) -> Message:
        return Message.create(
            sender=self.agent_id,
            recipient=message.sender,
            intent=Intent.VERIFY,
            proposal_id=message.proposal_id,
            payload={"status": "success", "output": "done"},
        )
    
    def _handle_verify(self, message: Message) -> Message:
        if message.payload.get("status") == "success":
            return Message.create(
                sender=self.agent_id,
                recipient=message.sender,
                intent=Intent.DONE,
                proposal_id=message.proposal_id,
                payload={"status": "done"},
            )
        else:
            return Message.create(
                sender=self.agent_id,
                recipient=message.sender,
                intent=Intent.ESCALATE,
                proposal_id=message.proposal_id,
                payload={"reason": "verification_failed"},
            )
    
    def _handle_done(self, message: Message) -> None:
        pass