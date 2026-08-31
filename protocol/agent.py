import uuid
import time
from typing import Dict, Any, Optional, List
from .message import Message
from .intent import Intent
from .state import DialogueState, DialogueStateMachine
from .capabilities import CapabilityRegistry


class Agent:
    def __init__(self, agent_id: str, bus, model: str = None, executor=None):
        self.agent_id = agent_id
        self.bus = bus
        self.model = model
        self.executor = executor
        self.capabilities = CapabilityRegistry()
        self.state = DialogueStateMachine()  # Використовуємо нову версію
        self._pending_proposals: Dict[str, Message] = {}
        self._execution_history: List[Dict] = []  # Для аудиту
        
        # Запускаємо таймаут-чекер
        self.state.start()
        
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
        """
        Повний цикл: PROPOSED → COMMITTED → RUNNING → VERIFYING → DONE
        """
        conversation_id = proposal.conversation_id
        
        # ============================================================
        # 1. ПЕРЕВІРКА КОНТРАКТУ
        # ============================================================
        contract = proposal.payload.get("contract")
        if contract:
            is_valid, error = contract.validate(proposal.payload)
            if not is_valid:
                self.reject(proposal, reason=f"Contract violation: {error}")
                return
        
        # ============================================================
        # 2. НАДСИЛАЄМО COMMIT
        # ============================================================
        self.bus.publish(proposal.sender, Message(
            sender=self.agent_id,
            recipient=proposal.sender,
            intent=Intent.COMMIT,
            payload={"proposal_id": proposal.message_id},
            conversation_id=conversation_id
        ))
        self.state.transition(conversation_id, DialogueState.COMMITTED)
        
        # ============================================================
        # 3. ПЕРЕХОДИМО В RUNNING І ВИКОНУЄМО КОД
        # ============================================================
        self.state.transition(conversation_id, DialogueState.RUNNING)
        
        result = None
        error = None
        execution_start = time.time()
        
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
        
        execution_time = time.time() - execution_start
        
        # ============================================================
        # 4. 🆕 ПЕРЕХОДИМО В VERIFYING (перевірка результату)
        # ============================================================
        self.state.transition(conversation_id, DialogueState.VERIFYING)
        
        verify_result = None
        verify_error = None
        
        # Перевіряємо контракт на наявність verify умови
        if not error and contract and hasattr(contract, 'verify') and contract.verify:
            try:
                is_verified, verify_msg = self._verify_result(result, contract.verify)
                if not is_verified:
                    verify_error = f"Verification failed: {verify_msg}"
                    
                    # 🆕 Якщо верифікація не пройшла → ESCALATED
                    self.state.transition(conversation_id, DialogueState.ESCALATED)
                    self._cleanup_pending(proposal)
                    
                    self.bus.publish(proposal.sender, Message(
                        sender=self.agent_id,
                        recipient=proposal.sender,
                        intent=Intent.INFORM,
                        payload={
                            "proposal_id": proposal.message_id,
                            "result": result,
                            "error": verify_error,
                            "verified": False,
                            "escalated": True
                        },
                        conversation_id=conversation_id
                    ))
                    
                    # Зберігаємо історію
                    self._execution_history.append({
                        "proposal_id": proposal.message_id,
                        "conversation_id": conversation_id,
                        "status": "escalated",
                        "error": verify_error,
                        "timestamp": time.time()
                    })
                    return
                    
                verify_result = is_verified
                
            except Exception as e:
                verify_error = str(e)
                # 🆕 Помилка верифікації → ESCALATED
                self.state.transition(conversation_id, DialogueState.ESCALATED)
                self._cleanup_pending(proposal)
                
                self.bus.publish(proposal.sender, Message(
                    sender=self.agent_id,
                    recipient=proposal.sender,
                    intent=Intent.INFORM,
                    payload={
                        "proposal_id": proposal.message_id,
                        "result": result,
                        "error": f"Verification error: {verify_error}",
                        "verified": False,
                        "escalated": True
                    },
                    conversation_id=conversation_id
                ))
                
                self._execution_history.append({
                    "proposal_id": proposal.message_id,
                    "conversation_id": conversation_id,
                    "status": "escalated",
                    "error": verify_error,
                    "timestamp": time.time()
                })
                return
        
        # ============================================================
        # 5. 🆕 ВЕРИФІКАЦІЯ ПРОЙШЛА → DONE
        # ============================================================
        if error:
            self.state.transition(conversation_id, DialogueState.FAILED)
        else:
            self.state.transition(conversation_id, DialogueState.DONE)
        
        # ============================================================
        # 6. НАДСИЛАЄМО INFORM
        # ============================================================
        inform_payload = {
            "proposal_id": proposal.message_id,
            "result": result,
            "error": error,
            "execution_time": execution_time,
            "verified": verify_result if verify_result is not None else True
        }
        
        self.bus.publish(proposal.sender, Message(
            sender=self.agent_id,
            recipient=proposal.sender,
            intent=Intent.INFORM,
            payload=inform_payload,
            conversation_id=conversation_id
        ))
        
        # ============================================================
        # 7. ОЧИЩУЄМО ТА ЗБЕРІГАЄМО ІСТОРІЮ
        # ============================================================
        self._cleanup_pending(proposal)
        
        self._execution_history.append({
            "proposal_id": proposal.message_id,
            "conversation_id": conversation_id,
            "sender": proposal.sender,
            "recipient": self.agent_id,
            "task": proposal.payload.get("task", ""),
            "execution_time": execution_time,
            "result": result,
            "error": error,
            "verified": verify_result if verify_result is not None else True,
            "timestamp": time.time()
        })
    
    def _verify_result(self, result: Any, verify_condition: str) -> tuple[bool, str]:
        """
        Перевіряє результат виконання за умовою verify.
        """
        if not result:
            return False, "No result to verify"
        
        if isinstance(result, dict):
            if "accuracy" in result:
                accuracy = result.get("accuracy", 0)
                if accuracy > 0.9:
                    return True, f"Verification passed: accuracy={accuracy}"
                else:
                    return False, f"Verification failed: accuracy={accuracy} < 0.9"
            
            if "status" in result and result["status"] == "success":
                return True, "Verification passed: status=success"
        
        return True, "Verification passed (no specific condition)"
    
    def _cleanup_pending(self, proposal: Message) -> None:
        """Очищує _pending_proposals від завершених пропозицій."""
        proposal_id = proposal.message_id
        if proposal_id in self._pending_proposals:
            self._pending_proposals.pop(proposal_id)
            print(f"🧹 Cleaned up pending proposal: {proposal_id}")
    
    def reject(self, proposal: Message, reason: str = "") -> None:
        self.state.transition(proposal.conversation_id, DialogueState.REJECTED)
        self.bus.publish(proposal.sender, Message(
            sender=self.agent_id,
            recipient=proposal.sender,
            intent=Intent.REJECT,
            payload={"proposal_id": proposal.message_id, "reason": reason},
            conversation_id=proposal.conversation_id
        ))
        self._cleanup_pending(proposal)
    
    # ============================================================
    # ОБРОБКА ПОВІДОМЛЕНЬ
    # ============================================================
    
    def _handle_message(self, message: Message) -> None:
        print(f"Agent {self.agent_id} received: {message.intent}")
        
        handlers = {
            Intent.PROPOSE: self._handle_propose,
            Intent.COMMIT: self._handle_commit,
            Intent.REJECT: self._handle_reject,
            Intent.INFORM: self._handle_inform,
            Intent.QUERY_CAPABILITIES: self._handle_query_capabilities,
            Intent.INFORM_CAPABILITIES: self._handle_inform_capabilities,
            Intent.NEGOTIATE: self._handle_negotiate,
            Intent.CANCEL: self._handle_cancel,
            Intent.VERIFY: self._handle_verify,  # 🆕
            Intent.ESCALATE: self._handle_escalate,  # 🆕
        }
        
        handler = handlers.get(message.intent)
        if handler:
            handler(message)
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
        verified = message.payload.get("verified", True)
        
        if proposal_id and proposal_id in self._pending_proposals:
            self._pending_proposals.pop(proposal_id)
            print(f"🧹 Cleaned up pending proposal: {proposal_id}")
        
        if error:
            self.state.transition(message.conversation_id, DialogueState.FAILED)
            print(f"❌ Execution failed for {proposal_id}: {error}")
        else:
            # 🆕 Якщо result вже верифіковано → DONE
            if verified:
                self.state.transition(message.conversation_id, DialogueState.DONE)
                print(f"✅ Verified result for {proposal_id}: {result}")
            else:
                # Якщо ще не верифіковано → VERIFYING
                self.state.transition(message.conversation_id, DialogueState.VERIFYING)
                print(f"🔍 Verification pending for {proposal_id}")
    
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
    
    # ============================================================
    # 🆕 НОВІ ОБРОБНИКИ ДЛЯ VERIFY ТА ESCALATE
    # ============================================================
    
    def _handle_verify(self, message: Message) -> None:
        """Обробка запиту на верифікацію."""
        proposal_id = message.payload.get("proposal_id")
        result = message.payload.get("result")
        verify_condition = message.payload.get("condition", "")
        
        if not proposal_id:
            print(f"⚠️ Verify request without proposal_id")
            return
        
        print(f"🔍 Verifying proposal {proposal_id}")
        
        # Перевіряємо результат
        is_verified, msg = self._verify_result(result, verify_condition)
        
        if is_verified:
            self.state.transition(message.conversation_id, DialogueState.DONE)
            print(f"✅ Verification passed for {proposal_id}")
        else:
            self.state.transition(message.conversation_id, DialogueState.ESCALATED)
            print(f"⚠️ Verification failed for {proposal_id}: {msg}")
    
    def _handle_escalate(self, message: Message) -> None:
        """Обробка ескалації диспуту."""
        proposal_id = message.payload.get("proposal_id")
        reason = message.payload.get("reason", "No reason provided")
        
        if proposal_id:
            self.state.transition(message.conversation_id, DialogueState.ESCALATED)
            print(f"🚨 Escalated proposal {proposal_id}: {reason}")
            
            # Повідомляємо Guardian (якщо є)
            self.bus.publish("guardian", Message(
                sender=self.agent_id,
                recipient="guardian",
                intent=Intent.INFORM,
                payload={
                    "type": "escalation",
                    "proposal_id": proposal_id,
                    "reason": reason,
                    "conversation_id": message.conversation_id
                }
            ))
    
    # ============================================================
    # ДОПОМІЖНІ МЕТОДИ
    # ============================================================
    
    def query_capabilities(self, agent_id: str) -> None:
        self.bus.publish(agent_id, Message(
            sender=self.agent_id,
            recipient=agent_id,
            intent=Intent.QUERY_CAPABILITIES,
            payload={}
        ))
    
    def get_execution_history(self) -> List[Dict]:
        """Отримати історію виконань для аудиту."""
        return self._execution_history.copy()
    
    def get_pending_proposals(self) -> Dict[str, Message]:
        """Отримати список очікуючих пропозицій."""
        return self._pending_proposals.copy()
    
    def __del__(self):
        """Зупиняємо таймаут-чекер при видаленні."""
        if hasattr(self, 'state'):
            self.state.stop()
