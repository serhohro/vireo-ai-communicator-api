#!/usr/bin/env python3
"""
Conformance Tests: Negotiation

Tests for negotiation and contract functionality.
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from protocol.agents.negotiator_agent import NegotiatorAgent, NegotiatorConfig
from core.protocol import Message, Contract


class TestNegotiatorAgent:
    """Negotiator agent conformance tests."""
    
    @pytest.fixture
    def negotiator(self):
        """Create a negotiator agent for testing."""
        config = NegotiatorConfig(
            name="TestNegotiator",
            min_price=50,
            max_price=500,
            max_rounds=5,
            strategy="collaborative"
        )
        return NegotiatorAgent(config)
    
    def test_negotiator_initialization(self, negotiator):
        """Test negotiator initialization."""
        assert negotiator is not None
        assert negotiator.negotiator_config.min_price == 50
        assert negotiator.negotiator_config.max_price == 500
        assert negotiator.negotiator_config.max_rounds == 5
        assert len(negotiator._negotiations) == 0
        
    def test_validate_proposal(self, negotiator):
        """Test proposal validation."""
        valid_terms = {
            "price": 100,
            "deadline": 30,
            "scope": "Data analysis"
        }
        
        result = negotiator._validate_proposal(valid_terms)
        assert result["valid"] is True
        
        invalid_terms = {
            "price": 100
            # Missing deadline and scope
        }
        
        result = negotiator._validate_proposal(invalid_terms)
        assert result["valid"] is False
        assert len(result["suggestions"]) > 0
        
    def test_validate_proposal_price(self, negotiator):
        """Test proposal price validation."""
        terms = {"price": 30, "deadline": 30, "scope": "test"}
        
        result = negotiator._validate_proposal(terms)
        assert result["valid"] is False
        assert "below minimum" in result["reason"].lower()
        
        terms = {"price": 600, "deadline": 30, "scope": "test"}
        result = negotiator._validate_proposal(terms)
        assert result["valid"] is False
        assert "above maximum" in result["reason"].lower()
        
    def test_evaluate_proposal(self, negotiator):
        """Test proposal evaluation."""
        # Excellent proposal
        terms = {"price": 400, "deadline": 7, "quality": "premium"}
        result = negotiator._evaluate_proposal(terms)
        assert result["accepted"] is True
        assert result["score"] >= 0.8
        
        # Good proposal (counter)
        terms = {"price": 300, "deadline": 14, "quality": "high"}
        result = negotiator._evaluate_proposal(terms)
        assert result["accepted"] is False
        assert result["counter_offer"] is not None
        
        # Poor proposal (counter from scratch)
        terms = {"price": 100, "deadline": 60, "quality": "basic"}
        result = negotiator._evaluate_proposal(terms)
        assert result["accepted"] is False
        assert result["counter_offer"] is not None
        
    def test_generate_counter_offer(self, negotiator):
        """Test counter-offer generation."""
        proposal = {
            "terms": {"price": 100, "deadline": 30, "scope": "test"}
        }
        evaluation = {
            "accepted": False,
            "score": 0.5,
            "reason": "Price too low"
        }
        
        counter = negotiator._generate_counter_offer(proposal, evaluation)
        assert counter is not None
        assert "terms" in counter
        assert "metadata" in counter
        assert counter["terms"]["price"] > 100
        
    def test_handle_propose(self, negotiator):
        """Test handling propose message."""
        message = Message(
            type="propose",
            sender="alice",
            recipient=negotiator.id,
            payload={
                "negotiation_id": "test_neg",
                "proposal": {
                    "terms": {
                        "price": 400,
                        "deadline": 7,
                        "scope": "Test project",
                        "quality": "premium"
                    }
                }
            }
        )
        
        # Should accept excellent proposal
        import asyncio
        response = asyncio.run(negotiator._handle_propose(message))
        assert response is not None
        assert response.type == "accept"
        assert response.payload["accepted"] is True
        
    def test_handle_propose_counter(self, negotiator):
        """Test handling propose with counter-offer."""
        message = Message(
            type="propose",
            sender="alice",
            recipient=negotiator.id,
            payload={
                "negotiation_id": "test_neg2",
                "proposal": {
                    "terms": {
                        "price": 100,
                        "deadline": 30,
                        "scope": "Test project",
                        "quality": "standard"
                    }
                }
            }
        )
        
        import asyncio
        response = asyncio.run(negotiator._handle_propose(message))
        assert response is not None
        assert response.type == "counter"
        assert "counter_offer" in response.payload
        
    def test_handle_counter(self, negotiator):
        """Test handling counter-offer."""
        # Create a negotiation
        negotiation_id = "test_counter_neg"
        negotiator._negotiations[negotiation_id] = {
            "id": negotiation_id,
            "counterparty": "alice",
            "status": "active",
            "round": 1,
            "proposal": {"terms": {"price": 100}},
            "history": [],
            "created_at": datetime.now().isoformat()
        }
        
        message = Message(
            type="counter",
            sender="alice",
            recipient=negotiator.id,
            payload={
                "negotiation_id": negotiation_id,
                "round": 2,
                "proposal": {
                    "terms": {
                        "price": 200,
                        "deadline": 20,
                        "scope": "Updated scope"
                    }
                }
            }
        )
        
        import asyncio
        response = asyncio.run(negotiator._handle_counter(message))
        assert response is not None
        
    def test_handle_accept(self, negotiator):
        """Test handling accept message."""
        negotiation_id = "test_accept_neg"
        negotiator._negotiations[negotiation_id] = {
            "id": negotiation_id,
            "counterparty": "alice",
            "status": "active",
            "round": 3,
            "proposal": {"terms": {"price": 300}},
            "history": [],
            "created_at": datetime.now().isoformat()
        }
        
        message = Message(
            type="accept",
            sender="alice",
            recipient=negotiator.id,
            payload={
                "negotiation_id": negotiation_id,
                "proposal": {
                    "terms": {
                        "price": 300,
                        "deadline": 14,
                        "scope": "Accepted scope"
                    }
                }
            }
        )
        
        import asyncio
        response = asyncio.run(negotiator._handle_accept(message))
        assert response is not None
        assert response.type == "contract_ready"
        assert "contract" in response.payload
        
    def test_create_contract(self, negotiator):
        """Test contract creation."""
        proposal = {
            "terms": {
                "price": 300,
                "deadline": 14,
                "scope": "Data analysis",
                "quality": "premium"
            }
        }
        parties = ["alice", "bob"]
        
        contract = negotiator._create_contract(
            negotiation_id="test_neg",
            proposal=proposal,
            parties=parties
        )
        
        assert contract is not None
        assert len(contract["parties"]) == 2
        assert contract["terms"]["price"] == 300
        assert contract["status"] == "pending"
        assert contract["id"] is not None
        
    def test_strategy_competitive(self, negotiator):
        """Test competitive negotiation strategy."""
        negotiator.negotiator_config.strategy = "competitive"
        
        terms = {"price": 100, "deadline": 30, "scope": "test"}
        counter = negotiator._generate_counter_from_scratch(terms, 0.5)
        
        # Competitive strategy should increase price more
        assert counter["terms"]["price"] > 100
        assert counter["terms"]["price"] > negotiator.negotiator_config.min_price
        
    def test_strategy_collaborative(self, negotiator):
        """Test collaborative negotiation strategy."""
        negotiator.negotiator_config.strategy = "collaborative"
        
        terms = {"price": 100, "deadline": 30, "scope": "test"}
        counter = negotiator._generate_counter_from_scratch(terms, 0.6)
        
        # Collaborative strategy should be more moderate
        assert counter["terms"]["price"] > 100
        assert counter["terms"]["price"] < terms["price"] * 1.2
        
    def test_get_negotiation(self, negotiator):
        """Test getting negotiation details."""
        # Create a negotiation
        negotiator._negotiations["test_get"] = {
            "id": "test_get",
            "status": "active",
            "counterparty": "alice",
            "round": 2
        }
        
        result = negotiator.get_negotiation("test_get")
        assert result is not None
        assert result["status"] == "active"
        
    def test_list_negotiations(self, negotiator):
        """Test listing negotiations."""
        negotiator._negotiations["neg1"] = {"id": "neg1", "status": "active"}
        negotiator._negotiations["neg2"] = {"id": "neg2", "status": "active"}
        
        results = negotiator.list_negotiations()
        assert len(results) == 2
        
    def test_register_template(self, negotiator):
        """Test registering a contract template."""
        template = {
            "price": 100,
            "deadline": 30,
            "scope": "Template scope",
            "quality": "standard"
        }
        
        negotiator.register_template("standard", template)
        assert "standard" in negotiator._templates
        
        retrieved = negotiator.get_template("standard")
        assert retrieved["price"] == 100