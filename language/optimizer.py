# ============================================================
# VIREO OPTIMIZER
# Оптимізація AST
# ============================================================

from typing import List, Dict, Any, Optional
from .ast import AST, ASTNode, NodeType


class Optimizer:
    """
    Оптимізатор Vireo AST.
    
    Виконує:
    - Спрощення констант
    - Видалення мертвого коду
    - Згортання виразів
    - Оптимізація тензорних операцій
    """
    
    def __init__(self):
        self.optimizations_applied = 0
    
    def optimize(self, ast: AST) -> AST:
        """
        Оптимізує AST.
        
        Args:
            ast: AST для оптимізації
            
        Returns:
            AST: Оптимізований AST
        """
        self.optimizations_applied = 0
        
        # Проходимо по всіх вузлах
        for i, node in enumerate(ast.nodes):
            optimized = self._optimize_node(node)
            if optimized != node:
                ast.nodes[i] = optimized
                self.optimizations_applied += 1
        
        return ast
    
    def _optimize_node(self, node: ASTNode) -> ASTNode:
        """Оптимізує конкретний вузол."""
        # Оптимізація виразів
        if node.type == NodeType.VARIABLE_DEF:
            return self._optimize_variable_def(node)
        elif node.type == NodeType.PRINT:
            return self._optimize_print(node)
        elif node.type == NodeType.IF:
            return self._optimize_if(node)
        elif node.type == NodeType.FOR:
            return self._optimize_for(node)
        elif node.type == NodeType.WHILE:
            return self._optimize_while(node)
        
        # Оптимізація дочірніх вузлів
        for i, child in enumerate(node.children):
            node.children[i] = self._optimize_node(child)
        
        return node
    
    def _optimize_variable_def(self, node: ASTNode) -> ASTNode:
        """Оптимізація визначення змінної."""
        value = node.data.get('value', '')
        
        # Спрощення констант
        if value.isdigit():
            # Вже константа
            pass
        elif '+' in value:
            parts = value.split('+')
            if all(p.strip().isdigit() for p in parts):
                # 2 + 3 → 5
                result = sum(int(p.strip()) for p in parts)
                node.data['value'] = str(result)
                self.optimizations_applied += 1
        
        return node
    
    def _optimize_print(self, node: ASTNode) -> ASTNode:
        """Оптимізація виводу."""
        expr = node.data.get('expression', '')
        
        # Видалення зайвих пробілів
        node.data['expression'] = expr.strip()
        
        return node
    
    def _optimize_if(self, node: ASTNode) -> ASTNode:
        """Оптимізація умов."""
        condition = node.data.get('condition', '')
        
        # Спрощення умов
        if condition == 'true':
            # Завжди виконується
            pass
        elif condition == 'false':
            # Ніколи не виконується
            pass
        
        return node
    
    def _optimize_for(self, node: ASTNode) -> ASTNode:
        """Оптимізація циклів."""
        collection = node.data.get('collection', '')
        
        # Перевірка на порожню колекцію
        if collection == '[]':
            # Цикл ніколи не виконується
            node.data['optimized_out'] = True
            self.optimizations_applied += 1
        
        return node
    
    def _optimize_while(self, node: ASTNode) -> ASTNode:
        """Оптимізація циклів while."""
        condition = node.data.get('condition', '')
        
        if condition == 'true':
            # Можливий нескінченний цикл
            self.warnings.append("Potential infinite loop detected")
        
        return node
    
    def get_stats(self) -> Dict[str, int]:
        """Повертає статистику оптимізації."""
        return {
            'optimizations_applied': self.optimizations_applied
        }


def optimize(ast: AST) -> AST:
    """Зручна функція для оптимізації AST."""
    optimizer = Optimizer()
    return optimizer.optimize(ast)