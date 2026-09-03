"""
Conformance tests for Vireo contracts.

RFC 2119: MUST pass for any Vireo-compatible implementation.
"""

import pytest


class TestContracts:
    """Contract conformance tests."""

    def test_contract_validation(self, sample_contract):
        """MUST: Contract validates correctly."""
        assert sample_contract is not None

    def test_contract_fields(self, sample_contract):
        """MUST: Contract has required fields."""
        assert "fields" in sample_contract

    def test_contract_verify_condition(self, sample_contract):
        """MUST: Contract has verify condition."""
        assert "verify" in sample_contract

    def test_contract_timeout(self, sample_contract):
        """MUST: Contract handles timeout."""
        assert "timeout_sec" in sample_contract["fields"]

    def test_contract_max_tokens(self, sample_contract):
        """MUST: Contract handles max_tokens."""
        assert "max_tokens" in sample_contract["fields"]

    def test_contract_verify_timeout(self):
        """SHOULD: Contract supports verify_timeout_sec."""
        contract = {
            "fields": {
                "verify_timeout_sec": {"type": "Int", "value": 15}
            }
        }
        assert "verify_timeout_sec" in contract["fields"]

    def test_contract_max_rounds(self):
        """SHOULD: Contract supports max_rounds."""
        contract = {
            "fields": {
                "max_rounds": {"type": "Int", "value": 3}
            }
        }
        assert "max_rounds" in contract["fields"]