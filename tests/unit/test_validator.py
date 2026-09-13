# tests/unit/test_validator.py

import pytest
from core.protocol.validator import Validator
from core.protocol.message import Message

class TestValidator:
    """Тести валідатора повідомлень"""
    
    def test_valid_message(self):
        """Валідне повідомлення"""
        msg = Message(
            type="PROPOSE",
            sender="agent1",
            recipient="agent2",
            payload={"contract_id": "123"}
        )
        assert Validator.validate(msg) is True
    
    def test_missing_sender(self):
        """Відсутній відправник"""
        msg = Message(type="PROPOSE", recipient="agent2")
        with pytest.raises(ValidationError):
            Validator.validate(msg)
    
    def test_missing_recipient(self):
        """Відсутній отримувач"""
        msg = Message(type="PROPOSE", sender="agent1")
        with pytest.raises(ValidationError):
            Validator.validate(msg)
    
    def test_invalid_type(self):
        """Невідомий тип"""
        msg = Message(type="INVALID", sender="a", recipient="b")
        with pytest.raises(ValidationError):
            Validator.validate(msg)
    
    def test_contract_validation(self):
        """Валідація контракту"""
        contract = {
            "id": "123",
            "terms": {"price": 100},
            "deadline": "2026-12-31"
        }
        assert Validator.validate_contract(contract) is True
    
    def test_invalid_contract(self):
        """Невірний контракт"""
        contract = {
            "id": "123",
            # Відсутні terms
        }
        with pytest.raises(ValidationError):
            Validator.validate_contract(contract)
    
    def test_schema_validation(self):
        """Валідація по схемі"""
        msg = Message(
            type="COMMIT",
            sender="alice",
            recipient="bob",
            payload={"signature": "0x1234567890abcdef"}
        )
        assert Validator.validate_schema(msg) is True