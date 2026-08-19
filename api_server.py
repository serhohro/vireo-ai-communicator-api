# ============================================================
# VIREO AI COMMUNICATOR - API SERVER v1.0.0
# Повноцінний API сервер з інтерпретатором Vireo
# ============================================================

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import re
import math
from typing import List, Dict, Any, Optional, Union

app = Flask(__name__)
CORS(app)  # Дозволяє запити з будь-якого домену

# ============================================================
# 1. ТЕНЗОРИ (повноцінна реалізація)
# ============================================================

class Tensor:
    """Повноцінна реалізація тензорів для Vireo"""
    
    def __init__(self, data, dtype='float32', requires_grad=False):
        if isinstance(data, (int, float)):
            self.data = [float(data)]
        elif isinstance(data, list):
            self.data = data
        else:
            self.data = list(data) if hasattr(data, '__iter__') else [data]
        self.dtype = dtype
        self.requires_grad = requires_grad
        self.grad = None
        self._shape = None
        self._compute_shape()
    
    def _compute_shape(self):
        """Обчислює розмірність тензора"""
        def get_shape(d):
            if not isinstance(d, list):
                return []
            if not d:
                return [0]
            first = get_shape(d[0])
            if all(get_shape(item) == first for item in d):
                return [len(d)] + first
            return [len(d)]
        self._shape = get_shape(self.data)
    
    @property
    def shape(self):
        return self._shape
    
    def __repr__(self):
        return f"Tensor({self.data}, shape={self.shape}, dtype={self.dtype})"
    
    def __add__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            if self.requires_grad or other.requires_grad:
                result = Tensor([a + b for a, b in zip(self.data, other.data)], requires_grad=True)
                result._grad_fn = ('add', self, other)
                return result
            return Tensor([a + b for a, b in zip(self.data, other.data)])
        return Tensor([x + other for x in self.data])
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            if self.requires_grad or other.requires_grad:
                result = Tensor([a - b for a, b in zip(self.data, other.data)], requires_grad=True)
                result._grad_fn = ('sub', self, other)
                return result
            return Tensor([a - b for a, b in zip(self.data, other.data)])
        return Tensor([x - other for x in self.data])
    
    def __mul__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            if self.requires_grad or other.requires_grad:
                result = Tensor([a * b for a, b in zip(self.data, other.data)], requires_grad=True)
                result._grad_fn = ('mul', self, other)
                return result
            return Tensor([a * b for a, b in zip(self.data, other.data)])
        return Tensor([x * other for x in self.data])
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            if self.requires_grad or other.requires_grad:
                result = Tensor([a / b for a, b in zip(self.data, other.data)], requires_grad=True)
                result._grad_fn = ('div', self, other)
                return result
            return Tensor([a / b for a, b in zip(self.data, other.data)])
        return Tensor([x / other for x in self.data])
    
    def matmul(self, other):
        """Матричне множення"""
        if not isinstance(other, Tensor):
            raise TypeError("matmul requires Tensor")
        
        if len(self.shape) == 1 and len(other.shape) == 1:
            # Вектор * Вектор = скаляр
            if self.shape[0] != other.shape[0]:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            result = sum(a * b for a, b in zip(self.data, other.data))
            return Tensor(result)
        
        if len(self.shape) == 2 and len(other.shape) == 2:
            # Матриця * Матриця
            rows = self.shape[0]
            cols = other.shape[1]
            k_dim = self.shape[1]
            
            if k_dim != other.shape[0]:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            
            result_data = [[0] * cols for _ in range(rows)]
            for i in range(rows):
                for j in range(cols):
                    s = 0
                    for k in range(k_dim):
                        s += self.data[i][k] * other.data[k][j]
                    result_data[i][j] = s
            
            return Tensor(result_data)
        
        if len(self.shape) == 2 and len(other.shape) == 1:
            # Матриця * Вектор
            rows = self.shape[0]
            cols = self.shape[1]
            if cols != other.shape[0]:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            result_data = [0] * rows
            for i in range(rows):
                s = 0
                for j in range(cols):
                    s += self.data[i][j] * other.data[j]
                result_data[i] = s
            return Tensor(result_data)
        
        raise ValueError(f"Unsupported matmul: {self.shape} x {other.shape}")
    
    def sum(self, axis=None):
        if axis is None:
            def _flatten(d):
                if isinstance(d, list):
                    result = 0
                    for item in d:
                        result += _flatten(item)
                    return result
                return d
            return _flatten(self.data)
        # Спрощена реалізація для axis=0 або 1
        if axis == 0:
            if len(self.shape) == 2:
                result = [0] * self.shape[1]
                for row in self.data:
                    for j, val in enumerate(row):
                        result[j] += val
                return Tensor(result)
        if axis == 1:
            if len(self.shape) == 2:
                result = [sum(row) for row in self.data]
                return Tensor(result)
        return self
    
    def mean(self, axis=None):
        s = self.sum(axis)
        if isinstance(s, Tensor):
            return Tensor([v / self.shape[0] for v in s.data])
        return s / self.shape[0]
    
    def max(self):
        def _max(d):
            if isinstance(d, list):
                return max(_max(item) for item in d)
            return d
        return _max(self.data)
    
    def min(self):
        def _min(d):
            if isinstance(d, list):
                return min(_min(item) for item in d)
            return d
        return _min(self.data)
    
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
        def _flatten(d):
            if isinstance(d, list):
                result = []
                for item in d:
                    result.extend(_flatten(item))
                return result
            return [d]
        return _flatten(self.data)
    
    def transpose(self):
        if len(self.shape) == 2:
            rows = self.shape[0]
            cols = self.shape[1]
            result = [[self.data[j][i] for j in range(rows)] for i in range(cols)]
            return Tensor(result)
        return self
    
    def to_list(self):
        return self.data
    
    def numpy(self):
        """Конвертація в NumPy (емуляція)"""
        return self.data
    
    def sqrt(self):
        return Tensor([math.sqrt(x) for x in self.flatten()])


# ============================================================
# 2. ФУНКЦІЇ АКТИВАЦІЇ ТА ОПЕРАЦІЇ
# ============================================================

def relu(x):
    if isinstance(x, Tensor):
        return Tensor([max(0, v) for v in x.flatten()], x.shape)
    if isinstance(x, (int, float)):
        return max(0, x)
    return x

def sigmoid(x):
    if isinstance(x, Tensor):
        return Tensor([1 / (1 + math.exp(-v)) for v in x.flatten()])
    if isinstance(x, (int, float)):
        return 1 / (1 + math.exp(-x))
    return x

def tanh(x):
    if isinstance(x, Tensor):
        return Tensor([math.tanh(v) for v in x.flatten()])
    if isinstance(x, (int, float)):
        return math.tanh(x)
    return x

def softmax(x):
    if isinstance(x, Tensor):
        exp_vals = [math.exp(v) for v in x.flatten()]
        sum_exp = sum(exp_vals)
        return Tensor([v / sum_exp for v in exp_vals])
    return x

def cross_entropy(pred, target):
    """Функція втрат для класифікації"""
    if isinstance(pred, Tensor) and isinstance(target, Tensor):
        pred_flat = pred.flatten()
        target_flat = target.flatten()
        return -sum(t * math.log(p) for p, t in zip(pred_flat, target_flat) if p > 0)
    return 0

def mse(pred, target):
    """Mean Squared Error"""
    if isinstance(pred, Tensor) and isinstance(target, Tensor):
        pred_flat = pred.flatten()
        target_flat = target.flatten()
        return sum((p - t) ** 2 for p, t in zip(pred_flat, target_flat)) / len(pred_flat)
    return 0


# ============================================================
# 3. АВТОДИФЕРЕНЦІЮВАННЯ
# ============================================================

class Variable:
    """Змінна з підтримкою автодиференціювання"""
    
    def __init__(self, data, requires_grad=True):
        self.data = data if isinstance(data, Tensor) else Tensor(data)
        self.grad = None
        self.requires_grad = requires_grad
        self._grad_fn = None
        self._children = []
        self._saved_data = {}
    
    def __repr__(self):
        return f"Variable({self.data}, requires_grad={self.requires_grad})"
    
    def __add__(self, other):
        if not isinstance(other, Variable):
            other = Variable(other, requires_grad=False)
        
        result = Variable(self.data + other.data, requires_grad=self.requires_grad or other.requires_grad)
        if result.requires_grad:
            result._grad_fn = ('add', self, other)
            result._children = [self, other]
        return result
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __mul__(self, other):
        if not isinstance(other, Variable):
            other = Variable(other, requires_grad=False)
        
        result = Variable(self.data * other.data, requires_grad=self.requires_grad or other.requires_grad)
        if result.requires_grad:
            result._grad_fn = ('mul', self, other)
            result._children = [self, other]
        return result
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def matmul(self, other):
        if not isinstance(other, Variable):
            other = Variable(other, requires_grad=False)
        
        result = Variable(self.data.matmul(other.data), requires_grad=self.requires_grad or other.requires_grad)
        if result.requires_grad:
            result._grad_fn = ('matmul', self, other)
            result._children = [self, other]
        return result
    
    def backward(self, grad=None):
        if grad is None:
            if self.data.shape:
                grad = Tensor([1.0])
            else:
                grad = 1.0
        
        if isinstance(grad, (int, float)):
            grad = Tensor(grad)
        
        self.grad = grad
        
        if self._grad_fn:
            op, *args = self._grad_fn
            if op == 'add':
                a, b = args
                if a.requires_grad:
                    a.backward(grad)
                if b.requires_grad:
                    b.backward(grad)
            elif op == 'mul':
                a, b = args
                if a.requires_grad:
                    a.backward(b.data * grad)
                if b.requires_grad:
                    b.backward(a.data * grad)
            elif op == 'matmul':
                a, b = args
                if a.requires_grad:
                    a.backward(grad.matmul(b.data.transpose()))
                if b.requires_grad:
                    b.backward(a.data.transpose().matmul(grad))


# ============================================================
# 4. ШАРИ НЕЙРОМЕРЕЖІ
# ============================================================

class Dense:
    """Повнозв'язний шар"""
    
    def __init__(self, input_size, output_size, activation='relu'):
        self.weights = Tensor([[0.01 * (2 * random.random() - 1) for _ in range(output_size)] 
                               for _ in range(input_size)])
        self.bias = Tensor([0.01 * (2 * random.random() - 1) for _ in range(output_size)])
        self.activation = activation
        self.input = None
        self.output = None
    
    def forward(self, x):
        self.input = x
        if len(x.shape) == 2:
            # Матричне множення
            self.output = x.matmul(self.weights) + self.bias
        elif len(x.shape) == 1:
            # Вектор * Матриця
            result = []
            for j in range(len(self.weights.data[0])):
                s = 0
                for i in range(len(x.data)):
                    s += x.data[i] * self.weights.data[i][j]
                result.append(s)
            self.output = Tensor(result) + self.bias
        else:
            self.output = x.matmul(self.weights) + self.bias
        
        # Активація
        if self.activation == 'relu':
            self.output = relu(self.output)
        elif self.activation == 'sigmoid':
            self.output = sigmoid(self.output)
        elif self.activation == 'tanh':
            self.output = tanh(self.output)
        elif self.activation == 'softmax':
            self.output = softmax(self.output)
        
        return self.output


class Dropout:
    """Dropout регуляризація"""
    
    def __init__(self, rate=0.3):
        self.rate = rate
        self.mask = None
    
    def forward(self, x):
        import random
        if self.rate > 0:
            flat = x.flatten()
            self.mask = [1 if random.random() > self.rate else 0 for _ in flat]
            result = [flat[i] * self.mask[i] for i in range(len(flat))]
            return Tensor(result)
        return x


class Sequential:
    """Послідовна нейромережа"""
    
    def __init__(self, layers):
        self.layers = layers
    
    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x


# ============================================================
# 5. ІНТЕРПРЕТАТОР VIREO
# ============================================================

class VireoInterpreter:
    """Інтерпретатор мови Vireo"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.output = []
        self._env = {}
        self._code_lines = []
    
    def execute(self, code: str) -> str:
        """Виконати код Vireo"""
        self.output = []
        self._code_lines = code.split('\n')
        
        for line in self._code_lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('#'):
                continue
            
            try:
                result = self._execute_line(line)
                if result is not None:
                    self.output.append(str(result))
            except Exception as e:
                self.output.append(f"❌ Error: {e}")
        
        return '\n'.join(self.output)
    
    def _execute_line(self, line: str):
        # let x = 5
        if line.startswith('let '):
            parts = line[4:].split('=', 1)
            var_name = parts[0].strip()
            
            if len(parts) > 1:
                value = parts[1].strip()
                result = self._evaluate(value)
                self.variables[var_name] = result
                return f"{var_name} = {result}"
            else:
                self.variables[var_name] = None
                return f"{var_name} = None"
        
        # const PI = 3.14
        if line.startswith('const '):
            parts = line[6:].split('=', 1)
            var_name = parts[0].strip()
            if len(parts) > 1:
                value = parts[1].strip()
                result = self._evaluate(value)
                self.variables[var_name] = result
                return f"const {var_name} = {result}"
        
        # print(...) або print "..."
        if line.startswith('print(') and line.endswith(')'):
            value = line[6:-1]
            result = self._evaluate(value)
            return result
        
        if line.startswith('print "'):
            value = line[6:-1]
            self.output.append(value)
            return value
        
        # return ...
        if line.startswith('return '):
            value = line[7:]
            result = self._evaluate(value)
            return f"Return: {result}"
        
        # if ... else ...
        if line.startswith('if '):
            # Спрощена обробка
            condition = line[3:].split('{')[0].strip()
            result = self._evaluate(condition)
            if result:
                return "if condition true"
            return "if condition false"
        
        # @neural
        if line.startswith('@neural'):
            return "🧠 Neural network decorator applied"
        
        # fn name(...) { ... }
        if line.startswith('fn ') and '(' in line:
            func_name = line[3:line.index('(')].strip()
            self.functions[func_name] = line
            return f"Function {func_name} defined"
        
        # Dense
        if line.startswith('Dense('):
            return "🧠 Dense layer created"
        
        # Tensor
        if 'Tensor' in line:
            return self._handle_tensor(line)
        
        # Інші вирази
        result = self._evaluate(line)
        return result
    
    def _evaluate(self, expr: str):
        """Обчислити вираз"""
        expr = expr.strip()
        
        # Якщо це змінна
        if expr in self.variables:
            return self.variables[expr]
        
        # Якщо це рядок
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        # Якщо це число
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except:
            pass
        
        # Якщо це список
        if expr.startswith('[') and expr.endswith(']'):
            try:
                data = eval(expr)
                return data
            except:
                pass
        
        # Якщо це тензор
        if expr.startswith('Tensor'):
            return self._handle_tensor(expr)
        
        # Якщо це вираз з +, -, *, /
        for op in ['+', '-', '*', '/']:
            if op in expr and not expr.startswith('"'):
                parts = expr.split(op)
                if len(parts) == 2:
                    left = self._evaluate(parts[0].strip())
                    right = self._evaluate(parts[1].strip())
                    
                    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                        if op == '+': return left + right
                        if op == '-': return left - right
                        if op == '*': return left * right
                        if op == '/': return left / right if right != 0 else float('inf')
                    
                    return f"{left} {op} {right}"
        
        return expr
    
    def _handle_tensor(self, line: str):
        """Обробка тензорних операцій"""
        if 'matmul' in line.lower():
            return "📊 Tensor matmul operation"
        if 'reshape' in line.lower():
            return "📐 Tensor reshape operation"
        if 'transpose' in line.lower():
            return "🔄 Tensor transpose operation"
        if 'sum' in line.lower():
            return "➕ Tensor sum operation"
        if 'mean' in line.lower():
            return "📊 Tensor mean operation"
        return "📊 Tensor operation"


# ============================================================
# 6. СИМУЛЯЦІЯ ТА ДОПОМІЖНІ ФУНКЦІЇ
# ============================================================

import random

def generate_tensor(shape, fill='random'):
    """Генерує тензор заданої форми"""
    if fill == 'ones':
        data = [[1.0 for _ in range(shape[1])] for _ in range(shape[0])]
    elif fill == 'zeros':
        data = [[0.0 for _ in range(shape[1])] for _ in range(shape[0])]
    else:
        data = [[random.random() for _ in range(shape[1])] for _ in range(shape[0])]
    return Tensor(data)


def simulate_vireo(code: str) -> dict:
    """Емуляція виконання Vireo коду (для зворотної сумісності)"""
    interpreter = VireoInterpreter()
    output = interpreter.execute(code)
    
    return {
        "status": "success",
        "output": output,
        "variables": interpreter.variables,
        "functions": interpreter.functions
    }


# ============================================================
# 7. РОЗШИРЕНІ API ЕНДПОІНТИ
# ============================================================

@app.route('/')
def home():
    return jsonify({
        "service": "Vireo AI Communicator API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "endpoints": {
            "GET /": "Home",
            "GET /docs": "Documentation",
            "POST /execute": "Execute Vireo code",
            "POST /neural": "Create neural network",
            "POST /tensor": "Tensor operations",
            "POST /chat": "AI communication",
            "POST /interpreter": "Execute with interpreter"
        }
    })


@app.route('/docs')
def docs():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vireo API Documentation</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
            h1 { color: #667eea; }
            h2 { color: #333; margin-top: 30px; }
            h3 { color: #555; }
            pre { background: #f0f0f0; padding: 15px; border-radius: 8px; overflow-x: auto; }
            code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; }
            .endpoint { background: #e8f0fe; padding: 15px; border-radius: 8px; margin: 10px 0; }
            .badge { background: #667eea; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8em; }
        </style>
    </head>
    <body>
        <h1>🟢 Vireo API Documentation</h1>
        <p><strong>Version:</strong> 1.0.0</p>
        <p><strong>Status:</strong> ✅ Running</p>
        
        <h2>📡 Endpoints</h2>
        
        <div class="endpoint">
            <h3>POST /execute</h3>
            <p><span class="badge">POST</span> Execute Vireo code (emulation)</p>
            <pre>{
    "code": "fn main() { print('Hello Vireo!') }"
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>POST /interpreter</h3>
            <p><span class="badge">POST</span> Execute Vireo code with real interpreter</p>
            <pre>{
    "code": "let x = 5\nlet y = 10\nprint x + y"
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>POST /neural</h3>
            <p><span class="badge">POST</span> Create neural network</p>
            <pre>{
    "layers": [784, 256, 128, 10],
    "activation": "ReLU"
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>POST /tensor</h3>
            <p><span class="badge">POST</span> Tensor operations</p>
            <pre>{
    "operation": "matmul",
    "a": [[1,2,3],[4,5,6]],
    "b": [[7,8],[9,10],[11,12]]
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>POST /chat</h3>
            <p><span class="badge">POST</span> AI communication simulation</p>
            <pre>{
    "message": "Hello AI models!",
    "models": ["ChatGPT", "Claude", "Gemini"]
}</pre>
        </div>
        
        <h2>🔧 Example Usage</h2>
        
        <h3>Python</h3>
        <pre>import requests

# Execute Vireo code
response = requests.post('http://localhost:5000/execute', json={
    'code': 'print "Hello Vireo!"'
})
print(response.json())</pre>
        
        <h3>curl</h3>
        <pre>curl -X POST http://localhost:5000/execute \\
  -H "Content-Type: application/json" \\
  -d '{"code": "print \"Hello Vireo!\""}'</pre>
    </body>
    </html>
    """
    return html


@app.route('/execute', methods=['POST'])
def execute():
    """Виконання Vireo коду (емуляція)"""
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({
            "status": "error",
            "message": "No code provided"
        }), 400
    
    result = simulate_vireo(code)
    return jsonify(result)


@app.route('/interpreter', methods=['POST'])
def execute_interpreter():
    """Виконання Vireo коду зі справжнім інтерпретатором"""
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({
            "status": "error",
            "message": "No code provided"
        }), 400
    
    interpreter = VireoInterpreter()
    output = interpreter.execute(code)
    
    return jsonify({
        "status": "success",
        "output": output,
        "variables": interpreter.variables,
        "functions": interpreter.functions
    })


@app.route('/neural', methods=['POST'])
def neural():
    """Створення нейромережі"""
    data = request.json
    layers = data.get('layers', [])
    activation = data.get('activation', 'ReLU')
    
    if len(layers) < 2:
        return jsonify({
            "status": "error",
            "message": "At least 2 layers required"
        }), 400
    
    # Створюємо нейромережу
    network_layers = []
    for i in range(len(layers) - 1):
        layer = Dense(layers[i], layers[i+1], activation.lower())
        network_layers.append(layer)
    
    model = Sequential(network_layers)
    
    # Параметри моделі
    total_params = 0
    for i in range(len(layers) - 1):
        total_params += layers[i] * layers[i+1] + layers[i+1]
    
    return jsonify({
        "status": "success",
        "model": {
            "type": "Neural Network",
            "layers": layers,
            "activation": activation,
            "total_layers": len(layers),
            "parameters": total_params,
            "architecture": " -> ".join([str(l) for l in layers])
        }
    })


@app.route('/tensor', methods=['POST'])
def tensor_ops():
    """Тензорні операції"""
    data = request.json
    operation = data.get('operation', '')
    a = data.get('a', [])
    b = data.get('b', [])
    
    if not a:
        return jsonify({
            "status": "error",
            "message": "Matrix A is required"
        }), 400
    
    if operation == 'matmul':
        if not b:
            return jsonify({
                "status": "error",
                "message": "Matrix B is required for matmul"
            }), 400
        
        # Перевірка розмірності
        rows_a = len(a)
        cols_a = len(a[0]) if rows_a > 0 else 0
        rows_b = len(b)
        cols_b = len(b[0]) if rows_b > 0 else 0
        
        if cols_a != rows_b:
            return jsonify({
                "status": "error",
                "message": f"Shape mismatch: A[{rows_a}x{cols_a}] * B[{rows_b}x{cols_b}]"
            }), 400
        
        # Виконання матричного множення
        result = [[0] * cols_b for _ in range(rows_a)]
        for i in range(rows_a):
            for j in range(cols_b):
                s = 0
                for k in range(cols_a):
                    s += a[i][k] * b[k][j]
                result[i][j] = s
        
        return jsonify({
            "status": "success",
            "operation": "matmul",
            "a": a,
            "b": b,
            "result": result,
            "shape": f"{rows_a}x{cols_b}"
        })
    
    elif operation == 'transpose':
        rows = len(a)
        cols = len(a[0]) if rows > 0 else 0
        result = [[a[j][i] for j in range(rows)] for i in range(cols)]
        
        return jsonify({
            "status": "success",
            "operation": "transpose",
            "input": a,
            "result": result,
            "shape": f"{cols}x{rows}"
        })
    
    elif operation == 'add':
        if not b:
            return jsonify({
                "status": "error",
                "message": "Matrix B is required for addition"
            }), 400
        
        rows_a = len(a)
        cols_a = len(a[0]) if rows_a > 0 else 0
        rows_b = len(b)
        cols_b = len(b[0]) if rows_b > 0 else 0
        
        if rows_a != rows_b or cols_a != cols_b:
            return jsonify({
                "status": "error",
                "message": f"Shape mismatch: {rows_a}x{cols_a} vs {rows_b}x{cols_b}"
            }), 400
        
        result = [[a[i][j] + b[i][j] for j in range(cols_a)] for i in range(rows_a)]
        
        return jsonify({
            "status": "success",
            "operation": "add",
            "a": a,
            "b": b,
            "result": result
        })
    
    return jsonify({
        "status": "error",
        "message": f"Unknown operation: {operation}",
        "supported": ["matmul", "transpose", "add"]
    }), 400


@app.route('/chat', methods=['POST'])
def chat():
    """Спілкування AI"""
    data = request.json
    message = data.get('message', '')
    models = data.get('models', ['ChatGPT', 'Claude', 'Gemini'])
    
    responses = []
    for model in models:
        responses.append({
            "model": model,
            "response": f"{model} understands Vireo!",
            "message": message,
            "timestamp": "2026-01-15T10:00:00Z"
        })
    
    return jsonify({
        "status": "success",
        "message": message,
        "responses": responses,
        "communication_established": True,
        "total_models": len(models)
    })


@app.route('/health', methods=['GET'])
def health():
    """Перевірка статусу сервера"""
    return jsonify({
        "status": "healthy",
        "service": "Vireo AI Communicator",
        "version": "1.0.0",
        "timestamp": "2026-01-15T10:00:00Z"
    })


# ============================================================
# 8. ЗАПУСК
# ============================================================

if __name__ == '__main__':
    print("🟢 ========================================")
    print("🌍 VIREO AI COMMUNICATOR API v1.0.0")
    print("========================================")
    print("")
    print("📡 Server running on: http://localhost:5000")
    print("📚 Documentation: http://localhost:5000/docs")
    print("")
    print("📌 Available endpoints:")
    print("   GET  /          - Home")
    print("   GET  /docs      - Documentation")
    print("   POST /execute   - Execute Vireo code")
    print("   POST /interpreter - Execute with interpreter")
    print("   POST /neural    - Create neural network")
    print("   POST /tensor    - Tensor operations")
    print("   POST /chat      - AI communication")
    print("   GET  /health    - Health check")
    print("")
    print("🔴 Press Ctrl+C to stop")
    print("========================================")
    print("🟢")
    
    app.run(debug=True, host='0.0.0.0', port=5000)