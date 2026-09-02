"""Protocol State Machine for Vireo v2.0.1"""

from enum import Enum, auto
from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ProtocolState(Enum):
    """Vireo protocol states"""
    DISCOVER = "discover"
    PROPOSE = "propose"
    NEGOTIATE = "negotiate"
    COMMIT = "commit"
    EXECUTE = "execute"
    VERIFY = "verify"
    DONE = "done"
    
    # Error states
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    FAILED = "failed"
    ESCALATED = "escalated"
    TIMEOUT = "timeout"


class ProtocolEvent(Enum):
    """Protocol events"""
    DISCOVER = auto()
    PROPOSE = auto()
    ACCEPT = auto()
    REJECT = auto()
    COMMIT = auto()
    EXECUTE = auto()
    VERIFY = auto()
    ESCALATE = auto()
    DONE = auto()
    TIMEOUT = auto()
    CANCEL = auto()


@dataclass
class StateTransition:
    """State transition definition"""
    from_state: ProtocolState
    to_state: ProtocolState
    event: ProtocolEvent
    condition: Optional[Callable[[Dict], bool]] = None


class StateMachine:
    """Protocol state machine"""
    
    _transitions: List[StateTransition] = []
    
    @classmethod
    def _init_transitions(cls):
        if cls._transitions:
            return
        
        # Define transitions
        transitions = [
            # Normal flow
            StateTransition(ProtocolState.DISCOVER, ProtocolState.PROPOSE, ProtocolEvent.DISCOVER),
            StateTransition(ProtocolState.PROPOSE, ProtocolState.NEGOTIATE, ProtocolEvent.ACCEPT),
            StateTransition(ProtocolState.NEGOTIATE, ProtocolState.COMMIT, ProtocolEvent.COMMIT),
            StateTransition(ProtocolState.COMMIT, ProtocolState.EXECUTE, ProtocolEvent.EXECUTE),
            StateTransition(ProtocolState.EXECUTE, ProtocolState.VERIFY, ProtocolEvent.VERIFY),
            StateTransition(ProtocolState.VERIFY, ProtocolState.DONE, ProtocolEvent.DONE),
            
            # Error transitions
            StateTransition(ProtocolState.PROPOSE, ProtocolState.REJECTED, ProtocolEvent.REJECT),
            StateTransition(ProtocolState.NEGOTIATE, ProtocolState.REJECTED, ProtocolEvent.REJECT),
            StateTransition(ProtocolState.COMMIT, ProtocolState.CANCELLED, ProtocolEvent.CANCEL),
            StateTransition(ProtocolState.EXECUTE, ProtocolState.FAILED, ProtocolEvent.TIMEOUT),
            StateTransition(ProtocolState.VERIFY, ProtocolState.ESCALATED, ProtocolEvent.ESCALATE),
            
            # Timeout transitions
            StateTransition(ProtocolState.PROPOSE, ProtocolState.TIMEOUT, ProtocolEvent.TIMEOUT),
            StateTransition(ProtocolState.NEGOTIATE, ProtocolState.TIMEOUT, ProtocolEvent.TIMEOUT),
            StateTransition(ProtocolState.COMMIT, ProtocolState.TIMEOUT, ProtocolEvent.TIMEOUT),
            StateTransition(ProtocolState.EXECUTE, ProtocolState.TIMEOUT, ProtocolEvent.TIMEOUT),
        ]
        
        cls._transitions = transitions
    
    def __init__(self, initial_state: ProtocolState = ProtocolState.DISCOVER):
        self._init_transitions()
        self.state = initial_state
        self.history: List[StateTransition] = []
        self._timers: Dict[str, datetime] = {}
        self.context: Dict[str, Any] = {}
        self._logger = logging.getLogger(f"{__name__}.StateMachine")
    
    def can_transition(self, event: ProtocolEvent, context: Optional[Dict] = None) -> bool:
        """Check if transition is valid"""
        context = context or {}
        for transition in self._transitions:
            if (transition.from_state == self.state and 
                transition.event == event):
                if transition.condition:
                    if transition.condition(context):
                        return True
                else:
                    return True
        return False
    
    def transition(self, event: ProtocolEvent, context: Optional[Dict] = None) -> bool:
        """Execute a transition"""
        context = context or {}
        
        if not self.can_transition(event, context):
            self._logger.warning(
                f"Invalid transition: {self.state.value} --{event}--> ?"
            )
            return False
        
        # Find transition
        for transition in self._transitions:
            if (transition.from_state == self.state and 
                transition.event == event):
                old_state = self.state
                self.state = transition.to_state
                self.history.append(transition)
                self.context.update(context)
                self._logger.info(
                    f"Transition: {old_state.value} --{event}--> {self.state.value}"
                )
                return True
        
        return False
    
    def is_terminal(self) -> bool:
        """Check if state is terminal"""
        return self.state in [
            ProtocolState.DONE,
            ProtocolState.REJECTED,
            ProtocolState.CANCELLED,
            ProtocolState.FAILED,
            ProtocolState.ESCALATED,
            ProtocolState.TIMEOUT
        ]
    
    def is_error(self) -> bool:
        """Check if state is error"""
        return self.state in [
            ProtocolState.REJECTED,
            ProtocolState.CANCELLED,
            ProtocolState.FAILED,
            ProtocolState.ESCALATED,
            ProtocolState.TIMEOUT
        ]
    
    def start_timer(self, name: str, timeout_sec: int) -> None:
        """Start a timer"""
        self._timers[name] = datetime.now() + timedelta(seconds=timeout_sec)
    
    def check_timer(self, name: str) -> bool:
        """Check if timer has expired"""
        if name not in self._timers:
            return False
        return datetime.now() > self._timers[name]
    
    def cancel_timer(self, name: str) -> None:
        """Cancel a timer"""
        if name in self._timers:
            del self._timers[name]
    
    def reset(self) -> None:
        """Reset state machine"""
        self.state = ProtocolState.DISCOVER
        self.history = []
        self.context = {}
        self._timers = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dict"""
        return {
            "state": self.state.value,
            "history": [t.to_state.value for t in self.history[-10:]],
            "context": self.context,
            "is_terminal": self.is_terminal(),
            "is_error": self.is_error()
        }


# Valid state transitions for reference
VALID_TRANSITIONS = {
    ProtocolState.DISCOVER: [ProtocolEvent.DISCOVER],
    ProtocolState.PROPOSE: [ProtocolEvent.ACCEPT, ProtocolEvent.REJECT, ProtocolEvent.TIMEOUT],
    ProtocolState.NEGOTIATE: [ProtocolEvent.COMMIT, ProtocolEvent.REJECT, ProtocolEvent.TIMEOUT],
    ProtocolState.COMMIT: [ProtocolEvent.EXECUTE, ProtocolEvent.CANCEL, ProtocolEvent.TIMEOUT],
    ProtocolState.EXECUTE: [ProtocolEvent.VERIFY, ProtocolEvent.TIMEOUT],
    ProtocolState.VERIFY: [ProtocolEvent.DONE, ProtocolEvent.ESCALATE],
}