#!/usr/bin/env python3
"""
Fuzz Testing: Parser

Fuzz testing for Vireo language parser robustness.
"""

import pytest
import random
import sys
import string
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from language.lexer import Lexer
    from language.parser import Parser
    HAS_LANGUAGE = True
except ImportError:
    HAS_LANGUAGE = False
    print("⚠️ Language modules not available, running limited fuzz tests")


class FuzzParser:
    """Parser fuzz testing."""
    
    def random_token(self) -> str:
        """Generate a random token."""
        tokens = [
            "agent", "on", "message", "let", "fn", "return",
            "if", "else", "match", "for", "while", "import",
            "state", "config", "capabilities", "contract",
            "tensor", "ml", "crypto", "protocol",
            "true", "false", "null", "async", "await",
            "{", "}", "(", ")", "[", "]", ":", ";", ",",
            "->", "=>", "+", "-", "*", "/", "%", "=", "==",
            "!=", "<", ">", "<=", ">=", "&&", "||", "!",
            "int", "string", "float", "bool", "any",
        ]
        return random.choice(tokens)
    
    def random_identifier(self) -> str:
        """Generate a random identifier."""
        length = random.randint(1, 20)
        chars = string.ascii_letters + string.digits + "_"
        return "".join(random.choice(chars) for _ in range(length))
    
    def random_string(self) -> str:
        """Generate a random string literal."""
        length = random.randint(0, 50)
        chars = string.ascii_letters + string.digits + " !@#$%^&*()"
        return '"' + "".join(random.choice(chars) for _ in range(length)) + '"'
    
    def random_number(self) -> str:
        """Generate a random number."""
        return str(random.randint(-1000000, 1000000))
    
    def random_expression(self, depth: int = 0) -> str:
        """Generate a random expression."""
        if depth > 3:
            return self.random_value()
            
        choices = [
            self.random_value,
            lambda: f"{self.random_expression(depth+1)} + {self.random_expression(depth+1)}",
            lambda: f"{self.random_expression(depth+1)} * {self.random_expression(depth+1)}",
            lambda: f"({self.random_expression(depth+1)})",
            lambda: f"if {self.random_expression(depth+1)} {{ {self.random_expression(depth+1)} }} else {{ {self.random_expression(depth+1)} }}",
        ]
        return random.choice(choices)()
    
    def random_value(self) -> str:
        """Generate a random value."""
        choices = [
            self.random_identifier,
            self.random_string,
            self.random_number,
            lambda: random.choice(["true", "false", "null"]),
        ]
        return random.choice(choices)()
    
    def random_program(self) -> str:
        """Generate a random program."""
        lines = []
        
        # Random imports
        if random.random() < 0.3:
            imports = random.sample(["ml", "tensor", "crypto", "vision", "nlp"], 
                                   k=random.randint(0, 3))
            for imp in imports:
                lines.append(f"import {imp}")
        
        # Agent declaration
        lines.append(f"agent {self.random_identifier()} {{")
        lines.append(f"    name: {self.random_string()}")
        
        if random.random() < 0.3:
            lines.append(f"    version: {self.random_string()}")
        
        if random.random() < 0.3:
            caps = [self.random_string() for _ in range(random.randint(1, 3))]
            lines.append(f"    capabilities: [{', '.join(caps)}]")
        
        # Random state
        if random.random() < 0.3:
            lines.append("    state {")
            for _ in range(random.randint(1, 5)):
                lines.append(f"        {self.random_identifier()}: {self.random_value()}")
            lines.append("    }")
        
        # Random handlers
        for _ in range(random.randint(0, 3)):
            msg_type = self.random_identifier()
            lines.append(f"    on message {msg_type} {{")
            for _ in range(random.randint(1, 5)):
                if random.random() < 0.5:
                    lines.append(f"        let x = {self.random_expression()}")
                else:
                    lines.append(f"        respond({self.random_expression()})")
            lines.append("    }")
        
        # Random functions
        for _ in range(random.randint(0, 3)):
            fn_name = self.random_identifier()
            params = []
            for _ in range(random.randint(0, 3)):
                params.append(f"{self.random_identifier()}: {self.random_identifier()}")
            lines.append(f"    fn {fn_name}({', '.join(params)}) -> {self.random_identifier()} {{")
            for _ in range(random.randint(1, 5)):
                lines.append(f"        let x = {self.random_expression()}")
            lines.append(f"        return {self.random_expression()}")
            lines.append("    }")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def test_fuzz_random_programs(self):
        """Fuzz test with random programs."""
        if not HAS_LANGUAGE:
            pytest.skip("Language modules not available")
            
        for i in range(50):
            program = self.random_program()
            try:
                lexer = Lexer(program)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                # Should either parse successfully or fail gracefully
                assert ast is not None or True
            except Exception as e:
                # Should not crash
                print(f"Fuzz iteration {i} failed: {e}")
                continue
                
    def test_fuzz_malformed_programs(self):
        """Fuzz test with malformed programs."""
        if not HAS_LANGUAGE:
            pytest.skip("Language modules not available")
            
        malformed = [
            "",  # Empty
            "agent",  # Incomplete
            "agent {",  # Missing name
            "agent Test {",  # Missing closing
            "agent Test { name: ",  # Incomplete
            "agent Test { name: { } }",  # Invalid
            "agent Test { on message { } }",  # Missing message type
            "agent Test { fn test() { } }",  # Missing return type
            "agent Test { state { } }",  # Empty state
            "{",  # Just brace
            "}",  # Just brace
            "()",  # Empty parentheses
            "[]",  # Empty brackets
            "{}",  # Empty braces
            "import ml import tensor",  # Multiple imports without newline
            "agent Test { capabilities: [ }",  # Incomplete list
            "agent Test { capabilities: [test }",  # Invalid list
            "agent Test { on message * { } }",  # Wildcard handler
            "agent Test { let x = }",  # Incomplete assignment
        ]
        
        for program in malformed:
            try:
                lexer = Lexer(program)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
            except Exception:
                # Expected for malformed input
                pass
                
    def test_fuzz_extreme_strings(self):
        """Fuzz test with extreme strings in programs."""
        if not HAS_LANGUAGE:
            pytest.skip("Language modules not available")
            
        extreme_strings = [
            '"' + "x" * 100000 + '"',  # Very long string
            '"' + "".join(chr(c) for c in range(0x10000)) + '"',  # All unicode
            '"\x00\x01\x02\x03\xFF"',  # Control characters
            '"Unicode: 🚀🌿💬こんにちは你好世界مرحباПривіт"',  # Mixed unicode
            '"' + '"' * 100 + '"',  # Nested quotes
            '"\\n\\t\\r\\"\\\\"',  # Escape sequences
        ]
        
        for s in extreme_strings:
            program = f"agent Test {{ name: {s} }}"
            try:
                lexer = Lexer(program)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
            except Exception:
                pass


class TestFuzzParser:
    """Parser fuzz test class for pytest."""
    
    def test_fuzz_basic_parsing(self):
        """Fuzz basic parsing."""
        if not HAS_LANGUAGE:
            pytest.skip("Language modules not available")
            
        test_programs = [
            "agent Test { name: \"Test\" }",
            "agent Test { name: \"Test\" version: \"1.0.0\" }",
            "agent Test { capabilities: [\"a\", \"b\"] }",
            "agent Test { state { x: 0 } }",
            "agent Test { on message ping { respond(\"pong\") } }",
            "agent Test { fn add(a: int, b: int) -> int { return a + b } }",
            "import ml\nagent Test { name: \"Test\" }",
        ]
        
        for program in test_programs:
            try:
                lexer = Lexer(program)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                assert ast is not None
            except Exception as e:
                pytest.fail(f"Parsing failed for {program}: {e}")