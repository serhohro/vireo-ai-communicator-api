# ============================================================
# VIREO INTERPRETER v0.1.0
# Простий інтерпретатор мови Vireo на Python
# ============================================================

import re
import math
import json
from typing import List, Dict, Any, Optional

# ============================================================
# 1. ТЕНЗОРИ
# ============================================================

class Tensor:
    """Спрощена реалізація тензорів для Vireo"""
    
    def __init__(self, data, shape=None):
        self.data = data
        if shape is None:
            self.shape = self._infer_shape(data)
        else:
            self.shape = shape
    
    def _infer_shape(self, data):
        if isinstance(data, list):
            if not data:
                return [0]
            if isinstance(data[0], list):
                return [len(data)] + self._infer_shape(data[0])
            return [len(data)]
        if isinstance(data, (int, float)):
            return []
        return [0]
    
    def __repr__(self):
        return f"Tensor({self.data}, shape={self.shape})"
    
    def __add__(self, other):
        if isinstance(other, Tensor):
            return Tensor([a + b for a, b in zip(self.data, other.data)])
        return Tensor([x + other for x in self.data])
    
    def __mul__(self, other):
        if isinstance(other, Tensor):
            return Tensor([a * b for a, b in zip(self.data, other.data)])
        return Tensor([x * other for x in self.data])
    
    def matmul(self, other):
        """Матричне множення"""
        if not isinstance(other, Tensor):
            raise TypeError("matmul requires Tensor")
        
        if len(self.shape) == 1 and len(other.shape) == 1:
            # Вектор * Вектор = скаляр
            return sum(a * b for a, b in zip(self.data, other.data))
        
        if len(self.shape) == 2 and len(other.shape) == 2:
            # Матриця * Матриця
            rows = self.shape[0]
            cols = other.shape[1]
            result = [[0] * cols for _ in range(rows)]
            
            for i in range(rows):
                for j in range(cols):
                    s = 0
                    for k in range(self.shape[1]):
                        s += self.data[i][k] * other.data[k][j]
                    result[i][j] = s
            return Tensor(result)
        
        raise ValueError(f"Unsupported matmul: {self.shape} x {other.shape}")
    
    def sum(self):
        return sum(self.data)
    
    def mean(self):
        return sum(self.data) / len(self.data)
    
    def max(self):
        return max(self.data)
    
    def min(self):
        return min(self.data)
    
    def reshape(self, new_shape):
        flat = self.flatten()
        if len(new_shape) == 1:
            return Tensor(flat[:new_shape[0]])
        if len(new_shape) == 2:
            result = []
            idx = 0
            for i in range(new_shape[0]):
                row = flat[idx:idx+new_shape[1]]
                result.append(row)
                idx += new_shape[1]
            return Tensor(result)
        return self
    
    def flatten(self):
        def _flatten(data):
            if isinstance(data, list):
                result = []
                for item in data:
                    result.extend(_flatten(item))
                return result
            return [data]
        return _flatten(self.data)


# ============================================================
# 2. АВТОДИФЕРЕНЦІЮВАННЯ
# ============================================================

class Variable:
    """Змінна з підтримкою автодиференціювання"""
    
    def __init__(self, data, requires_grad=True):
        self.data = data if isinstance(data, Tensor) else Tensor(data)
        self.grad = None
        self.requires_grad = requires_grad
        self._backward = None
    
    def __repr__(self):
        return f"Variable({self.data})"
    
    def __add__(self, other):
        if not self.requires_grad and not other.requires_grad:
            return Variable(self.data + other.data, requires_grad=False)
        
        result = Variable(self.data + other.data, requires_grad=True)
        
        def backward():
            if self.grad is not None:
                self.grad += result.grad
            else:
                self.grad = result.grad
            
            if other.grad is not None:
                other.grad += result.grad
            else:
                other.grad = result.grad
        
        result._backward = backward
        return result
    
    def __mul__(self, other):
        if not self.requires_grad and not other.requires_grad:
            return Variable(self.data * other.data, requires_grad=False)
        
        result = Variable(self.data * other.data, requires_grad=True)
        
        def backward():
            if self.grad is not None:
                self.grad += other.data * result.grad
            else:
                self.grad = other.data * result.grad
            
            if other.grad is not None:
                other.grad += self.data * result.grad
            else:
                other.grad = self.data * result.grad
        
        result._backward = backward
        return result
    
    def backward(self, grad=None):
        if grad is None:
            grad = Tensor([1.0])
        self.grad = grad
        if self._backward:
            self._backward()


# ============================================================
# 3. ФУНКЦІЇ АКТИВАЦІЇ
# ============================================================

def relu(x):
    if isinstance(x, Tensor):
        return Tensor([max(0, v) for v in x.data])
    if isinstance(x, (int, float)):
        return max(0, x)
    return x

def sigmoid(x):
    if isinstance(x, Tensor):
        return Tensor([1 / (1 + math.exp(-v)) for v in x.data])
    if isinstance(x, (int, float)):
        return 1 / (1 + math.exp(-x))
    return x

def softmax(x):
    if isinstance(x, Tensor):
        exp_vals = [math.exp(v) for v in x.data]
        sum_exp = sum(exp_vals)
        return Tensor([v / sum_exp for v in exp_vals])
    return x


# ============================================================
# 4. ІНТЕРПРЕТАТОР VIREO
# ============================================================

class VireoInterpreter:
    """Спрощений інтерпретатор Vireo"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.output = []
    
    def execute(self, code: str) -> str:
        """Виконати код Vireo"""
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            try:
                self._execute_line(line)
            except Exception as e:
                self.output.append(f"Error: {e}")
        
        return '\n'.join(self.output) if self.output else "Execution completed."
    
    def _execute_line(self, line: str):
        # let x = 5
        if line.startswith('let '):
            parts = line[4:].split('=')
            var_name = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else None
            
            if value is None:
                self.variables[var_name] = None
                self.output.append(f"Variable {var_name} = None")
                return
            
            # Обробка значення
            result = self._evaluate_expression(value)
            self.variables[var_name] = result
            self.output.append(f"Variable {var_name} = {result}")
            return
        
        # print(...)
        if line.startswith('print(') or line.startswith('print "'):
            value = line[6:-1]
            if value.startswith('"') and value.endswith('"'):
                self.output.append(value[1:-1])
            elif value in self.variables:
                self.output.append(str(self.variables[value]))
            else:
                self.output.append(value)
            return
        
        # return ...
        if line.startswith('return '):
            value = line[7:]
            result = self._evaluate_expression(value)
            self.output.append(f"Return: {result}")
            return
        
        # fn main() { ... }
        if line.startswith('fn ') and '(' in line and ')' in line:
            # Спрощена обробка функцій
            func_name = line[3:line.index('(')]
            self.functions[func_name] = line
            self.output.append(f"Function {func_name} defined.")
            return
        
        # @neural
        if line.startswith('@neural'):
            self.output.append("Neural network decorator applied")
            return
        
        # Тензорні операції
        if 'Tensor' in line:
            self.output.append(f"Tensor operation: {line}")
            return
        
        # Якщо нічого не підходить
        self.output.append(f"Executing: {line}")
    
    def _evaluate_expression(self, expr: str):
        """Обчислити вираз"""
        expr = expr.strip()
        
        # Тензор: Tensor<F32, [2, 3]>
        if expr.startswith('Tensor'):
            # Спрощена обробка
            if '[' in expr and ']' in expr:
                # tensor = [1, 2, 3]
                pass
            return Tensor([1, 2, 3])
        
        # Список: [1, 2, 3]
        if expr.startswith('[') and expr.endswith(']'):
            try:
                data = eval(expr)
                return data
            except:
                pass
        
        # Число
        try:
            return float(expr)
        except:
            pass
        
        # Змінна
        if expr in self.variables:
            return self.variables[expr]
        
        return expr


# ============================================================
# 5. API ІНТЕГРАЦІЯ
# ============================================================

def execute_vireo_code(code: str) -> dict:
    """Виконати Vireo код через інтерпретатор"""
    interpreter = VireoInterpreter()
    output = interpreter.execute(code)
    return {
        "status": "success",
        "output": output,
        "variables": interpreter.variables
    }


# ============================================================
# 6. ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    # Тестовий код
    test_code = """
    let x = 5
    let y = 10
    print x + y
    print "Hello Vireo!"
    
    @neural
    fn test(x) {
        return x * 2
    }
    """
    
    result = execute_vireo_code(test_code)
    print(result["output"])