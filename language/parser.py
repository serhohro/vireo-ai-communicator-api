# ============================================================
# VIREO LANGUAGE PARSER
# Vireo → AST (Abstract Syntax Tree)
# ============================================================

from typing import List, Dict, Any, Optional
from .ast import AST, ASTNode, NodeType


class Parser:
    """
    Парсер Vireo мови.
    Перетворює текстовий код Vireo в AST.
    """
    
    def __init__(self):
        self.tokens = []
        self.pos = 0
        self.ast = None
    
    def parse(self, code: str) -> AST:
        """
        Парсить Vireo код і повертає AST.
        
        Args:
            code: Вхідний Vireo код
            
        Returns:
            AST: Abstract Syntax Tree
        """
        self.tokens = self._tokenize(code)
        self.pos = 0
        self.ast = AST()
        
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            
            if token[0] == 'IMPORT':
                self.ast.add_node(self._parse_import())
            elif token[0] == 'LET':
                self.ast.add_node(self._parse_variable_def())
            elif token[0] == 'FN':
                self.ast.add_node(self._parse_function_def())
            elif token[0] == 'PRINT':
                self.ast.add_node(self._parse_print())
            elif token[0] == 'RETURN':
                self.ast.add_node(self._parse_return())
            elif token[0] == 'IF':
                self.ast.add_node(self._parse_if())
            elif token[0] == 'WHILE':
                self.ast.add_node(self._parse_while())
            elif token[0] == 'FOR':
                self.ast.add_node(self._parse_for())
            elif token[0] == 'MODEL':
                self.ast.add_node(self._parse_model_def())
            elif token[0] == 'AGENT':
                self.ast.add_node(self._parse_agent_def())
            elif token[0] == 'CONTRACT':
                self.ast.add_node(self._parse_contract_def())
            elif token[0] == 'NEGOTIATION':
                self.ast.add_node(self._parse_negotiation_def())
            else:
                self.pos += 1
        
        return self.ast
    
    def _tokenize(self, code: str) -> List[tuple]:
        """Розбиває код на токени."""
        tokens = []
        i = 0
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # Простий токенізатор
            words = line.split()
            for word in words:
                if word == 'import':
                    tokens.append(('IMPORT', line_num))
                elif word == 'let':
                    tokens.append(('LET', line_num))
                elif word == 'fn':
                    tokens.append(('FN', line_num))
                elif word == 'print':
                    tokens.append(('PRINT', line_num))
                elif word == 'return':
                    tokens.append(('RETURN', line_num))
                elif word == 'if':
                    tokens.append(('IF', line_num))
                elif word == 'else':
                    tokens.append(('ELSE', line_num))
                elif word == 'while':
                    tokens.append(('WHILE', line_num))
                elif word == 'for':
                    tokens.append(('FOR', line_num))
                elif word == 'model':
                    tokens.append(('MODEL', line_num))
                elif word == 'agent':
                    tokens.append(('AGENT', line_num))
                elif word == 'contract':
                    tokens.append(('CONTRACT', line_num))
                elif word == 'negotiation':
                    tokens.append(('NEGOTIATION', line_num))
                elif word == 'identity':
                    tokens.append(('IDENTITY', line_num))
                elif word == 'capability':
                    tokens.append(('CAPABILITY', line_num))
                elif word == 'role':
                    tokens.append(('ROLE', line_num))
                elif word == 'layer':
                    tokens.append(('LAYER', line_num))
                elif word == 'activation':
                    tokens.append(('ACTIVATION', line_num))
                elif word == 'loss':
                    tokens.append(('LOSS', line_num))
                elif word == 'optimizer':
                    tokens.append(('OPTIMIZER', line_num))
                elif word == 'train':
                    tokens.append(('TRAIN', line_num))
                elif word == 'predict':
                    tokens.append(('PREDICT', line_num))
                elif word == 'evaluate':
                    tokens.append(('EVALUATE', line_num))
                elif word == 'propose':
                    tokens.append(('PROPOSE', line_num))
                elif word == 'commit':
                    tokens.append(('COMMIT', line_num))
                elif word == 'reject':
                    tokens.append(('REJECT', line_num))
                elif word == 'execute':
                    tokens.append(('EXECUTE', line_num))
                elif word == 'inform':
                    tokens.append(('INFORM', line_num))
                elif word == 'agent':
                    tokens.append(('AGENT', line_num))
                elif word == 'party':
                    tokens.append(('PARTY', line_num))
                elif word == 'timeout':
                    tokens.append(('TIMEOUT', line_num))
                elif word == 'max_rounds':
                    tokens.append(('MAX_ROUNDS', line_num))
                elif word == 'on':
                    tokens.append(('ON', line_num))
                elif word == 'offer':
                    tokens.append(('OFFER', line_num))
                elif word == 'accept':
                    tokens.append(('ACCEPT', line_num))
                elif word == 'condition':
                    tokens.append(('CONDITION', line_num))
                else:
                    if word.startswith('"') and word.endswith('"'):
                        tokens.append(('STRING', word[1:-1], line_num))
                    elif word.isdigit() or (word.startswith('-') and word[1:].isdigit()):
                        tokens.append(('NUMBER', int(word), line_num))
                    elif word.startswith('did:key:'):
                        tokens.append(('DID', word, line_num))
                    elif '=' in word and not word.startswith('=='):
                        # Присвоєння
                        parts = word.split('=')
                        if len(parts) == 2:
                            tokens.append(('NAME', parts[0].strip(), line_num))
                            tokens.append(('ASSIGN', '=', line_num))
                            tokens.append(('NAME', parts[1].strip(), line_num))
                    else:
                        tokens.append(('NAME', word, line_num))
        
        return tokens
    
    def _parse_import(self) -> ASTNode:
        """Парсить import."""
        self.pos += 1
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NAME':
            name = self.tokens[self.pos][1]
            self.pos += 1
            return ASTNode(
                type=NodeType.IMPORT,
                data={'name': name}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid import'})
    
    def _parse_variable_def(self) -> ASTNode:
        """Парсить let name = value."""
        self.pos += 1  # пропускаємо 'let'
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NAME':
            name = self.tokens[self.pos][1]
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'ASSIGN':
                self.pos += 1
                if self.pos < len(self.tokens):
                    value = self.tokens[self.pos][1]
                    self.pos += 1
                    return ASTNode(
                        type=NodeType.VARIABLE_DEF,
                        data={'name': name, 'value': value}
                    )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid variable definition'})
    
    def _parse_function_def(self) -> ASTNode:
        """Парсить fn name(params) { ... }."""
        self.pos += 1  # пропускаємо 'fn'
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NAME':
            name = self.tokens[self.pos][1]
            self.pos += 1
            # Пропускаємо параметри (спрощено)
            params = []
            if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NAME':
                # Параметри в дужках
                pass
            return ASTNode(
                type=NodeType.FUNCTION_DEF,
                data={'name': name, 'params': params}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid function definition'})
    
    def _parse_print(self) -> ASTNode:
        """Парсить print(expr)."""
        self.pos += 1
        if self.pos < len(self.tokens):
            expr = self.tokens[self.pos][1]
            self.pos += 1
            return ASTNode(
                type=NodeType.PRINT,
                data={'expression': expr}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid print'})
    
    def _parse_return(self) -> ASTNode:
        """Парсить return expr."""
        self.pos += 1
        if self.pos < len(self.tokens):
            expr = self.tokens[self.pos][1]
            self.pos += 1
            return ASTNode(
                type=NodeType.RETURN,
                data={'expression': expr}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid return'})
    
    def _parse_if(self) -> ASTNode:
        """Парсить if condition { ... }."""
        self.pos += 1
        if self.pos < len(self.tokens):
            condition = self.tokens[self.pos][1]
            self.pos += 1
            return ASTNode(
                type=NodeType.IF,
                data={'condition': condition}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid if'})
    
    def _parse_while(self) -> ASTNode:
        """Парсить while condition { ... }."""
        self.pos += 1
        if self.pos < len(self.tokens):
            condition = self.tokens[self.pos][1]
            self.pos += 1
            return ASTNode(
                type=NodeType.WHILE,
                data={'condition': condition}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid while'})
    
    def _parse_for(self) -> ASTNode:
        """Парсить for item in collection { ... }."""
        self.pos += 1
        if self.pos < len(self.tokens):
            var = self.tokens[self.pos][1]
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == 'in':
                self.pos += 1
                if self.pos < len(self.tokens):
                    collection = self.tokens[self.pos][1]
                    self.pos += 1
                    return ASTNode(
                        type=NodeType.FOR,
                        data={'var': var, 'collection': collection}
                    )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid for'})
    
    def _parse_model_def(self) -> ASTNode:
        """Парсить model Name { ... }."""
        self.pos += 1
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NAME':
            name = self.tokens[self.pos][1]
            self.pos += 1
            return ASTNode(
                type=NodeType.MODEL_DEF,
                data={'name': name}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid model definition'})
    
    def _parse_agent_def(self) -> ASTNode:
        """Парсить agent Name { ... }."""
        self.pos += 1
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NAME':
            name = self.tokens[self.pos][1]
            self.pos += 1
            return ASTNode(
                type=NodeType.AGENT_DEF,
                data={'name': name}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid agent definition'})
    
    def _parse_contract_def(self) -> ASTNode:
        """Парсить contract Name { ... }."""
        self.pos += 1
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NAME':
            name = self.tokens[self.pos][1]
            self.pos += 1
            return ASTNode(
                type=NodeType.CONTRACT_DEF,
                data={'name': name}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid contract definition'})
    
    def _parse_negotiation_def(self) -> ASTNode:
        """Парсить negotiation Name { ... }."""
        self.pos += 1
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NAME':
            name = self.tokens[self.pos][1]
            self.pos += 1
            return ASTNode(
                type=NodeType.NEGOTIATION_DEF,
                data={'name': name}
            )
        return ASTNode(type=NodeType.ERROR, data={'message': 'Invalid negotiation definition'})


def parse(code: str) -> AST:
    """Зручна функція для парсингу Vireo коду."""
    parser = Parser()
    return parser.parse(code)