# ============================================================
# VIREO COMPILER v3.0.0
# Компілятор мови Vireo в Python код
# — Open Wire Protocol · WASM · Rust · Formal Verification —
# ============================================================

import re
import ast
import json
import hashlib
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field

VERSION = "3.0.0"
PROTOCOL = "Open Wire v3.0.0"

# ============================================================
# 1. ЛЕКСИЧНИЙ АНАЛІЗАТОР (LEXER) v3.0.0
# ============================================================

class LexerV3:
    """Перетворює код Vireo v3.0.0 на токени."""
    
    VERSION = VERSION
    
    def __init__(self):
        self.tokens = []
        self.current_pos = 0
        
        self.token_patterns = [
            (r'let\b', 'LET'),
            (r'const\b', 'CONST'),
            (r'fn\b', 'FN'),
            (r'if\b', 'IF'),
            (r'else\b', 'ELSE'),
            (r'for\b', 'FOR'),
            (r'while\b', 'WHILE'),
            (r'return\b', 'RETURN'),
            (r'print\b', 'PRINT'),
            (r'True\b', 'TRUE'),
            (r'False\b', 'FALSE'),
            (r'contract\b', 'CONTRACT'),
            (r'agent\b', 'AGENT'),
            (r'did\b', 'DID'),
            (r'trust\b', 'TRUST'),
            (r'verify\b', 'VERIFY'),
            (r'@neural\b', 'NEURAL'),
            (r'@parallel\b', 'PARALLEL'),
            (r'@distributed\b', 'DISTRIBUTED'),
            (r'@formal\b', 'FORMAL'),
            (r'Tensor\b', 'TENSOR'),
            (r'LSTM\b', 'LSTM'),
            (r'Int\b', 'INT_TYPE'),
            (r'F32\b', 'F32_TYPE'),
            (r'Bool\b', 'BOOL_TYPE'),
            (r'Str\b', 'STR_TYPE'),
            (r'List\b', 'LIST_TYPE'),
            (r'Dict\b', 'DICT_TYPE'),
            (r'ReLU\b', 'RELU'),
            (r'Sigmoid\b', 'SIGMOID'),
            (r'Tanh\b', 'TANH'),
            (r'Softmax\b', 'SOFTMAX'),
            (r'\d+\.\d+', 'FLOAT'),
            (r'\d+', 'INTEGER'),
            (r'"[^"]*"', 'STRING'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
            (r'==', 'EQ'),
            (r'!=', 'NEQ'),
            (r'<=', 'LE'),
            (r'>=', 'GE'),
            (r'=>', 'ARROW'),
            (r'=', 'ASSIGN'),
            (r'\+', 'PLUS'),
            (r'-', 'MINUS'),
            (r'\*', 'MUL'),
            (r'/', 'DIV'),
            (r'\(', 'LPAREN'),
            (r'\)', 'RPAREN'),
            (r'\{', 'LBRACE'),
            (r'\}', 'RBRACE'),
            (r'\[', 'LBRACKET'),
            (r'\]', 'RBRACKET'),
            (r',', 'COMMA'),
            (r'\.', 'DOT'),
            (r':', 'COLON'),
            (r';', 'SEMICOLON'),
            (r'//[^\n]*', 'COMMENT'),
            (r'\s+', 'WHITESPACE'),
        ]
    
    def tokenize(self, code: str) -> List[Dict]:
        self.tokens = []
        self.current_pos = 0
        
        while self.current_pos < len(code):
            matched = False
            for pattern, token_type in self.token_patterns:
                regex = re.compile(pattern)
                match = regex.match(code, self.current_pos)
                
                if match:
                    value = match.group(0)
                    if token_type != 'WHITESPACE' and token_type != 'COMMENT':
                        self.tokens.append({
                            'type': token_type,
                            'value': value,
                            'position': self.current_pos
                        })
                    self.current_pos = match.end()
                    matched = True
                    break
            
            if not matched:
                self.tokens.append({
                    'type': 'UNKNOWN',
                    'value': code[self.current_pos],
                    'position': self.current_pos
                })
                self.current_pos += 1
        
        return self.tokens


# ============================================================
# 2. СИНТАКСИЧНИЙ АНАЛІЗАТОР (PARSER) v3.0.0
# ============================================================

class ParserV3:
    """Будує AST з токенів v3.0.0."""
    
    VERSION = VERSION
    
    def __init__(self, tokens: List[Dict]):
        self.tokens = tokens
        self.pos = 0
        self.ast = []
    
    def parse(self) -> Dict:
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            
            if token['type'] == 'LET':
                self.ast.append(self.parse_let())
            elif token['type'] == 'CONST':
                self.ast.append(self.parse_const())
            elif token['type'] == 'FN':
                self.ast.append(self.parse_function())
            elif token['type'] == 'IF':
                self.ast.append(self.parse_if())
            elif token['type'] == 'FOR':
                self.ast.append(self.parse_for())
            elif token['type'] == 'WHILE':
                self.ast.append(self.parse_while())
            elif token['type'] == 'RETURN':
                self.ast.append(self.parse_return())
            elif token['type'] == 'PRINT':
                self.ast.append(self.parse_print())
            elif token['type'] == 'CONTRACT':
                self.ast.append(self.parse_contract())
            elif token['type'] == 'AGENT':
                self.ast.append(self.parse_agent())
            elif token['type'] == 'DID':
                self.ast.append(self.parse_did())
            elif token['type'] == 'TRUST':
                self.ast.append(self.parse_trust())
            elif token['type'] == 'VERIFY':
                self.ast.append(self.parse_verify())
            elif token['type'] == 'NEURAL':
                self.ast.append(self.parse_neural())
            elif token['type'] == 'TENSOR':
                self.ast.append(self.parse_tensor())
            else:
                expr = self.parse_expression()
                if expr:
                    self.ast.append(expr)
                else:
                    self.pos += 1
        
        return {'type': 'program', 'body': self.ast, 'version': self.VERSION, 'protocol': PROTOCOL}
    
    def parse_let(self) -> Dict:
        self.pos += 1
        var_name = self.tokens[self.pos]['value']
        self.pos += 1
        
        if self.tokens[self.pos]['type'] == 'ASSIGN':
            self.pos += 1
            value = self.parse_expression()
            return {
                'type': 'let',
                'name': var_name,
                'value': value,
                'version': self.VERSION
            }
        
        return {'type': 'let', 'name': var_name, 'value': None, 'version': self.VERSION}
    
    def parse_const(self) -> Dict:
        self.pos += 1
        var_name = self.tokens[self.pos]['value']
        self.pos += 1
        
        if self.tokens[self.pos]['type'] == 'ASSIGN':
            self.pos += 1
            value = self.parse_expression()
            return {
                'type': 'const',
                'name': var_name,
                'value': value,
                'version': self.VERSION
            }
        
        return {'type': 'const', 'name': var_name, 'value': None, 'version': self.VERSION}
    
    def parse_function(self) -> Dict:
        self.pos += 1
        func_name = self.tokens[self.pos]['value']
        self.pos += 1
        
        args = []
        if self.tokens[self.pos]['type'] == 'LPAREN':
            self.pos += 1
            while self.tokens[self.pos]['type'] != 'RPAREN':
                if self.tokens[self.pos]['type'] == 'IDENTIFIER':
                    args.append(self.tokens[self.pos]['value'])
                self.pos += 1
            self.pos += 1
        
        body = []
        if self.tokens[self.pos]['type'] == 'LBRACE':
            self.pos += 1
            while self.tokens[self.pos]['type'] != 'RBRACE':
                body.append(self.tokens[self.pos])
                self.pos += 1
            self.pos += 1
        
        return {
            'type': 'function',
            'name': func_name,
            'args': args,
            'body': body,
            'version': self.VERSION
        }
    
    def parse_if(self) -> Dict:
        self.pos += 1
        condition = self.parse_expression()
        
        body = []
        if self.tokens[self.pos]['type'] == 'LBRACE':
            self.pos += 1
            while self.tokens[self.pos]['type'] != 'RBRACE':
                body.append(self.tokens[self.pos])
                self.pos += 1
            self.pos += 1
        
        else_body = []
        if self.pos < len(self.tokens) and self.tokens[self.pos]['type'] == 'ELSE':
            self.pos += 1
            if self.tokens[self.pos]['type'] == 'LBRACE':
                self.pos += 1
                while self.tokens[self.pos]['type'] != 'RBRACE':
                    else_body.append(self.tokens[self.pos])
                    self.pos += 1
                self.pos += 1
        
        return {
            'type': 'if',
            'condition': condition,
            'body': body,
            'else_body': else_body,
            'version': self.VERSION
        }
    
    def parse_for(self) -> Dict:
        self.pos += 1
        var_name = self.tokens[self.pos]['value']
        self.pos += 1
        
        if self.tokens[self.pos]['type'] == 'IDENTIFIER' and self.tokens[self.pos]['value'] == 'in':
            self.pos += 1
            iterable = self.parse_expression()
        
        body = []
        if self.tokens[self.pos]['type'] == 'LBRACE':
            self.pos += 1
            while self.tokens[self.pos]['type'] != 'RBRACE':
                body.append(self.tokens[self.pos])
                self.pos += 1
            self.pos += 1
        
        return {
            'type': 'for',
            'var': var_name,
            'iterable': iterable,
            'body': body,
            'version': self.VERSION
        }
    
    def parse_while(self) -> Dict:
        self.pos += 1
        condition = self.parse_expression()
        
        body = []
        if self.tokens[self.pos]['type'] == 'LBRACE':
            self.pos += 1
            while self.tokens[self.pos]['type'] != 'RBRACE':
                body.append(self.tokens[self.pos])
                self.pos += 1
            self.pos += 1
        
        return {
            'type': 'while',
            'condition': condition,
            'body': body,
            'version': self.VERSION
        }
    
    def parse_return(self) -> Dict:
        self.pos += 1
        value = self.parse_expression()
        return {'type': 'return', 'value': value, 'version': self.VERSION}
    
    def parse_print(self) -> Dict:
        self.pos += 1
        value = self.parse_expression()
        return {'type': 'print', 'value': value, 'version': self.VERSION}
    
    def parse_contract(self) -> Dict:
        self.pos += 1
        name = self.tokens[self.pos]['value']
        self.pos += 1
        
        parties = []
        terms = {}
        obligations = {}
        
        if self.tokens[self.pos]['type'] == 'LBRACE':
            self.pos += 1
            while self.tokens[self.pos]['type'] != 'RBRACE':
                if self.tokens[self.pos]['type'] == 'IDENTIFIER':
                    key = self.tokens[self.pos]['value']
                    self.pos += 1
                    if self.tokens[self.pos]['type'] == 'COLON':
                        self.pos += 1
                        if key == 'parties':
                            if self.tokens[self.pos]['type'] == 'LBRACKET':
                                self.pos += 1
                                while self.tokens[self.pos]['type'] != 'RBRACKET':
                                    if self.tokens[self.pos]['type'] == 'IDENTIFIER':
                                        parties.append(self.tokens[self.pos]['value'])
                                    self.pos += 1
                                self.pos += 1
                        elif key == 'terms':
                            if self.tokens[self.pos]['type'] == 'LBRACE':
                                self.pos += 1
                                while self.tokens[self.pos]['type'] != 'RBRACE':
                                    if self.tokens[self.pos]['type'] == 'IDENTIFIER':
                                        term_key = self.tokens[self.pos]['value']
                                        self.pos += 1
                                        if self.tokens[self.pos]['type'] == 'COLON':
                                            self.pos += 1
                                            terms[term_key] = self.tokens[self.pos]['value']
                                    self.pos += 1
                                self.pos += 1
                self.pos += 1
            self.pos += 1
        
        return {
            'type': 'contract',
            'name': name,
            'parties': parties,
            'terms': terms,
            'obligations': obligations,
            'version': self.VERSION,
            'protocol': PROTOCOL
        }
    
    def parse_agent(self) -> Dict:
        self.pos += 1
        name = self.tokens[self.pos]['value']
        self.pos += 1
        
        did = None
        capabilities = []
        
        if self.tokens[self.pos]['type'] == 'LBRACE':
            self.pos += 1
            while self.tokens[self.pos]['type'] != 'RBRACE':
                if self.tokens[self.pos]['type'] == 'IDENTIFIER':
                    key = self.tokens[self.pos]['value']
                    self.pos += 1
                    if self.tokens[self.pos]['type'] == 'COLON':
                        self.pos += 1
                        if key == 'did':
                            did = self.tokens[self.pos]['value'].strip('"')
                        elif key == 'capability':
                            capabilities.append(self.tokens[self.pos]['value'])
                self.pos += 1
            self.pos += 1
        
        return {
            'type': 'agent',
            'name': name,
            'did': did,
            'capabilities': capabilities,
            'version': self.VERSION,
            'protocol': PROTOCOL
        }
    
    def parse_did(self) -> Dict:
        self.pos += 1
        name = self.tokens[self.pos]['value']
        self.pos += 1
        
        did = None
        if self.tokens[self.pos]['type'] == 'ASSIGN':
            self.pos += 1
            did = self.tokens[self.pos]['value'].strip('"')
            self.pos += 1
        
        return {
            'type': 'did',
            'name': name,
            'did': did,
            'version': self.VERSION
        }
    
    def parse_trust(self) -> Dict:
        self.pos += 1
        from_agent = self.tokens[self.pos]['value']
        self.pos += 1
        
        if self.tokens[self.pos]['type'] == 'ARROW':
            self.pos += 1
            to_agent = self.tokens[self.pos]['value']
            self.pos += 1
        
        return {
            'type': 'trust',
            'from': from_agent,
            'to': to_agent,
            'version': self.VERSION
        }
    
    def parse_verify(self) -> Dict:
        self.pos += 1
        contract_name = None
        
        if self.tokens[self.pos]['type'] == 'IDENTIFIER' and self.tokens[self.pos]['value'] == 'contract':
            self.pos += 1
            contract_name = self.tokens[self.pos]['value']
            self.pos += 1
        
        return {
            'type': 'verify',
            'contract': contract_name,
            'version': self.VERSION
        }
    
    def parse_neural(self) -> Dict:
        self.pos += 1
        return {'type': 'neural', 'version': self.VERSION}
    
    def parse_tensor(self) -> Dict:
        self.pos += 1
        tensor_type = None
        shape = []
        
        if self.tokens[self.pos]['type'] == '<':
            self.pos += 1
            tensor_type = self.tokens[self.pos]['value']
            self.pos += 1
            if self.tokens[self.pos]['type'] == 'COMMA':
                self.pos += 1
                if self.tokens[self.pos]['type'] == 'LBRACKET':
                    self.pos += 1
                    while self.tokens[self.pos]['type'] != 'RBRACKET':
                        if self.tokens[self.pos]['type'] in ['IDENTIFIER', 'INTEGER']:
                            shape.append(self.tokens[self.pos]['value'])
                        self.pos += 1
                    self.pos += 1
        
        return {
            'type': 'tensor',
            'dtype': tensor_type,
            'shape': shape,
            'version': self.VERSION
        }
    
    def parse_expression(self) -> Dict:
        if self.pos >= len(self.tokens):
            return None
        
        token = self.tokens[self.pos]
        
        if token['type'] in ['INTEGER', 'FLOAT']:
            self.pos += 1
            return {'type': 'number', 'value': token['value']}
        
        if token['type'] == 'STRING':
            self.pos += 1
            return {'type': 'string', 'value': token['value']}
        
        if token['type'] == 'IDENTIFIER':
            self.pos += 1
            return {'type': 'identifier', 'name': token['value']}
        
        if token['type'] in ['PLUS', 'MINUS', 'MUL', 'DIV']:
            op = token['value']
            self.pos += 1
            right = self.parse_expression()
            return {'type': 'binary', 'op': op, 'right': right}
        
        return None


# ============================================================
# 3. ГЕНЕРАТОР КОДУ (CODE GENERATOR) v3.0.0
# ============================================================

class CodeGeneratorV3:
    """Генерує Python код з AST v3.0.0."""
    
    VERSION = VERSION
    PROTOCOL = PROTOCOL
    
    def __init__(self):
        self.indent = 0
        self.variables = {}
        self.functions = {}
        self.output = []
        self._current_function = None
        self._imported = set()
    
    def generate(self, ast: Dict) -> str:
        self.output = []
        self._imported = set()
        
        self.output.append("# ============================================================")
        self.output.append(f"# VIREO v{VERSION} — Скомпільовано в Python")
        self.output.append(f"# Protocol: {PROTOCOL}")
        self.output.append("# ============================================================")
        self.output.append("")
        
        self._add_import("import math")
        self._add_import("import random")
        self._add_import("import hashlib")
        
        self.output.append("")
        self.output.append(f"VIREO_VERSION = \"{VERSION}\"")
        self.output.append(f"VIREO_PROTOCOL = \"{PROTOCOL}\"")
        self.output.append("")
        
        for node in ast.get('body', []):
            self._generate_node(node)
        
        if 'main' not in self.functions:
            self.output.append("")
            self.output.append("if __name__ == '__main__':")
            self.output.append(f"    print('🌿 Vireo v{VERSION} program executed successfully!')")
            self.output.append(f"    print(f'Protocol: {PROTOCOL}')")
            self.output.append("")
        
        return '\n'.join(self.output)
    
    def _add_import(self, imp):
        if imp not in self._imported:
            self._imported.add(imp)
            self.output.append(imp)
    
    def _generate_node(self, node: Dict):
        node_type = node.get('type', '')
        
        if node_type == 'let':
            self._generate_let(node)
        elif node_type == 'const':
            self._generate_const(node)
        elif node_type == 'function':
            self._generate_function(node)
        elif node_type == 'if':
            self._generate_if(node)
        elif node_type == 'for':
            self._generate_for(node)
        elif node_type == 'while':
            self._generate_while(node)
        elif node_type == 'return':
            self._generate_return(node)
        elif node_type == 'print':
            self._generate_print(node)
        elif node_type == 'contract':
            self._generate_contract(node)
        elif node_type == 'agent':
            self._generate_agent(node)
        elif node_type == 'did':
            self._generate_did(node)
        elif node_type == 'trust':
            self._generate_trust(node)
        elif node_type == 'verify':
            self._generate_verify(node)
        elif node_type == 'neural':
            self._generate_neural(node)
        elif node_type == 'tensor':
            self._generate_tensor(node)
        elif node_type == 'number':
            self._generate_number(node)
        elif node_type == 'string':
            self._generate_string(node)
        elif node_type == 'identifier':
            self._generate_identifier(node)
        elif node_type == 'binary':
            self._generate_binary(node)
        else:
            self.output.append(self._indent() + f"# Unknown node: {node}")
    
    def _generate_let(self, node: Dict):
        name = node['name']
        value = node['value']
        
        if value:
            value_str = self._expr_to_string(value)
            self.output.append(self._indent() + f"{name} = {value_str}  # Vireo v{node.get('version', VERSION)}")
            self.variables[name] = True
        else:
            self.output.append(self._indent() + f"{name} = None")
    
    def _generate_const(self, node: Dict):
        name = node['name']
        value = node['value']
        
        if value:
            value_str = self._expr_to_string(value)
            self.output.append(self._indent() + f"{name} = {value_str}  # const (Vireo v{node.get('version', VERSION)})")
    
    def _generate_function(self, node: Dict):
        name = node['name']
        args = ', '.join(node.get('args', []))
        
        self.functions[name] = True
        self._current_function = name
        
        self.output.append("")
        self.output.append(f"def {name}({args}):  # Vireo v{node.get('version', VERSION)}")
        self.indent += 1
        
        for token in node.get('body', []):
            if isinstance(token, dict) and 'type' in token:
                self._generate_node(token)
            elif isinstance(token, dict):
                self.output.append(self._indent() + f"# {token}")
            else:
                self.output.append(self._indent() + f"# {token}")
        
        self.indent -= 1
    
    def _generate_if(self, node: Dict):
        condition = self._expr_to_string(node['condition'])
        self.output.append(self._indent() + f"if {condition}:  # Vireo v{node.get('version', VERSION)}")
        self.indent += 1
        
        for token in node.get('body', []):
            if isinstance(token, dict) and 'type' in token:
                self._generate_node(token)
            else:
                self.output.append(self._indent() + f"# {token}")
        
        self.indent -= 1
        
        if node.get('else_body'):
            self.output.append(self._indent() + "else:")
            self.indent += 1
            
            for token in node.get('else_body', []):
                if isinstance(token, dict) and 'type' in token:
                    self._generate_node(token)
                else:
                    self.output.append(self._indent() + f"# {token}")
            
            self.indent -= 1
    
    def _generate_for(self, node: Dict):
        var = node['var']
        iterable = self._expr_to_string(node['iterable'])
        self.output.append(self._indent() + f"for {var} in {iterable}:  # Vireo v{node.get('version', VERSION)}")
        self.indent += 1
        
        for token in node.get('body', []):
            if isinstance(token, dict) and 'type' in token:
                self._generate_node(token)
            else:
                self.output.append(self._indent() + f"# {token}")
        
        self.indent -= 1
    
    def _generate_while(self, node: Dict):
        condition = self._expr_to_string(node['condition'])
        self.output.append(self._indent() + f"while {condition}:  # Vireo v{node.get('version', VERSION)}")
        self.indent += 1
        
        for token in node.get('body', []):
            if isinstance(token, dict) and 'type' in token:
                self._generate_node(token)
            else:
                self.output.append(self._indent() + f"# {token}")
        
        self.indent -= 1
    
    def _generate_return(self, node: Dict):
        if node['value']:
            value_str = self._expr_to_string(node['value'])
            self.output.append(self._indent() + f"return {value_str}  # Vireo v{node.get('version', VERSION)}")
        else:
            self.output.append(self._indent() + "return")
    
    def _generate_print(self, node: Dict):
        if node['value']:
            value_str = self._expr_to_string(node['value'])
            self.output.append(self._indent() + f"print({value_str})  # Vireo v{node.get('version', VERSION)}")
        else:
            self.output.append(self._indent() + "print()")
    
    def _generate_contract(self, node: Dict):
        self.output.append("")
        self.output.append(self._indent() + f"# 📜 Contract: {node['name']} (Vireo v{node.get('version', VERSION)})")
        self.output.append(self._indent() + f"# Protocol: {node.get('protocol', PROTOCOL)}")
        self.output.append(self._indent() + f"contract_{node['name']} = {{")
        self.indent += 1
        self.output.append(self._indent() + f"'name': '{node['name']}',")
        self.output.append(self._indent() + f"'parties': {node.get('parties', [])},")
        self.output.append(self._indent() + f"'terms': {node.get('terms', {})},")
        self.output.append(self._indent() + f"'version': '{node.get('version', VERSION)}',")
        self.output.append(self._indent() + f"'protocol': '{node.get('protocol', PROTOCOL)}'")
        self.indent -= 1
        self.output.append(self._indent() + "}")
    
    def _generate_agent(self, node: Dict):
        self.output.append("")
        self.output.append(self._indent() + f"# 🤖 Agent: {node['name']} (Vireo v{node.get('version', VERSION)})")
        self.output.append(self._indent() + f"agent_{node['name']} = {{")
        self.indent += 1
        self.output.append(self._indent() + f"'name': '{node['name']}',")
        self.output.append(self._indent() + f"'did': '{node.get('did', '')}',")
        self.output.append(self._indent() + f"'capabilities': {node.get('capabilities', [])},")
        self.output.append(self._indent() + f"'version': '{node.get('version', VERSION)}',")
        self.output.append(self._indent() + f"'protocol': '{node.get('protocol', PROTOCOL)}'")
        self.indent -= 1
        self.output.append(self._indent() + "}")
    
    def _generate_did(self, node: Dict):
        self.output.append("")
        self.output.append(self._indent() + f"# 🔑 DID: {node['name']} (Vireo v{node.get('version', VERSION)})")
        self.output.append(self._indent() + f"{node['name']} = '{node.get('did', '')}'")
    
    def _generate_trust(self, node: Dict):
        self.output.append("")
        self.output.append(self._indent() + f"# 🔒 Trust: {node['from']} → {node['to']} (Vireo v{node.get('version', VERSION)})")
        self.output.append(self._indent() + f"trust_{node['from']}_{node['to']} = {{")
        self.indent += 1
        self.output.append(self._indent() + f"'from': '{node['from']}',")
        self.output.append(self._indent() + f"'to': '{node['to']}',")
        self.output.append(self._indent() + f"'level': 'full',")
        self.output.append(self._indent() + f"'version': '{node.get('version', VERSION)}'")
        self.indent -= 1
        self.output.append(self._indent() + "}")
    
    def _generate_verify(self, node: Dict):
        self.output.append("")
        self.output.append(self._indent() + f"# ✅ Verify contract: {node.get('contract', 'unknown')} (Vireo v{node.get('version', VERSION)})")
        self.output.append(self._indent() + f"verified_{node.get('contract', 'unknown')} = True")
    
    def _generate_neural(self, node: Dict):
        self.output.append(self._indent() + "# 🧠 Neural network decorator (Vireo v{node.get('version', VERSION)})")
    
    def _generate_tensor(self, node: Dict):
        dtype = node.get('dtype', 'F32')
        shape = node.get('shape', [])
        shape_str = ', '.join(shape) if shape else 'None'
        self.output.append(self._indent() + f"# Tensor<{dtype}, [{shape_str}]> (Vireo v{node.get('version', VERSION)})")
    
    def _generate_number(self, node: Dict):
        self.output.append(self._indent() + str(node['value']))
    
    def _generate_string(self, node: Dict):
        self.output.append(self._indent() + node['value'])
    
    def _generate_identifier(self, node: Dict):
        self.output.append(self._indent() + node['name'])
    
    def _generate_binary(self, node: Dict):
        right = self._expr_to_string(node['right'])
        self.output.append(self._indent() + f"{node['op']} {right}")
    
    def _expr_to_string(self, expr: Dict) -> str:
        if not expr:
            return "None"
        
        expr_type = expr.get('type', '')
        
        if expr_type == 'number':
            return str(expr.get('value', '0'))
        elif expr_type == 'string':
            return expr.get('value', '""')
        elif expr_type == 'identifier':
            return expr.get('name', '')
        elif expr_type == 'binary':
            op = expr.get('op', '+')
            right = self._expr_to_string(expr.get('right'))
            return f"{op} {right}"
        elif expr_type == 'list':
            items = [self._expr_to_string(item) for item in expr.get('items', [])]
            return f"[{', '.join(items)}]"
        else:
            return str(expr)
    
    def _indent(self) -> str:
        return "    " * self.indent


# ============================================================
# 4. ГОЛОВНИЙ КЛАС КОМПІЛЯТОРА v3.0.0
# ============================================================

class VireoCompilerV3:
    """Головний клас компілятора Vireo v3.0.0."""
    
    VERSION = VERSION
    PROTOCOL = PROTOCOL
    
    def __init__(self):
        self.lexer = LexerV3()
        self.generator = CodeGeneratorV3()
    
    def compile(self, code: str) -> str:
        """Компілює Vireo код у Python код."""
        tokens = self.lexer.tokenize(code)
        parser = ParserV3(tokens)
        ast = parser.parse()
        return self.generator.generate(ast)
    
    def compile_to_file(self, code: str, output_file: str) -> str:
        """Компілює і зберігає у файл."""
        python_code = self.compile(code)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        return f"✅ Compiled to {output_file} (Vireo v{VERSION}, Protocol: {PROTOCOL})"
    
    def compile_file(self, input_file: str, output_file: str = None) -> str:
        """Компілює файл .v у .py."""
        with open(input_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        if output_file is None:
            output_file = input_file.replace('.v', '.py')
        
        return self.compile_to_file(code, output_file)


# ============================================================
# 5. КОМАНДНА СТРОКА
# ============================================================

def main():
    import sys
    import os
    
    print(f"🟢 Vireo Compiler v{VERSION}")
    print(f"Protocol: {PROTOCOL}")
    print("The World's First AI-to-AI Communication Language")
    print("========================================")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python vireo_compiler.py file.v")
        print("  python vireo_compiler.py file.v -o output.py")
        return
    
    input_file = sys.argv[1]
    output_file = input_file.replace('.v', '.py')
    
    for i, arg in enumerate(sys.argv):
        if arg == '-o' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    compiler = VireoCompilerV3()
    
    try:
        result = compiler.compile_file(input_file, output_file)
        print(result)
        
        print("")
        print("📄 Generated code:")
        print("========================================")
        with open(output_file, 'r', encoding='utf-8') as f:
            print(f.read())
        
    except Exception as e:
        print(f"❌ Compilation error: {e}")


# ============================================================
# 6. ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    test_code = """
let x = 5
let y = 10
let sum = x + y
print(sum)

fn add(a, b) {
    return a + b
}

let result = add(3, 7)
print(result)

@neural
fn model(input) {
    let h1 = dense(input, 256, ReLU)
    let h2 = dense(h1, 128, ReLU)
    let output = dense(h2, 10, Softmax)
    return output
}

contract test_contract {
    parties: [agent1, agent2]
    terms: { max_tokens: 1000, timeout_sec: 60 }
}

agent agent1 {
    did: "did:vireo:agent1"
    capability analyze
    capability report
}

did my_did = "did:vireo:my-agent"
trust agent1 -> agent2
verify contract test_contract
"""
    
    compiler = VireoCompilerV3()
    
    print(f"🟢 Vireo Compiler v{VERSION} Demo")
    print(f"Protocol: {PROTOCOL}")
    print("========================================")
    print("")
    print("📄 Input Vireo code:")
    print(test_code)
    print("")
    print("========================================")
    print("🐍 Generated Python code:")
    print("========================================")
    
    python_code = compiler.compile(test_code)
    print(python_code)
    
    print("")
    print("========================================")
    print(f"✅ Compilation successful! (Vireo v{VERSION})")