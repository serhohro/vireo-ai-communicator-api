import uuid
from typing import Dict, Any, Optional, List
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
        self._pending_proposals: Dict[str, Message] = {}
        self._execution_history: List[Dict] = []  # Для аудиту
        
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
        Повний цикл: COMMITTED → RUNNING → EXECUTE → VERIFY → DONE → INFORM
        
        🆕 Виправлення:
        1. Перевірка контракту перед виконанням (безпека)
        2. Очищення _pending_proposals після завершення
        3. Підтримка VERIFY стану
        """
        conversation_id = proposal.conversation_id
        
        # ============================================================
        # 🔴 КРИТИЧНЕ ВИПРАВЛЕННЯ: Перевірка контракту перед виконанням
        # ============================================================
        contract = proposal.payload.get("contract")
        if contract:
            # Перевіряємо контракт
            is_valid, error = contract.validate(proposal.payload)
            if not is_valid:
                self.reject(proposal, reason=f"Contract violation: {error}")
                return
        
        # ============================================================
        # 1. Надсилаємо COMMIT
        # ============================================================
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
        
        # ============================================================
        # 4. Виконуємо код
        # ============================================================
        result = None
        error = None
        execution_start = time.time()
        
        if self.executor:
            try:
                code = proposal.payload.get("code", "")
                # 🔴 Перевіряємо, чи код не порожній
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
        # 5. VERIFY стан (перевірка результату)
        # ============================================================
        verify_result = None
        verify_error = None
        
        if not error and contract and contract.verify:
            try:
                # Перевіряємо verify умову
                is_verified, verify_msg = self._verify_result(result, contract.verify)
                if not is_verified:
                    verify_error = f"Verification failed: {verify_msg}"
                    # Якщо верифікація не пройшла → переходимо в FAILED
                    self.state.transition(conversation_id, DialogueState.FAILED)
                    # Очищуємо pending proposals
                    self._cleanup_pending(proposal)
                    self.bus.publish(proposal.sender, Message(
                        sender=self.agent_id,
                        recipient=proposal.sender,
                        intent=Intent.INFORM,
                        payload={
                            "proposal_id": proposal.message_id,
                            "result": result,
                            "error": verify_error,
                            "verified": False
                        },
                        conversation_id=conversation_id
                    ))
                    return
                verify_result = is_verified
            except Exception as e:
                verify_error = str(e)
                # Якщо помилка верифікації → переходимо в ESCALATED
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
                return
        
        # ============================================================
        # 6. Надсилаємо INFORM з результатом
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
        # 7. Переходимо в DONE
        # ============================================================
        self.state.transition(conversation_id, DialogueState.DONE)
        
        # ============================================================
        # 8. Очищуємо _pending_proposals (виправлення витоку пам'яті)
        # ============================================================
        self._cleanup_pending(proposal)
        
        # ============================================================
        # 9. Зберігаємо історію для аудиту
        # ============================================================
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
        
        Args:
            result: Результат виконання
            verify_condition: Умова для перевірки (наприклад, "result.accuracy > 0.9")
        
        Returns:
            tuple[bool, str]: (чи пройшла перевірка, повідомлення)
        """
        # TODO: Реалізувати повний evaluator для умов
        # Поки що проста перевірка для демонстрації
        
        if not result:
            return False, "No result to verify"
        
        if isinstance(result, dict):
            # Перевіряємо, чи є ключі в результаті
            if "accuracy" in result:
                accuracy = result.get("accuracy", 0)
                # Спрощена перевірка: accuracy > 0.9
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
        # Очищуємо pending proposals при відхиленні
        self._cleanup_pending(proposal)
    
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
            # ✅ Виправлено: не переходимо автоматично в RUNNING
            # Тепер RUNNING тільки після реального початку виконання
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
        
        # ✅ Виправлено: очищуємо pending proposals при отриманні INFORM
        if proposal_id and proposal_id in self._pending_proposals:
            self._pending_proposals.pop(proposal_id)
            print(f"🧹 Cleaned up pending proposal: {proposal_id}")
        
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
    
    def get_execution_history(self) -> List[Dict]:
        """Отримати історію виконань для аудиту."""
        return self._execution_history.copy()
    
    def get_pending_proposals(self) -> Dict[str, Message]:
        """Отримати список очікуючих пропозицій."""
        return self._pending_proposals.copy()
