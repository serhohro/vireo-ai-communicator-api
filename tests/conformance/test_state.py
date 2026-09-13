"""Vireo v3.1 state machine tests."""

import pytest

from core.protocol.state import (
    ProtocolState, VireoStateMachine, IllegalTransitionError, TERMINAL_STATES,
)


class TestHappyPath:
    def test_initial(self):
        assert VireoStateMachine().state == ProtocolState.DISCOVER

    def test_full_lifecycle(self):
        sm = VireoStateMachine()
        for s in (ProtocolState.PROPOSE, ProtocolState.NEGOTIATE,
                  ProtocolState.COMMIT, ProtocolState.EXECUTE,
                  ProtocolState.VERIFY, ProtocolState.DONE):
            sm.transition(s)
        assert sm.state == ProtocolState.DONE

    def test_reject(self):
        sm = VireoStateMachine()
        sm.transition(ProtocolState.PROPOSE)
        sm.transition(ProtocolState.REJECTED)
        assert sm.is_terminal


class TestIllegal:
    def test_discover_to_done(self):
        sm = VireoStateMachine()
        with pytest.raises(IllegalTransitionError):
            sm.transition(ProtocolState.DONE)

    def test_wrong_type(self):
        with pytest.raises(TypeError):
            VireoStateMachine().transition("PROPOSE")


class TestIntrospection:
    def test_history(self):
        sm = VireoStateMachine()
        sm.transition(ProtocolState.PROPOSE)
        assert [s.value for s in sm.history] == ["DISCOVER", "PROPOSE"]

    def test_terminal_states(self):
        assert ProtocolState.DONE in TERMINAL_STATES
        assert ProtocolState.DISCOVER not in TERMINAL_STATES
