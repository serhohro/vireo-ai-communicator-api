# ============================================================
# LAYER 3 — AI PROTOCOL: DIALOGUE STATE MACHINE
# ============================================================

from __future__ import annotations

import time
import threading
import logging
from enum import Enum
from typing import Dict, Optional, Set, Callable

logger = logging.getLogger("vireo.protocol.state")


class DialogueState(str, Enum):
    NEW = "NEW"
    PROPOSED = "PROPOSED"
    COMMITTED = "COMMITTED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


_TRANSITIONS: Dict[DialogueState, Set[DialogueState]] = {
    DialogueState.NEW: {DialogueState.PROPOSED, DialogueState.CANCELLED},
    DialogueState.PROPOSED: {
        DialogueState.COMMITTED,
        DialogueState.REJECTED,
        DialogueState.TIMEOUT,
        DialogueState.CANCELLED,
    },
    DialogueState.COMMITTED: {
        DialogueState.RUNNING,
        DialogueState.CANCELLED,
        DialogueState.TIMEOUT,
    },
    DialogueState.RUNNING: {
        DialogueState.DONE,
        DialogueState.FAILED,
        DialogueState.TIMEOUT,
        DialogueState.CANCELLED,
    },
    DialogueState.DONE: set(),
    DialogueState.FAILED: set(),
    DialogueState.TIMEOUT: set(),
    DialogueState.REJECTED: set(),
    DialogueState.CANCELLED: set(),
}


class InvalidTransition(Exception):
    pass


class DialogueStateMachine:
    def __init__(self):
        self._states: Dict[str, DialogueState] = {}
        self._timeouts: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def get(self, conversation_id: str) -> DialogueState:
        return self._states.get(conversation_id, DialogueState.NEW)
    
    def transition(self, conversation_id: str, to_state: DialogueState) -> DialogueState:
        with self._lock:
            current = self.get(conversation_id)
            
            if current == to_state:
                return current
            
            allowed = _TRANSITIONS.get(current, set())
            if to_state not in allowed:
                raise InvalidTransition(
                    f"[{conversation_id}] cannot go {current.value} -> {to_state.value}"
                )
            
            self._states[conversation_id] = to_state
            logger.debug(f"[{conversation_id}] {current.value} → {to_state.value}")
            return to_state
    
    def is_terminal(self, conversation_id: str) -> bool:
        return len(_TRANSITIONS.get(self.get(conversation_id), set())) == 0
    
    def list_conversations(self) -> Dict[str, DialogueState]:
        return dict(self._states)