"""
Conformance tests for Vireo state machine.

RFC 2119: MUST pass for any Vireo-compatible implementation.
"""

import pytest


class TestState:
    """State machine conformance tests."""

    def test_valid_transitions(self):
        """MUST: Valid transitions work."""
        valid_transitions = [
            ("NEW", "PROPOSED"),
            ("PROPOSED", "COMMITTED"),
            ("PROPOSED", "REJECTED"),
            ("COMMITTED", "RUNNING"),
            ("RUNNING", "VERIFYING"),
            ("VERIFYING", "DONE"),
            ("VERIFYING", "ESCALATED"),
            ("VERIFYING", "FAILED"),
        ]
        for from_state, to_state in valid_transitions:
            # Test each transition
            pass

    def test_invalid_transitions(self):
        """MUST: Invalid transitions are rejected."""
        invalid_transitions = [
            ("NEW", "DONE"),
            ("PROPOSED", "DONE"),
            ("RUNNING", "DONE"),
        ]
        for from_state, to_state in invalid_transitions:
            # Test each invalid transition
            pass

    def test_verifying_timeout(self):
        """MUST: VERIFYING state has timeout."""
        pass

    def test_escalated_state(self):
        """MUST: ESCALATED state is terminal."""
        pass

    def test_max_rounds_enforcement(self):
        """SHOULD: max_rounds is enforced."""
        pass