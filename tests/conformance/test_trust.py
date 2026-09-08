#!/usr/bin/env python3
"""
Conformance Tests: Trust

Tests for trust and reputation system.
"""

import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.identity.trust_bootstrap import TrustBootstrap, TrustScore
from core.identity.reputation import ReputationSystem, ReputationRecord


class TestTrustBootstrap:
    """Trust bootstrap conformance tests."""
    
    def test_trust_initialization(self):
        """Test trust initialization."""
        trust = TrustBootstrap()
        assert trust is not None
        assert len(trust._witnesses) == 0
        
    def test_add_witness(self):
        """Test adding witnesses."""
        trust = TrustBootstrap()
        
        trust.add_witness("did:vireo:witness1")
        trust.add_witness("did:vireo:witness2")
        
        assert len(trust._witnesses) == 2
        assert "did:vireo:witness1" in trust._witnesses
        assert "did:vireo:witness2" in trust._witnesses
        
    def test_remove_witness(self):
        """Test removing witnesses."""
        trust = TrustBootstrap()
        
        trust.add_witness("did:vireo:witness1")
        trust.add_witness("did:vireo:witness2")
        assert len(trust._witnesses) == 2
        
        trust.remove_witness("did:vireo:witness1")
        assert len(trust._witnesses) == 1
        assert "did:vireo:witness1" not in trust._witnesses
        
    def test_verify_trust(self):
        """Test trust verification."""
        trust = TrustBootstrap()
        
        trust.add_witness("did:vireo:witness1")
        trust.add_witness("did:vireo:witness2")
        
        # Add agent with vouches
        trust.add_agent(
            "did:vireo:agent1",
            vouched_by=["did:vireo:witness1", "did:vireo:witness2"]
        )
        
        assert trust.verify("did:vireo:agent1") is True
        
    def test_verify_trust_insufficient(self):
        """Test trust verification with insufficient vouches."""
        trust = TrustBootstrap(threshold=2)
        
        trust.add_witness("did:vireo:witness1")
        trust.add_witness("did:vireo:witness2")
        trust.add_witness("did:vireo:witness3")
        
        trust.add_agent(
            "did:vireo:agent1",
            vouched_by=["did:vireo:witness1"]
        )
        
        # Not enough vouches
        assert trust.verify("did:vireo:agent1") is False
        
    def test_get_trust_score(self):
        """Test getting trust score."""
        trust = TrustBootstrap()
        
        trust.add_witness("did:vireo:witness1")
        trust.add_witness("did:vireo:witness2")
        
        trust.add_agent(
            "did:vireo:agent1",
            vouched_by=["did:vireo:witness1", "did:vireo:witness2"]
        )
        
        score = trust.get_trust_score("did:vireo:agent1")
        assert score >= 0.5
        
    def test_trust_decay(self):
        """Test trust score decay over time."""
        trust = TrustBootstrap(decay_rate=0.1)
        
        trust.add_witness("did:vireo:witness1")
        trust.add_witness("did:vireo:witness2")
        
        trust.add_agent(
            "did:vireo:agent1",
            vouched_by=["did:vireo:witness1", "did:vireo:witness2"],
            initial_score=1.0
        )
        
        score1 = trust.get_trust_score("did:vireo:agent1")
        
        # Simulate time passing
        time.sleep(0.1)
        score2 = trust.get_trust_score("did:vireo:agent1")
        
        # Score should decrease over time
        assert score2 < score1


class TestReputationSystem:
    """Reputation system conformance tests."""
    
    def test_reputation_initialization(self):
        """Test reputation system initialization."""
        repo = ReputationSystem()
        assert repo is not None
        
    def test_record_interaction(self):
        """Test recording an interaction."""
        repo = ReputationSystem()
        
        repo.record_interaction(
            agent_id="did:vireo:agent1",
            interaction_type="contract_fulfilled",
            outcome="success",
            value=0.9
        )
        
        assert len(repo._records) == 1
        
    def test_get_reputation(self):
        """Test getting reputation score."""
        repo = ReputationSystem()
        
        repo.record_interaction(
            agent_id="did:vireo:agent1",
            interaction_type="contract_fulfilled",
            outcome="success",
            value=0.9
        )
        repo.record_interaction(
            agent_id="did:vireo:agent1",
            interaction_type="contract_fulfilled",
            outcome="success",
            value=0.8
        )
        
        score = repo.get_reputation("did:vireo:agent1")
        assert score > 0.8
        
    def test_reputation_negative(self):
        """Test negative reputation."""
        repo = ReputationSystem()
        
        repo.record_interaction(
            agent_id="did:vireo:agent1",
            interaction_type="contract_fulfilled",
            outcome="failure",
            value=0.0
        )
        
        score = repo.get_reputation("did:vireo:agent1")
        assert score < 0.5
        
    def test_reputation_weighted(self):
        """Test weighted reputation calculation."""
        repo = ReputationSystem()
        
        # Recent interaction (higher weight)
        repo.record_interaction(
            agent_id="did:vireo:agent1",
            interaction_type="contract_fulfilled",
            outcome="success",
            value=0.9
        )
        
        # Old interaction (lower weight)
        old_record = ReputationRecord(
            agent_id="did:vireo:agent1",
            interaction_type="contract_fulfilled",
            outcome="failure",
            value=0.0,
            timestamp=time.time() - 10000
        )
        repo._records.append(old_record)
        
        score = repo.get_reputation("did:vireo:agent1")
        # Should be weighted toward recent success
        assert score > 0.5
        
    def test_reputation_cleanup(self):
        """Test reputation cleanup."""
        repo = ReputationSystem(max_age=1)
        
        repo.record_interaction(
            agent_id="did:vireo:agent1",
            interaction_type="test",
            outcome="success",
            value=0.5
        )
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Cleanup should remove old records
        assert len(repo._records) == 0