"""
Vireo Language Module

This module contains the core language components:
- Parser: Vireo → AST
- AST: Abstract Syntax Tree
- Code Generator: AST → Python
- Validator: Semantic analysis
- Optimizer: Code optimization
"""

from .parser import Parser, parse
from .ast import AST, ASTNode, NodeType
from .codegen import CodeGenerator, generate_code
from .validator import Validator, validate
from .optimizer import Optimizer, optimize

__all__ = [
    'Parser',
    'parse',
    'AST',
    'ASTNode',
    'NodeType',
    'CodeGenerator',
    'generate_code',
    'Validator',
    'validate',
    'Optimizer',
    'optimize'
]