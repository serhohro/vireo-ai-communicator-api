# Vireo v3.0.0 — Async Client

import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable

from sdk.python.client import VireoClient
from core.protocol.message import Message


class AsyncVireoClient(VireoClient):
    """Async Vireo client."""
    
    async def async_propose(self, recipient: str, contract: Dict[str, Any]) -> Message:
        return await asyncio.get_event_loop().run_in_executor(
            None, self.propose, recipient, contract
        )
    
    async def async_commit(self, recipient: str, proposal_id: str) -> Message:
        return await asyncio.get_event_loop().run_in_executor(
            None, self.commit, recipient, proposal_id
        )
    
    async def async_execute(self, recipient: str, proposal_id: str) -> Message:
        return await asyncio.get_event_loop().run_in_executor(
            None, self.execute, recipient, proposal_id
        )
    
    async def async_verify(self, recipient: str, proposal_id: str, result: Dict[str, Any]) -> Message:
        return await asyncio.get_event_loop().run_in_executor(
            None, self.verify, recipient, proposal_id, result
        )
    
    async def async_receive(self, message: Message) -> Optional[Message]:
        return await asyncio.get_event_loop().run_in_executor(
            None, self.receive, message
        )