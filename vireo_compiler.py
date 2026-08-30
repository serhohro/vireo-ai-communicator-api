# ============================================================
# VIREO COMPILER v1.4.3
# Компілятор мови Vireo в Python код
# Підтримує формальну граматику v1.4.3
# ============================================================

import re
import ast
import json
from typing import List, Dict, Any, Optional, Union

# ============================================================
# 1. ЛЕКСИЧНИЙ АНАЛІЗАТОР (LEXER)
# ============================================================

class Lexer:
    """Перетворює код Vireo на токени"""
    
    VERSION = "1.4.3"
    
    def __init__(self):
        self.tokens = []
        self.current_pos = 0
        
        # Регулярні вирази для токенів
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
            (r'@neural\b', 'NEURAL'),
            (r'@parallel\b', 'PARALLEL'),
            (r'@distributed\b', 'DISTRIBUTED'),
            (r'Tensor\b', 'TENSOR'),
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
        """Розбиває код на токени"""
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
# 2. СИНТАКСИЧНИЙ АНАЛІЗАТОР (PARSER)
# ============================================================

class Parser:
    """Будує AST з токенів"""
    
    VERSION = "1.4.3"
    
    def __init__(self, tokens: List[Dict]):
        self.tokens = tokens
        self.pos = 0
        self.ast = []
    
    def parse(self) -> Dict:
        """Головна функція парсингу"""
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
        
        return {'type': 'program', 'body': self.ast, 'version': self.VERSION}
    
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
                'value': value
            }
        
        return {'type': 'let', 'name': var_name, 'value': None}
    
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
                'value': value
            }
        
        return {'type': 'const', 'name': var_name, 'value': None}
    
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
            'body': body
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
            'else_body': else_body
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
            'body': body
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
            'body': body
        }
    
    def parse_return(self) -> Dict:
        self.pos += 1
        value = self.parse_expression()
        return {'type': 'return', 'value': value}
    
    def parse_print(self) -> Dict:
        self.pos += 1
        value = self.parse_expression()
        return {'type': 'print', 'value': value}
    
    def parse_neural(self) -> Dict:
        self.pos += 1
        return {'type': 'neural'}
    
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
            'shape': shape
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
# 3. ГЕНЕРАТОР КОДУ (CODE GENERATOR)
# ============================================================

class CodeGenerator:
    """Генерує Python код з AST"""
    
    VERSION = "1.4.3"
    
    def __init__(self):
        self.indent = 0
        self.variables = {}
        self.functions = {}
        self.output = []
        self._current_function = None
    
    def generate(self, ast: Dict) -> str:
        """Генерує Python код"""
        self.output = []
        
        self.output.append("# ============================================================")
        self.output.append(f"# Скомпільовано з Vireo v{self.VERSION} в Python")
        self.output.append("# ============================================================")
        self.output.append("")
        self.output.append("import math")
        self.output.append("import random")
        self.output.append("")
        
        for node in ast.get('body', []):
            self._generate_node(node)
        
        if 'main' not in self.functions:
            self.output.append("")
            self.output.append("if __name__ == '__main__':")
            self.output.append("    print('🌿 Vireo v1.4.3 program executed successfully!')")
            self.output.append("")
        
        return '\n'.join(self.output)
    
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
            self.output.append(self._indent() + f"{name} = {value_str}")
            self.variables[name] = True
        else:
            self.output.append(self._indent() + f"{name} = None")
    
    def _generate_const(self, node: Dict):
        name = node['name']
        value = node['value']
        
        if value:
            value_str = self._expr_to_string(value)
            self.output.append(self._indent() + f"{name} = {value_str}  # const")
    
    def _generate_function(self, node: Dict):
        name = node['name']
        args = ', '.join(node.get('args', []))
        
        self.functions[name] = True
        self._current_function = name
        
        self.output.append("")
        self.output.append(f"def {name}({args}):")
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
        self.output.append(self._indent() + f"if {condition}:")
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
        self.output.append(self._indent() + f"for {var} in {iterable}:")
        self.indent += 1
        
        for token in node.get('body', []):
            if isinstance(token, dict) and 'type' in token:
                self._generate_node(token)
            else:
                self.output.append(self._indent() + f"# {token}")
        
        self.indent -= 1
    
    def _generate_while(self, node: Dict):
        condition = self._expr_to_string(node['condition'])
        self.output.append(self._indent() + f"while {condition}:")
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
            self.output.append(self._indent() + f"return {value_str}")
        else:
            self.output.append(self._indent() + "return")
    
    def _generate_print(self, node: Dict):
        if node['value']:
            value_str = self._expr_to_string(node['value'])
            self.output.append(self._indent() + f"print({value_str})")
        else:
            self.output.append(self._indent() + "print()")
    
    def _generate_neural(self, node: Dict):
        self.output.append(self._indent() + "# 🧠 Neural network decorator (Vireo v1.4.3)")
    
    def _generate_tensor(self, node: Dict):
        dtype = node.get('dtype', 'F32')
        shape = node.get('shape', [])
        shape_str = ', '.join(shape) if shape else 'None'
        self.output.append(self._indent() + f"# Tensor<{dtype}, [{shape_str}]> (Vireo v1.4.3)")
    
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
# 4. ГОЛОВНИЙ КЛАС КОМПІЛЯТОРА
# ============================================================

class VireoCompiler:
    """Головний клас компілятора Vireo v1.4.3"""
    
    VERSION = "1.4.3"
    
    def __init__(self):
        self.lexer = Lexer()
        self.parser = None
        self.generator = CodeGenerator()
    
    def compile(self, code: str) -> str:
        """Компілює Vireo код у Python код"""
        tokens = self.lexer.tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        return self.generator.generate(ast)
    
    def compile_to_file(self, code: str, output_file: str) -> str:
        """Компілює і зберігає у файл"""
        python_code = self.compile(code)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        return f"✅ Compiled to {output_file} (Vireo v{self.VERSION})"
    
    def compile_file(self, input_file: str, output_file: str = None) -> str:
        """Компілює файл .v у .py"""
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
    
    print("🟢 Vireo Compiler v1.4.3")
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
    
    compiler = VireoCompiler()
    
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
print sum

fn add(a, b) {
    return a + b
}

let result = add(3, 7)
print result

@neural
fn model(input) {
    let h1 = dense(input, 256, ReLU)
    let h2 = dense(h1, 128, ReLU)
    let output = dense(h2, 10, Softmax)
    return output
}
"""
    
    compiler = VireoCompiler()
    
    print("🟢 Vireo Compiler v1.4.3 Demo")
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
    print("✅ Compilation successful! (Vireo v1.4.3)")