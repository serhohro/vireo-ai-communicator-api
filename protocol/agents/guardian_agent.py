"""
GUARDIAN AGENT — агент-охоронець для вирішення ескалацій
"""

import time
import logging
from typing import Dict, Any, Optional
from ..agent import Agent
from ..message import Message
from ..intent import Intent

logger = logging.getLogger(__name__)


class GuardianAgent(Agent):
    """Агент-охоронець для вирішення ескалацій."""
    
    def __init__(self, agent_id: str = "guardian", **kwargs):
        super().__init__(agent_id, **kwargs)
        self._escalated_tasks: Dict[str, Dict] = {}
        self._resolved_tasks: Dict[str, Dict] = {}
    
    def _handle_message(self, message: Message) -> None:
        """Обробка вхідних повідомлень."""
        if message.intent == Intent.INFORM and message.payload.get("type") == "escalation":
            self._handle_escalation(message)
        else:
            super()._handle_message(message)
    
    def _handle_escalation(self, message: Message) -> None:
        """Обробка ескалації."""
        conversation_id = message.conversation_id
        self._escalated_tasks[conversation_id] = {
            "message": message,
            "sender": message.sender,
            "recipient": message.recipient,
            "reason": message.payload.get("reason", "No reason"),
            "proposal_id": message.payload.get("proposal_id"),
            "status": "pending",
            "timestamp": time.time()
        }
        logger.info(f"🛡️ [{self.id}] Escalation received: {conversation_id}")
    
    def resolve_escalation(self, conversation_id: str, 
                           decision: str, 
                           reason: str = "") -> None:
        """
        Вирішує ескалований діалог.
        
        Args:
            conversation_id: ID діалогу
            decision: "accept" | "reject" | "delegate"
            reason: Причина рішення
        """
        if conversation_id not in self._escalated_tasks:
            raise ValueError(f"Unknown escalation: {conversation_id}")
        
        task = self._escalated_tasks[conversation_id]
        task["decision"] = decision
        task["reason"] = reason
        task["resolved_at"] = time.time()
        task["status"] = "resolved"
        
        # Повідомляємо обох агентів
        message = task["message"]
        
        # Повідомлення відправнику
        self.bus.publish(message.sender, Message(
            sender=self.id,
            recipient=message.sender,
            intent=Intent.INFORM,
            payload={
                "type": "escalation_resolution",
                "conversation_id": conversation_id,
                "decision": decision,
                "reason": reason,
                "proposal_id": task.get("proposal_id")
            }
        ))
        
        # Повідомлення отримувачу
        self.bus.publish(message.recipient, Message(
            sender=self.id,
            recipient=message.recipient,
            intent=Intent.INFORM,
            payload={
                "type": "escalation_resolution",
                "conversation_id": conversation_id,
                "decision": decision,
                "reason": reason,
                "proposal_id": task.get("proposal_id")
            }
        ))
        
        # Переміщуємо в розв'язані
        self._resolved_tasks[conversation_id] = self._escalated_tasks.pop(conversation_id)
        
        logger.info(f"✅ [{self.id}] Escalation resolved: {conversation_id} → {decision}")
    
    def get_pending_escalations(self) -> Dict[str, Dict]:
        """Отримує список очікуючих ескалацій."""
        return {
            cid: task for cid, task in self._escalated_tasks.items()
            if task["status"] == "pending"
        }
    
    def get_resolved_escalations(self) -> Dict[str, Dict]:
        """Отримує список розв'язаних ескалацій."""
        return self._resolved_tasks
    
    def get_escalation_stats(self) -> Dict[str, int]:
        """Отримує статистику ескалацій."""
        return {
            "pending": len(self._escalated_tasks),
            "resolved": len(self._resolved_tasks),
            "total": len(self._escalated_tasks) + len(self._resolved_tasks)
        }