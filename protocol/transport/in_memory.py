# ============================================================
# LAYER 4 — Transport: in-memory Event Bus VERSION = "1.4.3"
# ============================================================

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from .base import Transport, Handler
from ..message import Message


class InMemoryEventBus(Transport):
    def __init__(self):
        self._subscribers: Dict[str, List[Handler]] = defaultdict(list)
        self.log: List[Message] = []

    def publish(self, channel: str, message: Message) -> None:
        self.log.append(message)
        for handler in self._subscribers.get(channel, []):
            handler(message)

    def subscribe(self, channel: str, handler: Handler) -> None:
        self._subscribers[channel].append(handler)