"""
Pytest configuration for conformance tests.
"""

import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_contract():
    """Sample contract for testing."""
    return {
        "name": "TestContract",
        "fields": {
            "max_tokens": {"type": "Int", "value": 1000},
            "timeout_sec": {"type": "Int", "value": 30}
        },
        "verify": "result.accuracy > 0.9"
    }


@pytest.fixture
def sample_agent():
    """Sample agent for testing."""
    return {
        "name": "TestAgent",
        "capabilities": ["test_capability"],
        "role": "test"
    }


@pytest.fixture
def sample_proposal():
    """Sample proposal for testing."""
    return {
        "protocol": "VIREO-A2A",
        "version": "2.0.1",
        "message_id": "msg-test-001",
        "conversation_id": "conv-test-001",
        "sender": {"id": "agent-a"},
        "recipient": {"id": "agent-b"},
        "intent": "PROPOSE",
        "payload": {"code": "let x = 5", "task": "test task"},
        "timestamp": 1234567890
    }


@pytest.fixture
def sample_contract_vireo():
    """Sample Vireo contract code."""
    return """
contract TestContract {
    max_tokens: Int = 1000
    timeout_sec: Int = 30
    verify { result.accuracy > 0.9 }
}
"""


@pytest.fixture
def sample_agent_vireo():
    """Sample Vireo agent code."""
    return """
agent TestAgent {
    capability test_capability
    role test
}
"""


@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "data"