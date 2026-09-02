"""Protocol Message Handler for Vireo v2.0.1"""

from typing import Dict, Any, Optional, Callable, List
import logging
from dataclasses import dataclass

from .message import Message, MessageType
from .state import StateMachine, ProtocolState, ProtocolEvent
from ..core.contract.contract import Contract
from ..core.contract.validator import ContractValidator


@dataclass
class HandlerContext:
    """Context for message handling"""
    sender_id: str
    recipient_id: str
    state_machine: StateMachine
    contract_validator: ContractValidator
    handlers: Dict[str, Callable]


class MessageHandler:
    """Handles protocol messages"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._handlers: Dict[MessageType, Callable] = {}
        self._state_machine = StateMachine()
        self._validator = ContractValidator()
        self._logger = logging.getLogger(f"{__name__}.{agent_id}")
        
        # Register default handlers
        self.register_handler(MessageType.DISCOVER, self.handle_discover)
        self.register_handler(MessageType.PROPOSAL, self.handle_proposal)
        self.register_handler(MessageType.ACCEPT, self.handle_accept)
        self.register_handler(MessageType.REJECT, self.handle_reject)
        self.register_handler(MessageType.COMMIT, self.handle_commit)
        self.register_handler(MessageType.EXECUTE, self.handle_execute)
        self.register_handler(MessageType.VERIFY, self.handle_verify)
        self.register_handler(MessageType.ESCALATE, self.handle_escalate)
    
    def register_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Register a handler for a message type"""
        self._handlers[message_type] = handler
        self._logger.debug(f"Registered handler for {message_type.value}")
    
    async def handle(self, message: Message) -> Optional[Message]:
        """Handle an incoming message"""
        if message.type not in self._handlers:
            self._logger.warning(f"No handler for {message.type}")
            return self.create_error_response(message, "E001", "No handler for message type")
        
        try:
            handler = self._handlers[message.type]
            context = HandlerContext(
                sender_id=message.sender_id,
                recipient_id=self.agent_id,
                state_machine=self._state_machine,
                contract_validator=self._validator,
                handlers=self._handlers
            )
            return await handler(message, context)
        except Exception as e:
            self._logger.error(f"Handler error: {e}")
            return self.create_error_response(message, "E500", str(e))
    
    async def handle_discover(self, message: Message, context: HandlerContext) -> Message:
        """Handle DISCOVER message"""
        capabilities_required = message.payload.get("capabilities_required", [])
        
        # Find matching capabilities
        # In production, this would query the capability registry
        matching = [cap for cap in capabilities_required if cap in ["analyze", "report"]]
        
        return Message(
            type=MessageType.DISCOVER_RESPONSE,
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            payload={
                "capabilities": [
                    {"name": cap, "description": f"{cap} capability"}
                    for cap in matching
                ],
                "accepts_contracts": True
            }
        )
    
    async def handle_proposal(self, message: Message, context: HandlerContext) -> Message:
        """Handle PROPOSAL message"""
        contract_data = message.payload.get("contract")
        if not contract_data:
            return self.create_error_response(message, "E003", "Missing contract")
        
        contract = Contract.from_dict(contract_data)
        errors = context.contract_validator.validate(contract)
        
        if errors:
            return Message(
                type=MessageType.REJECT,
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                payload={
                    "proposal_id": message.message_id,
                    "reason": "Contract validation failed",
                    "errors": errors
                }
            )
        
        context.state_machine.transition(ProtocolEvent.ACCEPT)
        
        return Message(
            type=MessageType.ACCEPT,
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            payload={
                "proposal_id": message.message_id,
                "contract_id": contract.contract_id
            }
        )
    
    async def handle_accept(self, message: Message, context: HandlerContext) -> Message:
        """Handle ACCEPT message"""
        context.state_machine.transition(ProtocolEvent.COMMIT)
        
        return Message(
            type=MessageType.COMMIT,
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            payload={
                "contract_id": message.payload.get("contract_id"),
                "signatures": {self.agent_id: "signature_placeholder"}
            }
        )
    
    async def handle_reject(self, message: Message, context: HandlerContext) -> Message:
        """Handle REJECT message"""
        context.state_machine.transition(ProtocolEvent.REJECT)
        return None
    
    async def handle_commit(self, message: Message, context: HandlerContext) -> Message:
        """Handle COMMIT message"""
        context.state_machine.transition(ProtocolEvent.EXECUTE)
        
        return Message(
            type=MessageType.EXECUTE,
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            payload={
                "contract_id": message.payload.get("contract_id"),
                "inputs": {}
            }
        )
    
    async def handle_execute(self, message: Message, context: HandlerContext) -> Message:
        """Handle EXECUTE message"""
        context.state_machine.transition(ProtocolEvent.VERIFY)
        
        return Message(
            type=MessageType.EXECUTION_RESULT,
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            payload={
                "contract_id": message.payload.get("contract_id"),
                "outputs": {"status": "success"},
                "tokens_used": 100
            }
        )
    
    async def handle_verify(self, message: Message, context: HandlerContext) -> Message:
        """Handle VERIFY message"""
        context.state_machine.transition(ProtocolEvent.DONE)
        
        return Message(
            type=MessageType.VERIFICATION_RESULT,
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            payload={
                "contract_id": message.payload.get("contract_id"),
                "verified": True,
                "proof": "verification_proof_placeholder"
            }
        )
    
    async def handle_escalate(self, message: Message, context: HandlerContext) -> Message:
        """Handle ESCALATE message"""
        context.state_machine.transition(ProtocolEvent.ESCALATE)
        return None
    
    def create_error_response(self, original: Message, code: str, message: str) -> Message:
        """Create an error response"""
        return Message(
            type=MessageType.ERROR,
            sender_id=self.agent_id,
            recipient_id=original.sender_id,
            payload={
                "code": code,
                "message": message,
                "original_message_id": original.message_id
            }
        )
    
    def get_state(self) -> Dict[str, Any]:
        """Get current protocol state"""
        return self._state_machine.to_dict()