"""
Conformance tests for Vireo capabilities.

RFC 2119: MUST pass for any Vireo-compatible implementation.
"""

import pytest


class TestCapabilities:
    """Capability conformance tests."""

    def test_capability_definition(self, sample_agent):
        """MUST: Capability is defined in agent."""
        assert "capabilities" in sample_agent

    def test_capability_discovery(self):
        """MUST: Agents can discover capabilities."""
        pass

    def test_capability_query(self):
        """MUST: QUERY_CAPABILITIES intent exists."""
        pass

    def test_capability_inform(self):
        """MUST: INFORM_CAPABILITIES intent exists."""
        pass

    def test_capability_filtering(self):
        """SHOULD: Capabilities can be filtered."""
        pass