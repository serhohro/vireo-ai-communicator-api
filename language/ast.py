# ============================================================
# VIREO AST (Abstract Syntax Tree)
# ============================================================

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


class NodeType(Enum):
    """Типи вузлів AST."""
    # Програма
    PROGRAM = "program"
    
    # Імпорти
    IMPORT = "import"
    
    # Змінні
    VARIABLE_DEF = "variable_def"
    ASSIGN = "assign"
    
    # Функції
    FUNCTION_DEF = "function_def"
    FUNCTION_CALL = "function_call"
    RETURN = "return"
    
    # Контроль потоку
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    FOR = "for"
    
    # Вивід
    PRINT = "print"
    
    # Моделі
    MODEL_DEF = "model_def"
    MODEL_LAYER = "model_layer"
    MODEL_ACTIVATION = "model_activation"
    MODEL_LOSS = "model_loss"
    MODEL_OPTIMIZER = "model_optimizer"
    TRAIN = "train"
    PREDICT = "predict"
    EVALUATE = "evaluate"
    
    # Агенти
    AGENT_DEF = "agent_def"
    AGENT_IDENTITY = "agent_identity"
    AGENT_CAPABILITY = "agent_capability"
    AGENT_ROLE = "agent_role"
    
    # Контракти
    CONTRACT_DEF = "contract_def"
    CONTRACT_FIELD = "contract_field"
    CONTRACT_CONDITION = "contract_condition"
    
    # Переговори
    NEGOTIATION_DEF = "negotiation_def"
    NEGOTIATION_PARTY = "negotiation_party"
    NEGOTIATION_TIMEOUT = "negotiation_timeout"
    NEGOTIATION_MAX_ROUNDS = "negotiation_max_rounds"
    NEGOTIATION_ON_OFFER = "negotiation_on_offer"
    PROPOSE = "propose"
    COMMIT = "commit"
    REJECT = "reject"
    EXECUTE = "execute"
    INFORM = "inform"
    
    # Тензори
    TENSOR = "tensor"
    TENSOR_OP = "tensor_op"
    
    # Блоки
    BLOCK = "block"
    
    # Вирази
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    
    # Помилка
    ERROR = "error"


@dataclass
class ASTNode:
    """Вузол AST."""
    type: NodeType
    data: Dict[str, Any] = field(default_factory=dict)
    children: List['ASTNode'] = field(default_factory=list)
    line: int = 0
    column: int = 0
    
    def add_child(self, child: 'ASTNode'):
        """Додає дочірній вузол."""
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертує вузол у словник."""
        return {
            'type': self.type.value,
            'data': self.data,
            'children': [c.to_dict() for c in self.children],
            'line': self.line,
            'column': self.column
        }
    
    def __repr__(self):
        return f"ASTNode(type={self.type.value}, data={self.data})"


class AST:
    """Abstract Syntax Tree для Vireo."""
    
    def __init__(self):
        self.root = ASTNode(
            type=NodeType.PROGRAM,
            data={'version': '1.4.3'}
        )
        self.nodes: List[ASTNode] = []
    
    def add_node(self, node: ASTNode):
        """Додає вузол до AST."""
        self.nodes.append(node)
        self.root.add_child(node)
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[ASTNode]:
        """Повертає всі вузли заданого типу."""
        return [n for n in self.nodes if n.type == node_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертує AST у словник."""
        return {
            'version': '1.4.3',
            'nodes': [n.to_dict() for n in self.nodes]
        }
    
    def to_json(self) -> str:
        """Конвертує AST у JSON."""
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    def __repr__(self):
        return f"AST(nodes={len(self.nodes)})"