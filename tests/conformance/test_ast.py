#!/usr/bin/env python3
"""
Conformance Tests: AST

Tests for the Vireo Abstract Syntax Tree.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from language.ast import (
    ASTNode, AgentNode, MessageHandlerNode, FunctionNode,
    VariableNode, AssignmentNode, CallNode, MatchNode,
    IfNode, ForNode, WhileNode, ReturnNode,
    BinaryOpNode, UnaryOpNode, LiteralNode, IdentifierNode,
    TensorNode, TypeNode, ContractNode, ImportNode,
    visitor, Transformer
)


class TestAST:
    """AST conformance tests."""
    
    def test_agent_node_creation(self):
        """Test AgentNode creation."""
        node = AgentNode(
            name="TestAgent",
            version="1.0.0",
            description="Test agent",
            capabilities=["test"],
            imports=[],
            state={},
            config={},
            contracts={},
            functions=[],
            handlers=[]
        )
        
        assert node.name == "TestAgent"
        assert node.version == "1.0.0"
        assert "test" in node.capabilities
        assert node.node_type == "Agent"
        
    def test_handler_node_creation(self):
        """Test MessageHandlerNode creation."""
        node = MessageHandlerNode(
            message_type="test",
            pattern=None,
            body=[],
            is_request=False
        )
        
        assert node.message_type == "test"
        assert node.is_request is False
        assert node.node_type == "MessageHandler"
        
    def test_function_node_creation(self):
        """Test FunctionNode creation."""
        node = FunctionNode(
            name="test_fn",
            params=[("a", "int"), ("b", "int")],
            return_type="int",
            body=[],
            is_async=False
        )
        
        assert node.name == "test_fn"
        assert len(node.params) == 2
        assert node.return_type == "int"
        assert node.node_type == "Function"
        
    def test_variable_node_creation(self):
        """Test VariableNode creation."""
        node = VariableNode(
            name="x",
            type="int",
            value=LiteralNode(42),
            is_mutable=False
        )
        
        assert node.name == "x"
        assert node.type == "int"
        assert node.is_mutable is False
        
    def test_binary_op_node(self):
        """Test BinaryOpNode creation."""
        node = BinaryOpNode(
            op="+",
            left=LiteralNode(1),
            right=LiteralNode(2)
        )
        
        assert node.op == "+"
        assert node.left.value == 1
        assert node.right.value == 2
        
    def test_match_node_creation(self):
        """Test MatchNode creation."""
        node = MatchNode(
            value=IdentifierNode("x"),
            cases=[
                ("1", LiteralNode(1)),
                ("2", LiteralNode(2)),
                ("_", LiteralNode(0))
            ]
        )
        
        assert len(node.cases) == 3
        assert node.cases[0][0] == "1"
        assert node.cases[1][0] == "2"
        assert node.cases[2][0] == "_"
        
    def test_tensor_node_creation(self):
        """Test TensorNode creation."""
        node = TensorNode(
            values=[
                [1, 2],
                [3, 4]
            ],
            dtype="float32",
            shape=[2, 2]
        )
        
        assert node.values[0][0] == 1
        assert node.dtype == "float32"
        assert node.shape == [2, 2]
        
    def test_contract_node_creation(self):
        """Test ContractNode creation."""
        node = ContractNode(
            name="TestContract",
            fields={
                "price": TypeNode("int"),
                "deadline": TypeNode("string")
            },
            defaults={
                "quality": "standard"
            }
        )
        
        assert node.name == "TestContract"
        assert "price" in node.fields
        assert "deadline" in node.fields
        assert node.defaults["quality"] == "standard"


class TestASTVisitor:
    """AST visitor tests."""
    
    def test_visitor_base(self):
        """Test basic visitor functionality."""
        class TestVisitor(visitor.Visitor):
            def visit_Agent(self, node):
                return f"Agent: {node.name}"
            
            def visit_Literal(self, node):
                return f"Literal: {node.value}"
        
        visitor_obj = TestVisitor()
        agent = AgentNode(name="Test", version="1.0.0")
        result = visitor_obj.visit(agent)
        assert result == "Agent: Test"
        
    def test_visitor_traversal(self):
        """Test visitor traversal."""
        class CountVisitor(visitor.Visitor):
            def __init__(self):
                self.count = 0
            
            def visit_Agent(self, node):
                self.count += 1
                self.generic_visit(node)
            
            def visit_Function(self, node):
                self.count += 1
                self.generic_visit(node)
        
        agent = AgentNode(
            name="Test",
            version="1.0.0",
            functions=[
                FunctionNode("fn1", [], "void", []),
                FunctionNode("fn2", [], "void", [])
            ]
        )
        
        visitor_obj = CountVisitor()
        visitor_obj.visit(agent)
        assert visitor_obj.count == 3  # Agent + 2 functions


class TestASTTransformer:
    """AST transformer tests."""
    
    def test_transformer_base(self):
        """Test basic transformer functionality."""
        class TestTransformer(transformer.Transformer):
            def transform_Agent(self, node):
                node.name = node.name + "_transformed"
                return self.generic_transform(node)
        
        agent = AgentNode(name="Test", version="1.0.0")
        transformer_obj = TestTransformer()
        result = transformer_obj.transform(agent)
        assert result.name == "Test_transformed"
        
    def test_transformer_replace(self):
        """Test transformer replacement."""
        class ReplaceTransformer(transformer.Transformer):
            def transform_Literal(self, node):
                if node.value == 0:
                    return LiteralNode(42)
                return self.generic_transform(node)
        
        transformer_obj = ReplaceTransformer()
        result = transformer_obj.transform(LiteralNode(0))
        assert result.value == 42


class TestASTSerialization:
    """AST serialization tests."""
    
    def test_serialize_agent(self):
        """Test serializing AgentNode."""
        import json
        
        agent = AgentNode(
            name="TestAgent",
            version="1.0.0",
            capabilities=["test"]
        )
        
        data = agent.to_dict()
        assert data["name"] == "TestAgent"
        assert data["version"] == "1.0.0"
        assert "test" in data["capabilities"]
        
        # Roundtrip
        restored = AgentNode.from_dict(data)
        assert restored.name == agent.name
        assert restored.version == agent.version
        
    def test_serialize_complex(self):
        """Test serializing complex AST."""
        import json
        
        agent = AgentNode(
            name="ComplexAgent",
            version="1.0.0",
            capabilities=["test", "ml"],
            functions=[
                FunctionNode(
                    "process",
                    [("x", "int")],
                    "int",
                    [BinaryOpNode("*", IdentifierNode("x"), LiteralNode(2))]
                )
            ]
        )
        
        data = agent.to_dict()
        json_str = json.dumps(data)
        restored = AgentNode.from_dict(json.loads(json_str))
        
        assert restored.name == agent.name
        assert len(restored.functions) == len(agent.functions)