# ============================================================
# LAYER 3 — AI PROTOCOL: DIALOGUE STATE MACHINE
# ============================================================

from __future__ import annotations

import time
import threading
import logging
from enum import Enum
from typing import Dict, Optional, Set, Callable, List, Tuple

logger = logging.getLogger("vireo.protocol.state")


class DialogueState(str, Enum):
    """States for agent conversation lifecycle."""
    
    NEW = "NEW"
    PROPOSED = "PROPOSED"
    NEGOTIATING = "NEGOTIATING"
    COMMITTED = "COMMITTED"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"      # 🆕 Result verification
    DONE = "DONE"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    ESCALATED = "ESCALATED"      # 🆕 Dispute escalation


# ============================================================
# TERMINAL STATES
# ============================================================

_TERMINAL_STATES = {
    DialogueState.DONE,
    DialogueState.FAILED,
    DialogueState.TIMEOUT,
    DialogueState.REJECTED,
    DialogueState.CANCELLED,
    DialogueState.ESCALATED,     # 🆕
}


# ============================================================
# STATE TRANSITIONS
# ============================================================

_TRANSITIONS: Dict[DialogueState, Set[DialogueState]] = {
    # Initial
    DialogueState.NEW: {
        DialogueState.PROPOSED,
        DialogueState.CANCELLED,
    },
    
    # Proposal phase
    DialogueState.PROPOSED: {
        DialogueState.NEGOTIATING,
        DialogueState.COMMITTED,
        DialogueState.REJECTED,
        DialogueState.TIMEOUT,
        DialogueState.CANCELLED,
    },
    
    # Negotiation phase (multi-round)
    DialogueState.NEGOTIATING: {
        DialogueState.PROPOSED,      # Back to proposal
        DialogueState.COMMITTED,
        DialogueState.REJECTED,
        DialogueState.TIMEOUT,
        DialogueState.CANCELLED,
    },
    
    # Commitment phase
    DialogueState.COMMITTED: {
        DialogueState.RUNNING,
        DialogueState.CANCELLED,
        DialogueState.TIMEOUT,
    },
    
    # Execution phase
    DialogueState.RUNNING: {
        DialogueState.VERIFYING,     # 🆕 Instead of DONE
        DialogueState.FAILED,
        DialogueState.TIMEOUT,
        DialogueState.CANCELLED,
    },
    
    # Verification phase (NEW!)
    DialogueState.VERIFYING: {
        DialogueState.DONE,
        DialogueState.ESCALATED,     # 🆕 If verification fails
        DialogueState.FAILED,
        DialogueState.TIMEOUT,
    },
    
    # Terminal states
    DialogueState.DONE: set(),
    DialogueState.FAILED: set(),
    DialogueState.TIMEOUT: set(),
    DialogueState.REJECTED: set(),
    DialogueState.CANCELLED: set(),
    DialogueState.ESCALATED: set(),  # 🆕 Terminal (or can be resolved later)
}


# ============================================================
# STATE DESCRIPTIONS
# ============================================================

_STATE_DESCRIPTIONS = {
    DialogueState.NEW: "New conversation",
    DialogueState.PROPOSED: "Proposal made",
    DialogueState.NEGOTIATING: "Negotiation in progress",
    DialogueState.COMMITTED: "Agreement reached",
    DialogueState.RUNNING: "Execution in progress",
    DialogueState.VERIFYING: "Verifying result",
    DialogueState.DONE: "Completed successfully",
    DialogueState.FAILED: "Execution failed",
    DialogueState.TIMEOUT: "Timeout exceeded",
    DialogueState.REJECTED: "Proposal rejected",
    DialogueState.CANCELLED: "Cancelled",
    DialogueState.ESCALATED: "Dispute escalated",
}


# ============================================================
# EXCEPTION
# ============================================================

class InvalidTransition(Exception):
    pass


# ============================================================
# STATE MACHINE
# ============================================================

class DialogueStateMachine:
    """
    State machine for tracking agent conversations.
    
    Lifecycle:
        NEW → PROPOSED → NEGOTIATING → COMMITTED → RUNNING → VERIFYING → DONE
             │              │            │            │            │
             ├→ REJECTED   ├→ REJECTED  ├→ CANCELLED ├→ FAILED   ├→ ESCALATED
             └→ TIMEOUT     └→ TIMEOUT   └→ TIMEOUT    └→ TIMEOUT  └→ FAILED
    """
    
    def __init__(self, timeout_check_interval: float = 5.0):
        self._states: Dict[str, DialogueState] = {}
        self._timeouts: Dict[str, float] = {}  # conversation_id -> deadline (Unix timestamp)
        self._timeout_callbacks: Dict[str, List[Callable[[str], None]]] = {}
        self._history: Dict[str, List[Tuple[float, DialogueState, DialogueState]]] = {}
        self._lock = threading.Lock()
        
        # Timeout checker thread
        self._running = False
        self._timeout_event = threading.Event()
        self._check_thread: Optional[threading.Thread] = None
        self._check_interval = timeout_check_interval
    
    # ============================================================
    # TIMEOUT CHECKER
    # ============================================================
    
    def start(self) -> None:
        """Start the background timeout checker."""
        if self._running:
            return
        
        self._running = True
        self._timeout_event.clear()
        self._check_thread = threading.Thread(target=self._timeout_worker, daemon=True)
        self._check_thread.start()
        logger.info("🔄 Timeout checker started")
    
    def stop(self) -> None:
        """Stop the background timeout checker."""
        self._running = False
        self._timeout_event.set()
        if self._check_thread:
            self._check_thread.join(timeout=2.0)
            self._check_thread = None
        logger.info("🛑 Timeout checker stopped")
    
    def _timeout_worker(self) -> None:
        """Background worker that checks for timeouts."""
        while self._running:
            self.check_timeouts()
            # Wait for interval or event
            self._timeout_event.wait(timeout=self._check_interval)
            self._timeout_event.clear()
    
    def check_timeouts(self) -> List[str]:
        """
        Check for expired timeouts and transition to TIMEOUT state.
        
        Returns:
            List of conversation IDs that timed out.
        """
        expired = []
        now = time.time()
        
        with self._lock:
            for conv_id, deadline in list(self._timeouts.items()):
                current_state = self._states.get(conv_id, DialogueState.NEW)
                
                # Only check non-terminal states
                if current_state not in _TERMINAL_STATES and now > deadline:
                    try:
                        self._states[conv_id] = DialogueState.TIMEOUT
                        self._history.setdefault(conv_id, []).append(
                            (now, current_state, DialogueState.TIMEOUT)
                        )
                        expired.append(conv_id)
                        logger.info(f"⏰ [{conv_id}] Timed out from {current_state.value}")
                        
                        # Call timeout callbacks
                        for callback in self._timeout_callbacks.get(conv_id, []):
                            try:
                                callback(conv_id)
                            except Exception as e:
                                logger.error(f"Timeout callback error: {e}")
                        
                        del self._timeouts[conv_id]
                    except Exception as e:
                        logger.error(f"Error processing timeout for {conv_id}: {e}")
        
        return expired
    
    def set_timeout(self, conversation_id: str, timeout_sec: float, 
                    callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Set a timeout for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            timeout_sec: Timeout in seconds
            callback: Optional callback to call on timeout
        """
        deadline = time.time() + timeout_sec
        with self._lock:
            self._timeouts[conversation_id] = deadline
            if callback:
                self._timeout_callbacks.setdefault(conversation_id, []).append(callback)
            logger.debug(f"⏱️ [{conversation_id}] Timeout set to {timeout_sec}s")
    
    def get_timeout(self, conversation_id: str) -> Optional[float]:
        """Get the timeout deadline for a conversation."""
        return self._timeouts.get(conversation_id)
    
    def clear_timeout(self, conversation_id: str) -> None:
        """Clear the timeout for a conversation."""
        with self._lock:
            if conversation_id in self._timeouts:
                del self._timeouts[conversation_id]
            if conversation_id in self._timeout_callbacks:
                del self._timeout_callbacks[conversation_id]
            logger.debug(f"⏱️ [{conversation_id}] Timeout cleared")
    
    def ping_timeout(self) -> None:
        """Wake up the timeout checker immediately."""
        self._timeout_event.set()
    
    # ============================================================
    # STATE MANAGEMENT
    # ============================================================
    
    def get(self, conversation_id: str) -> DialogueState:
        """Get current state of a conversation."""
        return self._states.get(conversation_id, DialogueState.NEW)
    
    def transition(self, conversation_id: str, to_state: DialogueState) -> DialogueState:
        """
        Transition to a new state.
        
        Args:
            conversation_id: ID of the conversation
            to_state: New state
            
        Returns:
            New state
            
        Raises:
            InvalidTransition: If transition is not allowed
        """
        with self._lock:
            current = self.get(conversation_id)
            
            if current == to_state:
                return current
            
            allowed = _TRANSITIONS.get(current, set())
            if to_state not in allowed:
                raise InvalidTransition(
                    f"[{conversation_id}] cannot go {current.value} -> {to_state.value}"
                )
            
            # Record history
            self._history.setdefault(conversation_id, []).append(
                (time.time(), current, to_state)
            )
            
            self._states[conversation_id] = to_state
            logger.debug(f"[{conversation_id}] {current.value} → {to_state.value}")
            
            # Clear timeout on terminal states
            if to_state in _TERMINAL_STATES:
                self.clear_timeout(conversation_id)
            
            # Ping timeout checker on state change
            self.ping_timeout()
            
            return to_state
    
    def is_terminal(self, conversation_id: str) -> bool:
        """Check if a conversation is in a terminal state."""
        return self.get(conversation_id) in _TERMINAL_STATES
    
    def is_active(self, conversation_id: str) -> bool:
        """Check if a conversation is active (not terminal)."""
        return not self.is_terminal(conversation_id)
    
    def get_history(self, conversation_id: str) -> List[Tuple[float, DialogueState, DialogueState]]:
        """Get transition history for a conversation."""
        return self._history.get(conversation_id, [])
    
    def list_conversations(self) -> Dict[str, DialogueState]:
        """Get all conversations with their current states."""
        with self._lock:
            return dict(self._states)
    
    def get_timeouts(self) -> Dict[str, float]:
        """Get all active timeouts."""
        with self._lock:
            return dict(self._timeouts)
    
    def get_terminals(self) -> List[str]:
        """Get all conversations in terminal states."""
        with self._lock:
            return [cid for cid, state in self._states.items() if state in _TERMINAL_STATES]
    
    def reset_conversation(self, conversation_id: str) -> None:
        """Reset a conversation to NEW state."""
        with self._lock:
            self._states[conversation_id] = DialogueState.NEW
            self.clear_timeout(conversation_id)
            logger.debug(f"[{conversation_id}] Reset to NEW")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_valid_transition(from_state: DialogueState, to_state: DialogueState) -> bool:
    """Check if a transition is valid."""
    return to_state in _TRANSITIONS.get(from_state, set())


def get_allowed_transitions(state: DialogueState) -> Set[DialogueState]:
    """Get allowed transitions from a state."""
    return _TRANSITIONS.get(state, set())


def is_terminal_state(state: DialogueState) -> bool:
    """Check if a state is terminal."""
    return state in _TERMINAL_STATES


def get_state_description(state: DialogueState) -> str:
    """Get description of a state."""
    return _STATE_DESCRIPTIONS.get(state, state.value)