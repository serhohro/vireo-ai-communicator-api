# ============================================================
# LAYER 4 — Transport (abstract interface)
# ============================================================

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from ..message import Message

Handler = Callable[[Message], None]


class Transport(ABC):
    @abstractmethod
    def publish(self, channel: str, message: Message) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, channel: str, handler: Handler) -> None:
        raise NotImplementedError