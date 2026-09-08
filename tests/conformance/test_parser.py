#!/usr/bin/env python3
"""
Conformance Tests: Parser

Tests for the Vireo language parser.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from language.lexer import Lexer
from language.parser import Parser
from language.ast import (
    ASTNode, AgentNode, MessageHandlerNode, FunctionNode,
    VariableNode, TypeNode, TensorNode, MatchNode
)


class TestParser:
    """Parser conformance tests."""
    
    def test_parse_simple_agent(self):
        """Test parsing a simple agent definition."""
        code = """
        agent SimpleAgent {
            name: "SimpleAgent"
            version: "1.0.0"
            capabilities: ["test"]
            
            on message "ping" {
                respond("pong")
            }
        }
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast is not None
        assert len(ast) == 1
        assert isinstance(ast[0], AgentNode)
        assert ast[0].name == "SimpleAgent"
        assert ast[0].version == "1.0.0"
        assert "test" in ast[0].capabilities
        
    def test_parse_agent_with_state(self):
        """Test parsing agent with state."""
        code = """
        agent StateAgent {
            name: "StateAgent"
            
            state {
                count: 0
                messages: []
                status: "idle"
                config: {
                    timeout: 30
                    retries: 3
                }
            }
        }
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast is not None
        assert len(ast) == 1
        assert isinstance(ast[0], AgentNode)
        assert "count" in ast[0].state
        assert ast[0].state["count"] == 0
        assert ast[0].state["messages"] == []
        assert ast[0].state["status"] == "idle"
        assert "timeout" in ast[0].state["config"]
        
    def test_parse_agent_with_handlers(self):
        """Test parsing agent with message handlers."""
        code = """
        agent HandlerAgent {
            name: "HandlerAgent"
            
            on message "greeting" {
                let name = message.payload.name
                respond("Hello, ${name}!")
            }
            
            on message "calculate" {
                let a = message.payload.a
                let b = message.payload.b
                let result = a + b
                respond({result: result})
            }
        }
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast is not None
        assert len(ast) == 1
        assert isinstance(ast[0], AgentNode)
        assert len(ast[0].handlers) == 2
        
        # Check first handler
        handler1 = ast[0].handlers[0]
        assert handler1.message_type == "greeting"
        assert len(handler1.body) > 0
        
        # Check second handler
        handler2 = ast[0].handlers[1]
        assert handler2.message_type == "calculate"
        
    def test_parse_agent_with_functions(self):
        """Test parsing agent with functions."""
        code = """
        agent FunctionAgent {
            name: "FunctionAgent"
            
            fn add(a: int, b: int) -> int {
                return a + b
            }
            
            fn greet(name: string, prefix: string = "Hello") -> string {
                return "${prefix}, ${name}!"
            }
        }
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast is not None
        assert len(ast) == 1
        assert isinstance(ast[0], AgentNode)
        assert len(ast[0].functions) == 2
        
        fn1 = ast[0].functions[0]
        assert fn1.name == "add"
        assert fn1.params[0] == ("a", "int")
        assert fn1.params[1] == ("b", "int")
        assert fn1.return_type == "int"
        
        fn2 = ast[0].functions[1]
        assert fn2.name == "greet"
        assert fn2.params[0] == ("name", "string")
        assert fn2.params[1] == ("prefix", "string", "Hello")
        
    def test_parse_agent_with_extensions(self):
        """Test parsing agent with extensions."""
        code = """
        import ml
        import tensor
        
        agent MLExtension {
            name: "MLExtension"
            
            on message "train" {
                let model = ml.nn.Sequential(
                    ml.nn.Linear(784, 256),
                    ml.nn.ReLU(),
                    ml.nn.Dropout(0.2)
                )
                
                let tensor = tensor.zeros([3, 3])
            }
        }
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast is not None
        assert len(ast) == 1
        assert isinstance(ast[0], AgentNode)
        assert "ml" in ast[0].imports
        assert "tensor" in ast[0].imports
        
    def test_parse_agent_with_contract(self):
        """Test parsing agent with contract definition."""
        code = """
        agent ContractAgent {
            name: "ContractAgent"
            
            contract MyContract {
                price: int
                deadline: string
                scope: string
                deliverables: [string]
                quality: string = "standard"
            }
            
            on message "propose" {
                let contract = MyContract {
                    price: 100
                    deadline: "2024-12-31"
                    scope: "Data analysis"
                    deliverables: ["report", "model"]
                }
            }
        }
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast is not None
        assert len(ast) == 1
        assert isinstance(ast[0], AgentNode)
        assert "MyContract" in ast[0].contracts
        
    def test_parse_match_expression(self):
        """Test parsing match expressions."""
        code = """
        agent MatchAgent {
            name: "MatchAgent"
            
            on message "process" {
                let value = message.payload.value
                
                match value {
                    "hello" => respond("Greeting")
                    "goodbye" => respond("Farewell")
                    s: string => respond("String: ${s}")
                    _ => respond("Unknown")
                }
            }
        }
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast is not None
        assert len(ast) == 1
        assert isinstance(ast[0], AgentNode)
        
        # Find match expression in handler body
        handler = ast[0].handlers[0]
        match_node = None
        for node in handler.body:
            if isinstance(node, MatchNode):
                match_node = node
                break
        
        assert match_node is not None
        assert len(match_node.cases) == 4
        
    def test_parse_tensor_operations(self):
        """Test parsing tensor operations."""
        code = """
        import tensor
        
        agent TensorAgent {
            name: "TensorAgent"
            
            on message "compute" {
                let a = tensor.zeros([3, 3])
                let b = tensor.ones([3, 3])
                let c = a + b
                let d = a @ b.T
                let e = a.matmul(b)
            }
        }
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast is not None
        assert len(ast) == 1
        assert isinstance(ast[0], AgentNode)
        
    def test_parse_error_handling(self):
        """Test error handling for invalid syntax."""
        code = """
        agent BadAgent {
            name: "BadAgent"
            // Missing closing brace
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        
        with pytest.raises(Exception):
            parser.parse()
    
    def test_parse_complex_agent(self):
        """Test parsing a complex agent with all features."""
        code = """
        import ml
        import tensor
        import crypto
        
        agent ComplexAgent {
            name: "ComplexAgent"
            version: "3.0.0"
            description: "Complex AI agent"
            
            capabilities: ["text", "image", "video"]
            
            config {
                timeout: 30
                retries: 3
                language: "en"
            }
            
            state {
                model: null
                trained: false
                accuracy: 0.0
                history: []
            }
            
            contract ServiceContract {
                price: int
                deadline: string
                scope: string
                quality: string = "standard"
            }
            
            fn process(data: tensor) -> tensor {
                return data * 2
            }
            
            fn train_model(
                x_train: tensor,
                y_train: tensor,
                epochs: int = 10
            ) -> dict {
                let model = ml.nn.Sequential(
                    ml.nn.Linear(784, 256),
                    ml.nn.ReLU(),
                    ml.nn.Dropout(0.2)
                )
                
                let result = model.train(x_train, y_train, epochs)
                return result
            }
            
            on message "train" {
                let data = message.payload
                let result = train_model(data.x, data.y)
                respond({status: "done", result: result})
            }
            
            on message "predict" {
                let input = message.payload.input
                let output = state.model.forward(input)
                respond({prediction: output})
            }
        }
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast is not None
        assert len(ast) == 1
        assert isinstance(ast[0], AgentNode)
        
        agent = ast[0]
        assert agent.name == "ComplexAgent"
        assert agent.version == "3.0.0"
        assert len(agent.capabilities) == 3
        assert "ml" in agent.imports
        assert "tensor" in agent.imports
        assert "crypto" in agent.imports
        assert len(agent.handlers) == 2
        assert len(agent.functions) == 2
        assert "ServiceContract" in agent.contracts


class TestLexer:
    """Lexer conformance tests."""
    
    def test_tokenize_simple(self):
        """Test tokenizing simple code."""
        code = "agent Test { name: \"Test\" }"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        assert len(tokens) > 0
        assert tokens[0].type == "IDENTIFIER"
        assert tokens[0].value == "agent"
        assert tokens[1].type == "IDENTIFIER"
        assert tokens[1].value == "Test"
        
    def test_tokenize_strings(self):
        """Test tokenizing strings."""
        code = """
        let s1 = "Hello, world!"
        let s2 = "Multi-line\\nstring"
        let s3 = """Triple-quoted
            multi-line
            string"""
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        strings = [t for t in tokens if t.type == "STRING"]
        assert len(strings) >= 3
        
    def test_tokenize_numbers(self):
        """Test tokenizing numbers."""
        code = """
        let int = 42
        let float = 3.14159
        let hex = 0xFF
        let binary = 0b1010
        let octal = 0o777
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        numbers = [t for t in tokens if t.type == "NUMBER"]
        assert len(numbers) >= 5
        
    def test_tokenize_comments(self):
        """Test tokenizing comments."""
        code = """
        // Single line comment
        let x = 42
        /* Multi-line
           comment */
        let y = 24
        """
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # Comments should be filtered out
        token_values = [t.value for t in tokens]
        assert "//" not in token_values
        assert "/*" not in token_values
        
    def test_tokenize_operators(self):
        """Test tokenizing operators."""
        code = "let x = 1 + 2 - 3 * 4 / 5"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        operators = [t for t in tokens if t.type == "OPERATOR"]
        assert len(operators) >= 4