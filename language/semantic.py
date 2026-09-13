# ============================================================
# VIREO SEMANTIC ANALYZER
# Семантичний аналіз Vireo
# ============================================================

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from .ast import AST, ASTNode, NodeType


class SymbolKind(Enum):
    """Типи символів у таблиці символів."""
    VARIABLE = "variable"
    FUNCTION = "function"
    PARAMETER = "parameter"
    MODEL = "model"
    AGENT = "agent"
    CONTRACT = "contract"
    NEGOTIATION = "negotiation"
    IMPORT = "import"
    TYPE = "type"
    CONSTANT = "constant"


@dataclass
class Symbol:
    """Символ у таблиці символів."""
    name: str
    kind: SymbolKind
    type: Optional[str] = None
    node: Optional[ASTNode] = None
    scope: Optional['Scope'] = None
    defined: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Symbol(name={self.name}, kind={self.kind.value}, type={self.type})"


@dataclass
class Scope:
    """Область видимості."""
    name: str
    parent: Optional['Scope'] = None
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    children: List['Scope'] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Пошук символу в поточній та батьківських областях."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Пошук символу тільки в поточній області."""
        return self.symbols.get(name)
    
    def declare(self, symbol: Symbol) -> bool:
        """Оголосити символ у поточній області."""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def add_child(self, scope: 'Scope') -> None:
        """Додати дочірню область."""
        scope.parent = self
        self.children.append(scope)
    
    def get_all_symbols(self) -> Dict[str, Symbol]:
        """Отримати всі символи в області (включаючи батьківські)."""
        result = {}
        if self.parent:
            result.update(self.parent.get_all_symbols())
        result.update(self.symbols)
        return result
    
    def get_local_symbols(self) -> Dict[str, Symbol]:
        """Отримати локальні символи."""
        return self.symbols.copy()
    
    def __repr__(self) -> str:
        return f"Scope(name={self.name}, symbols={len(self.symbols)}, children={len(self.children)})"


class SemanticAnalyzer:
    """
    Семантичний аналізатор Vireo.
    
    Перевіряє:
    - Оголошення змінних перед використанням
    - Типи даних
    - Області видимості
    - Правильність конструкцій
    - Сумісність типів
    - Унікальність імен
    """
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.global_scope = Scope("global")
        self.current_scope: Scope = self.global_scope
        self.function_stack: List[str] = []
        self.loop_depth: int = 0
        self.imports: Set[str] = set()
        
        # Вбудовані функції та типи
        self.builtins = {
            'print': 'function',
            'len': 'function',
            'range': 'function',
            'int': 'function',
            'float': 'function',
            'str': 'function',
            'type': 'function',
            'true': 'boolean',
            'false': 'boolean',
            'none': 'null',
            'Tensor': 'type',
            'Math': 'type',
            'Agent': 'type',
            'Contract': 'type',
            'DID': 'type',
        }
    
    def analyze(self, ast: AST) -> bool:
        """
        Аналізує AST.
        
        Args:
            ast: AST для аналізу
            
        Returns:
            bool: True якщо помилок немає
        """
        self.errors = []
        self.warnings = []
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.function_stack = []
        self.loop_depth = 0
        self.imports = set()
        
        # Реєструємо вбудовані символи
        for name, type_name in self.builtins.items():
            kind = SymbolKind.FUNCTION if type_name == 'function' else SymbolKind.TYPE
            symbol = Symbol(name, kind, type_name)
            self.global_scope.declare(symbol)
        
        for node in ast.nodes:
            self._analyze_node(node)
        
        return len(self.errors) == 0
    
    def _analyze_node(self, node: ASTNode) -> Optional[str]:
        """Аналізує конкретний вузол."""
        if node.type == NodeType.IMPORT:
            return self._analyze_import(node)
        elif node.type == NodeType.VARIABLE_DEF:
            return self._analyze_variable_def(node)
        elif node.type == NodeType.ASSIGN:
            return self._analyze_assignment(node)
        elif node.type == NodeType.FUNCTION_DEF:
            return self._analyze_function_def(node)
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
        elif node.type == NodeType.PRINT:
            return self._analyze_print(node)
        elif node.type == NodeType.LITERAL:
            return self._analyze_literal(node)
        elif node.type == NodeType.BINARY_OP:
            return self._analyze_binary_op(node)
        elif node.type == NodeType.UNARY_OP:
            return self._analyze_unary_op(node)
        else:
            # Рекурсивно аналізуємо дітей
            for child in node.children:
                self._analyze_node(child)
            return None
    
    def _analyze_import(self, node: ASTNode) -> Optional[str]:
        """Аналізує import."""
        name = node.data.get('name', '')
        if not name:
            self.errors.append("Import name required")
            return None
        
        # Перевіряємо чи модуль існує
        # (спрощена перевірка)
        if name in self.imports:
            self.warnings.append(f"Module '{name}' already imported")
        
        self.imports.add(name)
        
        symbol = Symbol(name, SymbolKind.IMPORT, 'module', node)
        self.global_scope.declare(symbol)
        
        return 'module'
    
    def _analyze_variable_def(self, node: ASTNode) -> Optional[str]:
        """Аналізує визначення змінної."""
        name = node.data.get('name', '')
        value = node.data.get('value', '')
        
        if not name:
            self.errors.append("Variable name required")
            return None
        
        # Перевіряємо чи змінна вже оголошена в цій області
        if self.current_scope.lookup_local(name):
            self.errors.append(f"Variable '{name}' already declared in this scope")
            return None
        
        # Визначаємо тип змінної
        var_type = self._infer_type(value)
        
        # Оголошуємо змінну
        symbol = Symbol(name, SymbolKind.VARIABLE, var_type, node)
        self.current_scope.declare(symbol)
        
        return var_type
    
    def _analyze_assignment(self, node: ASTNode) -> Optional[str]:
        """Аналізує присвоєння."""
        name = node.data.get('name', '')
        value = node.data.get('value', '')
        
        # Перевіряємо чи змінна існує
        symbol = self.current_scope.lookup(name)
        if not symbol:
            self.errors.append(f"Variable '{name}' not declared")
            return None
        
        # Перевіряємо сумісність типів
        value_type = self._infer_type(value)
        if symbol.type and value_type and symbol.type != value_type:
            self.warnings.append(
                f"Type mismatch: '{name}' is {symbol.type}, assigned {value_type}"
            )
        
        return symbol.type
    
    def _analyze_function_def(self, node: ASTNode) -> Optional[str]:
        """Аналізує визначення функції."""
        name = node.data.get('name', '')
        params = node.data.get('params', [])
        
        if not name:
            self.errors.append("Function name required")
            return None
        
        # Перевіряємо чи функція вже оголошена
        if self.global_scope.lookup(name):
            self.errors.append(f"Function '{name}' already declared")
            return None
        
        # Створюємо область для функції
        func_scope = Scope(f"function:{name}", self.current_scope)
        self.current_scope = func_scope
        
        # Додаємо параметри
        for param in params:
            symbol = Symbol(param, SymbolKind.PARAMETER, 'any', node)
            func_scope.declare(symbol)
        
        self.function_stack.append(name)
        
        # Аналізуємо тіло функції
        for child in node.children:
            self._analyze_node(child)
        
        self.function_stack.pop()
        self.current_scope = self.current_scope.parent or self.global_scope
        
        # Оголошуємо функцію в глобальній області
        symbol = Symbol(name, SymbolKind.FUNCTION, 'function', node, func_scope)
        self.global_scope.declare(symbol)
        
        return 'function'
    
    def _analyze_return(self, node: ASTNode) -> Optional[str]:
        """Аналізує оператор return."""
        if not self.function_stack:
            self.errors.append("Return statement outside function")
            return None
        
        expr = node.data.get('expression', '')
        if expr:
            return self._infer_type(expr)
        
        return 'null'
    
    def _analyze_if(self, node: ASTNode) -> Optional[str]:
        """Аналізує умовний оператор."""
        condition = node.data.get('condition', '')
        
        # Перевіряємо умову
        cond_type = self._infer_type(condition)
        if cond_type and cond_type not in ['boolean', 'bool']:
            self.warnings.append(f"Condition should be boolean, got {cond_type}")
        
        # Створюємо область для if
        if_scope = Scope("if", self.current_scope)
        self.current_scope = if_scope
        
        for child in node.children:
            if child.type != NodeType.ELSE:
                self._analyze_node(child)
        
        self.current_scope = self.current_scope.parent or self.global_scope
        
        # Аналізуємо else
        else_node = next((c for c in node.children if c.type == NodeType.ELSE), None)
        if else_node:
            else_scope = Scope("else", self.current_scope)
            self.current_scope = else_scope
            for child in else_node.children:
                self._analyze_node(child)
            self.current_scope = self.current_scope.parent or self.global_scope
        
        return None
    
    def _analyze_while(self, node: ASTNode) -> Optional[str]:
        """Аналізує цикл while."""
        condition = node.data.get('condition', '')
        
        # Перевіряємо умову
        cond_type = self._infer_type(condition)
        if cond_type and cond_type not in ['boolean', 'bool']:
            self.warnings.append(f"Condition should be boolean, got {cond_type}")
        
        self.loop_depth += 1
        
        while_scope = Scope("while", self.current_scope)
        self.current_scope = while_scope
        
        for child in node.children:
            self._analyze_node(child)
        
        self.current_scope = self.current_scope.parent or self.global_scope
        self.loop_depth -= 1
        
        return None
    
    def _analyze_for(self, node: ASTNode) -> Optional[str]:
        """Аналізує цикл for."""
        var = node.data.get('var', '')
        collection = node.data.get('collection', '')
        
        if not var:
            self.errors.append("Loop variable name required")
            return None
        
        self.loop_depth += 1
        
        for_scope = Scope("for", self.current_scope)
        self.current_scope = for_scope
        
        # Додаємо змінну циклу
        symbol = Symbol(var, SymbolKind.VARIABLE, 'any', node)
        for_scope.declare(symbol)
        
        # Аналізуємо колекцію
        coll_type = self._infer_type(collection)
        if coll_type and not coll_type.startswith('list'):
            self.warnings.append(f"Iterating over non-list: {coll_type}")
        
        for child in node.children:
            self._analyze_node(child)
        
        self.current_scope = self.current_scope.parent or self.global_scope
        self.loop_depth -= 1
        
        return None
    
    def _analyze_model_def(self, node: ASTNode) -> Optional[str]:
        """Аналізує визначення моделі."""
        name = node.data.get('name', '')
        
        if not name:
            self.errors.append("Model name required")
            return None
        
        # Перевіряємо унікальність
        if self.global_scope.lookup(name):
            self.errors.append(f"Model '{name}' already declared")
            return None
        
        symbol = Symbol(name, SymbolKind.MODEL, 'model', node)
        self.global_scope.declare(symbol)
        
        # Аналізуємо вміст моделі
        model_scope = Scope(f"model:{name}", self.current_scope)
        self.current_scope = model_scope
        
        for child in node.children:
            self._analyze_node(child)
        
        self.current_scope = self.current_scope.parent or self.global_scope
        
        return 'model'
    
    def _analyze_agent_def(self, node: ASTNode) -> Optional[str]:
        """Аналізує визначення агента."""
        name = node.data.get('name', '')
        
        if not name:
            self.errors.append("Agent name required")
            return None
        
        # Перевіряємо унікальність
        if self.global_scope.lookup(name):
            self.errors.append(f"Agent '{name}' already declared")
            return None
        
        symbol = Symbol(name, SymbolKind.AGENT, 'agent', node)
        self.global_scope.declare(symbol)
        
        # Аналізуємо вміст агента
        agent_scope = Scope(f"agent:{name}", self.current_scope)
        self.current_scope = agent_scope
        
        for child in node.children:
            self._analyze_node(child)
        
        self.current_scope = self.current_scope.parent or self.global_scope
        
        return 'agent'
    
    def _analyze_contract_def(self, node: ASTNode) -> Optional[str]:
        """Аналізує визначення контракту."""
        name = node.data.get('name', '')
        
        if not name:
            self.errors.append("Contract name required")
            return None
        
        # Перевіряємо унікальність
        if self.global_scope.lookup(name):
            self.errors.append(f"Contract '{name}' already declared")
            return None
        
        symbol = Symbol(name, SymbolKind.CONTRACT, 'contract', node)
        self.global_scope.declare(symbol)
        
        # Аналізуємо вміст контракту
        contract_scope = Scope(f"contract:{name}", self.current_scope)
        self.current_scope = contract_scope
        
        for child in node.children:
            self._analyze_node(child)
        
        self.current_scope = self.current_scope.parent or self.global_scope
        
        return 'contract'
    
    def _analyze_negotiation_def(self, node: ASTNode) -> Optional[str]:
        """Аналізує визначення переговорів."""
        name = node.data.get('name', '')
        
        if not name:
            self.errors.append("Negotiation name required")
            return None
        
        # Перевіряємо унікальність
        if self.global_scope.lookup(name):
            self.errors.append(f"Negotiation '{name}' already declared")
            return None
        
        symbol = Symbol(name, SymbolKind.NEGOTIATION, 'negotiation', node)
        self.global_scope.declare(symbol)
        
        # Аналізуємо вміст переговорів
        negotiation_scope = Scope(f"negotiation:{name}", self.current_scope)
        self.current_scope = negotiation_scope
        
        for child in node.children:
            self._analyze_node(child)
        
        self.current_scope = self.current_scope.parent or self.global_scope
        
        return 'negotiation'
    
    def _analyze_function_call(self, node: ASTNode) -> Optional[str]:
        """Аналізує виклик функції."""
        name = node.data.get('name', '')
        
        if not name:
            self.errors.append("Function name required")
            return None
        
        # Перевіряємо чи функція існує
        symbol = self.current_scope.lookup(name)
        if not symbol and name not in self.builtins:
            self.errors.append(f"Function '{name}' not found")
            return None
        
        # Аналізуємо аргументи
        for child in node.children:
            self._analyze_node(child)
        
        return symbol.type if symbol else 'any'
    
    def _analyze_identifier(self, node: ASTNode) -> Optional[str]:
        """Аналізує ідентифікатор."""
        name = node.data.get('name', '')
        
        if not name:
            return None
        
        # Перевіряємо вбудовані
        if name in self.builtins:
            return self.builtins[name]
        
        # Перевіряємо чи ідентифікатор існує
        symbol = self.current_scope.lookup(name)
        if not symbol:
            self.errors.append(f"Identifier '{name}' not found")
            return None
        
        return symbol.type
    
    def _analyze_print(self, node: ASTNode) -> Optional[str]:
        """Аналізує оператор print."""
        expr = node.data.get('expression', '')
        if expr:
            self._infer_type(expr)
        return None
    
    def _analyze_literal(self, node: ASTNode) -> Optional[str]:
        """Аналізує літерал."""
        value = node.data.get('value')
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, list):
            return 'list'
        elif isinstance(value, dict):
            return 'object'
        return 'any'
    
    def _analyze_binary_op(self, node: ASTNode) -> Optional[str]:
        """Аналізує бінарну операцію."""
        op = node.data.get('operator', '')
        left = node.data.get('left', '')
        right = node.data.get('right', '')
        
        left_type = self._infer_type(left)
        right_type = self._infer_type(right)
        
        # Перевіряємо сумісність типів
        if left_type and right_type and left_type != right_type:
            self.warnings.append(
                f"Type mismatch in binary operation: {left_type} {op} {right_type}"
            )
        
        return left_type or right_type or 'any'
    
    def _analyze_unary_op(self, node: ASTNode) -> Optional[str]:
        """Аналізує унарну операцію."""
        op = node.data.get('operator', '')
        expr = node.data.get('expression', '')
        
        expr_type = self._infer_type(expr)
        
        if op == '!' and expr_type and expr_type not in ['boolean', 'bool']:
            self.warnings.append(f"Logical not on non-boolean: {expr_type}")
        
        return expr_type
    
    def _infer_type(self, expr: str) -> Optional[str]:
        """Визначає тип виразу (спрощено)."""
        if not expr:
            return None
        
        expr = expr.strip()
        
        # Літерали
        if expr in ['true', 'false']:
            return 'boolean'
        if expr == 'None' or expr == 'none':
            return 'null'
        if expr.startswith('"') and expr.endswith('"'):
            return 'string'
        if expr.startswith("'") and expr.endswith("'"):
            return 'string'
        if expr.isdigit():
            return 'integer'
        if self._is_float(expr):
            return 'float'
        if expr.startswith('[') and expr.endswith(']'):
            return 'list'
        if expr.startswith('{') and expr.endswith('}'):
            return 'object'
        if expr.startswith('did:'):
            return 'did'
        
        # Змінні та функції
        if expr in self.builtins:
            return self.builtins[expr]
        
        symbol = self.current_scope.lookup(expr)
        if symbol:
            return symbol.type
        
        return 'any'
    
    def _is_float(self, value: str) -> bool:
        """Перевіряє чи рядок є числом з плаваючою точкою."""
        try:
            float(value)
            return '.' in value
        except ValueError:
            return False
    
    def get_errors(self) -> List[str]:
        """Повертає список помилок."""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Повертає список попереджень."""
        return self.warnings
    
    def get_scope(self) -> Scope:
        """Повертає поточну область видимості."""
        return self.current_scope
    
    def get_global_scope(self) -> Scope:
        """Повертає глобальну область видимості."""
        return self.global_scope
    
    def get_symbols(self) -> Dict[str, Symbol]:
        """Повертає всі символи в поточній області."""
        return self.current_scope.get_local_symbols()
    
    def get_all_symbols(self) -> Dict[str, Symbol]:
        """Повертає всі символи (включаючи батьківські області)."""
        return self.current_scope.get_all_symbols()
    
    def to_dict(self) -> Dict[str, Any]:
        """Експортує стан аналізатора в словник."""
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "global_scope": {
                "name": self.global_scope.name,
                "symbols": {
                    name: {
                        "kind": symbol.kind.value,
                        "type": symbol.type,
                    }
                    for name, symbol in self.global_scope.symbols.items()
                }
            },
            "current_scope": {
                "name": self.current_scope.name,
                "symbols": {
                    name: {
                        "kind": symbol.kind.value,
                        "type": symbol.type,
                    }
                    for name, symbol in self.current_scope.symbols.items()
                }
            },
            "function_stack": self.function_stack,
            "loop_depth": self.loop_depth,
            "imports": list(self.imports),
        }


def analyze(ast: AST) -> bool:
    """Зручна функція для семантичного аналізу."""
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast)


def analyze_with_errors(ast: AST) -> tuple[bool, List[str], List[str]]:
    """Аналізує AST і повертає помилки та попередження."""
    analyzer = SemanticAnalyzer()
    is_valid = analyzer.analyze(ast)
    return is_valid, analyzer.get_errors(), analyzer.get_warnings()