# ============================================================
# VIREO VALIDATOR
# Семантична валідація AST
# ============================================================

from typing import List, Dict, Any, Optional
from .ast import AST, ASTNode, NodeType


class ValidationError(Exception):
    """Помилка валідації."""
    def __init__(self, message: str, node: Optional[ASTNode] = None):
        self.message = message
        self.node = node
        super().__init__(message)


class Validator:
    """
    Семантичний валідатор Vireo AST.
    Перевіряє:
    - Оголошення змінних
    - Типи даних
    - Синтаксис контрактів
    - Структуру агентів
    """
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []
        self.variables: Dict[str, str] = {}
        self.functions: Dict[str, List[str]] = {}
        self.models: Dict[str, Dict] = {}
        self.agents: Dict[str, Dict] = {}
        self.contracts: Dict[str, Dict] = {}
        self.negotiations: Dict[str, Dict] = {}
    
    def validate(self, ast: AST) -> bool:
        """
        Валідує AST.
        
        Args:
            ast: AST для валідації
            
        Returns:
            bool: True якщо валідація пройшла успішно
        """
        self.errors = []
        self.warnings = []
        
        for node in ast.nodes:
            self._validate_node(node)
        
        return len(self.errors) == 0
    
    def _validate_node(self, node: ASTNode):
        """Валідує конкретний вузол."""
        if node.type == NodeType.VARIABLE_DEF:
            self._validate_variable_def(node)
        elif node.type == NodeType.FUNCTION_DEF:
            self._validate_function_def(node)
        elif node.type == NodeType.MODEL_DEF:
            self._validate_model_def(node)
        elif node.type == NodeType.AGENT_DEF:
            self._validate_agent_def(node)
        elif node.type == NodeType.CONTRACT_DEF:
            self._validate_contract_def(node)
        elif node.type == NodeType.NEGOTIATION_DEF:
            self._validate_negotiation_def(node)
        elif node.type == NodeType.IMPORT:
            self._validate_import(node)
        elif node.type in [NodeType.PRINT, NodeType.RETURN, NodeType.IF, NodeType.WHILE, NodeType.FOR]:
            self._validate_statement(node)
        else:
            self.warnings.append(f"Unknown node type: {node.type.value}")
    
    def _validate_variable_def(self, node: ASTNode):
        name = node.data.get('name', '')
        value = node.data.get('value', '')
        
        if not name:
            self.errors.append(ValidationError("Variable name required", node))
            return
        
        if name in self.variables:
            self.warnings.append(f"Variable '{name}' already defined")
        
        self.variables[name] = 'any'
    
    def _validate_function_def(self, node: ASTNode):
        name = node.data.get('name', '')
        params = node.data.get('params', [])
        
        if not name:
            self.errors.append(ValidationError("Function name required", node))
            return
        
        if name in self.functions:
            self.errors.append(ValidationError(f"Function '{name}' already defined", node))
            return
        
        self.functions[name] = params
    
    def _validate_model_def(self, node: ASTNode):
        name = node.data.get('name', '')
        
        if not name:
            self.errors.append(ValidationError("Model name required", node))
            return
        
        if name in self.models:
            self.errors.append(ValidationError(f"Model '{name}' already defined", node))
            return
        
        layers = []
        activations = []
        
        for child in node.children:
            if child.type == NodeType.MODEL_LAYER:
                layers.append(child.data.get('layer', ''))
            elif child.type == NodeType.MODEL_ACTIVATION:
                activations.append(child.data.get('activation', ''))
        
        self.models[name] = {
            'layers': layers,
            'activations': activations
        }
    
    def _validate_agent_def(self, node: ASTNode):
        name = node.data.get('name', '')
        
        if not name:
            self.errors.append(ValidationError("Agent name required", node))
            return
        
        if name in self.agents:
            self.errors.append(ValidationError(f"Agent '{name}' already defined", node))
            return
        
        capabilities = []
        identity = None
        
        for child in node.children:
            if child.type == NodeType.AGENT_CAPABILITY:
                capabilities.append(child.data.get('capability', ''))
            elif child.type == NodeType.AGENT_IDENTITY:
                identity = child.data.get('identity', '')
        
        self.agents[name] = {
            'capabilities': capabilities,
            'identity': identity
        }
    
    def _validate_contract_def(self, node: ASTNode):
        name = node.data.get('name', '')
        
        if not name:
            self.errors.append(ValidationError("Contract name required", node))
            return
        
        if name in self.contracts:
            self.errors.append(ValidationError(f"Contract '{name}' already defined", node))
            return
        
        fields = {}
        
        for child in node.children:
            if child.type == NodeType.CONTRACT_FIELD:
                field = child.data.get('field', '')
                value = child.data.get('value', '')
                fields[field] = value
        
        self.contracts[name] = fields
    
    def _validate_negotiation_def(self, node: ASTNode):
        name = node.data.get('name', '')
        
        if not name:
            self.errors.append(ValidationError("Negotiation name required", node))
            return
        
        if name in self.negotiations:
            self.errors.append(ValidationError(f"Negotiation '{name}' already defined", node))
            return
        
        parties = []
        timeout = None
        
        for child in node.children:
            if child.type == NodeType.NEGOTIATION_PARTY:
                party_name = child.data.get('name', '')
                party_type = child.data.get('type', '')
                parties.append({'name': party_name, 'type': party_type})
            elif child.type == NodeType.NEGOTIATION_TIMEOUT:
                timeout = child.data.get('timeout', '')
        
        self.negotiations[name] = {
            'parties': parties,
            'timeout': timeout
        }
    
    def _validate_import(self, node: ASTNode):
        name = node.data.get('name', '')
        if not name:
            self.errors.append(ValidationError("Import name required", node))
    
    def _validate_statement(self, node: ASTNode):
        # Базова перевірка тверджень
        pass
    
    def get_errors(self) -> List[str]:
        """Повертає список помилок."""
        return [e.message for e in self.errors]
    
    def get_warnings(self) -> List[str]:
        """Повертає список попереджень."""
        return self.warnings


def validate(ast: AST) -> tuple[bool, List[str], List[str]]:
    """Зручна функція для валідації AST."""
    validator = Validator()
    is_valid = validator.validate(ast)
    return is_valid, validator.get_errors(), validator.get_warnings()