"""
Conformance tests for Vireo AST.

RFC 2119: MUST pass for any Vireo-compatible implementation.
"""

import pytest


class TestAST:
    """AST conformance tests."""

    def test_agent_ast_structure(self, sample_agent_vireo):
        """MUST: Agent AST has correct structure."""
        # This test assumes we have an AST builder
        # For now, it's a placeholder
        pass

    def test_contract_ast_structure(self, sample_contract_vireo):
        """MUST: Contract AST has correct structure."""
        pass

    def test_ast_validation(self):
        """MUST: AST validation catches semantic errors."""
        pass

    def test_ast_serialization(self):
        """SHOULD: AST can be serialized to JSON."""
        pass