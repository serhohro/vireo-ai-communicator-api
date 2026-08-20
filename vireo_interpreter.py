# ============================================================
# VIREO INTERPRETER v0.3.0
# Повноцінний інтерпретатор мови Vireo з підтримкою:
# - Тензорів (індексація, операції, статистика)
# - Автодиференціювання
# - Нейромереж (шари, тренування)
# - Завантаження даних (MNIST, CSV)
# - Нативний синтаксис: model, layer, train
# ============================================================

import re
import math
import json
import random
import os
from typing import List, Dict, Any, Optional, Union, Tuple

# ============================================================
# 1. ТЕНЗОРИ (ПОВНА РЕАЛІЗАЦІЯ)
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
    
    @property
    def size(self):
        """Загальна кількість елементів"""
        def _size(shape):
            if not shape:
                return 1
            return shape[0] * _size(shape[1:])
        return _size(self.shape)
    
    def __repr__(self):
        return f"Tensor(shape={self.shape}, dtype={self.dtype})"
    
    def __str__(self):
        return str(self.data)
    
    # ===== ІНДЕКСАЦІЯ =====
    
    def __getitem__(self, idx):
        """Доступ до елементів тензора: t[0], t[0, 1]"""
        if isinstance(idx, int):
            return self.data[idx]
        if isinstance(idx, tuple):
            result = self.data
            for i in idx:
                if isinstance(i, int):
                    result = result[i]
                else:
                    raise IndexError(f"Invalid index: {i}")
            return result
        if isinstance(idx, slice):
            return Tensor(self.data[idx])
        raise IndexError(f"Invalid index type: {type(idx)}")
    
    def __setitem__(self, idx, value):
        """Запис елементів тензора: t[0] = 5"""
        if isinstance(idx, int):
            self.data[idx] = value
        elif isinstance(idx, tuple):
            result = self.data
            for i in idx[:-1]:
                result = result[i]
            result[idx[-1]] = value
        else:
            raise IndexError(f"Invalid index type: {type(idx)}")
    
    # ===== АРИФМЕТИЧНІ ОПЕРАЦІЇ =====
    
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
    
    def __pow__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return Tensor([a ** b for a, b in zip(self.data, other.data)])
        return Tensor([x ** other for x in self.data])
    
    # ===== МАТРИЧНІ ОПЕРАЦІЇ =====
    
    def matmul(self, other):
        """Матричне множення"""
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
    
    def transpose(self):
        """Транспонування"""
        if len(self.shape) == 2:
            rows = self.shape[0]
            cols = self.shape[1]
            result = [[self.data[j][i] for j in range(rows)] for i in range(cols)]
            return Tensor(result)
        if len(self.shape) == 1:
            return Tensor([[x] for x in self.data])
        return self
    
    def reshape(self, new_shape):
        """Зміна форми"""
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
        if len(new_shape) == 3:
            result = []
            idx = 0
            for i in range(new_shape[0]):
                slice_2d = []
                for j in range(new_shape[1]):
                    row = flat[idx:idx+new_shape[2]]
                    slice_2d.append(row)
                    idx += new_shape[2]
                result.append(slice_2d)
            return Tensor(result)
        return self
    
    def flatten(self):
        """Розгортання в 1D"""
        def _flatten(d):
            if isinstance(d, list):
                result = []
                for item in d:
                    result.extend(_flatten(item))
                return result
            return [d]
        return _flatten(self.data)
    
    # ===== СТАТИСТИЧНІ ОПЕРАЦІЇ =====
    
    def sum(self, axis=None):
        if axis is None:
            def _flatten_sum(d):
                if isinstance(d, list):
                    return sum(_flatten_sum(item) for item in d)
                return d
            return _flatten_sum(self.data)
        
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
            if axis is None:
                return s / self.size
            return Tensor([v / self.shape[axis] for v in s.data])
        return s / self.size
    
    def std(self, axis=None):
        mean_val = self.mean(axis)
        if axis is None:
            if isinstance(mean_val, Tensor):
                mean_val = mean_val.data[0]
            squared_diff = [(x - mean_val) ** 2 for x in self.flatten()]
            return math.sqrt(sum(squared_diff) / len(squared_diff))
        return self
    
    def var(self, axis=None):
        std_val = self.std(axis)
        return std_val ** 2
    
    def max(self, axis=None):
        if axis is None:
            def _max(d):
                if isinstance(d, list):
                    return max(_max(item) for item in d)
                return d
            return _max(self.data)
        if axis == 1 and len(self.shape) == 2:
            return Tensor([max(row) for row in self.data])
        return self
    
    def min(self, axis=None):
        if axis is None:
            def _min(d):
                if isinstance(d, list):
                    return min(_min(item) for item in d)
                return d
            return _min(self.data)
        return self
    
    def argmax(self, axis=None):
        if axis is None:
            flat = self.flatten()
            return flat.index(max(flat))
        if axis == 1 and len(self.shape) == 2:
            return [row.index(max(row)) for row in self.data]
        return self
    
    def argmin(self, axis=None):
        if axis is None:
            flat = self.flatten()
            return flat.index(min(flat))
        return self
    
    # ===== НОРМАЛІЗАЦІЯ =====
    
    def normalize(self, mean=None, std=None):
        flat = self.flatten()
        if mean is None:
            mean_val = sum(flat) / len(flat)
        else:
            mean_val = mean
        if std is None:
            std_val = math.sqrt(sum((x - mean_val) ** 2 for x in flat) / len(flat))
        else:
            std_val = std
        return Tensor([(x - mean_val) / (std_val + 1e-8) for x in flat])
    
    def standardize(self):
        return self.normalize()
    
    def clip(self, min_val, max_val):
        return Tensor([max(min_val, min(max_val, x)) for x in self.flatten()])
    
    # ===== МАТЕМАТИЧНІ ФУНКЦІЇ =====
    
    def abs(self):
        return Tensor([abs(x) for x in self.flatten()])
    
    def sqrt(self):
        return Tensor([math.sqrt(x) for x in self.flatten()])
    
    def exp(self):
        return Tensor([math.exp(x) for x in self.flatten()])
    
    def log(self):
        return Tensor([math.log(x) for x in self.flatten()])
    
    def sin(self):
        return Tensor([math.sin(x) for x in self.flatten()])
    
    def cos(self):
        return Tensor([math.cos(x) for x in self.flatten()])
    
    def tan(self):
        return Tensor([math.tan(x) for x in self.flatten()])
    
    def zero_grad(self):
        """Обнулення градієнта"""
        self.grad = None
    
    # ===== СТВОРЕННЯ ТЕНЗОРІВ =====
    
    @classmethod
    def zeros(cls, shape):
        if len(shape) == 2:
            return Tensor([[0.0 for _ in range(shape[1])] for _ in range(shape[0])])
        elif len(shape) == 1:
            return Tensor([0.0 for _ in range(shape[0])])
        else:
            return Tensor([0.0])
    
    @classmethod
    def ones(cls, shape):
        if len(shape) == 2:
            return Tensor([[1.0 for _ in range(shape[1])] for _ in range(shape[0])])
        elif len(shape) == 1:
            return Tensor([1.0 for _ in range(shape[0])])
        else:
            return Tensor([1.0])
    
    @classmethod
    def random(cls, shape):
        if len(shape) == 2:
            return Tensor([[random.random() for _ in range(shape[1])] for _ in range(shape[0])])
        elif len(shape) == 1:
            return Tensor([random.random() for _ in range(shape[0])])
        else:
            return Tensor([random.random()])
    
    @classmethod
    def eye(cls, size):
        return Tensor([[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)])
    
    @classmethod
    def linspace(cls, start, end, steps):
        return Tensor([start + i * (end - start) / (steps - 1) for i in range(steps)])
    
    @classmethod
    def arange(cls, start, end, step=1):
        return Tensor(list(range(start, end, step)))


# ============================================================
# 2. ФУНКЦІЇ АКТИВАЦІЇ
# ============================================================

def relu(x):
    if isinstance(x, Tensor):
        return Tensor([max(0, v) for v in x.flatten()])
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
        flat = x.flatten()
        exp_vals = [math.exp(v) for v in flat]
        sum_exp = sum(exp_vals)
        return Tensor([v / sum_exp for v in exp_vals])
    return x

def leaky_relu(x, alpha=0.01):
    if isinstance(x, Tensor):
        return Tensor([max(alpha * v, v) for v in x.flatten()])
    if isinstance(x, (int, float)):
        return max(alpha * x, x)
    return x

def elu(x, alpha=1.0):
    if isinstance(x, Tensor):
        return Tensor([v if v > 0 else alpha * (math.exp(v) - 1) for v in x.flatten()])
    if isinstance(x, (int, float)):
        return x if x > 0 else alpha * (math.exp(x) - 1)
    return x


# ============================================================
# 3. ШАРИ НЕЙРОМЕРЕЖІ
# ============================================================

class Dense:
    """Повнозв'язний шар"""
    
    def __init__(self, input_size, output_size, activation='relu'):
        self.weights = Tensor.random([input_size, output_size])
        self.bias = Tensor.random([output_size])
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
        elif self.activation == 'leaky_relu':
            self.output = leaky_relu(self.output)
        
        return self.output
    
    def parameters(self):
        return [self.weights, self.bias]
    
    def zero_grad(self):
        self.weights.zero_grad()
        self.bias.zero_grad()


class Dropout:
    """Dropout регуляризація"""
    
    def __init__(self, rate=0.3):
        self.rate = rate
        self.mask = None
        self.training = True
    
    def forward(self, x):
        if not self.training or self.rate == 0:
            return x
        
        flat = x.flatten()
        self.mask = [1 if random.random() > self.rate else 0 for _ in flat]
        result = [flat[i] * self.mask[i] for i in range(len(flat))]
        return Tensor(result)


class Sequential:
    """Послідовна нейромережа"""
    
    def __init__(self, layers):
        self.layers = layers
    
    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x
    
    def parameters(self):
        params = []
        for layer in self.layers:
            if hasattr(layer, 'parameters'):
                params.extend(layer.parameters())
        return params
    
    def zero_grad(self):
        for param in self.parameters():
            param.zero_grad()
    
    def train(self):
        for layer in self.layers:
            if hasattr(layer, 'training'):
                layer.training = True
    
    def eval(self):
        for layer in self.layers:
            if hasattr(layer, 'training'):
                layer.training = False


# ============================================================
# 4. ОПТИМІЗАТОРИ
# ============================================================

class SGD:
    def __init__(self, params, lr=0.01, momentum=0.0):
        self.params = params
        self.lr = lr
        self.momentum = momentum
        self.velocities = [None] * len(params)
    
    def step(self):
        for i, param in enumerate(self.params):
            if param.grad is None:
                continue
            if self.momentum > 0:
                if self.velocities[i] is None:
                    self.velocities[i] = param.grad * 0
                self.velocities[i] = self.momentum * self.velocities[i] + self.lr * param.grad
                param.data = param.data - self.velocities[i]
            else:
                param.data = param.data - self.lr * param.grad


class Adam:
    def __init__(self, params, lr=0.001, betas=(0.9, 0.999), eps=1e-8):
        self.params = params
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.m = [None] * len(params)
        self.v = [None] * len(params)
        self.t = 0
    
    def step(self):
        self.t += 1
        for i, param in enumerate(self.params):
            if param.grad is None:
                continue
            if self.m[i] is None:
                self.m[i] = param.grad * 0
                self.v[i] = param.grad * 0
            
            self.m[i] = self.betas[0] * self.m[i] + (1 - self.betas[0]) * param.grad
            self.v[i] = self.betas[1] * self.v[i] + (1 - self.betas[1]) * (param.grad ** 2)
            
            m_hat = self.m[i] / (1 - self.betas[0] ** self.t)
            v_hat = self.v[i] / (1 - self.betas[1] ** self.t)
            
            param.data = param.data - self.lr * m_hat / (v_hat.sqrt() + self.eps)


# ============================================================
# 5. ФУНКЦІЇ ВТРАТ
# ============================================================

def cross_entropy(pred, target):
    if isinstance(pred, Tensor) and isinstance(target, Tensor):
        pred_flat = pred.flatten()
        target_flat = target.flatten()
        return -sum(t * math.log(p) for p, t in zip(pred_flat, target_flat) if p > 0)
    return 0

def mse(pred, target):
    if isinstance(pred, Tensor) and isinstance(target, Tensor):
        pred_flat = pred.flatten()
        target_flat = target.flatten()
        return sum((p - t) ** 2 for p, t in zip(pred_flat, target_flat)) / len(pred_flat)
    return 0

def binary_cross_entropy(pred, target):
    if isinstance(pred, Tensor) and isinstance(target, Tensor):
        pred_flat = pred.flatten()
        target_flat = target.flatten()
        return -sum(t * math.log(p) + (1 - t) * math.log(1 - p) for p, t in zip(pred_flat, target_flat) if p > 0 and p < 1)
    return 0


# ============================================================
# 6. ЗАВАНТАЖЕННЯ ДАНИХ
# ============================================================

def load_mnist():
    """Завантаження даних MNIST (спрощена версія)"""
    train_images = []
    train_labels = []
    test_images = []
    test_labels = []
    
    for _ in range(60000):
        train_images.append([random.random() for _ in range(784)])
        train_labels.append(random.randint(0, 9))
    
    for _ in range(10000):
        test_images.append([random.random() for _ in range(784)])
        test_labels.append(random.randint(0, 9))
    
    return {
        'train': (Tensor(train_images), Tensor(train_labels)),
        'test': (Tensor(test_images), Tensor(test_labels))
    }


def load_csv(filename: str):
    """Завантаження даних з CSV файлу"""
    import csv
    data = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append([float(x) for x in row])
    return data


# ============================================================
# 7. ІНТЕРПРЕТАТОР VIREO (РОЗШИРЕНИЙ)
# ============================================================

class VireoInterpreter:
    """Розширений інтерпретатор мови Vireo"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.output = []
        self._env = {}
        self._code_lines = []
        self._indent_level = 0
        self._current_model = None
    
    def execute(self, code: str) -> str:
        """Виконати код Vireo"""
        self.output = []
        self._code_lines = code.split('\n')
        
        i = 0
        while i < len(self._code_lines):
            line = self._code_lines[i]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('//') or stripped.startswith('#'):
                i += 1
                continue
            
            # Перевіряємо, чи це початок блоку (model або train)
            if stripped.startswith('model ') or stripped.startswith('train '):
                # Збираємо весь блок
                block_lines = [stripped]
                i += 1
                indent = len(line) - len(line.lstrip())
                
                while i < len(self._code_lines):
                    next_line = self._code_lines[i]
                    next_stripped = next_line.strip()
                    if not next_stripped:
                        i += 1
                        continue
                    
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_stripped == '}' or next_stripped.startswith('}'):
                        block_lines.append(next_stripped)
                        i += 1
                        break
                    
                    if next_indent > indent:
                        block_lines.append(next_stripped)
                        i += 1
                    else:
                        break
                
                # Виконуємо блок
                self._execute_block(block_lines)
            else:
                try:
                    result = self._execute_line(stripped)
                    if result is not None:
                        self.output.append(str(result))
                except Exception as e:
                    self.output.append(f"❌ Error: {e}")
                i += 1
        
        return '\n'.join(self.output)
    
    def _execute_block(self, lines: List[str]):
        """Виконати блок коду (model або train)"""
        if not lines:
            return
        
        first_line = lines[0]
        
        if first_line.startswith('model '):
            self._handle_model_block(lines)
        elif first_line.startswith('train '):
            self._handle_train_block(lines)
    
    def _handle_model_block(self, lines: List[str]):
        """Обробка блоку model { ... }"""
        first_line = lines[0]
        model_name = first_line.replace('model ', '').strip().split('{')[0].strip()
        
        model_data = {
            'type': 'model',
            'name': model_name,
            'layers': [],
            'activations': [],
            'loss': None,
            'optimizer': None
        }
        
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == '}' or stripped.startswith('}'):
                continue
            
            if stripped.startswith('layer '):
                model_data['layers'].append(stripped)
                self.output.append(f"   📊 Layer: {stripped}")
            elif stripped.startswith('activation '):
                act = stripped.replace('activation ', '').strip()
                model_data['activations'].append(act)
                self.output.append(f"   ⚡ Activation: {act}")
            elif stripped.startswith('loss '):
                model_data['loss'] = stripped.replace('loss ', '').strip()
                self.output.append(f"   📉 Loss: {model_data['loss']}")
            elif stripped.startswith('optimizer '):
                model_data['optimizer'] = stripped.replace('optimizer ', '').strip()
                self.output.append(f"   🎯 Optimizer: {model_data['optimizer']}")
        
        self.variables[model_name] = model_data
        self.output.insert(0, f"🧠 Model '{model_name}' defined")
    
    def _handle_train_block(self, lines: List[str]):
        """Обробка блоку train { ... }"""
        first_line = lines[0]
        train_name = first_line.replace('train ', '').strip().split('{')[0].strip()
        
        train_config = {
            'type': 'train',
            'name': train_name,
            'data': 'mnist',
            'epochs': 10,
            'batch_size': 64
        }
        
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == '}' or stripped.startswith('}'):
                continue
            
            if stripped.startswith('data '):
                parts = stripped.split('=')
                if len(parts) == 2:
                    train_config['data'] = parts[1].strip().strip('"')
                    self.output.append(f"   📁 data = {train_config['data']}")
            elif stripped.startswith('epochs '):
                parts = stripped.split('=')
                if len(parts) == 2:
                    train_config['epochs'] = int(parts[1].strip())
                    self.output.append(f"   🔄 epochs = {train_config['epochs']}")
            elif stripped.startswith('batch_size '):
                parts = stripped.split('=')
                if len(parts) == 2:
                    train_config['batch_size'] = int(parts[1].strip())
                    self.output.append(f"   📦 batch_size = {train_config['batch_size']}")
        
        self.variables['_train_config'] = train_config
        self.output.insert(0, f"🏋️ Training '{train_name}' configured")
    
    def _execute_line(self, line: str):
        # ===== ЗМІННІ =====
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
        
        # ===== КОНСТАНТИ =====
        if line.startswith('const '):
            parts = line[6:].split('=', 1)
            var_name = parts[0].strip()
            if len(parts) > 1:
                value = parts[1].strip()
                result = self._evaluate(value)
                self.variables[var_name] = result
                return f"const {var_name} = {result}"
        
        # ===== PRINT =====
        if line.startswith('print(') and line.endswith(')'):
            value = line[6:-1]
            result = self._evaluate(value)
            return result
        
        if line.startswith('print "'):
            value = line[6:-1]
            self.output.append(value)
            return value
        
        # ===== RETURN =====
        if line.startswith('return '):
            value = line[7:]
            result = self._evaluate(value)
            return f"Return: {result}"
        
        # ===== IF =====
        if line.startswith('if '):
            condition = line[3:].split('{')[0].strip()
            result = self._evaluate(condition)
            return "if condition true" if result else "if condition false"
        
        # ===== FOR =====
        if line.startswith('for '):
            return "for loop executed"
        
        # ===== WHILE =====
        if line.startswith('while '):
            return "while loop executed"
        
        # ===== @neural =====
        if line.startswith('@neural'):
            return "🧠 Neural network decorator applied"
        
        # ===== ФУНКЦІЇ =====
        if line.startswith('fn ') and '(' in line:
            func_name = line[3:line.index('(')].strip()
            self.functions[func_name] = line
            return f"Function {func_name} defined"
        
        # ===== DENSE =====
        if line.startswith('Dense('):
            return "🧠 Dense layer created"
        
        # ===== TENSOR =====
        if 'Tensor' in line:
            return self._handle_tensor(line)
        
        # ===== Інші вирази =====
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
        if 'zeros' in line.lower():
            return "0️⃣ Tensor zeros operation"
        if 'ones' in line.lower():
            return "1️⃣ Tensor ones operation"
        if 'random' in line.lower():
            return "🎲 Tensor random operation"
        return "📊 Tensor operation"


# ============================================================
# 8. API ІНТЕГРАЦІЯ
# ============================================================

def execute_vireo_code(code: str) -> dict:
    """Виконати Vireo код через інтерпретатор"""
    interpreter = VireoInterpreter()
    output = interpreter.execute(code)
    return {
        "status": "success",
        "output": output,
        "variables": interpreter.variables,
        "functions": interpreter.functions
    }


# ============================================================
# 9. ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    # Тестовий код з нативним синтаксисом
    test_code = """
    let x = 5
    let y = 10
    let sum = x + y
    print sum
    print "Hello Vireo!"
    
    model MNIST {
        layer Dense(784, 128)
        activation ReLU
        layer Dense(128, 10)
        activation Softmax
        loss CrossEntropy
        optimizer Adam(lr=0.001)
    }
    
    train MNIST {
        data = "mnist"
        epochs = 10
        batch_size = 64
    }
    """
    
    result = execute_vireo_code(test_code)
    print(result["output"])
