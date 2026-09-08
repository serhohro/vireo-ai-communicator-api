#!/usr/bin/env python3
"""
Conformance Tests: Contracts

Tests for smart contract functionality.
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.protocol import Contract, ContractStatus
from core.protocol.contract import ContractManager, ContractValidator
from core.identity import DID


class TestContract:
    """Contract conformance tests."""
    
    def test_contract_creation(self):
        """Test contract creation."""
        contract = Contract(
            parties=["did:vireo:alice", "did:vireo:bob"],
            terms={
                "price": 100,
                "deadline": "2024-12-31",
                "scope": "Data analysis"
            },
            duration_days=30
        )
        
        assert len(contract.parties) == 2
        assert contract.terms["price"] == 100
        assert contract.status == ContractStatus.PENDING
        assert contract.id is not None
        assert contract.created_at is not None
        
    def test_contract_signing(self):
        """Test contract signing."""
        contract = Contract(
            parties=["alice", "bob"],
            terms={"price": 100}
        )
        
        # Sign by alice
        contract.sign("alice", "signature_alice")
        assert "alice" in contract.signatures
        assert contract.signatures["alice"] == "signature_alice"
        
        # Sign by bob
        contract.sign("bob", "signature_bob")
        assert "bob" in contract.signatures
        assert contract.signatures["bob"] == "signature_bob"
        
        # All parties signed
        assert contract.is_fully_signed() is True
        assert contract.status == ContractStatus.ACTIVE
        
    def test_contract_verification(self):
        """Test contract verification."""
        contract = Contract(
            parties=["alice", "bob"],
            terms={"price": 100}
        )
        
        # Add signatures
        contract.sign("alice", "sig_alice")
        contract.sign("bob", "sig_bob")
        
        # Verify signatures
        assert contract.verify_signature("alice", "sig_alice") is True
        assert contract.verify_signature("alice", "wrong_sig") is False
        
    def test_contract_expiration(self):
        """Test contract expiration."""
        contract = Contract(
            parties=["alice", "bob"],
            terms={"price": 100},
            duration_days=1
        )
        
        assert contract.is_expired() is False
        
        # Manually expire
        contract._expires_at = datetime.now() - timedelta(days=1)
        assert contract.is_expired() is True
        assert contract.status == ContractStatus.EXPIRED
        
    def test_contract_serialization(self):
        """Test contract serialization."""
        original = Contract(
            parties=["alice", "bob"],
            terms={"price": 100, "scope": "test"}
        )
        
        json_str = original.to_json()
        restored = Contract.from_json(json_str)
        
        assert restored.parties == original.parties
        assert restored.terms == original.terms
        assert restored.status == original.status


class TestContractManager:
    """Contract manager conformance tests."""
    
    def test_manager_creation(self):
        """Test contract manager creation."""
        manager = ContractManager()
        assert manager is not None
        assert len(manager.list_contracts()) == 0
        
    def test_manager_create_contract(self):
        """Test creating contract via manager."""
        manager = ContractManager()
        
        contract = manager.create_contract(
            parties=["alice", "bob"],
            terms={"price": 100},
            duration_days=30
        )
        
        assert contract.id is not None
        assert len(manager.list_contracts()) == 1
        
    def test_manager_get_contract(self):
        """Test getting contract by ID."""
        manager = ContractManager()
        
        contract = manager.create_contract(
            parties=["alice", "bob"],
            terms={"price": 100}
        )
        
        retrieved = manager.get_contract(contract.id)
        assert retrieved is not None
        assert retrieved.id == contract.id
        
    def test_manager_sign_contract(self):
        """Test signing contract via manager."""
        manager = ContractManager()
        
        contract = manager.create_contract(
            parties=["alice", "bob"],
            terms={"price": 100}
        )
        
        result = manager.sign_contract(contract.id, "alice", "sig_alice")
        assert result is True
        
        contract = manager.get_contract(contract.id)
        assert "alice" in contract.signatures
        
    def test_manager_find_contracts(self):
        """Test finding contracts."""
        manager = ContractManager()
        
        # Create multiple contracts
        manager.create_contract(
            parties=["alice", "bob"],
            terms={"price": 100}
        )
        manager.create_contract(
            parties=["alice", "charlie"],
            terms={"price": 200}
        )
        manager.create_contract(
            parties=["bob", "charlie"],
            terms={"price": 150}
        )
        
        # Find by party
        contracts = manager.find_contracts(party="alice")
        assert len(contracts) == 2
        
        # Find by status
        contracts = manager.find_contracts(status=ContractStatus.PENDING)
        assert len(contracts) == 3


class TestContractValidator:
    """Contract validator conformance tests."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = ContractValidator()
        assert validator is not None
        
    def test_validator_valid_contract(self):
        """Test validating a valid contract."""
        validator = ContractValidator()
        contract = Contract(
            parties=["alice", "bob"],
            terms={"price": 100, "deadline": "2024-12-31"}
        )
        
        result = validator.validate(contract)
        assert result.is_valid is True
        
    def test_validator_missing_parties(self):
        """Test validating contract with missing parties."""
        validator = ContractValidator()
        contract = Contract(
            parties=[],
            terms={"price": 100}
        )
        
        result = validator.validate(contract)
        assert result.is_valid is False
        assert "parties" in result.errors[0].lower()
        
    def test_validator_missing_terms(self):
        """Test validating contract with missing terms."""
        validator = ContractValidator()
        contract = Contract(
            parties=["alice", "bob"],
            terms={}
        )
        
        result = validator.validate(contract)
        assert result.is_valid is False
        assert "terms" in result.errors[0].lower()
        
    def test_validator_invalid_duration(self):
        """Test validating contract with invalid duration."""
        validator = ContractValidator()
        contract = Contract(
            parties=["alice", "bob"],
            terms={"price": 100},
            duration_days=0
        )
        
        result = validator.validate(contract)
        assert result.is_valid is False
        assert "duration" in result.errors[0].lower()