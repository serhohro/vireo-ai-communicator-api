"""
Conformance tests for Vireo parser.

RFC 2119: MUST pass for any Vireo-compatible implementation.
"""

import pytest
from lark import Lark
from pathlib import Path


class TestParser:
    """Parser conformance tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load grammar."""
        grammar_path = Path(__file__).parent.parent.parent / "language" / "grammar.lark"
        if grammar_path.exists():
            self.parser = Lark(grammar_path.read_text(), parser="lalr", start="program")
        else:
            pytest.skip("Grammar file not found")

    def test_parse_agent(self):
        """MUST: Parse agent definition."""
        code = """
agent TestAgent {
    capability test
    role test
}
"""
        result = self.parser.parse(code)
        assert result is not None

    def test_parse_contract(self):
        """MUST: Parse contract definition."""
        code = """
contract TestContract {
    max_tokens: Int = 1000
    verify { result.accuracy > 0.9 }
}
"""
        result = self.parser.parse(code)
        assert result is not None

    def test_parse_negotiation(self):
        """MUST: Parse negotiation."""
        code = """
negotiate AgentA -> AgentB {
    propose "Test task"
    commit "Commit task"
    execute "Execute task"
    verify "Verify result"
    inform "Result done"
}
"""
        result = self.parser.parse(code)
        assert result is not None

    def test_parse_invalid_syntax(self):
        """MUST: Reject invalid syntax."""
        invalid_code = """
agent TestAgent {
    capability test
    role test
    invalid syntax here
}
"""
        with pytest.raises(Exception):
            self.parser.parse(invalid_code)

    def test_parse_empty_program(self):
        """SHOULD: Handle empty program."""
        result = self.parser.parse("")
        assert result is not None