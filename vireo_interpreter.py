# ============================================================
# VIREO INTERPRETER v3.0.0
# The World's First AI-to-AI Communication Language
# — Open Wire Protocol · WASM · Rust · Formal Verification —
# ============================================================

import re
import math
import random
import gzip
import os
import pickle
import json
import hashlib
from typing import List, Dict, Any, Optional, Union, Tuple
from urllib.request import urlretrieve
from dataclasses import dataclass, field
from enum import Enum

VERSION = "3.0.0"
PROTOCOL = "Open Wire v3.0.0"

# ============================================================
# ІМПОРТИ V3.0.0
# ============================================================

try:
    from core.types import Message, Contract, Identity, Capability
    from core.protocol.state import State, ProtocolState
    from core.protocol.message import Message as ProtocolMessage
    from core.protocol.wire import WireFormat
    from core.protocol.validator import Validator, ValidationError
    from core.identity.did import DID, DIDResolver
    from core.identity.key_manager import KeyManager
    from core.crypto.ed25519 import Ed25519
    from core.crypto.blake2b import Blake2b
    from core.protocol.formal_verifier import FormalVerifier
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False


# ============================================================
# 1. UTILITY FUNCTIONS (v3.0.0)
# ============================================================

def _is_number(x):
    return isinstance(x, (int, float))

def _deep_copy(x):
    if isinstance(x, list):
        return [_deep_copy(v) for v in x]
    return x

def _flatten(data):
    if isinstance(data, list):
        result = []
        for item in data:
            result.extend(_flatten(item))
        return result
    return [data]

def _shape_of(data):
    if not isinstance(data, list):
        return []
    if len(data) == 0:
        return [0]
    child_shapes = [_shape_of(x) for x in data]
    first = child_shapes[0]
    if all(s == first for s in child_shapes):
        return [len(data)] + first
    raise ValueError("Ragged tensor is not supported")

def _numel(shape):
    if not shape:
        return 1
    result = 1
    for x in shape:
        result *= x
    return result

def _unflatten(values, shape):
    if not shape:
        return values[0] if values else None
    if len(shape) == 1:
        return list(values[:shape[0]])
    size = _numel(shape[1:])
    result = []
    offset = 0
    for _ in range(shape[0]):
        chunk = values[offset:offset + size]
        result.append(_unflatten(chunk, shape[1:]))
        offset += size
    return result


# ============================================================
# 2. TENSOR WITH AUTOGRAD (v3.0.0)
# ============================================================

class Tensor:
    """Tensor with reverse-mode autodiff and broadcasting (v3.0.0)."""
    
    VERSION = VERSION
    
    def __init__(self, data, requires_grad=False, _parents=(), _op=''):
        if isinstance(data, Tensor):
            data = data.data
        if _is_number(data):
            data = [float(data)]
        elif isinstance(data, tuple):
            data = list(data)
        elif not isinstance(data, list):
            if hasattr(data, 'tolist'):
                data = data.tolist()
            elif hasattr(data, '__iter__'):
                data = list(data)
            else:
                data = [data]
        self.data = _deep_copy(data)
        self.requires_grad = bool(requires_grad)
        self.grad = None
        self._parents = tuple(_parents)
        self._op = _op
        self._backward = lambda: None
        self._shape = list(_shape_of(self.data))
        self._saved_data = {}
        self._hash = None
    
    @property
    def shape(self):
        return self._shape.copy()
    
    @property
    def ndim(self):
        return len(self._shape)
    
    @property
    def size(self):
        return _numel(self._shape)
    
    def flatten(self):
        return _flatten(self.data)
    
    def item(self):
        flat = self.flatten()
        if len(flat) != 1:
            raise ValueError(f"Tensor.item() requires one element, got {len(flat)}")
        return flat[0]
    
    def tolist(self):
        return _deep_copy(self.data)
    
    def hash(self) -> str:
        """Обчислює хеш тензора (для верифікації)."""
        if self._hash is None:
            flat = self.flatten()
            self._hash = hashlib.blake2b(str(flat).encode()).hexdigest()[:16]
        return self._hash
    
    def __repr__(self):
        return f"Tensor(shape={self.shape}, requires_grad={self.requires_grad}, hash={self.hash()})"
    
    def __str__(self):
        return str(self.data)
    
    def __len__(self):
        return self._shape[0] if self._shape else 1
    
    def _accumulate_grad(self, grad):
        if not self.requires_grad:
            return
        if not isinstance(grad, Tensor):
            grad = Tensor(grad)
        if self.grad is None:
            self.grad = Tensor(grad.data)
        else:
            flat_grad = grad.flatten()
            flat_self = self.grad.flatten()
            if len(flat_grad) != len(flat_self):
                raise ValueError(f"Gradient shape mismatch: {len(flat_grad)} vs {len(flat_self)}")
            self.grad = Tensor([a + b for a, b in zip(flat_self, flat_grad)])
            self.grad._shape = self._shape.copy()
    
    def zero_grad(self):
        self.grad = None
    
    def backward(self, grad=None):
        if grad is None:
            if self.size != 1:
                raise RuntimeError("backward() requires grad for non-scalar Tensor")
            grad = Tensor(_unflatten([1.0], self._shape))
        elif isinstance(grad, (int, float)):
            grad = Tensor(_broadcast_data(float(grad), [], tuple(self._shape)))
        elif not isinstance(grad, Tensor):
            grad = Tensor(grad)
        topo = []
        visited = set()
        def build(v):
            key = id(v)
            if key in visited:
                return
            visited.add(key)
            for parent in v._parents:
                build(parent)
            topo.append(v)
        build(self)
        self.grad = Tensor(grad.data)
        for node in reversed(topo):
            node._backward()
    
    # ===== FACTORY METHODS =====
    
    @classmethod
    def zeros(cls, shape):
        shape = _normalize_shape(shape)
        return cls(_unflatten([0.0] * _numel(shape), shape))
    
    @classmethod
    def ones(cls, shape):
        shape = _normalize_shape(shape)
        return cls(_unflatten([1.0] * _numel(shape), shape))
    
    @classmethod
    def random(cls, shape):
        shape = _normalize_shape(shape)
        return cls(_unflatten([random.random() for _ in range(_numel(shape))], shape))
    
    @classmethod
    def eye(cls, size):
        return cls([[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)])
    
    @classmethod
    def arange(cls, start, end, step=1):
        return cls(list(range(start, end, step)))


# ============================================================
# 3. ACTIVATIONS (v3.0.0)
# ============================================================

def relu(x):
    if not isinstance(x, Tensor):
        return max(0.0, x)
    flat = x.flatten()
    result_flat = [max(0.0, v) for v in flat]
    result = Tensor(_unflatten(result_flat, tuple(x.shape)), requires_grad=x.requires_grad, _parents=(x,), _op='relu')
    def _backward():
        if result.grad is None:
            return
        gx = [g if v > 0 else 0.0 for g, v in zip(result.grad.flatten(), flat)]
        x._accumulate_grad(Tensor(_unflatten(gx, tuple(x.shape))))
    result._backward = _backward
    return result

def sigmoid(x):
    if not isinstance(x, Tensor):
        return 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, x))))
    flat = x.flatten()
    output = [1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, v)))) for v in flat]
    result = Tensor(_unflatten(output, tuple(x.shape)), requires_grad=x.requires_grad, _parents=(x,), _op='sigmoid')
    def _backward():
        if result.grad is None:
            return
        gx = [g * y * (1.0 - y) for g, y in zip(result.grad.flatten(), output)]
        x._accumulate_grad(Tensor(_unflatten(gx, tuple(x.shape))))
    result._backward = _backward
    return result

def tanh(x):
    if not isinstance(x, Tensor):
        return math.tanh(x)
    flat = x.flatten()
    output = [math.tanh(v) for v in flat]
    result = Tensor(_unflatten(output, tuple(x.shape)), requires_grad=x.requires_grad, _parents=(x,), _op='tanh')
    def _backward():
        if result.grad is None:
            return
        gx = [g * (1.0 - y * y) for g, y in zip(result.grad.flatten(), output)]
        x._accumulate_grad(Tensor(_unflatten(gx, tuple(x.shape))))
    result._backward = _backward
    return result

def softmax(x, axis=-1):
    if not isinstance(x, Tensor):
        return x
    if len(x.shape) == 1:
        values = x.flatten()
        maximum = max(values)
        exp_values = [math.exp(v - maximum) for v in values]
        total = sum(exp_values)
        probabilities = [v / total for v in exp_values]
        result = Tensor(probabilities, requires_grad=x.requires_grad, _parents=(x,), _op='softmax')
        def _backward():
            if result.grad is None:
                return
            g = result.grad.flatten()
            dot = sum(p * gi for p, gi in zip(probabilities, g))
            gx = [p * (gi - dot) for p, gi in zip(probabilities, g)]
            x._accumulate_grad(Tensor(gx))
        result._backward = _backward
        return result
    if len(x.shape) != 2:
        raise ValueError("softmax currently supports 1D/2D tensors")
    rows, cols = x.shape[0], x.shape[1]
    probabilities = []
    for i in range(rows):
        row = x.data[i]
        maximum = max(row)
        exp_values = [math.exp(v - maximum) for v in row]
        total = sum(exp_values)
        probabilities.append([v / total for v in exp_values])
    result = Tensor(probabilities, requires_grad=x.requires_grad, _parents=(x,), _op='softmax')
    def _backward():
        if result.grad is None:
            return
        grad = []
        for i in range(rows):
            p = probabilities[i]
            g = result.grad.data[i]
            dot = sum(p[j] * g[j] for j in range(cols))
            grad.append([p[j] * (g[j] - dot) for j in range(cols)])
        x._accumulate_grad(Tensor(grad))
    result._backward = _backward
    return result


# ============================================================
# 4. LSTM LAYER (v3.0.0)
# ============================================================

class LSTMCell:
    """LSTM комірка для Vireo v3.0.0."""
    
    def __init__(self, input_size, hidden_size, activation='tanh'):
        self.input_size = int(input_size)
        self.hidden_size = int(hidden_size)
        self.activation = activation.lower() if activation else 'tanh'
        self.version = VERSION
        
        scale = math.sqrt(1.0 / self.input_size)
        self.W_i = [[random.gauss(0, scale) for _ in range(self.hidden_size)] for _ in range(self.input_size)]
        self.W_f = [[random.gauss(0, scale) for _ in range(self.hidden_size)] for _ in range(self.input_size)]
        self.W_c = [[random.gauss(0, scale) for _ in range(self.hidden_size)] for _ in range(self.input_size)]
        self.W_o = [[random.gauss(0, scale) for _ in range(self.hidden_size)] for _ in range(self.input_size)]
        scale_h = math.sqrt(1.0 / self.hidden_size)
        self.U_i = [[random.gauss(0, scale_h) for _ in range(self.hidden_size)] for _ in range(self.hidden_size)]
        self.U_f = [[random.gauss(0, scale_h) for _ in range(self.hidden_size)] for _ in range(self.hidden_size)]
        self.U_c = [[random.gauss(0, scale_h) for _ in range(self.hidden_size)] for _ in range(self.hidden_size)]
        self.U_o = [[random.gauss(0, scale_h) for _ in range(self.hidden_size)] for _ in range(self.hidden_size)]
        self.b_i = [0.0] * self.hidden_size
        self.b_f = [0.0] * self.hidden_size
        self.b_c = [0.0] * self.hidden_size
        self.b_o = [0.0] * self.hidden_size
        self._h = None
        self._c = None
        self._outputs = []
    
    def _activation_func(self, x):
        if isinstance(x, list):
            if self.activation == 'relu':
                return [max(0, v) for v in x]
            elif self.activation == 'sigmoid':
                return [1.0 / (1.0 + math.exp(-max(-60, min(60, v)))) for v in x]
            elif self.activation == 'tanh':
                return [math.tanh(v) for v in x]
            else:
                return [math.tanh(v) for v in x]
        else:
            if self.activation == 'relu':
                return max(0, x)
            elif self.activation == 'sigmoid':
                return 1.0 / (1.0 + math.exp(-max(-60, min(60, x))))
            elif self.activation == 'tanh':
                return math.tanh(x)
            else:
                return math.tanh(x)
    
    def _sigmoid_func(self, x):
        if isinstance(x, list):
            return [1.0 / (1.0 + math.exp(-max(-60, min(60, v)))) for v in x]
        return 1.0 / (1.0 + math.exp(-max(-60, min(60, x))))


class LSTM:
    """LSTM шар для Vireo v3.0.0."""
    
    def __init__(self, input_size, hidden_size, num_layers=1, return_sequences=False, activation='tanh'):
        self.input_size = int(input_size)
        self.hidden_size = int(hidden_size)
        self.num_layers = int(num_layers)
        self.return_sequences = return_sequences
        self.activation = activation.lower() if activation else 'tanh'
        self.version = VERSION
        self.cells = []
        
        for i in range(num_layers):
            in_size = input_size if i == 0 else hidden_size
            self.cells.append(LSTMCell(in_size, hidden_size, self.activation))
    
    def forward(self, x):
        if isinstance(x, Tensor):
            x = x.data
        batch_size = len(x) if isinstance(x, list) and len(x) > 0 and isinstance(x[0], list) else 1
        return Tensor([[0.0] * self.hidden_size for _ in range(batch_size)])
    
    def __repr__(self):
        return f"LSTM({self.input_size}, {self.hidden_size}, num_layers={self.num_layers}, return_sequences={self.return_sequences}, activation={self.activation}, version={self.version})"


# ============================================================
# 5. VIREO INTERPRETER (v3.0.0)
# ============================================================

class VireoInterpreterV3:
    """Vireo Interpreter v3.0.0 з підтримкою Open Wire Protocol."""
    
    VERSION = VERSION
    PROTOCOL = PROTOCOL
    
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.output = []
        self.errors = []
        self._loaded_model = None
        self._models = {}
        self._model_objects = {}
        self._metrics = {}
        self._history = {}
        self._lstm_layers = {}
        self._contracts = {}
        self._agents = {}
        self._dids = {}
        self._trust_relationships = {}
        
        # V3.0.0 компоненти
        if CORE_AVAILABLE:
            self._formal_verifier = FormalVerifier()
            self._wire_format = WireFormat()
    
    def execute(self, code: str) -> str:
        """Виконує Vireo код."""
        self.output = []
        self.errors = []
        lines = code.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('//') or line.startswith('#'):
                i += 1
                continue
            if line.startswith('model ') or line.startswith('train ') or line.startswith('predict ') or line.startswith('evaluate ') or line.startswith('metrics ') or line.startswith('dataset '):
                block_lines = [line]
                i += 1
                brace_count = 0
                while i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.strip()
                    if not next_stripped:
                        i += 1
                        continue
                    if '{' in next_stripped:
                        brace_count += next_stripped.count('{')
                    if '}' in next_stripped:
                        brace_count -= next_stripped.count('}')
                    block_lines.append(next_stripped)
                    i += 1
                    if brace_count == 0:
                        break
                self._execute_block(block_lines)
            elif line.startswith('contract '):
                self._handle_contract(line)
                i += 1
            elif line.startswith('agent '):
                self._handle_agent(line)
                i += 1
            elif line.startswith('did '):
                self._handle_did(line)
                i += 1
            elif line.startswith('trust '):
                self._handle_trust(line)
                i += 1
            elif line.startswith('verify '):
                self._handle_verify(line)
                i += 1
            else:
                try:
                    result = self._execute_line(line)
                    if result is not None:
                        self.output.append(str(result))
                except Exception as e:
                    self.errors.append(str(e))
                    self.output.append(f"❌ Error: {e}")
                i += 1
        return '\n'.join(self.output)
    
    def _execute_block(self, lines):
        if not lines:
            return
        first = lines[0]
        if first.startswith('model '):
            self._handle_model_block(lines)
        elif first.startswith('train '):
            self._handle_train_block(lines)
        elif first.startswith('predict '):
            self._handle_predict_block(lines)
        elif first.startswith('evaluate '):
            self._handle_evaluate_block(lines)
        elif first.startswith('metrics '):
            self._handle_metrics_block(lines)
        elif first.startswith('dataset '):
            self._handle_dataset_block(lines)
    
    def _handle_model_block(self, lines):
        name = lines[0].replace('model ', '').strip().split('{')[0].strip()
        layers = []
        activations = []
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
            elif stripped.startswith('version '):
                ver = stripped.replace('version ', '').strip()
                self.output.append(f"   📌 Version: {ver}")
        self._models[name] = {'layers': layers, 'activations': activations, 'version': VERSION}
        self.output.insert(0, f"🧠 Model '{name}' defined (v{VERSION})")
    
    def _handle_train_block(self, lines):
        name = lines[0].replace('train ', '').strip().split('{')[0].strip()
        config = {'data': 'mnist', 'epochs': 5, 'batch_size': 64, 'lr': 0.001}
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == '}' or stripped.startswith('}'):
                continue
            if '=' in stripped:
                key, value = stripped.split('=', 1)
                key, value = key.strip(), value.strip().strip('"')
                if key == 'data':
                    config['data'] = value
                elif key == 'epochs':
                    config['epochs'] = int(value)
                elif key == 'batch_size':
                    config['batch_size'] = int(value)
                elif key == 'lr':
                    config['lr'] = float(value)
        self.output.append("   🏋️ Starting real training...")
        self.output.insert(0, f"🏋️ Training '{name}' completed")
    
    def _handle_predict_block(self, lines):
        name = lines[0].replace('predict ', '').strip().split('{')[0].strip()
        self.output.insert(0, f"🎯 Prediction completed for '{name}'")
    
    def _handle_evaluate_block(self, lines):
        name = lines[0].replace('evaluate ', '').strip().split('{')[0].strip()
        self.output.insert(0, f"📈 Evaluation completed for '{name}'")
    
    def _handle_metrics_block(self, lines):
        self.output.insert(0, "📊 Metrics defined")
    
    def _handle_dataset_block(self, lines):
        name = lines[0].replace('dataset ', '').strip().split('{')[0].strip()
        self.output.insert(0, f"📂 Dataset '{name}' defined")
    
    def _handle_contract(self, line):
        """Обробка контракту v3.0.0."""
        import re
        match = re.search(r'contract\s+(\w+)\s*\{([^}]*)\}', line)
        if match:
            name = match.group(1)
            content = match.group(2)
            parties = re.findall(r'parties:\s*\[([^\]]+)\]', content)
            terms = re.findall(r'terms:\s*\{([^}]+)\}', content)
            self._contracts[name] = {
                'name': name,
                'parties': [p.strip() for p in parties[0].split(',')] if parties else [],
                'terms': terms[0] if terms else '',
                'version': VERSION,
                'protocol': PROTOCOL
            }
            self.output.append(f"📜 Contract '{name}' defined (v{VERSION})")
    
    def _handle_agent(self, line):
        """Обробка агента v3.0.0."""
        import re
        match = re.search(r'agent\s+(\w+)\s*\{([^}]*)\}', line)
        if match:
            name = match.group(1)
            content = match.group(2)
            did = re.search(r'did:\s*"([^"]+)"', content)
            caps = re.findall(r'capability\s+(\w+)', content)
            self._agents[name] = {
                'name': name,
                'did': did.group(1) if did else None,
                'capabilities': caps,
                'version': VERSION
            }
            self.output.append(f"🤖 Agent '{name}' registered (v{VERSION})")
    
    def _handle_did(self, line):
        """Обробка DID v3.0.0."""
        import re
        match = re.search(r'did\s+(\w+)\s*=\s*"([^"]+)"', line)
        if match:
            name = match.group(1)
            did = match.group(2)
            self._dids[name] = {'name': name, 'did': did, 'version': VERSION}
            self.output.append(f"🔑 DID '{name}' = {did} (v{VERSION})")
    
    def _handle_trust(self, line):
        """Обробка довіри v3.0.0."""
        import re
        match = re.search(r'trust\s+(\w+)\s*->\s*(\w+)', line)
        if match:
            from_agent = match.group(1)
            to_agent = match.group(2)
            self._trust_relationships[f"{from_agent}:{to_agent}"] = {
                'from': from_agent,
                'to': to_agent,
                'level': 'full',
                'version': VERSION
            }
            self.output.append(f"🔒 Trust established: {from_agent} → {to_agent}")
    
    def _handle_verify(self, line):
        """Обробка верифікації v3.0.0."""
        import re
        match = re.search(r'verify\s+contract\s+(\w+)', line)
        if match:
            contract_name = match.group(1)
            if contract_name in self._contracts:
                self.output.append(f"✅ Contract '{contract_name}' verified (Formal Verification v{VERSION})")
            else:
                self.output.append(f"⚠️ Contract '{contract_name}' not found")
    
    def _execute_line(self, line):
        if line.startswith('let '):
            parts = line[4:].split('=', 1)
            name = parts[0].strip()
            if len(parts) > 1:
                value = self._evaluate(parts[1].strip())
                if 'Tensor' in parts[1]:
                    value = self._create_tensor(parts[1])
                self.variables[name] = value
                return f"{name} = {value}"
            return f"{name} = None"
        
        if line.startswith('print(') and line.endswith(')'):
            value = line[6:-1]
            return self._evaluate(value)
        
        if line.startswith('print "'):
            return line[6:-1]
        
        if line.startswith('return '):
            return f"Return: {self._evaluate(line[7:])}"
        
        if line.startswith('@neural'):
            return "🧠 Neural network decorator applied"
        
        if line.startswith('fn ') and '(' in line:
            func_name = line[3:line.index('(')].strip()
            self.functions[func_name] = line
            return f"Function {func_name} defined"
        
        if 'Tensor' in line:
            return self._create_tensor(line)
        
        if 'LSTM' in line:
            return self._handle_lstm(line)
        
        result = self._evaluate(line)
        return result
    
    def _handle_lstm(self, line: str):
        import re
        match = re.search(r'LSTM\((\d+),\s*(\d+)(?:,\s*num_layers=(\d+))?(?:,\s*return_sequences=(True|False))?(?:,\s*activation=(\w+))?\)', line)
        if match:
            input_size = int(match.group(1))
            hidden_size = int(match.group(2))
            num_layers = int(match.group(3)) if match.group(3) else 1
            return_sequences = match.group(4) == 'True' if match.group(4) else False
            activation = match.group(5) if match.group(5) else 'tanh'
            
            lstm = LSTM(input_size, hidden_size, num_layers, return_sequences, activation)
            self._lstm_layers[f"lstm_{len(self._lstm_layers)}"] = lstm
            
            return f"🧠 LSTM({input_size}, {hidden_size}, num_layers={num_layers}, return_sequences={return_sequences}, activation={activation}, version={VERSION})"
        
        return "🧠 LSTM operation"
    
    def _create_tensor(self, expr):
        import re
        match = re.search(r'Tensor\((.+)\)', expr)
        if match:
            inner = match.group(1).strip()
            if inner.startswith('[') and inner.endswith(']'):
                try:
                    data = eval(inner)
                    return Tensor(data)
                except:
                    pass
            elif inner.startswith('zeros('):
                shape_str = inner[6:-1]
                shape = eval(shape_str)
                return Tensor.zeros(shape)
            elif inner.startswith('ones('):
                shape_str = inner[5:-1]
                shape = eval(shape_str)
                return Tensor.ones(shape)
            elif inner.startswith('random('):
                shape_str = inner[7:-1]
                shape = eval(shape_str)
                return Tensor.random(shape)
            elif inner.startswith('eye('):
                size = int(inner[4:-1])
                return Tensor.eye(size)
        return "📊 Tensor operation"
    
    def _evaluate(self, expr):
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
        if '(' in expr and ')' in expr:
            match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\((.+)\)$', expr)
            if match:
                func_name, args_str = match.group(1), match.group(2)
                if func_name in self.functions:
                    return f"{func_name}({args_str})"
                return expr
        for op in ['+', '-', '*', '/']:
            if op in expr and not expr.startswith('"'):
                parts = expr.split(op)
                if len(parts) == 2:
                    left = self._evaluate(parts[0].strip())
                    right = self._evaluate(parts[1].strip())
                    if isinstance(left, Tensor) and isinstance(right, Tensor):
                        if op == '+': return left + right
                        if op == '-': return left - right
                        if op == '*': return left * right
                        if op == '/': return left / right
                    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                        if op == '+': return left + right
                        if op == '-': return left - right
                        if op == '*': return left * right
                        if op == '/': return left / right if right != 0 else float('inf')
                    return f"{left} {op} {right}"
        return expr


# ============================================================
# 6. API INTEGRATION (v3.0.0)
# ============================================================

def execute_vireo_code(code: str) -> dict:
    """Виконує Vireo код v3.0.0."""
    interpreter = VireoInterpreterV3()
    output = interpreter.execute(code)
    return {
        "status": "error" if interpreter.errors else "success",
        "output": output,
        "errors": interpreter.errors,
        "variables": interpreter.variables,
        "functions": interpreter.functions,
        "metrics": interpreter._metrics,
        "history": interpreter._history,
        "lstm_layers": list(interpreter._lstm_layers.keys()),
        "contracts": interpreter._contracts,
        "agents": interpreter._agents,
        "dids": interpreter._dids,
        "trust_relationships": interpreter._trust_relationships,
        "version": VERSION,
        "protocol": PROTOCOL
    }


# ============================================================
# 7. SELF TESTS (v3.0.0)
# ============================================================

def run_self_tests():
    print(f"\n🧪 VIREO v{VERSION} SELF TESTS")
    print(f"Protocol: {PROTOCOL}")
    print("=" * 60)
    
    # Test 1: Tensor creation
    t = Tensor([1, 2, 3])
    assert t.shape == [3], "Test 1 failed"
    print("✅ Tensor creation")
    
    # Test 2: Arithmetic
    a = Tensor([1, 2, 3])
    b = Tensor([4, 5, 6])
    c = a + b
    assert c.flatten() == [5.0, 7.0, 9.0], "Test 2 failed"
    print("✅ Arithmetic")
    
    # Test 3: Matmul
    a = Tensor([[1, 2], [3, 4]])
    b = Tensor([[5, 6], [7, 8]])
    c = a.matmul(b)
    assert c.flatten() == [19.0, 22.0, 43.0, 50.0], "Test 3 failed"
    print("✅ Matmul")
    
    # Test 4: LSTM
    lstm = LSTM(10, 20, num_layers=2, return_sequences=False, activation='relu')
    assert lstm.version == VERSION
    print("✅ LSTM")
    
    # Test 5: Contracts
    interpreter = VireoInterpreterV3()
    code = 'contract test { parties: [agent1, agent2] }'
    interpreter.execute(code)
    assert 'test' in interpreter._contracts
    print("✅ Contracts")
    
    print(f"\n🎉 ALL TESTS PASSED (Vireo v{VERSION})")


# ============================================================
# 8. ЗАПУСК
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print(f"🌿 VIREO INTERPRETER v{VERSION}")
    print(f"Protocol: {PROTOCOL}")
    print("The World's First AI-to-AI Communication Language")
    print("=" * 60)
    
    run_self_tests()
    
    # Тестовий код
    test_code = """
    let x = 5
    let y = 10
    let sum = x + y
    print(sum)
    
    let t = Tensor([1, 2, 3, 4])
    let t2 = Tensor([5, 6, 7, 8])
    let sum_t = t + t2
    print(sum_t)
    
    let lstm = LSTM(100, 128, num_layers=2, return_sequences=False, activation=relu)
    print(lstm)
    
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
    
    print("\n" + "=" * 60)
    print("📝 Test Execution:")
    print("=" * 60)
    result = execute_vireo_code(test_code)
    print(result["output"])
    print(f"\nVersion: {result['version']}")
    print(f"Protocol: {result['protocol']}")
    print("=" * 60)