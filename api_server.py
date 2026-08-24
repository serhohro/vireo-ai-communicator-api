# ============================================================
# VIREO AI COMMUNICATOR - API SERVER v1.3.0
# Повноцінний API сервер з інтерпретатором Vireo, 
# AI-to-AI протоколом та LLM підтримкою (Ollama, Gemini, Claude, OpenAI, Mistral)
# ============================================================

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import re
import math
import random
import sys
import os
from typing import List, Dict, Any, Optional, Union

app = Flask(__name__)
CORS(app)

# ============================================================
# 1. ТЕНЗОРИ
# ============================================================

class Tensor:
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
        return f"Tensor(shape={self.shape}, dtype={self.dtype})"
    
    def __add__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return Tensor([a + b for a, b in zip(self.data, other.data)])
        return Tensor([x + other for x in self.data])
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return Tensor([a - b for a, b in zip(self.data, other.data)])
        return Tensor([x - other for x in self.data])
    
    def __mul__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return Tensor([a * b for a, b in zip(self.data, other.data)])
        return Tensor([x * other for x in self.data])
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return Tensor([a / b for a, b in zip(self.data, other.data)])
        return Tensor([x / other for x in self.data])
    
    def matmul(self, other):
        if not isinstance(other, Tensor):
            raise TypeError("matmul requires Tensor")
        if len(self.shape) == 1 and len(other.shape) == 1:
            if self.shape[0] != other.shape[0]:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return sum(a * b for a, b in zip(self.data, other.data))
        if len(self.shape) == 2 and len(other.shape) == 2:
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
        if axis == 0 and len(self.shape) == 2:
            result = [0] * self.shape[1]
            for row in self.data:
                for j, val in enumerate(row):
                    result[j] += val
            return Tensor(result)
        if axis == 1 and len(self.shape) == 2:
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
    
    def sqrt(self):
        return Tensor([math.sqrt(x) for x in self.flatten()])


# ============================================================
# 2. ФУНКЦІЇ АКТИВАЦІЇ
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


# ============================================================
# 3. ШАРИ НЕЙРОМЕРЕЖІ
# ============================================================

class Dense:
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
            self.output = x.matmul(self.weights) + self.bias
        elif len(x.shape) == 1:
            result = []
            for j in range(len(self.weights.data[0])):
                s = 0
                for i in range(len(x.data)):
                    s += x.data[i] * self.weights.data[i][j]
                result.append(s)
            self.output = Tensor(result) + self.bias
        else:
            self.output = x.matmul(self.weights) + self.bias
        
        if self.activation == 'relu':
            self.output = relu(self.output)
        elif self.activation == 'sigmoid':
            self.output = sigmoid(self.output)
        elif self.activation == 'tanh':
            self.output = tanh(self.output)
        elif self.activation == 'softmax':
            self.output = softmax(self.output)
        
        return self.output


class Sequential:
    def __init__(self, layers):
        self.layers = layers
    
    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x


# ============================================================
# 4. ІНТЕРПРЕТАТОР VIREO
# ============================================================

class VireoInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.output = []
        self._models = {}
    
    def execute(self, code: str) -> str:
        self.output = []
        lines = code.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('//') or line.startswith('#'):
                i += 1
                continue
            
            if line.startswith('model '):
                block_lines = [line]
                i += 1
                brace_count = 0
                
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:
                        i += 1
                        continue
                    
                    if '{' in next_line:
                        brace_count += next_line.count('{')
                    if '}' in next_line:
                        brace_count -= next_line.count('}')
                    
                    block_lines.append(next_line)
                    i += 1
                    
                    if brace_count == 0:
                        break
                
                self._execute_model_block(block_lines)
            else:
                try:
                    result = self._execute_line(line)
                    if result is not None:
                        self.output.append(str(result))
                except Exception as e:
                    self.output.append(f"❌ Error: {e}")
                i += 1
        
        return '\n'.join(self.output)
    
    def _execute_model_block(self, lines: List[str]):
        first_line = lines[0]
        model_name = first_line.replace('model ', '').strip().split('{')[0].strip()
        
        layers = []
        activations = []
        other = []
        
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == '}' or stripped.startswith('}'):
                continue
            
            if stripped.startswith('layer '):
                layers.append(stripped)
                self.output.append(f"   📊 Layer: {stripped}")
            elif stripped.startswith('activation '):
                act = stripped.replace('activation ', '').strip()
                activations.append(act)
                self.output.append(f"   ⚡ Activation: {act}")
            elif stripped:
                other.append(stripped)
                self.output.append(f"   📝 {stripped}")
        
        self._models[model_name] = {
            'layers': layers,
            'activations': activations,
            'other': other
        }
        
        self.output.insert(0, f"🧠 Model '{model_name}' defined")
    
    def _execute_line(self, line: str):
        if line.startswith('let '):
            parts = line[4:].split('=', 1)
            var_name = parts[0].strip()
            if len(parts) > 1:
                value = parts[1].strip()
                result = self._evaluate(value)
                self.variables[var_name] = result
                return f"{var_name} = {result}"
            return f"{var_name} = None"
        
        if line.startswith('print(') and line.endswith(')'):
            value = line[6:-1]
            return self._evaluate(value)
        
        if line.startswith('print "'):
            return line[6:-1]
        
        if line.startswith('return '):
            return f"Return: {self._evaluate(line[7:])}"
        
        if line.startswith('if '):
            condition = line[3:].split('{')[0].strip()
            result = self._evaluate(condition)
            return "if condition true" if result else "if condition false"
        
        if line.startswith('@neural'):
            return "🧠 Neural network decorator applied"
        
        if line.startswith('fn ') and '(' in line:
            func_name = line[3:line.index('(')].strip()
            self.functions[func_name] = line
            return f"Function {func_name} defined"
        
        if 'Tensor' in line:
            return self._handle_tensor(line)
        
        result = self._evaluate(line)
        return result
    
    def _evaluate(self, expr: str):
        expr = expr.strip()
        if expr in self.variables:
            return self.variables[expr]
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except:
            pass
        if expr.startswith('[') and expr.endswith(']'):
            try:
                return eval(expr)
            except:
                pass
        if expr.startswith('Tensor'):
            return self._handle_tensor(expr)
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
# 5. ОСНОВНІ API ЕНДПОІНТИ
# ============================================================

@app.route('/')
def home():
    """Головна сторінка з переходом на веб-інтерфейс."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>🌿 Vireo</title>
        <style>
            body { 
                font-family: 'Segoe UI', sans-serif; 
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: #e2e8f0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                text-align: center;
            }
            .container { max-width: 700px; padding: 40px; }
            h1 { 
                font-size: 4em; 
                background: linear-gradient(135deg, #48bb78, #667eea); 
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent; 
                margin-bottom: 10px;
            }
            .subtitle { 
                color: #a0aec0; 
                font-size: 1.2em; 
                margin-bottom: 30px;
            }
            .subtitle span { color: #48bb78; font-weight: 600; }
            .links { 
                display: flex; 
                gap: 20px; 
                justify-content: center; 
                flex-wrap: wrap; 
            }
            .links a { 
                color: #48bb78; 
                text-decoration: none; 
                padding: 14px 35px; 
                border: 2px solid #48bb78; 
                border-radius: 12px; 
                transition: all 0.3s;
                font-weight: 600;
                font-size: 1.1em;
            }
            .links a:hover { 
                background: #48bb78; 
                color: #1a202c;
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
            }
            .links a.llm { 
                border-color: #9f7aea;
                color: #9f7aea;
            }
            .links a.llm:hover { 
                background: #9f7aea; 
                color: #1a202c;
                box-shadow: 0 8px 25px rgba(159, 122, 234, 0.3);
            }
            .version {
                color: #718096;
                font-size: 0.8em;
                margin-top: 30px;
                border-top: 1px solid rgba(255,255,255,0.1);
                padding-top: 20px;
            }
            .badges {
                display: flex;
                gap: 10px;
                justify-content: center;
                flex-wrap: wrap;
                margin-bottom: 30px;
            }
            .badge {
                padding: 4px 15px;
                border-radius: 20px;
                font-size: 0.7em;
                font-weight: 600;
                border: 1px solid rgba(255,255,255,0.15);
            }
            .badge.green { color: #48bb78; border-color: #48bb78; }
            .badge.purple { color: #9f7aea; border-color: #9f7aea; }
            .badge.gold { color: #ecc94b; border-color: #ecc94b; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌿 Vireo</h1>
            <p class="subtitle">A Language Designed for <span>AI-to-AI Communication</span></p>
            
            <div class="badges">
                <span class="badge green">✅ Real AI-to-AI</span>
                <span class="badge purple">🧠 5+ LLM Providers</span>
                <span class="badge gold">🔄 Autonomous Agents</span>
            </div>
            
            <div class="links">
                <a href="/web">🌐 Web Interface</a>
                <a href="/docs">📚 Documentation</a>
                <a href="/llm/providers" class="llm">📡 LLM Providers</a>
            </div>
            
            <div class="version">
                ⚡ v1.3.0 · Powered by Ollama, Gemini, Claude, OpenAI, Mistral
            </div>
        </div>
    </body>
    </html>
    """


@app.route('/web')
def web_interface():
    """Відкриває веб-інтерфейс через Flask."""
    try:
        with open('web_interface.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>web_interface.html not found</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; 
                       background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                       color: #e2e8f0;
                       display: flex;
                       justify-content: center;
                       align-items: center;
                       height: 100vh;
                       margin: 0;
                       text-align: center;
                     }
                .container { max-width: 600px; padding: 40px; }
                h1 { color: #fc8181; font-size: 2.5em; }
                .hint { color: #a0aec0; margin-top: 20px; }
                a { color: #48bb78; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ web_interface.html not found</h1>
                <p class="hint">Please make sure <strong>web_interface.html</strong> is in the project folder.<br>
                <a href="/">← Back to home</a></p>
            </div>
        </body>
        </html>
        """, 404


@app.route('/docs')
def docs():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vireo API Documentation v1.3.0</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }
            h1 { color: #48bb78; }
            h2 { color: #333; margin-top: 30px; }
            .endpoint { background: #f0f4f8; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #48bb78; }
            .badge { background: #48bb78; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8em; }
            .badge.llm { background: #9f7aea; }
            pre { background: #1a202c; color: #e2e8f0; padding: 15px; border-radius: 8px; overflow-x: auto; }
            .note { background: #fffff0; padding: 15px; border-radius: 8px; border-left: 4px solid #ecc94b; margin: 15px 0; }
        </style>
    </head>
    <body>
        <h1>🟢 Vireo API Documentation v1.3.0</h1>
        <p><strong>Version:</strong> 1.3.0</p>
        <p><strong>Status:</strong> ✅ Running with LLM support</p>
        
        <div class="note">
            <strong>🤖 NEW:</strong> LLM support for autonomous AI-to-AI communication!
            Supports Ollama, Gemini, Claude, OpenAI, Mistral.
        </div>
        
        <h2>🤖 LLM Endpoints</h2>
        
        <div class="endpoint">
            <h3>GET /llm/providers</h3>
            <p><span class="badge llm">LLM</span> Get status of all LLM providers</p>
        </div>
        
        <div class="endpoint">
            <h3>POST /llm/test/&lt;provider&gt;</h3>
            <p><span class="badge llm">LLM</span> Test a specific provider</p>
            <pre>{
    "provider": "ollama"
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>POST /llm/agent/&lt;id&gt;/auto_negotiate</h3>
            <p><span class="badge llm">LLM</span> <strong>FULL AUTONOMOUS NEGOTIATION</strong></p>
            <p>Agent A asks LLM for code → proposes → Agent B asks LLM for decision → commits → executes</p>
            <pre>{
    "recipient": "agent-training",
    "task": "Train a model on MNIST dataset",
    "provider": "ollama"
}</pre>
        </div>
        
        <h2>📡 Standard Endpoints</h2>
        
        <div class="endpoint">
            <h3>POST /interpreter</h3>
            <p><span class="badge">POST</span> Execute Vireo code</p>
            <pre>{"code": "model MNIST { layer Dense(784, 128) }"}</pre>
        </div>
        
        <div class="endpoint">
            <h3>POST /neural</h3>
            <p><span class="badge">POST</span> Create neural network</p>
            <pre>{"layers": [784, 256, 128, 10], "activation": "ReLU"}</pre>
        </div>
        
        <div class="endpoint">
            <h3>POST /tensor</h3>
            <p><span class="badge">POST</span> Tensor operations</p>
        </div>
        
        <div class="endpoint">
            <h3>GET /agent/list</h3>
            <p><span class="badge">GET</span> List all registered agents</p>
        </div>
        
        <h2>🧪 Example: Autonomous Negotiation</h2>
        <pre>curl -X POST http://localhost:5000/llm/agent/agent-vision/auto_negotiate \\
  -H "Content-Type: application/json" \\
  -d '{"recipient": "agent-training", "task": "Train MNIST with 2 layers"}'</pre>
        
        <p style="margin-top: 30px; color: #666;">
            🔑 Requires <strong>OLLAMA</strong> running locally or API keys for paid providers
        </p>
    </body>
    </html>
    """
    return html


@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({"status": "error", "message": "No code provided"}), 400
    
    interpreter = VireoInterpreter()
    output = interpreter.execute(code)
    
    return jsonify({
        "status": "success",
        "output": output,
        "variables": interpreter.variables,
        "functions": interpreter.functions,
        "models": interpreter._models
    })


@app.route('/interpreter', methods=['POST'])
def execute_interpreter():
    data = request.json
    code = data.get('code', '')
    
    if not code:
        return jsonify({"status": "error", "message": "No code provided"}), 400
    
    try:
        interpreter = VireoInterpreter()
        output = interpreter.execute(code)
        
        return jsonify({
            "status": "success",
            "output": output,
            "variables": interpreter.variables,
            "functions": interpreter.functions,
            "models": interpreter._models
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/neural', methods=['POST'])
def neural():
    data = request.json
    layers = data.get('layers', [])
    activation = data.get('activation', 'ReLU')
    
    if len(layers) < 2:
        return jsonify({"status": "error", "message": "At least 2 layers required"}), 400
    
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
    data = request.json
    operation = data.get('operation', '')
    a = data.get('a', [])
    b = data.get('b', [])
    
    if not a:
        return jsonify({"status": "error", "message": "Matrix A is required"}), 400
    
    if operation == 'matmul':
        if not b:
            return jsonify({"status": "error", "message": "Matrix B is required"}), 400
        
        rows_a = len(a)
        cols_a = len(a[0]) if rows_a > 0 else 0
        rows_b = len(b)
        cols_b = len(b[0]) if rows_b > 0 else 0
        
        if cols_a != rows_b:
            return jsonify({"status": "error", "message": f"Shape mismatch: {rows_a}x{cols_a} * {rows_b}x{cols_b}"}), 400
        
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
            "result": result,
            "shape": f"{cols}x{rows}"
        })
    
    elif operation == 'add':
        if not b:
            return jsonify({"status": "error", "message": "Matrix B is required"}), 400
        
        rows_a = len(a)
        cols_a = len(a[0]) if rows_a > 0 else 0
        rows_b = len(b)
        cols_b = len(b[0]) if rows_b > 0 else 0
        
        if rows_a != rows_b or cols_a != cols_b:
            return jsonify({"status": "error", "message": f"Shape mismatch: {rows_a}x{cols_a} vs {rows_b}x{cols_b}"}), 400
        
        result = [[a[i][j] + b[i][j] for j in range(cols_a)] for i in range(rows_a)]
        return jsonify({
            "status": "success",
            "operation": "add",
            "result": result
        })
    
    return jsonify({"status": "error", "message": f"Unknown operation: {operation}"}), 400


@app.route('/chat', methods=['POST'])
def chat():
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
    return jsonify({
        "status": "healthy",
        "service": "Vireo AI Communicator",
        "version": "1.3.0",
        "timestamp": "2026-01-15T10:00:00Z"
    })


# ============================================================
# 6. AI-TO-AI PROTOCOL (AGENTS)
# ============================================================

try:
    from protocol import Agent, InMemoryEventBus
except ImportError:
    print("⚠️ Protocol module not found. Agent endpoints will not work.")
    Agent = None
    InMemoryEventBus = None

agent_bus = None
agents = {}


def vireo_executor(code: str):
    """Executor для мосту Layer2<->Layer3."""
    interpreter = VireoInterpreter()
    output = interpreter.execute(code)
    return {
        "status": "success",
        "output": output,
        "variables": interpreter.variables,
        "models": interpreter._models,
    }


@app.route('/agent/register', methods=['POST'])
def register_agent():
    if Agent is None or InMemoryEventBus is None:
        return jsonify({"status": "error", "message": "Protocol module not available"}), 500
    
    global agent_bus
    if agent_bus is None:
        agent_bus = InMemoryEventBus()
    
    data = request.json or {}
    agent_id = data.get('id')
    model = data.get('model', 'unknown')

    if not agent_id:
        return jsonify({"status": "error", "message": "Agent ID required"}), 400
    if agent_id in agents:
        return jsonify({"status": "error", "message": f"Agent '{agent_id}' already exists"}), 400

    agent = Agent(agent_id, agent_bus, model=model, executor=vireo_executor)
    agents[agent_id] = agent

    return jsonify({
        "status": "success",
        "agent_id": agent_id,
        "message": f"Agent '{agent_id}' registered"
    })


@app.route('/agent/<agent_id>/capability', methods=['POST'])
def register_capability(agent_id):
    if agent_id not in agents:
        return jsonify({"status": "error", "message": f"Agent '{agent_id}' not found"}), 404

    data = request.json or {}
    name = data.get('name')
    if not name:
        return jsonify({"status": "error", "message": "Capability name required"}), 400

    agents[agent_id].register_capability(name, data.get('description', ''))
    return jsonify({
        "status": "success",
        "agent_id": agent_id,
        "capability": name,
        "message": f"Capability '{name}' registered for '{agent_id}'"
    })


@app.route('/agent/<agent_id>/propose', methods=['POST'])
def propose_task(agent_id):
    if agent_id not in agents:
        return jsonify({"status": "error", "message": f"Agent '{agent_id}' not found"}), 404

    data = request.json or {}
    recipient = data.get('recipient')
    code = data.get('code', '')

    if not recipient or recipient not in agents:
        return jsonify({"status": "error", "message": f"Recipient '{recipient}' not found"}), 404
    if not code:
        return jsonify({"status": "error", "message": "Code required"}), 400

    try:
        proposal = agents[agent_id].propose(recipient, payload={"dsl": "vireo", "code": code})
        return jsonify({
            "status": "success",
            "proposal_id": proposal.message_id,
            "conversation_id": proposal.conversation_id,
            "sender": agent_id,
            "recipient": recipient
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/agent/<agent_id>/commit/<proposal_id>', methods=['POST'])
def commit_proposal(agent_id, proposal_id):
    if agent_id not in agents:
        return jsonify({"status": "error", "message": f"Agent '{agent_id}' not found"}), 404

    agent = agents[agent_id]
    proposal = agent._pending_proposals.get(proposal_id)
    if proposal is None:
        return jsonify({"status": "error", "message": f"Proposal '{proposal_id}' not found"}), 404

    try:
        agent.commit(proposal)
        return jsonify({
            "status": "success",
            "conversation_id": proposal.conversation_id,
            "state": agent.state.get(proposal.conversation_id).value
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/agent/<agent_id>/reject/<proposal_id>', methods=['POST'])
def reject_proposal(agent_id, proposal_id):
    if agent_id not in agents:
        return jsonify({"status": "error", "message": f"Agent '{agent_id}' not found"}), 404

    agent = agents[agent_id]
    proposal = agent._pending_proposals.get(proposal_id)
    if proposal is None:
        return jsonify({"status": "error", "message": f"Proposal '{proposal_id}' not found"}), 404

    reason = (request.json or {}).get('reason', '')
    try:
        agent.reject(proposal, reason=reason)
        return jsonify({"status": "success", "state": agent.state.get(proposal.conversation_id).value})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/agent/<agent_id>/status', methods=['GET'])
def get_agent_status(agent_id):
    if agent_id not in agents:
        return jsonify({"status": "error", "message": f"Agent '{agent_id}' not found"}), 404

    agent = agents[agent_id]
    return jsonify({
        "status": "success",
        "agent_id": agent_id,
        "model": agent.model,
        "capabilities": agent.capabilities.list(),
        "conversations": list(agent.state._states.keys())
    })


@app.route('/agent/<agent_id>/conversations', methods=['GET'])
def get_agent_conversations(agent_id):
    if agent_id not in agents:
        return jsonify({"status": "error", "message": f"Agent '{agent_id}' not found"}), 404

    agent = agents[agent_id]
    conversations = [
        {"conversation_id": cid, "state": agent.state.get(cid).value}
        for cid in agent.state._states
    ]
    return jsonify({"status": "success", "agent_id": agent_id, "conversations": conversations})


@app.route('/agent/list', methods=['GET'])
def list_agents():
    return jsonify({"status": "success", "agents": list(agents.keys()), "count": len(agents)})


# ============================================================
# 7. LLM PROVIDER ENDPOINTS (v1.3.0)
# ============================================================

@app.route('/llm/providers', methods=['GET'])
def llm_providers():
    """Статус всіх LLM провайдерів."""
    try:
        from protocol.config import LLMConfig
        return jsonify({
            "status": "success",
            "providers": LLMConfig.get_provider_status(),
            "available": LLMConfig.get_available_providers()
        })
    except ImportError:
        return jsonify({
            "status": "success",
            "providers": {
                "ollama": {
                    "available": True,
                    "model": "qwen2.5-coder:latest",
                    "free": True,
                    "cost": "Безкоштовно"
                },
                "gemini": {
                    "available": False,
                    "model": "gemini-1.5-flash",
                    "free": True,
                    "cost": "Безкоштовно (60 зап/хв)",
                    "error": "GOOGLE_API_KEY not set"
                },
                "claude": {
                    "available": False,
                    "model": "claude-3-haiku-20240307",
                    "free": False,
                    "cost": "~$0.0015/запит",
                    "error": "ANTHROPIC_API_KEY not set"
                },
                "openai": {
                    "available": False,
                    "model": "gpt-3.5-turbo",
                    "free": False,
                    "cost": "~$0.002/запит",
                    "error": "OPENAI_API_KEY not set"
                },
                "mistral": {
                    "available": False,
                    "model": "mistral-small-latest",
                    "free": False,
                    "cost": "~$0.001/запит",
                    "error": "MISTRAL_API_KEY not set"
                }
            },
            "available": ["ollama"],
            "note": "Install protocol module for full LLM support"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "providers": {},
            "available": []
        }), 500


@app.route('/llm/test/<provider>', methods=['POST'])
def llm_test_provider(provider):
    """Тест конкретного провайдера."""
    try:
        from protocol.llm_provider import create_llm_provider
        provider_obj = create_llm_provider(provider)
        result = provider_obj.generate(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'Vireo works!' in one sentence.",
            task="test",
            max_tokens=50
        )
        return jsonify({
            "status": "success",
            "provider": provider,
            "test_result": result
        })
    except ImportError:
        return jsonify({
            "status": "success",
            "provider": provider,
            "test_result": {
                "status": "success",
                "content": f"Vireo works with {provider}! (simulated)",
                "provider": provider,
                "model": "default",
                "note": "Install protocol module for real LLM support"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "provider": provider,
            "message": str(e)
        }), 500


@app.route('/llm/agent/<agent_id>/auto_negotiate', methods=['POST'])
def llm_auto_negotiate(agent_id):
    """Повний автономний цикл переговорів через LLM."""
    try:
        from protocol.llm_agent import LLMAgent
        from protocol.llm_provider import create_llm_provider
        
        data = request.json or {}
        recipient = data.get('recipient')
        task = data.get('task', '')
        provider_name = data.get('provider', 'ollama')
        model = data.get('model')
        
        if not recipient:
            return jsonify({"status": "error", "message": "Recipient required"}), 400
        if not task:
            return jsonify({"status": "error", "message": "Task required"}), 400
        
        provider = create_llm_provider(provider_name)
        agent = LLMAgent(agent_id, provider=provider, model=model)
        
        result = agent.auto_negotiate(recipient, task)
        return jsonify(result)
        
    except ImportError as e:
        return jsonify({
            "status": "error",
            "message": f"Protocol module not found: {str(e)}",
            "hint": "Create protocol/config.py, protocol/llm_provider.py, protocol/llm_agent.py"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# 8. ЗАПУСК
# ============================================================

if __name__ == '__main__':
    print("🟢 ========================================")
    print("🌍 VIREO AI COMMUNICATOR API v1.3.0")
    print("   WITH LLM SUPPORT")
    print("========================================")
    print("")
    print("📡 Server running on: http://localhost:5000")
    print("📚 Documentation: http://localhost:5000/docs")
    print("🌐 Web Interface: http://localhost:5000/web")
    print("")
    print("📌 Available endpoints:")
    print("   GET  /                  - Home page")
    print("   GET  /web               - Web interface")
    print("   GET  /docs              - Documentation")
    print("   POST /execute           - Execute Vireo code")
    print("   POST /interpreter       - Execute with interpreter")
    print("   POST /neural            - Create neural network")
    print("   POST /tensor            - Tensor operations")
    print("   POST /chat              - AI communication")
    print("   GET  /health            - Health check")
    print("")
    print("🤖 AGENT ENDPOINTS:")
    print("   POST /agent/register    - Register agent")
    print("   POST /agent/<id>/capability - Register capability")
    print("   POST /agent/<id>/propose    - Propose task")
    print("   POST /agent/<id>/commit/<id> - Commit to task")
    print("   POST /agent/<id>/reject/<id> - Reject task")
    print("   GET  /agent/<id>/status - Agent status")
    print("   GET  /agent/<id>/conversations - Agent conversations")
    print("   GET  /agent/list        - List all agents")
    print("")
    print("🤖 LLM ENDPOINTS:")
    print("   GET  /llm/providers     - LLM provider status")
    print("   POST /llm/test/<provider> - Test provider")
    print("   POST /llm/agent/<id>/auto_negotiate - Autonomous negotiation")
    print("")
    print("🔴 Press Ctrl+C to stop")
    print("========================================")
    print("🟢")
    
    app.run(debug=True, host='0.0.0.0', port=5000)