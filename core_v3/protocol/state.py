"""
Protocol State Machine

Finite state machine for Vireo protocol.

Author: Serhii (serhohro)
License: Apache 2.0
Version: 3.0.0
"""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Set, List, Callable
from datetime import datetime
import threading
import logging

from ..errors import VireoStateError, VireoProtocolError


logger = logging.getLogger(__name__)


class ProtocolState(Enum):
    """Protocol states."""
    INIT = "init"
    PROPOSE = "propose"
    COMMIT = "commit"
    EXECUTE = "execute"
    VERIFY = "verify"
    ESCALATE = "escalate"
    DONE = "done"
    FAILED = "failed"
    TIMEOUT = "timeout"
    PAUSED = "paused"
    
    def is_terminal(self) -> bool:
        """Check if state is terminal."""
        return self in [ProtocolState.DONE, ProtocolState.FAILED, ProtocolState.TIMEOUT]
    
    def is_active(self) -> bool:
        """Check if state is active (non-terminal)."""
        return not self.is_terminal()


@dataclass
class StateTransition:
    """A transition between states."""
    from_state: ProtocolState
    to_state: ProtocolState
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    action: Optional[Callable[[Dict[str, Any]], None]] = None
    description: Optional[str] = None
    
    def can_transition(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if transition is allowed."""
        if self.condition is None:
            return True
        return self.condition(context or {})


class ProtocolStateMachine:
    """
    Protocol state machine.
    
    Manages state transitions for Vireo protocol.
    """
    
    def __init__(self, initial_state: ProtocolState = ProtocolState.INIT):
        self._state = initial_state
        self._transitions: Dict[ProtocolState, List[StateTransition]] = {}
        self._history: List[ProtocolState] = [initial_state]
        self._metadata: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._handlers: Dict[ProtocolState, List[Callable[[ProtocolState], None]]] = {}
        self._timeout_handlers: Dict[ProtocolState, Callable[[], None]] = {}
        self._state_timeout: Dict[ProtocolState, float] = {}
        self._start_time: datetime = datetime.now(datetime.timezone.utc)
        self._last_update: datetime = self._start_time
        
        # Setup default transitions
        self._setup_default_transitions()
    
    def _setup_default_transitions(self) -> None:
        """Setup default state transitions."""
        # INIT -> PROPOSE
        self.add_transition(
            ProtocolState.INIT, ProtocolState.PROPOSE,
            description="Initialize proposal"
        )
        
        # PROPOSE -> COMMIT
        self.add_transition(
            ProtocolState.PROPOSE, ProtocolState.COMMIT,
            description="Commit proposal"
        )
        
        # PROPOSE -> FAILED
        self.add_transition(
            ProtocolState.PROPOSE, ProtocolState.FAILED,
            description="Proposal failed"
        )
        
        # COMMIT -> EXECUTE
        self.add_transition(
            ProtocolState.COMMIT, ProtocolState.EXECUTE,
            description="Execute committed operation"
        )
        
        # COMMIT -> ESCALATE
        self.add_transition(
            ProtocolState.COMMIT, ProtocolState.ESCALATE,
            description="Escalate commit"
        )
        
        # EXECUTE -> VERIFY
        self.add_transition(
            ProtocolState.EXECUTE, ProtocolState.VERIFY,
            description="Verify execution"
        )
        
        # EXECUTE -> DONE
        self.add_transition(
            ProtocolState.EXECUTE, ProtocolState.DONE,
            description="Execution complete"
        )
        
        # EXECUTE -> FAILED
        self.add_transition(
            ProtocolState.EXECUTE, ProtocolState.FAILED,
            description="Execution failed"
        )
        
        # VERIFY -> DONE
        self.add_transition(
            ProtocolState.VERIFY, ProtocolState.DONE,
            description="Verification passed"
        )
        
        # VERIFY -> ESCALATE
        self.add_transition(
            ProtocolState.VERIFY, ProtocolState.ESCALATE,
            description="Verification needs escalation"
        )
        
        # VERIFY -> FAILED
        self.add_transition(
            ProtocolState.VERIFY, ProtocolState.FAILED,
            description="Verification failed"
        )
        
        # ESCALATE -> VERIFY
        self.add_transition(
            ProtocolState.ESCALATE, ProtocolState.VERIFY,
            description="Re-verify after escalation"
        )
        
        # ESCALATE -> DONE
        self.add_transition(
            ProtocolState.ESCALATE, ProtocolState.DONE,
            description="Escalation resolved"
        )
        
        # ESCALATE -> FAILED
        self.add_transition(
            ProtocolState.ESCALATE, ProtocolState.FAILED,
            description="Escalation failed"
        )
        
        # DONE -> (no transitions)
        # FAILED -> (no transitions)
        # TIMEOUT -> (no transitions)
    
    def add_transition(
        self,
        from_state: ProtocolState,
        to_state: ProtocolState,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        action: Optional[Callable[[Dict[str, Any]], None]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add a state transition."""
        with self._lock:
            if from_state not in self._transitions:
                self._transitions[from_state] = []
            self._transitions[from_state].append(
                StateTransition(from_state, to_state, condition, action, description)
            )
    
    def can_transition_to(self, target: ProtocolState, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if transition to target is allowed."""
        with self._lock:
            if self._state not in self._transitions:
                return False
            for transition in self._transitions[self._state]:
                if transition.to_state == target:
                    if transition.can_transition(context):
                        return True
            return False
    
    def transition(self, target: ProtocolState, context: Optional[Dict[str, Any]] = None) -> bool:
        """Transition to target state."""
        context = context or {}
        
        with self._lock:
            if not self.can_transition_to(target, context):
                return False
            
            # Execute transition
            old_state = self._state
            self._state = target
            self._history.append(target)
            self._last_update = datetime.now(datetime.timezone.utc)
            
            logger.debug(f"State transition: {old_state.value} -> {target.value}")
            
            # Execute action if any
            for transition in self._transitions.get(old_state, []):
                if transition.to_state == target and transition.action:
                    try:
                        transition.action(context)
                    except Exception as e:
                        logger.error(f"Action failed: {e}")
            
            # Notify handlers
            if target in self._handlers:
                for handler in self._handlers[target]:
                    try:
                        handler(target)
                    except Exception as e:
                        logger.error(f"Handler failed: {e}")
            
            return True
    
    def get_state(self) -> ProtocolState:
        """Get current state."""
        return self._state
    
    def get_history(self) -> List[ProtocolState]:
        """Get state history."""
        return self._history.copy()
    
    def is_terminal(self) -> bool:
        """Check if in terminal state."""
        return self._state.is_terminal()
    
    def is_active(self) -> bool:
        """Check if in active state."""
        return self._state.is_active()
    
    def reset(self, state: ProtocolState = ProtocolState.INIT) -> None:
        """Reset state machine."""
        with self._lock:
            self._state = state
            self._history = [state]
            self._start_time = datetime.now(datetime.timezone.utc)
            self._last_update = self._start_time
    
    def on_state(self, state: ProtocolState, handler: Callable[[ProtocolState], None]) -> None:
        """Register a state entry handler."""
        with self._lock:
            if state not in self._handlers:
                self._handlers[state] = []
            self._handlers[state].append(handler)
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata."""
        return self._metadata.get(key, default)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata."""
        self._metadata[key] = value
    
    def get_time_in_state(self) -> float:
        """Get time in current state in seconds."""
        return (datetime.now(datetime.timezone.utc) - self._last_update).total_seconds()
    
    def get_total_time(self) -> float:
        """Get total time since start in seconds."""
        return (datetime.now(datetime.timezone.utc) - self._start_time).total_seconds()
    
    def get_transition_stats(self) -> Dict[str, Any]:
        """Get transition statistics."""
        return {
            "current_state": self._state.value,
            "history": [s.value for s in self._history],
            "total_transitions": len(self._history) - 1,
            "time_in_state": self.get_time_in_state(),
            "total_time": self.get_total_time(),
            "is_terminal": self.is_terminal(),
        }


# Utility functions

def validate_state_transition(
    current: ProtocolState,
    target: ProtocolState,
    allowed_transitions: Dict[ProtocolState, Set[ProtocolState]],
) -> bool:
    """Validate state transition against allowed transitions."""
    if current not in allowed_transitions:
        return False
    return target in allowed_transitions[current]


def get_common_states() -> List[ProtocolState]:
    """Get common protocol states."""
    return [
        ProtocolState.INIT,
        ProtocolState.PROPOSE,
        ProtocolState.COMMIT,
        ProtocolState.EXECUTE,
        ProtocolState.VERIFY,
        ProtocolState.DONE,
    ]


def get_error_states() -> List[ProtocolState]:
    """Get error states."""
    return [
        ProtocolState.FAILED,
        ProtocolState.TIMEOUT,
    ]


class StateError(VireoStateError):
    """State error with additional context."""
    
    def __init__(
        self,
        message: str,
        current_state: Optional[ProtocolState] = None,
        target_state: Optional[ProtocolState] = None,
    ):
        super().__init__(
            message,
            current_state.value if current_state else None,
            target_state.value if target_state else None,
        )
        self.current_state = current_state
        self.target_state = target_state


class InvalidTransitionError(StateError):
    """Invalid state transition error."""
    
    def __init__(
        self,
        current_state: ProtocolState,
        target_state: ProtocolState,
        reason: Optional[str] = None,
    ):
        msg = f"Invalid transition from {current_state.value} to {target_state.value}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg, current_state, target_state)