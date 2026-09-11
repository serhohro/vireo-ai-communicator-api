"""
Vireo State Machine v3.1.

Lifecycle:
    DISCOVER → PROPOSE → NEGOTIATE → COMMIT → EXECUTE → VERIFY → DONE
                  ↓          ↓           ↓         ↓         ↓
              REJECTED   REJECTED   CANCELLED  FAILED   ESCALATED
                  ↓          ↓                                ↓
              TIMEOUT    TIMEOUT                     NEGOTIATE / DONE
"""

from enum import Enum


class ProtocolState(Enum):
    DISCOVER  = "DISCOVER"
    PROPOSE   = "PROPOSE"
    NEGOTIATE = "NEGOTIATE"
    COMMIT    = "COMMIT"
    EXECUTE   = "EXECUTE"
    VERIFY    = "VERIFY"
    DONE      = "DONE"
    REJECTED  = "REJECTED"
    ESCALATED = "ESCALATED"
    CANCELLED = "CANCELLED"
    FAILED    = "FAILED"
    TIMEOUT   = "TIMEOUT"


TERMINAL_STATES = frozenset({
    ProtocolState.DONE,
    ProtocolState.REJECTED,
    ProtocolState.CANCELLED,
    ProtocolState.FAILED,
    ProtocolState.TIMEOUT,
})


class IllegalTransitionError(Exception):
    def __init__(self, current: ProtocolState, attempted: ProtocolState):
        super().__init__(f"Illegal transition: {current.value} → {attempted.value}")
        self.current = current
        self.attempted = attempted


class VireoStateMachine:
    """
    Guard that physically forbids illegal state transitions.

    Usage:
        sm = VireoStateMachine()
        sm.transition(ProtocolState.PROPOSE)   # OK
        sm.transition(ProtocolState.DONE)      # raises IllegalTransitionError
    """

    VALID_TRANSITIONS = {
        ProtocolState.DISCOVER: {
            ProtocolState.DISCOVER,
            ProtocolState.PROPOSE,
        },
        ProtocolState.PROPOSE: {
            ProtocolState.NEGOTIATE,
            ProtocolState.REJECTED,
            ProtocolState.TIMEOUT,
        },
        ProtocolState.NEGOTIATE: {
            ProtocolState.PROPOSE,
            ProtocolState.COMMIT,
            ProtocolState.REJECTED,
            ProtocolState.TIMEOUT,
        },
        ProtocolState.COMMIT: {
            ProtocolState.EXECUTE,
            ProtocolState.CANCELLED,
        },
        ProtocolState.EXECUTE: {
            ProtocolState.VERIFY,
            ProtocolState.FAILED,
        },
        ProtocolState.VERIFY: {
            ProtocolState.DONE,
            ProtocolState.NEGOTIATE,
            ProtocolState.ESCALATED,
        },
        ProtocolState.ESCALATED: {
            ProtocolState.NEGOTIATE,
            ProtocolState.DONE,
        },
        ProtocolState.DONE:      frozenset(),
        ProtocolState.REJECTED:  frozenset(),
        ProtocolState.CANCELLED: frozenset(),
        ProtocolState.FAILED:    frozenset(),
        ProtocolState.TIMEOUT:   frozenset(),
    }

    def __init__(self, initial: ProtocolState = ProtocolState.DISCOVER):
        self._state = initial
        self._history: list[ProtocolState] = [initial]

    @property
    def state(self) -> ProtocolState:
        return self._state

    @property
    def history(self) -> list[ProtocolState]:
        return list(self._history)

    @property
    def is_terminal(self) -> bool:
        return self._state in TERMINAL_STATES

    def can_transition(self, next_state: ProtocolState) -> bool:
        return next_state in self.VALID_TRANSITIONS[self._state]

    def transition(self, next_state: ProtocolState) -> None:
        if not isinstance(next_state, ProtocolState):
            raise TypeError(f"Expected ProtocolState, got {type(next_state)}")
        if next_state not in self.VALID_TRANSITIONS[self._state]:
            raise IllegalTransitionError(self._state, next_state)
        self._state = next_state
        self._history.append(next_state)

    def reset(self) -> None:
        self._state = ProtocolState.DISCOVER
        self._history = [ProtocolState.DISCOVER]

    def to_dict(self) -> dict:
        return {
            "state": self._state.value,
            "is_terminal": self.is_terminal,
            "history": [s.value for s in self._history],
        }