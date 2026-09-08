# Vireo v3.0.0 — Agent Unit Tests

import pytest
import time
import uuid
from core.crypto.ed25519 import generate_keypair
from core.protocol.message import Message, Intent
from protocol.agent import Agent


class TestAgent:
    """Unit tests for Agent."""
    
    def test_agent_creation(self):
        """Test agent creation."""
        private_key, public_key = generate_keypair()
        agent = Agent(
            agent_id="test-agent-001",
            private_key=private_key,
            public_key=public_key,
            name="TestAgent",
            capabilities=["chat", "execute", "verify"]
        )
        
        assert agent.id == "test-agent-001"
        assert agent.did == "did:vireo:agent:test-agent-001"
        assert agent.name == "TestAgent"
        assert agent.capabilities == ["chat", "execute", "verify"]
        assert agent.get_state() == "DISCOVER"
        assert agent.is_complete() is False
    
    def test_agent_propose(self):
        """Test agent propose method."""
        private_key, public_key = generate_keypair()
        agent = Agent(
            agent_id="agent-alice",
            private_key=private_key,
            public_key=public_key,
            capabilities=["chat", "execute"]
        )
        
        contract = {
            "name": "TestContract",
            "terms": {"max_tokens": 1000, "timeout_sec": 30}
        }
        
        msg = agent.propose("agent-bob", contract)
        
        assert msg.intent == Intent.PROPOSE
        assert msg.sender == "did:vireo:agent:agent-alice"
        assert msg.recipient == "did:vireo:agent:agent-bob"
        assert msg.proposal_id.startswith("prop_agent-alice_")
        assert msg.payload == contract
        
        # Verify signature
        assert msg.verify(public_key)
        assert agent.get_state() == "PROPOSE"
    
    def test_agent_commit(self):
        """Test agent commit method."""
        private_key, public_key = generate_keypair()
        agent = Agent(
            agent_id="agent-alice",
            private_key=private_key,
            public_key=public_key
        )
        
        proposal_id = "prop_test_001"
        msg = agent.commit("agent-bob", proposal_id)
        
        assert msg.intent == Intent.COMMIT
        assert msg.sender == "did:vireo:agent:agent-alice"
        assert msg.recipient == "did:vireo:agent:agent-bob"
        assert msg.proposal_id == proposal_id
        assert msg.verify(public_key)
    
    def test_agent_execute(self):
        """Test agent execute method."""
        private_key, public_key = generate_keypair()
        agent = Agent(
            agent_id="agent-alice",
            private_key=private_key,
            public_key=public_key
        )
        
        proposal_id = "prop_test_001"
        msg = agent.execute("agent-bob", proposal_id)
        
        assert msg.intent == Intent.EXECUTE
        assert msg.sender == "did:vireo:agent:agent-alice"
        assert msg.recipient == "did:vireo:agent:agent-bob"
        assert msg.proposal_id == proposal_id
        assert msg.verify(public_key)
    
    def test_agent_verify(self):
        """Test agent verify method."""
        private_key, public_key = generate_keypair()
        agent = Agent(
            agent_id="agent-alice",
            private_key=private_key,
            public_key=public_key
        )
        
        proposal_id = "prop_test_001"
        result = {"status": "success", "accuracy": 0.95}
        msg = agent.verify("agent-bob", proposal_id, result)
        
        assert msg.intent == Intent.VERIFY
        assert msg.sender == "did:vireo:agent:agent-alice"
        assert msg.recipient == "did:vireo:agent:agent-bob"
        assert msg.proposal_id == proposal_id
        assert msg.payload == result
        assert msg.verify(public_key)
    
    def test_agent_done(self):
        """Test agent done method."""
        private_key, public_key = generate_keypair()
        agent = Agent(
            agent_id="agent-alice",
            private_key=private_key,
            public_key=public_key
        )
        
        proposal_id = "prop_test_001"
        msg = agent.done("agent-bob", proposal_id)
        
        assert msg.intent == Intent.DONE
        assert msg.sender == "did:vireo:agent:agent-alice"
        assert msg.recipient == "did:vireo:agent:agent-bob"
        assert msg.proposal_id == proposal_id
        assert msg.verify(public_key)
    
    def test_agent_escalate(self):
        """Test agent escalate method."""
        private_key, public_key = generate_keypair()
        agent = Agent(
            agent_id="agent-alice",
            private_key=private_key,
            public_key=public_key
        )
        
        proposal_id = "prop_test_001"
        reason = "Verification failed"
        msg = agent.escalate("agent-bob", proposal_id, reason)
        
        assert msg.intent == Intent.ESCALATE
        assert msg.sender == "did:vireo:agent:agent-alice"
        assert msg.recipient == "did:vireo:agent:agent-bob"
        assert msg.proposal_id == proposal_id
        assert msg.payload == {"reason": reason}
        assert msg.verify(public_key)
    
    def test_agent_receive_propose(self):
        """Test agent receiving PROPOSE message."""
        private_key_alice, public_key_alice = generate_keypair()
        private_key_bob, public_key_bob = generate_keypair()
        
        alice = Agent(
            agent_id="agent-alice",
            private_key=private_key_alice,
            public_key=public_key_alice,
            capabilities=["chat", "execute"]
        )
        
        bob = Agent(
            agent_id="agent-bob",
            private_key=private_key_bob,
            public_key=public_key_bob,
            capabilities=["chat", "execute"]
        )
        
        # Bob proposes to Alice
        contract = {"terms": {"max_tokens": 1000}}
        propose_msg = bob.propose("agent-alice", contract)
        
        # Alice receives proposal
        response = alice.receive(propose_msg)
        
        assert response is not None
        assert response.intent == Intent.COMMIT
        assert response.recipient == bob.did
        assert response.proposal_id == propose_msg.proposal_id
    
    def test_agent_receive_commit(self):
        """Test agent receiving COMMIT message."""
        private_key_alice, public_key_alice = generate_keypair()
        private_key_bob, public_key_bob = generate_keypair()
        
        alice = Agent(
            agent_id="agent-alice",
            private_key=private_key_alice,
            public_key=public_key_alice,
            capabilities=["chat", "execute"]
        )
        
        bob = Agent(
            agent_id="agent-bob",
            private_key=private_key_bob,
            public_key=public_key_bob,
            capabilities=["chat", "execute"]
        )
        
        # Alice proposes to Bob
        contract = {"terms": {"max_tokens": 1000}}
        propose_msg = alice.propose("agent-bob", contract)
        
        # Bob receives and commits
        commit_response = bob.receive(propose_msg)
        
        # Alice receives commit
        response = alice.receive(commit_response)
        
        assert response is not None
        assert response.intent == Intent.EXECUTE
        assert response.recipient == bob.did
        assert response.proposal_id == propose_msg.proposal_id
    
    def test_agent_receive_execute(self):
        """Test agent receiving EXECUTE message."""
        private_key_alice, public_key_alice = generate_keypair()
        private_key_bob, public_key_bob = generate_keypair()
        
        alice = Agent(
            agent_id="agent-alice",
            private_key=private_key_alice,
            public_key=public_key_alice,
            capabilities=["chat", "execute"]
        )
        
        bob = Agent(
            agent_id="agent-bob",
            private_key=private_key_bob,
            public_key=public_key_bob,
            capabilities=["chat", "execute"]
        )
        
        # Full negotiation flow
        propose_msg = alice.propose("agent-bob", {"terms": {"max_tokens": 1000}})
        commit_msg = bob.receive(propose_msg)
        execute_msg = alice.receive(commit_msg)
        
        # Bob receives execute
        response = bob.receive(execute_msg)
        
        assert response is not None
        assert response.intent == Intent.VERIFY
        assert response.recipient == alice.did
        assert response.proposal_id == propose_msg.proposal_id
    
    def test_agent_receive_verify(self):
        """Test agent receiving VERIFY message."""
        private_key_alice, public_key_alice = generate_keypair()
        private_key_bob, public_key_bob = generate_keypair()
        
        alice = Agent(
            agent_id="agent-alice",
            private_key=private_key_alice,
            public_key=public_key_alice,
            capabilities=["chat", "execute"]
        )
        
        bob = Agent(
            agent_id="agent-bob",
            private_key=private_key_bob,
            public_key=public_key_bob,
            capabilities=["chat", "execute"]
        )
        
        # Full negotiation flow
        propose_msg = alice.propose("agent-bob", {"terms": {"max_tokens": 1000}})
        commit_msg = bob.receive(propose_msg)
        execute_msg = alice.receive(commit_msg)
        verify_msg = bob.receive(execute_msg)
        
        # Alice receives verify
        response = alice.receive(verify_msg)
        
        assert response is not None
        assert response.intent == Intent.DONE
        assert response.recipient == bob.did
        assert response.proposal_id == propose_msg.proposal_id
    
    def test_agent_receive_done(self):
        """Test agent receiving DONE message."""
        private_key_alice, public_key_alice = generate_keypair()
        private_key_bob, public_key_bob = generate_keypair()
        
        alice = Agent(
            agent_id="agent-alice",
            private_key=private_key_alice,
            public_key=public_key_alice,
            capabilities=["chat", "execute"]
        )
        
        bob = Agent(
            agent_id="agent-bob",
            private_key=private_key_bob,
            public_key=public_key_bob,
            capabilities=["chat", "execute"]
        )
        
        # Full negotiation flow
        propose_msg = alice.propose("agent-bob", {"terms": {"max_tokens": 1000}})
        commit_msg = bob.receive(propose_msg)
        execute_msg = alice.receive(commit_msg)
        verify_msg = bob.receive(execute_msg)
        done_msg = alice.receive(verify_msg)
        
        # Bob receives done
        response = bob.receive(done_msg)
        
        assert response is None  # Done is terminal, no response
    
    def test_agent_reject_proposal(self):
        """Test agent rejecting a proposal."""
        private_key_alice, public_key_alice = generate_keypair()
        private_key_bob, public_key_bob = generate_keypair()
        
        alice = Agent(
            agent_id="agent-alice",
            private_key=private_key_alice,
            public_key=public_key_alice,
            capabilities=["chat"]  # No execute capability
        )
        
        bob = Agent(
            agent_id="agent-bob",
            private_key=private_key_bob,
            public_key=public_key_bob,
            capabilities=["chat", "execute"]
        )
        
        # Bob proposes with capability Alice doesn't have
        contract = {"capabilities": ["execute"]}
        propose_msg = bob.propose("agent-alice", contract)
        
        # Alice receives and rejects
        response = alice.receive(propose_msg)
        
        assert response is not None
        assert response.intent == Intent.REJECT
        assert response.recipient == bob.did
        assert response.proposal_id == propose_msg.proposal_id
    
    def test_agent_invalid_signature(self):
        """Test agent rejects message with invalid signature."""
        private_key_alice, public_key_alice = generate_keypair()
        private_key_bob, public_key_bob = generate_keypair()
        
        alice = Agent(
            agent_id="agent-alice",
            private_key=private_key_alice,
            public_key=public_key_alice
        )
        
        # Create message with wrong signature
        msg = Message.create(
            sender="did:vireo:agent:bob",
            recipient="did:vireo:agent:alice",
            intent=Intent.PROPOSE,
            proposal_id="prop_test",
            payload={"hello": "world"}
        )
        # Sign with Alice's key instead of Bob's
        msg.sign(private_key_alice)
        
        # Alice should reject
        with pytest.raises(Exception):
            alice.receive(msg)
    
    def test_agent_idempotency(self):
        """Test agent idempotency."""
        private_key_alice, public_key_alice = generate_keypair()
        private_key_bob, public_key_bob = generate_keypair()
        
        alice = Agent(
            agent_id="agent-alice",
            private_key=private_key_alice,
            public_key=public_key_alice,
            capabilities=["chat", "execute"]
        )
        
        bob = Agent(
            agent_id="agent-bob",
            private_key=private_key_bob,
            public_key=public_key_bob,
            capabilities=["chat", "execute"]
        )
        
        # Complete a transaction
        propose_msg = alice.propose("agent-bob", {"terms": {"max_tokens": 1000}})
        commit_msg = bob.receive(propose_msg)
        execute_msg = alice.receive(commit_msg)
        verify_msg = bob.receive(execute_msg)
        done_msg = alice.receive(verify_msg)
        bob.receive(done_msg)
        
        # Try to process the same commit again
        response = bob.receive(commit_msg)  # Same commit message
        
        # Should be idempotent - no response
        assert response is None
    
    def test_agent_state_transitions(self):
        """Test agent state machine transitions."""
        private_key, public_key = generate_keypair()
        agent = Agent(
            agent_id="agent-alice",
            private_key=private_key,
            public_key=public_key,
            capabilities=["chat", "execute"]
        )
        
        # Initial state
        assert agent.get_state() == "DISCOVER"
        
        # PROPOSE
        agent.propose("agent-bob", {})
        assert agent.get_state() == "PROPOSE"
        
        # COMMIT
        agent.commit("agent-bob", "prop_001")
        assert agent.get_state() == "COMMIT"
        
        # EXECUTE
        agent.execute("agent-bob", "prop_001")
        assert agent.get_state() == "EXECUTE"
        
        # VERIFY
        agent.verify("agent-bob", "prop_001", {})
        assert agent.get_state() == "VERIFY"
        
        # DONE
        agent.done("agent-bob", "prop_001")
        assert agent.get_state() == "DONE"
        assert agent.is_complete() is True
    
    def test_agent_escalate_flow(self):
        """Test agent escalation flow."""
        private_key_alice, public_key_alice = generate_keypair()
        private_key_bob, public_key_bob = generate_keypair()
        
        alice = Agent(
            agent_id="agent-alice",
            private_key=private_key_alice,
            public_key=public_key_alice
        )
        
        bob = Agent(
            agent_id="agent-bob",
            private_key=private_key_bob,
            public_key=public_key_bob
        )
        
        # Create a transaction
        propose_msg = alice.propose("agent-bob", {"terms": {"max_tokens": 1000}})
        commit_msg = bob.receive(propose_msg)
        execute_msg = alice.receive(commit_msg)
        
        # Bob fails verification
        verify_msg = bob.receive(execute_msg)
        
        # Alice receives verify failure
        response = alice.receive(verify_msg)
        
        assert response is not None
        assert response.intent == Intent.ESCALATE
        assert response.recipient == bob.did
        assert "reason" in response.payload
