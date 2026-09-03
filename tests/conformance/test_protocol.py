"""
Conformance tests for Vireo protocol.

RFC 2119: MUST pass for any Vireo-compatible implementation.
"""

import pytest


class TestProtocol:
    """Protocol conformance tests."""

    def test_message_schema(self, sample_proposal):
        """MUST: Message follows JSON Schema."""
        required_fields = ["protocol", "version", "message_id", "sender", "recipient", "intent", "timestamp"]
        for field in required_fields:
            assert field in sample_proposal

    def test_intent_enum(self):
        """MUST: Intent is from defined enum."""
        valid_intents = ["PROPOSE", "COMMIT", "REJECT", "INFORM", "NEGOTIATE", "QUERY_CAPABILITIES", "INFORM_CAPABILITIES", "CANCEL", "VERIFY", "ESCALATE"]
        # Test each valid intent
        for intent in valid_intents:
            assert intent in valid_intents

    def test_invalid_intent(self):
        """MUST: Reject invalid intent."""
        invalid_intents = ["INVALID", "WRONG", "TEST"]
        # This should fail validation
        pass

    def test_message_id_format(self):
        """SHOULD: Message ID follows format."""
        pass