# ============================================================
# VIREO COMPILER
# AST → Python / WASM / LLVM / Bytecode
# ============================================================

from typing import List, Dict, Any, Optional
from .ast import AST, ASTNode, NodeType


class Compiler:
    """Компілятор Vireo."""
    
    def __init__(self):
        self.indent_level = 0
        self.code_lines = []
        self.variables = {}
        self.functions = {}
        self.target = "python"
    
    def compile(self, ast: AST, target: str = "python") -> str:
        self.target = target
        self.code_lines = []
        self.indent_level = 0
        self.variables = {}
        self.functions = {}
        
        self.code_lines.append(f'# Generated from Vireo code (target: {target})')
        self.code_lines.append(f'# Vireo v3.0.0')
        self.code_lines.append('')
        
        if target == "python":
            return self._compile_python(ast)
        elif target == "wasm":
            return self._compile_wasm(ast)
        elif target == "llvm":
            return self._compile_llvm(ast)
        elif target == "bytecode":
            return self._compile_bytecode(ast)
        else:
            raise ValueError(f"Unknown target: {target}")
    
    def _compile_python(self, ast: AST) -> str:
        for node in ast.nodes:
            self._generate_node_python(node)
        return '\n'.join(self.code_lines)
    
    def _compile_wasm(self, ast: AST) -> str:
        self.code_lines.append('(module')
        self.code_lines.append('  (func $main (export "main")')
        for node in ast.nodes:
            self._generate_node_wasm(node)
        self.code_lines.append('  )')
        self.code_lines.append(')')
        return '\n'.join(self.code_lines)
    
    def _compile_llvm(self, ast: AST) -> str:
        self.code_lines.append('; ModuleID = "vireo"')
        self.code_lines.append('target triple = "x86_64-pc-linux-gnu"')
        self.code_lines.append('')
        for node in ast.nodes:
            self._generate_node_llvm(node)
        return '\n'.join(self.code_lines)
    
    def _compile_bytecode(self, ast: AST) -> str:
        self.code_lines.append('VIREO_BYTECODE')
        self.code_lines.append('version: 3.0.0')
        for i, node in enumerate(ast.nodes):
            self.code_lines.append(f'{i:04d}: {node.type.value} {node.data}')
        return '\n'.join(self.code_lines)
    
    def _indent(self) -> str:
        return '    ' * self.indent_level
    
    def _generate_node_python(self, node: ASTNode):
        if node.type == NodeType.VARIABLE_DEF:
            name = node.data.get('name', '')
            value = node.data.get('value', '')
            self.variables[name] = value
            self.code_lines.append(f'{self._indent()}{name} = {value}')
        elif node.type == NodeType.FUNCTION_DEF:
            name = node.data.get('name', '')
            params = node.data.get('params', [])
            params_str = ', '.join(params) if params else ''
            self.code_lines.append(f'{self._indent()}def {name}({params_str}):')
            self.indent_level += 1
            for child in node.children:
                self._generate_node_python(child)
            self.indent_level -= 1
        elif node.type == NodeType.PRINT:
            expr = node.data.get('expression', '')
            self.code_lines.append(f'{self._indent()}print({expr})')
        elif node.type == NodeType.RETURN:
            expr = node.data.get('expression', '')
            self.code_lines.append(f'{self._indent()}return {expr}')
        elif node.type == NodeType.IF:
            condition = node.data.get('condition', '')
            self.code_lines.append(f'{self._indent()}if {condition}:')
            self.indent_level += 1
            for child in node.children:
                if child.type != NodeType.ELSE:
                    self._generate_node_python(child)
            self.indent_level -= 1
            else_node = next((c for c in node.children if c.type == NodeType.ELSE), None)
            if else_node:
                self.code_lines.append(f'{self._indent()}else:')
                self.indent_level += 1
                for child in else_node.children:
                    self._generate_node_python(child)
                self.indent_level -= 1
        elif node.type == NodeType.WHILE:
            condition = node.data.get('condition', '')
            self.code_lines.append(f'{self._indent()}while {condition}:')
            self.indent_level += 1
            for child in node.children:
                self._generate_node_python(child)
            self.indent_level -= 1
        elif node.type == NodeType.FOR:
            var = node.data.get('var', '')
            collection = node.data.get('collection', '')
            self.code_lines.append(f'{self._indent()}for {var} in {collection}:')
            self.indent_level += 1
            for child in node.children:
                self._generate_node_python(child)
            self.indent_level -= 1
        elif node.type == NodeType.IMPORT:
            name = node.data.get('name', '')
            self.code_lines.append(f'import {name}')
        else:
            for child in node.children:
                self._generate_node_python(child)
    
    def _generate_node_wasm(self, node: ASTNode):
        # Спрощена WASM генерація
        if node.type == NodeType.VARIABLE_DEF:
            name = node.data.get('name', '')
            value = node.data.get('value', '')
            self.code_lines.append(f'    (local ${name} i32)')
            self.code_lines.append(f'    (i32.const {value})')
            self.code_lines.append(f'    (local.set ${name})')
        elif node.type == NodeType.PRINT:
            self.code_lines.append('    (call $print)')
    
    def _generate_node_llvm(self, node: ASTNode):
        if node.type == NodeType.VARIABLE_DEF:
            name = node.data.get('name', '')
            value = node.data.get('value', '')
            self.code_lines.append(f'%{name} = alloca i32')
            self.code_lines.append(f'store i32 {value}, i32* %{name}')
    
    def generate(self, ast: AST) -> str:
        return self.compile(ast, "python")


def compile_to_python(ast: AST) -> str:
    compiler = Compiler()
    return compiler.compile(ast, "python")


def compile_to_wasm(ast: AST) -> str:
    compiler = Compiler()
    return compiler.compile(ast, "wasm")


def compile_to_llvm(ast: AST) -> str:
    compiler = Compiler()
    return compiler.compile(ast, "llvm")


def compile_to_bytecode(ast: AST) -> str:
    compiler = Compiler()
    return compiler.compile(ast, "bytecode")