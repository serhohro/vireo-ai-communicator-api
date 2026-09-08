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
    AGENT_TRUST = "agent_trust"
    AGENT_REPUTATION = "agent_reputation"
    
    # Контракти
    CONTRACT_DEF = "contract_def"
    CONTRACT_FIELD = "contract_field"
    CONTRACT_CONDITION = "contract_condition"
    CONTRACT_VERIFY = "contract_verify"
    CONTRACT_INVARIANT = "contract_invariant"
    CONTRACT_ALLOWED_ACTIONS = "contract_allowed_actions"
    CONTRACT_REQUIRED_APPROVALS = "contract_required_approvals"
    
    # Переговори
    NEGOTIATION_DEF = "negotiation_def"
    NEGOTIATION_PARTY = "negotiation_party"
    NEGOTIATION_TIMEOUT = "negotiation_timeout"
    NEGOTIATION_MAX_ROUNDS = "negotiation_max_rounds"
    NEGOTIATION_ON_OFFER = "negotiation_on_offer"
    NEGOTIATION_ON_COMMIT = "negotiation_on_commit"
    NEGOTIATION_ON_VERIFY = "negotiation_on_verify"
    NEGOTIATION_ON_ESCALATE = "negotiation_on_escalate"
    NEGOTIATION_VERIFY_TIMEOUT = "negotiation_verify_timeout"
    
    # Протокол
    PROPOSE = "propose"
    COMMIT = "commit"
    REJECT = "reject"
    EXECUTE = "execute"
    INFORM = "inform"
    VERIFY = "verify"
    ESCALATE = "escalate"
    DONE = "done"
    
    # Тензори
    TENSOR = "tensor"
    TENSOR_OP = "tensor_op"
    TENSOR_ADD = "tensor_add"
    TENSOR_MATMUL = "tensor_matmul"
    TENSOR_TRANSPOSE = "tensor_transpose"
    TENSOR_RESHAPE = "tensor_reshape"
    
    # Безпека
    SECURITY_POLICY = "security_policy"
    ENCRYPTION = "encryption"
    SIGNATURE = "signature"
    VERIFICATION = "verification"
    
    # Типи
    TYPE_ANNOTATION = "type_annotation"
    
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
    type: NodeType
    data: Dict[str, Any] = field(default_factory=dict)
    children: List['ASTNode'] = field(default_factory=list)
    line: int = 0
    column: int = 0
    
    def add_child(self, child: 'ASTNode'):
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, Any]:
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
        self.root = ASTNode(type=NodeType.PROGRAM, data={'version': '3.0.0'})
        self.nodes: List[ASTNode] = []
    
    def add_node(self, node: ASTNode):
        self.nodes.append(node)
        self.root.add_child(node)
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[ASTNode]:
        return [n for n in self.nodes if n.type == node_type]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': '3.0.0',
            'nodes': [n.to_dict() for n in self.nodes]
        }
    
    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    def __repr__(self):
        return f"AST(nodes={len(self.nodes)})"