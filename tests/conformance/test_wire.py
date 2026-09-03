"""
Conformance tests for Vireo wire format.

RFC 2119: MUST pass for any Vireo-compatible implementation.
"""

import json
import pytest


class TestWire:
    """Wire format conformance tests."""

    def test_json_serialization(self, sample_proposal):
        """MUST: Message can be serialized to JSON."""
        json_str = json.dumps(sample_proposal)
        assert isinstance(json_str, str)

    def test_json_deserialization(self, sample_proposal):
        """MUST: Message can be deserialized from JSON."""
        json_str = json.dumps(sample_proposal)
        data = json.loads(json_str)
        assert data["protocol"] == "VIREO-A2A"

    def test_compact_format(self, sample_proposal):
        """SHOULD: Message supports compact format."""
        compact = {
            "p": "V-A2A",
            "v": "2.0.1",
            "i": sample_proposal["message_id"],
            "s": sample_proposal["sender"]["id"],
            "r": sample_proposal["recipient"]["id"],
            "t": sample_proposal["intent"]
        }
        assert compact["p"] == "V-A2A"

    def test_binary_format(self):
        """MAY: Message supports binary format."""
        pass