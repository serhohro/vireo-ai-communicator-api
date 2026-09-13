# ============================================================
# VIREO CODE GENERATOR
# AST → Python
# ============================================================

from typing import List, Dict, Any
from .ast import AST, ASTNode, NodeType


class CodeGenerator:
    """
    Генератор Python коду з AST.
    """
    
    def __init__(self):
        self.indent_level = 0
        self.code_lines = []
        self.variables = {}
        self.functions = {}
    
    def generate(self, ast: AST) -> str:
        """
        Генерує Python код з AST.
        
        Args:
            ast: AST Vireo програми
            
        Returns:
            str: Python код
        """
        self.code_lines = []
        self.indent_level = 0
        
        # Додаємо заголовок
        self.code_lines.append('# Generated from Vireo code')
        self.code_lines.append('# Vireo v1.4.3')
        self.code_lines.append('')
        
        # Генеруємо код для кожного вузла
        for node in ast.nodes:
            self._generate_node(node)
        
        return '\n'.join(self.code_lines)
    
    def _generate_node(self, node: ASTNode):
        """Генерує код для конкретного вузла."""
        if node.type == NodeType.IMPORT:
            self._generate_import(node)
        elif node.type == NodeType.VARIABLE_DEF:
            self._generate_variable_def(node)
        elif node.type == NodeType.FUNCTION_DEF:
            self._generate_function_def(node)
        elif node.type == NodeType.PRINT:
            self._generate_print(node)
        elif node.type == NodeType.RETURN:
            self._generate_return(node)
        elif node.type == NodeType.IF:
            self._generate_if(node)
        elif node.type == NodeType.WHILE:
            self._generate_while(node)
        elif node.type == NodeType.FOR:
            self._generate_for(node)
        elif node.type == NodeType.MODEL_DEF:
            self._generate_model_def(node)
        elif node.type == NodeType.AGENT_DEF:
            self._generate_agent_def(node)
        elif node.type == NodeType.CONTRACT_DEF:
            self._generate_contract_def(node)
        elif node.type == NodeType.NEGOTIATION_DEF:
            self._generate_negotiation_def(node)
        else:
            self.code_lines.append(f'# TODO: {node.type.value}')
    
    def _indent(self) -> str:
        """Повертає відступ для поточного рівня."""
        return '    ' * self.indent_level
    
    def _generate_import(self, node: ASTNode):
        name = node.data.get('name', '')
        self.code_lines.append(f'import {name}')
    
    def _generate_variable_def(self, node: ASTNode):
        name = node.data.get('name', '')
        value = node.data.get('value', '')
        self.variables[name] = value
        self.code_lines.append(f'{self._indent()}{name} = {value}')
    
    def _generate_print(self, node: ASTNode):
        expr = node.data.get('expression', '')
        self.code_lines.append(f'{self._indent()}print({expr})')
    
    def _generate_return(self, node: ASTNode):
        expr = node.data.get('expression', '')
        self.code_lines.append(f'{self._indent()}return {expr}')
    
    def _generate_if(self, node: ASTNode):
        condition = node.data.get('condition', '')
        self.code_lines.append(f'{self._indent()}if {condition}:')
        self.indent_level += 1
        for child in node.children:
            self._generate_node(child)
        self.indent_level -= 1
    
    def _generate_while(self, node: ASTNode):
        condition = node.data.get('condition', '')
        self.code_lines.append(f'{self._indent()}while {condition}:')
        self.indent_level += 1
        for child in node.children:
            self._generate_node(child)
        self.indent_level -= 1
    
    def _generate_for(self, node: ASTNode):
        var = node.data.get('var', '')
        collection = node.data.get('collection', '')
        self.code_lines.append(f'{self._indent()}for {var} in {collection}:')
        self.indent_level += 1
        for child in node.children:
            self._generate_node(child)
        self.indent_level -= 1
    
    def _generate_function_def(self, node: ASTNode):
        name = node.data.get('name', '')
        params = node.data.get('params', [])
        params_str = ', '.join(params) if params else ''
        self.functions[name] = params
        self.code_lines.append(f'{self._indent()}def {name}({params_str}):')
        self.indent_level += 1
        for child in node.children:
            self._generate_node(child)
        self.indent_level -= 1
    
    def _generate_model_def(self, node: ASTNode):
        name = node.data.get('name', '')
        self.code_lines.append(f'{self._indent()}# Model: {name}')
        self.code_lines.append(f'{self._indent()}class {name}Model:')
        self.indent_level += 1
        self.code_lines.append(f'{self._indent()}def __init__(self):')
        self.indent_level += 1
        self.code_lines.append(f'{self._indent()}self.layers = []')
        
        for child in node.children:
            if child.type == NodeType.MODEL_LAYER:
                layer_data = child.data.get('layer', '')
                self.code_lines.append(f'{self._indent()}self.layers.append({layer_data})')
            elif child.type == NodeType.MODEL_ACTIVATION:
                act = child.data.get('activation', '')
                self.code_lines.append(f'{self._indent()}self.activation = "{act}"')
        
        self.indent_level -= 2
    
    def _generate_agent_def(self, node: ASTNode):
        name = node.data.get('name', '')
        self.code_lines.append(f'{self._indent()}# Agent: {name}')
        self.code_lines.append(f'{self._indent()}class {name}Agent:')
        self.indent_level += 1
        self.code_lines.append(f'{self._indent()}def __init__(self):')
        self.indent_level += 1
        self.code_lines.append(f'{self._indent()}self.id = "{name}"')
        self.code_lines.append(f'{self._indent()}self.capabilities = []')
        
        for child in node.children:
            if child.type == NodeType.AGENT_IDENTITY:
                identity = child.data.get('identity', '')
                self.code_lines.append(f'{self._indent()}self.identity = "{identity}"')
            elif child.type == NodeType.AGENT_CAPABILITY:
                cap = child.data.get('capability', '')
                self.code_lines.append(f'{self._indent()}self.capabilities.append("{cap}")')
        
        self.indent_level -= 2
    
    def _generate_contract_def(self, node: ASTNode):
        name = node.data.get('name', '')
        self.code_lines.append(f'{self._indent()}# Contract: {name}')
        self.code_lines.append(f'{self._indent()}class {name}Contract:')
        self.indent_level += 1
        self.code_lines.append(f'{self._indent()}def __init__(self):')
        self.indent_level += 1
        
        for child in node.children:
            if child.type == NodeType.CONTRACT_FIELD:
                field_name = child.data.get('field', '')
                field_value = child.data.get('value', '')
                self.code_lines.append(f'{self._indent()}self.{field_name} = {field_value}')
        
        self.indent_level -= 2
    
    def _generate_negotiation_def(self, node: ASTNode):
        name = node.data.get('name', '')
        self.code_lines.append(f'{self._indent()}# Negotiation: {name}')
        self.code_lines.append(f'{self._indent()}class {name}Negotiation:')
        self.indent_level += 1
        self.code_lines.append(f'{self._indent()}def __init__(self):')
        self.indent_level += 1
        
        for child in node.children:
            if child.type == NodeType.NEGOTIATION_PARTY:
                party_name = child.data.get('name', '')
                party_type = child.data.get('type', '')
                self.code_lines.append(f'{self._indent()}self.{party_name} = "{party_type}"')
            elif child.type == NodeType.NEGOTIATION_TIMEOUT:
                timeout = child.data.get('timeout', '')
                self.code_lines.append(f'{self._indent()}self.timeout = {timeout}')
        
        self.indent_level -= 2


def generate_code(ast: AST) -> str:
    """Зручна функція для генерації Python коду."""
    generator = CodeGenerator()
    return generator.generate(ast)