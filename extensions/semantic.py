# ============================================================
# VIREO SEMANTIC ANALYZER
# Семантичний аналіз Vireo
# ============================================================

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from .ast import AST, ASTNode, NodeType


class SymbolKind(Enum):
    VARIABLE = "variable"
    FUNCTION = "function"
    PARAMETER = "parameter"
    MODEL = "model"
    AGENT = "agent"
    CONTRACT = "contract"
    NEGOTIATION = "negotiation"


@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    type: Optional[str] = None
    node: Optional[ASTNode] = None
    scope: Optional['Scope'] = None


@dataclass
class Scope:
    name: str
    parent: Optional['Scope'] = None
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    children: List['Scope'] = field(default_factory=list)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)
    
    def declare(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def add_child(self, scope: 'Scope') -> None:
        scope.parent = self
        self.children.append(scope)


class SemanticAnalyzer:
    """Семантичний аналізатор Vireo."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.global_scope = Scope("global")
        self.current_scope: Scope = self.global_scope
        self.function_stack: List[str] = []
        self.loop_depth: int = 0
        self.builtins = ['print', 'len', 'range', 'int', 'float', 'str', 'type',
                         'true', 'false', 'none', 'Tensor', 'Math', 'Agent']
    
    def analyze(self, ast: AST) -> bool:
        self.errors = []
        self.warnings = []
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.function_stack = []
        self.loop_depth = 0
        
        for node in ast.nodes:
            self._analyze_node(node)
        
        return len(self.errors) == 0
    
    def _analyze_node(self, node: ASTNode) -> Optional[str]:
        if node.type == NodeType.VARIABLE_DEF:
            return self._analyze_variable_def(node)
        elif node.type == NodeType.FUNCTION_DEF:
            return self._analyze_function_def(node)
        elif node.type == NodeType.ASSIGN:
            return self._analyze_assignment(node)
        elif node.type == NodeType.RETURN:
            return self._analyze_return(node)
        elif node.type == NodeType.IF:
            return self._analyze_if(node)
        elif node.type == NodeType.WHILE:
            return self._analyze_while(node)
        elif node.type == NodeType.FOR:
            return self._analyze_for(node)
        elif node.type == NodeType.MODEL_DEF:
            return self._analyze_model_def(node)
        elif node.type == NodeType.AGENT_DEF:
            return self._analyze_agent_def(node)
        elif node.type == NodeType.CONTRACT_DEF:
            return self._analyze_contract_def(node)
        elif node.type == NodeType.NEGOTIATION_DEF:
            return self._analyze_negotiation_def(node)
        elif node.type == NodeType.FUNCTION_CALL:
            return self._analyze_function_call(node)
        elif node.type == NodeType.IDENTIFIER:
            return self._analyze_identifier(node)
        else:
            for child in node.children:
                self._analyze_node(child)
            return None
    
    def _analyze_variable_def(self, node: ASTNode) -> Optional[str]:
        name = node.data.get('name', '')
        if not name:
            self.errors.append("Variable name required")
            return None
        if self.current_scope.lookup_local(name):
            self.warnings.append(f"Variable '{name}' already declared in this scope")
        symbol = Symbol(name, SymbolKind.VARIABLE, 'any', node)
        self.current_scope.declare(symbol)
        return 'any'
    
    def _analyze_function_def(self, node: ASTNode) -> Optional[str]:
        name = node.data.get('name', '')
        params = node.data.get('params', [])
        if not name:
            self.errors.append("Function name required")
            return None
        if self.global_scope.lookup(name):
            self.errors.append(f"Function '{name}' already declared")
            return None
        
        func_scope = Scope(f"function:{name}", self.current_scope)
        self.current_scope = func_scope
        for param in params:
            symbol = Symbol(param, SymbolKind.PARAMETER, 'any', node)
            func_scope.declare(symbol)
        
        self.function_stack.append(name)
        for child in node.children:
            self._analyze_node(child)
        self.function_stack.pop()
        self.current_scope = self.current_scope.parent or self.global_scope
        
        symbol = Symbol(name, SymbolKind.FUNCTION, 'function', node, func_scope)
        self.global_scope.declare(symbol)
        return 'function'
    
    def _analyze_assignment(self, node: ASTNode) -> Optional[str]:
        name = node.data.get('name', '')
        symbol = self.current_scope.lookup(name)
        if not symbol:
            self.errors.append(f"Variable '{name}' not declared")
            return None
        return symbol.type
    
    def _analyze_return(self, node: ASTNode) -> Optional[str]:
        if not self.function_stack:
            self.errors.append("Return statement outside function")
            return None
        return 'any'
    
    def _analyze_if(self, node: ASTNode) -> Optional[str]:
        if_scope = Scope("if", self.current_scope)
        self.current_scope = if_scope
        for child in node.children:
            self._analyze_node(child)
        self.current_scope = self.current_scope.parent or self.global_scope
        return None
    
    def _analyze_while(self, node: ASTNode) -> Optional[str]:
        self.loop_depth += 1
        while_scope = Scope("while", self.current_scope)
        self.current_scope = while_scope
        for child in node.children:
            self._analyze_node(child)
        self.current_scope = self.current_scope.parent or self.global_scope
        self.loop_depth -= 1
        return None
    
    def _analyze_for(self, node: ASTNode) -> Optional[str]:
        var = node.data.get('var', '')
        self.loop_depth += 1
        for_scope = Scope("for", self.current_scope)
        self.current_scope = for_scope
        symbol = Symbol(var, SymbolKind.VARIABLE, 'any', node)
        for_scope.declare(symbol)
        for child in node.children:
            self._analyze_node(child)
        self.current_scope = self.current_scope.parent or self.global_scope
        self.loop_depth -= 1
        return None
    
    def _analyze_model_def(self, node: ASTNode) -> Optional[str]:
        name = node.data.get('name', '')
        if not name:
            self.errors.append("Model name required")
            return None
        symbol = Symbol(name, SymbolKind.MODEL, 'model', node)
        self.global_scope.declare(symbol)
        for child in node.children:
            self._analyze_node(child)
        return 'model'
    
    def _analyze_agent_def(self, node: ASTNode) -> Optional[str]:
        name = node.data.get('name', '')
        if not name:
            self.errors.append("Agent name required")
            return None
        symbol = Symbol(name, SymbolKind.AGENT, 'agent', node)
        self.global_scope.declare(symbol)
        for child in node.children:
            self._analyze_node(child)
        return 'agent'
    
    def _analyze_contract_def(self, node: ASTNode) -> Optional[str]:
        name = node.data.get('name', '')
        if not name:
            self.errors.append("Contract name required")
            return None
        symbol = Symbol(name, SymbolKind.CONTRACT, 'contract', node)
        self.global_scope.declare(symbol)
        for child in node.children:
            self._analyze_node(child)
        return 'contract'
    
    def _analyze_negotiation_def(self, node: ASTNode) -> Optional[str]:
        name = node.data.get('name', '')
        if not name:
            self.errors.append("Negotiation name required")
            return None
        symbol = Symbol(name, SymbolKind.NEGOTIATION, 'negotiation', node)
        self.global_scope.declare(symbol)
        for child in node.children:
            self._analyze_node(child)
        return 'negotiation'
    
    def _analyze_function_call(self, node: ASTNode) -> Optional[str]:
        name = node.data.get('name', '')
        symbol = self.current_scope.lookup(name)
        if not symbol and name not in self.builtins:
            self.errors.append(f"Function '{name}' not found")
            return None
        for child in node.children:
            self._analyze_node(child)
        return 'any'
    
    def _analyze_identifier(self, node: ASTNode) -> Optional[str]:
        name = node.data.get('name', '')
        if name in self.builtins:
            return 'any'
        symbol = self.current_scope.lookup(name)
        if not symbol:
            self.errors.append(f"Identifier '{name}' not found")
            return None
        return symbol.type
    
    def get_errors(self) -> List[str]:
        return self.errors
    
    def get_warnings(self) -> List[str]:
        return self.warnings


def analyze(ast: AST) -> bool:
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)