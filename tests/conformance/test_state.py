#!/usr/bin/env python3
"""
Conformance Tests: State Machine

Tests for the Vireo protocol state machine implementation.
"""

import pytest
import sys
from pathlib import Path
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.protocol.state import (
    State, StateMachine, StateTransition, 
    StateMachineError, StateValidator
)
from core.protocol import Protocol


class TestState:
    """State enum conformance tests."""
    
    def test_state_values(self):
        """Test state enum values."""
        assert State.IDLE.value == "idle"
        assert State.PROPOSE.value == "propose"
        assert State.COMMIT.value == "commit"
        assert State.EXECUTE.value == "execute"
        assert State.VERIFY.value == "verify"
        assert State.ESCALATE.value == "escalate"
        assert State.DONE.value == "done"
        assert State.CANCEL.value == "cancel"
        assert State.ERROR.value == "error"
        
    def test_state_transitions(self):
        """Test state transition definitions."""
        transitions = StateTransition.get_transitions()
        
        # IDLE transitions
        assert State.PROPOSE in transitions[State.IDLE]
        assert State.CANCEL in transitions[State.IDLE]
        assert State.COMMIT not in transitions[State.IDLE]
        
        # PROPOSE transitions
        assert State.COMMIT in transitions[State.PROPOSE]
        assert State.CANCEL in transitions[State.PROPOSE]
        
        # COMMIT transitions
        assert State.EXECUTE in transitions[State.COMMIT]
        assert State.ESCALATE in transitions[State.COMMIT]
        
        # EXECUTE transitions
        assert State.VERIFY in transitions[State.EXECUTE]
        assert State.ESCALATE in transitions[State.EXECUTE]
        assert State.DONE in transitions[State.EXECUTE]
        
        # VERIFY transitions
        assert State.DONE in transitions[State.VERIFY]
        assert State.ESCALATE in transitions[State.VERIFY]


class TestStateMachine:
    """State machine conformance tests."""
    
    def test_machine_initialization(self):
        """Test state machine initialization."""
        machine = StateMachine()
        assert machine.current_state == State.IDLE
        assert len(machine.history) == 0
        assert machine.is_initialized is True
        
    def test_machine_transition(self):
        """Test state transitions."""
        machine = StateMachine()
        
        # IDLE -> PROPOSE
        assert machine.transition(State.PROPOSE) is True
        assert machine.current_state == State.PROPOSE
        assert len(machine.history) == 1
        
        # PROPOSE -> COMMIT
        assert machine.transition(State.COMMIT) is True
        assert machine.current_state == State.COMMIT
        assert len(machine.history) == 2
        
        # COMMIT -> EXECUTE
        assert machine.transition(State.EXECUTE) is True
        assert machine.current_state == State.EXECUTE
        assert len(machine.history) == 3
        
    def test_machine_invalid_transition(self):
        """Test invalid state transitions."""
        machine = StateMachine()
        
        # IDLE -> EXECUTE (invalid)
        with pytest.raises(StateMachineError):
            machine.transition(State.EXECUTE)
        
        assert machine.current_state == State.IDLE
        
    def test_machine_reset(self):
        """Test state machine reset."""
        machine = StateMachine()
        
        machine.transition(State.PROPOSE)
        machine.transition(State.COMMIT)
        assert machine.current_state == State.COMMIT
        
        machine.reset()
        assert machine.current_state == State.IDLE
        assert len(machine.history) == 0
        
    def test_machine_can_transition(self):
        """Test can_transition method."""
        machine = StateMachine()
        
        assert machine.can_transition(State.PROPOSE) is True
        assert machine.can_transition(State.COMMIT) is False
        assert machine.can_transition(State.EXECUTE) is False
        
        machine.transition(State.PROPOSE)
        assert machine.can_transition(State.COMMIT) is True
        assert machine.can_transition(State.EXECUTE) is False
        
    def test_machine_get_allowed(self):
        """Test get_allowed_transitions method."""
        machine = StateMachine()
        
        allowed = machine.get_allowed_transitions()
        assert State.PROPOSE in allowed
        assert State.CANCEL in allowed
        assert len(allowed) == 2
        
        machine.transition(State.PROPOSE)
        allowed = machine.get_allowed_transitions()
        assert State.COMMIT in allowed
        assert State.CANCEL in allowed
        assert len(allowed) == 2
        
    def test_machine_history_limit(self):
        """Test history limit."""
        machine = StateMachine(max_history=3)
        
        machine.transition(State.PROPOSE)
        machine.transition(State.COMMIT)
        machine.transition(State.EXECUTE)
        machine.transition(State.VERIFY)
        
        # History should be limited to 3
        assert len(machine.history) == 3
        assert machine.history[0] == State.COMMIT
        assert machine.history[1] == State.EXECUTE
        assert machine.history[2] == State.VERIFY


class TestStateValidator:
    """State validator conformance tests."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = StateValidator()
        assert validator is not None
        
    def test_validator_valid_state(self):
        """Test validating valid state."""
        validator = StateValidator()
        assert validator.is_valid_state(State.IDLE) is True
        assert validator.is_valid_state(State.PROPOSE) is True
        assert validator.is_valid_state(State.DONE) is True
        
    def test_validator_valid_transition(self):
        """Test validating valid transition."""
        validator = StateValidator()
        
        assert validator.is_valid_transition(State.IDLE, State.PROPOSE) is True
        assert validator.is_valid_transition(State.IDLE, State.COMMIT) is False
        
    def test_validator_validate_path(self):
        """Test validating a path of transitions."""
        validator = StateValidator()
        
        path = [State.IDLE, State.PROPOSE, State.COMMIT, State.EXECUTE]
        assert validator.validate_path(path) is True
        
        path = [State.IDLE, State.EXECUTE, State.VERIFY]
        assert validator.validate_path(path) is False


class TestProtocolStateIntegration:
    """Protocol state integration tests."""
    
    def test_protocol_state_flow(self):
        """Test complete protocol state flow."""
        protocol = Protocol()
        
        # Start
        assert protocol.get_state() == State.IDLE
        
        # Propose
        protocol.process("propose", {"task": "test"})
        assert protocol.get_state() == State.PROPOSE
        
        # Commit
        protocol.process("commit", {"accepted": True})
        assert protocol.get_state() == State.COMMIT
        
        # Execute
        protocol.process("execute", {"data": "test"})
        assert protocol.get_state() == State.EXECUTE
        
        # Verify
        protocol.process("verify", {"result": "success"})
        assert protocol.get_state() == State.VERIFY
        
        # Done
        protocol.process("done", {"status": "complete"})
        assert protocol.get_state() == State.DONE
        
    def test_protocol_escalation_flow(self):
        """Test protocol escalation flow."""
        protocol = Protocol()
        
        # Start
        protocol.process("propose", {"task": "test"})
        protocol.process("commit", {"accepted": True})
        protocol.process("execute", {"data": "test"})
        
        # Escalate from EXECUTE
        protocol.process("escalate", {"reason": "issue"})
        assert protocol.get_state() == State.ESCALATE
        
        # Done from ESCALATE
        protocol.process("done", {"status": "resolved"})
        assert protocol.get_state() == State.DONE
        
    def test_protocol_cancel_flow(self):
        """Test protocol cancellation flow."""
        protocol = Protocol()
        
        protocol.process("propose", {"task": "test"})
        protocol.process("commit", {"accepted": True})
        
        # Cancel from COMMIT
        protocol.process("cancel", {"reason": "cancelled"})
        assert protocol.get_state() == State.CANCEL
        
    def test_protocol_invalid_message(self):
        """Test protocol with invalid message."""
        protocol = Protocol()
        
        # Should ignore invalid message
        result = protocol.process("invalid", {})
        assert result is None
        assert protocol.get_state() == State.IDLE
        
    def test_protocol_message_validation(self):
        """Test protocol message validation."""
        protocol = Protocol()
        
        # Propose with missing payload
        result = protocol.process("propose", None)
        assert result is None
        assert protocol.get_state() == State.IDLE
        
        # Valid propose
        result = protocol.process("propose", {"task": "test"})
        assert result is not None
        assert protocol.get_state() == State.PROPOSE