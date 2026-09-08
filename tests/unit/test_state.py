# Vireo v3.0.0 — State Machine Unit Tests

import pytest
import time
import uuid
from core.protocol.state import StateMachine, State
from core.protocol.message import Intent
from core.errors import StateError, TimeoutError


class TestStateMachine:
    """Unit tests for State Machine."""
    
    def test_state_machine_creation(self):
        """Test state machine creation."""
        sm = StateMachine(agent_id="test-agent")
        
        assert sm.state == State.DISCOVER
        assert sm.agent_id == "test-agent"
        assert sm.counterparty is None
        assert sm.contract is None
        assert sm.result is None
        assert sm.started_at > 0
        assert sm.last_transition > 0
    
    def test_state_machine_transition_propose(self):
        """Test transition from DISCOVER to PROPOSE."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        assert sm.state == State.PROPOSE
    
    def test_state_machine_transition_commit(self):
        """Test transition from PROPOSE to COMMIT."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.COMMIT)
        assert sm.state == State.COMMIT
    
    def test_state_machine_transition_execute(self):
        """Test transition from COMMIT to EXECUTE."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.COMMIT)
        sm.transition(Intent.EXECUTE)
        assert sm.state == State.EXECUTE
    
    def test_state_machine_transition_verify(self):
        """Test transition from EXECUTE to VERIFY."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.COMMIT)
        sm.transition(Intent.EXECUTE)
        sm.transition(Intent.VERIFY)
        assert sm.state == State.VERIFY
    
    def test_state_machine_transition_done(self):
        """Test transition from VERIFY to DONE."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.COMMIT)
        sm.transition(Intent.EXECUTE)
        sm.transition(Intent.VERIFY)
        sm.transition(Intent.DONE)
        assert sm.state == State.DONE
        assert sm.is_complete() is True
    
    def test_state_machine_transition_escalate(self):
        """Test transition from VERIFY to ESCALATE."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.COMMIT)
        sm.transition(Intent.EXECUTE)
        sm.transition(Intent.VERIFY)
        sm.transition(Intent.ESCALATE)
        assert sm.state == State.ESCALATE
    
    def test_state_machine_transition_reject(self):
        """Test transition to REJECT."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.REJECT)
        assert sm.state == State.REJECT
        assert sm.is_complete() is True
    
    def test_state_machine_transition_timeout(self):
        """Test transition to TIMEOUT."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.COMMIT)
        sm.transition(Intent.EXECUTE)
        sm.transition(Intent.TIMEOUT)
        assert sm.state == State.TIMEOUT
        assert sm.is_complete() is True
    
    def test_state_machine_invalid_transition(self):
        """Test invalid transition raises error."""
        sm = StateMachine(agent_id="test-agent")
        
        # Can't go from DISCOVER to DONE
        with pytest.raises(StateError):
            sm.transition(Intent.DONE)
        
        # Can't go from PROPOSE to VERIFY
        sm.transition(Intent.PROPOSE)
        with pytest.raises(StateError):
            sm.transition(Intent.VERIFY)
    
    def test_state_machine_timeout(self):
        """Test timeout enforcement."""
        sm = StateMachine(agent_id="test-agent")
        sm.timeout_propose = 1
        
        sm.transition(Intent.PROPOSE)
        
        # Should not timeout immediately
        assert sm.state == State.PROPOSE
        
        # Wait for timeout
        time.sleep(1.1)
        
        with pytest.raises(TimeoutError):
            sm.transition(Intent.COMMIT)
    
    def test_state_machine_custom_timeouts(self):
        """Test custom timeouts."""
        sm = StateMachine(
            agent_id="test-agent",
            timeout_discover=10,
            timeout_propose=20,
            timeout_negotiate=30,
            timeout_commit=40,
            timeout_execute=50,
            timeout_verify=60,
            timeout_escalate=70
        )
        
        assert sm.timeout_discover == 10
        assert sm.timeout_propose == 20
        assert sm.timeout_negotiate == 30
        assert sm.timeout_commit == 40
        assert sm.timeout_execute == 50
        assert sm.timeout_verify == 60
        assert sm.timeout_escalate == 70
    
    def test_state_machine_context(self):
        """Test context passing in transitions."""
        sm = StateMachine(agent_id="test-agent")
        
        context = {
            "contract": {"max_tokens": 1000},
            "result": {"status": "success"},
            "counterparty": "agent-bob"
        }
        
        sm.transition(Intent.PROPOSE, context)
        
        assert sm.contract == {"max_tokens": 1000}
        assert sm.counterparty == "agent-bob"
    
    def test_state_machine_escalate(self):
        """Test escalate method."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.COMMIT)
        
        sm.escalate("Test reason")
        assert sm.state == State.ESCALATE
        
        # Can't escalate from terminal state
        sm.transition(Intent.DONE)
        with pytest.raises(StateError):
            sm.escalate("Cannot escalate")
    
    def test_state_machine_can_escalate(self):
        """Test can_escalate method."""
        sm = StateMachine(agent_id="test-agent")
        
        assert sm.can_escalate() is True
        
        sm.transition(Intent.PROPOSE)
        assert sm.can_escalate() is True
        
        sm.transition(Intent.COMMIT)
        assert sm.can_escalate() is True
        
        sm.transition(Intent.DONE)
        assert sm.can_escalate() is False
    
    def test_state_machine_is_complete(self):
        """Test is_complete method."""
        sm = StateMachine(agent_id="test-agent")
        
        assert sm.is_complete() is False
        
        sm.transition(Intent.PROPOSE)
        assert sm.is_complete() is False
        
        sm.transition(Intent.REJECT)
        assert sm.is_complete() is True
        
        # Reset
        sm = StateMachine(agent_id="test-agent")
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.COMMIT)
        sm.transition(Intent.EXECUTE)
        sm.transition(Intent.TIMEOUT)
        assert sm.is_complete() is True
    
    def test_state_machine_full_flow(self):
        """Test full state machine flow."""
        sm = StateMachine(agent_id="test-agent")
        
        # DISCOVER → PROPOSE
        sm.transition(Intent.PROPOSE, {"counterparty": "agent-bob"})
        assert sm.state == State.PROPOSE
        assert sm.counterparty == "agent-bob"
        
        # PROPOSE → COMMIT
        sm.transition(Intent.COMMIT, {"contract": {"max_tokens": 1000}})
        assert sm.state == State.COMMIT
        assert sm.contract == {"max_tokens": 1000}
        
        # COMMIT → EXECUTE
        sm.transition(Intent.EXECUTE)
        assert sm.state == State.EXECUTE
        
        # EXECUTE → VERIFY
        sm.transition(Intent.VERIFY, {"result": {"accuracy": 0.95}})
        assert sm.state == State.VERIFY
        assert sm.result == {"accuracy": 0.95}
        
        # VERIFY → DONE
        sm.transition(Intent.DONE)
        assert sm.state == State.DONE
        assert sm.is_complete() is True
    
    def test_state_machine_multiple_agents(self):
        """Test multiple agents with independent states."""
        sm1 = StateMachine(agent_id="agent-1")
        sm2 = StateMachine(agent_id="agent-2")
        
        sm1.transition(Intent.PROPOSE)
        sm1.transition(Intent.COMMIT)
        
        sm2.transition(Intent.PROPOSE)
        sm2.transition(Intent.REJECT)
        
        assert sm1.state == State.COMMIT
        assert sm2.state == State.REJECT
        assert sm1.agent_id == "agent-1"
        assert sm2.agent_id == "agent-2"
    
    def test_state_machine_timeout_reset(self):
        """Test timeout reset on transition."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        old_last_transition = sm.last_transition
        
        # Wait a bit
        time.sleep(0.1)
        
        sm.transition(Intent.COMMIT)
        assert sm.last_transition > old_last_transition
    
    def test_state_machine_contract_preservation(self):
        """Test contract preservation across transitions."""
        sm = StateMachine(agent_id="test-agent")
        
        contract = {"max_tokens": 1000, "timeout_sec": 30}
        
        sm.transition(Intent.PROPOSE, {"contract": contract})
        assert sm.contract == contract
        
        sm.transition(Intent.COMMIT)
        assert sm.contract == contract
        
        sm.transition(Intent.EXECUTE)
        assert sm.contract == contract
    
    def test_state_machine_result_preservation(self):
        """Test result preservation across transitions."""
        sm = StateMachine(agent_id="test-agent")
        
        sm.transition(Intent.PROPOSE)
        sm.transition(Intent.COMMIT)
        sm.transition(Intent.EXECUTE)
        
        result = {"accuracy": 0.95, "status": "success"}
        sm.transition(Intent.VERIFY, {"result": result})
        assert sm.result == result
        
        sm.transition(Intent.DONE)
        assert sm.result == result
