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
        """Повний цикл: COMMITTED → RUNNING → EXECUTE → DONE → INFORM"""
        conversation_id = proposal.conversation_id
        
        # 1. Надсилаємо COMMIT (щоб пропонент знав про COMMITTED)
        self.bus.publish(proposal.sender, Message(
            sender=self.agent_id,
            recipient=proposal.sender,
            intent=Intent.COMMIT,
            payload={"proposal_id": proposal.message_id},
            conversation_id=conversation_id
        ))
        
        # 2. Переходимо в COMMITTED
        self.state.transition(conversation_id, DialogueState.COMMITTED)
        
        # 3. Переходимо в RUNNING
        self.state.transition(conversation_id, DialogueState.RUNNING)
        
        # 4. Виконуємо код
        result = None
        error = None
        
        if self.executor:
            try:
                code = proposal.payload.get("code", "")
                if code:
                    result = self.executor(code)
                else:
                    result = {"status": "error", "message": "No code in proposal"}
            except Exception as e:
                error = str(e)
                result = {"status": "error", "message": error}
        else:
            result = {"status": "success", "message": "Committed (no executor)"}
        
        # 5. Надсилаємо INFORM з результатом
        inform_payload = {
            "proposal_id": proposal.message_id,
            "result": result,
            "error": error
        }
        
        self.bus.publish(proposal.sender, Message(
            sender=self.agent_id,
            recipient=proposal.sender,
            intent=Intent.INFORM,
            payload=inform_payload,
            conversation_id=conversation_id
        ))
        
        # 6. Переходимо в DONE
        self.state.transition(conversation_id, DialogueState.DONE)
    
    def reject(self, proposal: Message, reason: str = "") -> None:
        self.state.transition(proposal.conversation_id, DialogueState.REJECTED)
        self.bus.publish(proposal.sender, Message(
            sender=self.agent_id,
            recipient=proposal.sender,
            intent=Intent.REJECT,
            payload={"proposal_id": proposal.message_id, "reason": reason},
            conversation_id=proposal.conversation_id
        ))
    
    def _handle_message(self, message: Message) -> None:
        print(f"Agent {self.agent_id} received: {message.intent}")
        
        if message.intent == Intent.PROPOSE:
            self._handle_propose(message)
        elif message.intent == Intent.COMMIT:
            self._handle_commit(message)
        elif message.intent == Intent.REJECT:
            self._handle_reject(message)
        elif message.intent == Intent.INFORM:
            self._handle_inform(message)
        elif message.intent == Intent.QUERY_CAPABILITIES:
            self._handle_query_capabilities(message)
        elif message.intent == Intent.INFORM_CAPABILITIES:
            self._handle_inform_capabilities(message)
        elif message.intent == Intent.NEGOTIATE:
            self._handle_negotiate(message)
        elif message.intent == Intent.CANCEL:
            self._handle_cancel(message)
        else:
            print(f"⚠️ Unhandled intent: {message.intent}")
    
    def _handle_propose(self, message: Message) -> None:
        self._pending_proposals[message.message_id] = message
        self.state.transition(message.conversation_id, DialogueState.PROPOSED)
        print(f"📝 Proposal {message.message_id} received from {message.sender}")
    
    def _handle_commit(self, message: Message) -> None:
        proposal_id = message.payload.get("proposal_id")
        if proposal_id and proposal_id in self._pending_proposals:
            self._pending_proposals.pop(proposal_id)
            self.state.transition(message.conversation_id, DialogueState.COMMITTED)
            self.state.transition(message.conversation_id, DialogueState.RUNNING)  # ← ОСТАННІЙ ФІКС
            print(f"✅ Proposal {proposal_id} committed")
        else:
            print(f"⚠️ Unknown proposal: {proposal_id}")
    
    def _handle_reject(self, message: Message) -> None:
        proposal_id = message.payload.get("proposal_id")
        if proposal_id and proposal_id in self._pending_proposals:
            self._pending_proposals.pop(proposal_id)
            self.state.transition(message.conversation_id, DialogueState.REJECTED)
            reason = message.payload.get("reason", "No reason provided")
            print(f"❌ Proposal {proposal_id} rejected: {reason}")
        else:
            print(f"⚠️ Unknown proposal: {proposal_id}")
    
    def _handle_inform(self, message: Message) -> None:
        proposal_id = message.payload.get("proposal_id")
        result = message.payload.get("result")
        error = message.payload.get("error")
        
        if error:
            self.state.transition(message.conversation_id, DialogueState.FAILED)
            print(f"❌ Execution failed for {proposal_id}: {error}")
        else:
            self.state.transition(message.conversation_id, DialogueState.DONE)
            print(f"✅ Execution result for {proposal_id}: {result}")
    
    def _handle_query_capabilities(self, message: Message) -> None:
        capabilities = self.capabilities.list()
        self.bus.publish(message.sender, Message(
            sender=self.agent_id,
            recipient=message.sender,
            intent=Intent.INFORM_CAPABILITIES,
            payload={"capabilities": capabilities}
        ))
        print(f"📋 Capabilities sent to {message.sender}")
    
    def _handle_inform_capabilities(self, message: Message) -> None:
        capabilities = message.payload.get("capabilities", [])
        print(f"📋 Received capabilities from {message.sender}: {capabilities}")
    
    def _handle_negotiate(self, message: Message) -> None:
        print(f"🔄 Negotiation request from {message.sender}: {message.payload}")
    
    def _handle_cancel(self, message: Message) -> None:
        proposal_id = message.payload.get("proposal_id")
        if proposal_id and proposal_id in self._pending_proposals:
            self._pending_proposals.pop(proposal_id)
            self.state.transition(message.conversation_id, DialogueState.CANCELLED)
            print(f"⏹️ Proposal {proposal_id} cancelled")
        else:
            print(f"⚠️ Unknown proposal: {proposal_id}")
    
    def query_capabilities(self, agent_id: str) -> None:
        self.bus.publish(agent_id, Message(
            sender=self.agent_id,
            recipient=agent_id,
            intent=Intent.QUERY_CAPABILITIES,
            payload={}
        ))