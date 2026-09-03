"""
LLM Agent — інтелектуальний агент з підтримкою LLM
Тепер наслідує Agent і використовує реальний протокол
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List
from .agent import Agent
from .message import Message
from .intent import Intent
from .state import DialogueState
from .contract import Contract

logger = logging.getLogger(__name__)


class LLMAgent(Agent):
    """
    LLM-агент, який використовує велику мовну модель для прийняття рішень.
    
    Наслідує Agent — використовує протокол, state machine, bus.
    """
    
    def __init__(self, agent_id: str, bus, provider, model: str = None, 
                 executor=None, **kwargs):
        # 🔴 ВАЖЛИВО: викликаємо super() з bus
        super().__init__(agent_id, bus, model, executor, **kwargs)
        self.provider = provider
        self.model = model
        self._pending_responses: Dict[str, asyncio.Future] = {}
        
        # Реєструємо обробник для відповідей
        self.bus.subscribe(agent_id, self._handle_message)
    
    async def auto_negotiate(self, recipient_id: str, task: str, 
                             contract: Optional[Contract] = None,
                             timeout_sec: int = 30) -> Dict[str, Any]:
        """
        Автономні переговори з використанням LLM.
        
        Тепер використовує РЕАЛЬНИЙ протокол:
        1. Генерує пропозицію через LLM
        2. Надсилає PROPOSE через bus
        3. Чекає на COMMIT/REJECT
        4. Виконує через self.executor (успадкований від Agent)
        5. Надсилає INFORM через bus
        """
        # 1. Генеруємо пропозицію через LLM
        proposal_data = await self._generate_proposal(task, contract)
        
        # 2. Надсилаємо реальне PROPOSE повідомлення
        msg = self.propose(recipient_id, {
            "task": task,
            "code": proposal_data.get("code", ""),
            "reasoning": proposal_data.get("reasoning", ""),
            "contract": contract.to_dict() if contract else None
        })
        
        logger.info(f"📤 [{self.agent_id}] PROPOSE sent to {recipient_id}")
        
        # 3. Чекаємо на COMMIT/REJECT через asyncio
        future = asyncio.Future()
        self._pending_responses[msg.conversation_id] = future
        
        try:
            response = await asyncio.wait_for(future, timeout=timeout_sec)
            decision = response.get("decision")
            
            if decision == "commit":
                logger.info(f"✅ [{self.agent_id}] Proposal committed")
                
                # 4. Виконуємо через self.executor (успадкований від Agent)
                #    і надсилаємо INFORM через commit()
                result = await self._execute_and_commit(msg, proposal_data)
                return {
                    "status": "success",
                    "conversation_id": msg.conversation_id,
                    "decision": "commit",
                    "result": result
                }
            else:
                logger.info(f"❌ [{self.agent_id}] Proposal rejected")
                return {
                    "status": "rejected",
                    "conversation_id": msg.conversation_id,
                    "decision": "reject",
                    "reason": response.get("reason", "No reason provided")
                }
                
        except asyncio.TimeoutError:
            logger.error(f"⏰ [{self.agent_id}] Negotiation timeout")
            return {
                "status": "timeout",
                "conversation_id": msg.conversation_id,
                "error": "Negotiation timeout"
            }
        finally:
            self._pending_responses.pop(msg.conversation_id, None)
    
    async def _generate_proposal(self, task: str, 
                                  contract: Optional[Contract] = None) -> Dict[str, Any]:
        """Генерує пропозицію через LLM."""
        prompt = f"""
Generate Vireo code for the following task:

Task: {task}

Contract constraints:
{json.dumps(contract.to_dict() if contract else {}, indent=2)}

Return JSON with:
- code: Vireo code to execute
- reasoning: why this solution
"""
        # Тут виклик LLM (асинхронний)
        response = await self.provider.generate_async(prompt)
        try:
            return json.loads(response)
        except:
            return {"code": "", "reasoning": response}
    
    async def _execute_and_commit(self, proposal: Message, 
                                   proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Виконує код і надсилає INFORM через протокол."""
        # Використовуємо успадкований метод commit()
        result = await self.commit(proposal)
        return result
    
    async def _wait_for_response(self, conversation_id: str, 
                                  timeout_sec: int = 30) -> Dict[str, Any]:
        """Чекає на відповідь від іншого агента."""
        future = asyncio.Future()
        self._pending_responses[conversation_id] = future
        try:
            return await asyncio.wait_for(future, timeout=timeout_sec)
        finally:
            self._pending_responses.pop(conversation_id, None)
    
    async def _handle_message(self, message: Message) -> None:
        """Обробка вхідних повідомлень (async)."""
        # Викликаємо батьківський обробник
        await super()._handle_message(message)
        
        # Додаткова обробка для LLMAgent
        if message.intent == Intent.COMMIT:
            conversation_id = message.conversation_id
            if conversation_id in self._pending_responses:
                self._pending_responses[conversation_id].set_result({
                    "decision": "commit",
                    "message": message
                })
        elif message.intent == Intent.REJECT:
            conversation_id = message.conversation_id
            if conversation_id in self._pending_responses:
                self._pending_responses[conversation_id].set_result({
                    "decision": "reject",
                    "reason": message.payload.get("reason", "No reason")
                })