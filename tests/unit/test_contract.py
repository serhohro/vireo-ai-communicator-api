# Vireo v3.0.0 — Contract Unit Tests

import pytest
import json
from core.types import Contract


class TestContract:
    """Unit tests for Contract."""
    
    def test_contract_creation(self):
        """Test contract creation."""
        contract = Contract(
            name="TestContract",
            version="3.0.0",
            terms={
                "max_tokens": 1000,
                "timeout_sec": 30,
                "verify_timeout_sec": 15,
                "max_rounds": 3
            },
            conditions=[
                {"type": "balance", "min": 1000},
                {"type": "capability", "requires": ["chat", "execute"]}
            ],
            obligations=[
                {"action": "execute_task", "deadline": "2026-09-10T00:00:00Z"}
            ],
            penalties=[
                {"type": "fine", "amount": 100}
            ]
        )
        
        assert contract.name == "TestContract"
        assert contract.version == "3.0.0"
        assert contract.terms["max_tokens"] == 1000
        assert contract.terms["timeout_sec"] == 30
        assert len(contract.conditions) == 2
        assert len(contract.obligations) == 1
        assert len(contract.penalties) == 1
    
    def test_contract_validation_valid(self):
        """Test contract validation with valid contract."""
        contract = Contract(
            name="ValidContract",
            version="3.0.0",
            terms={"max_tokens": 1000},
            conditions=[{"type": "test"}],
            obligations=[{"action": "test"}],
            penalties=[{"type": "test"}]
        )
        
        assert contract.validate() is True
    
    def test_contract_validation_empty_name(self):
        """Test contract validation with empty name."""
        contract = Contract(
            name="",
            version="3.0.0",
            terms={"max_tokens": 1000},
            conditions=[],
            obligations=[],
            penalties=[]
        )
        
        assert contract.validate() is False
    
    def test_contract_validation_empty_version(self):
        """Test contract validation with empty version."""
        contract = Contract(
            name="TestContract",
            version="",
            terms={"max_tokens": 1000},
            conditions=[],
            obligations=[],
            penalties=[]
        )
        
        assert contract.validate() is False
    
    def test_contract_validation_empty_terms(self):
        """Test contract validation with empty terms."""
        contract = Contract(
            name="TestContract",
            version="3.0.0",
            terms={},
            conditions=[],
            obligations=[],
            penalties=[]
        )
        
        assert contract.validate() is False
    
    def test_contract_validation_null_conditions(self):
        """Test contract validation with null conditions."""
        contract = Contract(
            name="TestContract",
            version="3.0.0",
            terms={"max_tokens": 1000},
            conditions=None,
            obligations=[],
            penalties=[]
        )
        
        assert contract.validate() is False
    
    def test_contract_terms_access(self):
        """Test contract terms access."""
        contract = Contract(
            name="TestContract",
            version="3.0.0",
            terms={"max_tokens": 1000, "timeout_sec": 30},
            conditions=[],
            obligations=[],
            penalties=[]
        )
        
        assert contract.terms.get("max_tokens") == 1000
        assert contract.terms.get("timeout_sec") == 30
        assert contract.terms.get("nonexistent") is None
    
    def test_contract_conditions(self):
        """Test contract conditions."""
        contract = Contract(
            name="TestContract",
            version="3.0.0",
            terms={"max_tokens": 1000},
            conditions=[
                {"type": "balance", "min": 1000},
                {"type": "capability", "requires": ["chat"]}
            ],
            obligations=[],
            penalties=[]
        )
        
        assert len(contract.conditions) == 2
        assert contract.conditions[0]["type"] == "balance"
        assert contract.conditions[0]["min"] == 1000
        assert contract.conditions[1]["type"] == "capability"
        assert "chat" in contract.conditions[1]["requires"]
    
    def test_contract_obligations(self):
        """Test contract obligations."""
        contract = Contract(
            name="TestContract",
            version="3.0.0",
            terms={"max_tokens": 1000},
            conditions=[],
            obligations=[
                {"action": "execute_task", "deadline": "2026-09-10T00:00:00Z"},
                {"action": "verify_result", "deadline": "2026-09-11T00:00:00Z"}
            ],
            penalties=[]
        )
        
        assert len(contract.obligations) == 2
        assert contract.obligations[0]["action"] == "execute_task"
        assert contract.obligations[1]["action"] == "verify_result"
    
    def test_contract_penalties(self):
        """Test contract penalties."""
        contract = Contract(
            name="TestContract",
            version="3.0.0",
            terms={"max_tokens": 1000},
            conditions=[],
            obligations=[],
            penalties=[
                {"type": "fine", "amount": 100},
                {"type": "reputation", "deduction": 10}
            ]
        )
        
        assert len(contract.penalties) == 2
        assert contract.penalties[0]["type"] == "fine"
        assert contract.penalties[0]["amount"] == 100
        assert contract.penalties[1]["type"] == "reputation"
    
    def test_contract_serialization(self):
        """Test contract serialization to dict."""
        contract = Contract(
            name="TestContract",
            version="3.0.0",
            terms={"max_tokens": 1000},
            conditions=[{"type": "test"}],
            obligations=[{"action": "test"}],
            penalties=[{"type": "test"}]
        )
        
        # Convert to dict manually (dataclass already has it)
        data = {
            "name": contract.name,
            "version": contract.version,
            "terms": contract.terms,
            "conditions": contract.conditions,
            "obligations": contract.obligations,
            "penalties": contract.penalties
        }
        
        assert data["name"] == "TestContract"
        assert data["version"] == "3.0.0"
        assert data["terms"]["max_tokens"] == 1000
    
    def test_contract_to_json(self):
        """Test contract serialization to JSON."""
        import json
        contract = Contract(
            name="TestContract",
            version="3.0.0",
            terms={"max_tokens": 1000},
            conditions=[{"type": "test"}],
            obligations=[{"action": "test"}],
            penalties=[{"type": "test"}]
        )
        
        data = {
            "name": contract.name,
            "version": contract.version,
            "terms": contract.terms,
            "conditions": contract.conditions,
            "obligations": contract.obligations,
            "penalties": contract.penalties
        }
        
        json_str = json.dumps(data)
        assert isinstance(json_str, str)
        
        # Deserialize
        parsed = json.loads(json_str)
        assert parsed["name"] == "TestContract"
        assert parsed["terms"]["max_tokens"] == 1000
    
    def test_contract_from_dict(self):
        """Test contract creation from dict."""
        data = {
            "name": "TestContract",
            "version": "3.0.0",
            "terms": {"max_tokens": 1000},
            "conditions": [{"type": "test"}],
            "obligations": [{"action": "test"}],
            "penalties": [{"type": "test"}]
        }
        
        contract = Contract(
            name=data["name"],
            version=data["version"],
            terms=data["terms"],
            conditions=data["conditions"],
            obligations=data["obligations"],
            penalties=data["penalties"]
        )
        
        assert contract.name == "TestContract"
        assert contract.version == "3.0.0"
        assert contract.terms["max_tokens"] == 1000
    
    def test_contract_with_complex_terms(self):
        """Test contract with complex terms."""
        contract = Contract(
            name="ComplexContract",
            version="3.0.0",
            terms={
                "max_tokens": 2000,
                "timeout_sec": 60,
                "verify_timeout_sec": 30,
                "max_rounds": 5,
                "budget": 1000.50,
                "priority": "high"
            },
            conditions=[
                {"type": "balance", "min": 5000},
                {"type": "capability", "requires": ["chat", "execute", "verify"]}
            ],
            obligations=[
                {"action": "execute_task", "deadline": "2026-09-10T00:00:00Z"},
                {"action": "submit_report", "deadline": "2026-09-11T00:00:00Z"}
            ],
            penalties=[
                {"type": "fine", "amount": 500},
                {"type": "reputation", "deduction": 20}
            ]
        )
        
        assert contract.name == "ComplexContract"
        assert contract.terms["max_tokens"] == 2000
        assert contract.terms["timeout_sec"] == 60
        assert contract.terms["budget"] == 1000.50
        assert len(contract.conditions) == 2
        assert len(contract.obligations) == 2
        assert len(contract.penalties) == 2
    
    def test_contract_minimal(self):
        """Test contract with minimal required fields."""
        contract = Contract(
            name="MinimalContract",
            version="1.0.0",
            terms={"key": "value"},
            conditions=[],
            obligations=[],
            penalties=[]
        )
        
        assert contract.validate() is True
        assert contract.name == "MinimalContract"
        assert contract.terms["key"] == "value"
