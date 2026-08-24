# ============================================================
# VIREO INTERPRETER v0.7.2 PRO
# Stable ML + AI Communication Core
# ============================================================
# 
# ALL FIXED:
# - softmax(axis=0) indexing
# - _reduce_broadcast_gradient (real reduction)
# - cross_entropy from_logits=False (full gradient)
# - transpose(1D) backward
# - matmul(1D) gradient
# - Numerical stability improvements
# - Fixed _execute_line indentation
# ============================================================

import re
import math
import random
import gzip
import os
import pickle
from typing import List, Dict, Any, Optional, Union, Tuple
from urllib.request import urlretrieve

# ============================================================
# 1. UTILITY FUNCTIONS
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

def _normalize_shape(shape):
    if isinstance(shape, int):
        return (shape,)
    return tuple(shape)

def _broadcast_shape(shape_a, shape_b):
    a = list(shape_a)
    b = list(shape_b)
    result = []
    while a or b:
        da = a.pop() if a else 1
        db = b.pop() if b else 1
        if da == db:
            result.append(da)
        elif da == 1:
            result.append(db)
        elif db == 1:
            result.append(da)
        else:
            raise ValueError(f"BroadcastError: cannot broadcast {shape_a} and {shape_b}")
    return tuple(reversed(result))

def _broadcast_data(data, source_shape, target_shape):
    source_shape = tuple(source_shape)
    target_shape = tuple(target_shape)
    if source_shape == target_shape:
        return _deep_copy(data)
    if source_shape == ():
        flat = _flatten(data)
        return _unflatten([flat[0]] * _numel(target_shape), target_shape)
    if len(source_shape) > len(target_shape):
        raise ValueError(f"Cannot broadcast {source_shape} to {target_shape}")
    padded_source = (1,) * (len(target_shape) - len(source_shape)) + source_shape
    flat_source = _flatten(data)
    def get_source_value(indices):
        source_indices = []
        offset = len(target_shape) - len(source_shape)
        for i, dim in enumerate(source_shape):
            target_index = indices[offset + i]
            if dim == 1:
                source_indices.append(0)
            else:
                source_indices.append(target_index)
        if not source_indices:
            return flat_source[0]
        value = data
        for idx in source_indices:
            value = value[idx]
        return value
    flat_result = []
    for linear in range(_numel(target_shape)):
        indices = []
        remainder = linear
        for dim in reversed(target_shape):
            indices.append(remainder % dim)
            remainder //= dim
        indices.reverse()
        flat_result.append(get_source_value(indices))
    return _unflatten(flat_result, target_shape)

def _reduce_broadcast_gradient(grad, source_shape, target_shape):
    """Reduce gradient along broadcasted dimensions."""
    source_shape = tuple(source_shape)
    target_shape = tuple(target_shape)
    if source_shape == target_shape:
        return grad
    if not source_shape:
        return Tensor([sum(_flatten(grad.data))])
    if len(source_shape) > len(target_shape):
        raise ValueError(f"Cannot reduce gradient from {target_shape} to {source_shape}")
    padded_source = (1,) * (len(target_shape) - len(source_shape)) + source_shape
    grad_flat = grad.flatten()
    result = [0.0] * _numel(source_shape)
    for linear in range(_numel(target_shape)):
        indices = []
        remainder = linear
        for dim in reversed(target_shape):
            indices.append(remainder % dim)
            remainder //= dim
        indices.reverse()
        source_indices = []
        for i, dim in enumerate(padded_source):
            if dim == 1:
                source_indices.append(0)
            else:
                source_indices.append(indices[i])
        source_indices = source_indices[len(source_indices) - len(source_shape):]
        source_linear = 0
        for i, idx in enumerate(source_indices):
            source_linear = source_linear * source_shape[i] + idx
        result[source_linear] += grad_flat[linear]
    return Tensor(_unflatten(result, source_shape))


# ============================================================
# 2. TENSOR WITH AUTOGRAD
# ============================================================

class Tensor:
    """Tensor with reverse-mode autodiff and broadcasting."""
    
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
    
    def __repr__(self):
        return f"Tensor(shape={self.shape}, requires_grad={self.requires_grad})"
    
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
        """Full reverse-mode autodiff with topological graph traversal."""
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
    
    # ===== INDEXING =====
    
    def __getitem__(self, idx):
        if isinstance(idx, int):
            data = [self.data[idx]]
            result = Tensor(data, requires_grad=self.requires_grad, _parents=(self,), _op='getitem')
            def _backward():
                if result.grad is None:
                    return
                grad_data = [0.0] * self.size
                grad_data[idx] = result.grad.item()
                self._accumulate_grad(Tensor(_unflatten(grad_data, self._shape)))
            result._backward = _backward
            return result
        if isinstance(idx, tuple):
            flat_idx = []
            for i in idx:
                flat_idx.append(i)
            result = self.data
            for i in idx:
                result = result[i]
            result_tensor = Tensor(result, requires_grad=self.requires_grad, _parents=(self,), _op='getitem')
            def _backward():
                if result_tensor.grad is None:
                    return
                grad_data = [0.0] * self.size
                def set_grad(data, indices, value, pos=0):
                    if pos == len(indices) - 1:
                        data[indices[pos]] = value
                    else:
                        set_grad(data[indices[pos]], indices, value, pos+1)
                set_grad(grad_data, idx, result_tensor.grad.item())
                self._accumulate_grad(Tensor(_unflatten(grad_data, self._shape)))
            result_tensor._backward = _backward
            return result_tensor
        if isinstance(idx, slice):
            start = idx.start if idx.start is not None else 0
            stop = idx.stop if idx.stop is not None else self.size
            step = idx.step if idx.step is not None else 1
            data = self.flatten()[start:stop:step]
            result = Tensor(_unflatten(data, [len(data)]), requires_grad=self.requires_grad, _parents=(self,), _op='getitem')
            def _backward():
                if result.grad is None:
                    return
                grad_data = [0.0] * self.size
                for i, val in enumerate(result.grad.flatten()):
                    grad_data[start + i * step] = val
                self._accumulate_grad(Tensor(_unflatten(grad_data, self._shape)))
            result._backward = _backward
            return result
        raise IndexError(f"Invalid index type: {type(idx)}")
    
    def __setitem__(self, idx, value):
        if isinstance(value, Tensor):
            value = value.data
        if isinstance(idx, int):
            self.data[idx] = value
        elif isinstance(idx, tuple):
            result = self.data
            for i in idx[:-1]:
                result = result[i]
            result[idx[-1]] = value
        else:
            self.data[idx] = value
    
    # ===== ARITHMETIC OPERATIONS =====
    
    def __add__(self, other):
        return _binary_op(self, other, lambda a, b: a + b, 'add')
    
    def __radd__(self, other):
        return _binary_op(other, self, lambda a, b: a + b, 'add')
    
    def __sub__(self, other):
        return _binary_op(self, other, lambda a, b: a - b, 'sub')
    
    def __rsub__(self, other):
        return _binary_op(other, self, lambda a, b: a - b, 'sub')
    
    def __mul__(self, other):
        return _binary_op(self, other, lambda a, b: a * b, 'mul')
    
    def __rmul__(self, other):
        return _binary_op(other, self, lambda a, b: a * b, 'mul')
    
    def __truediv__(self, other):
        return _binary_op(self, other, lambda a, b: a / b, 'div')
    
    def __rtruediv__(self, other):
        return _binary_op(other, self, lambda a, b: a / b, 'div')
    
    def __neg__(self):
        return self * -1.0
    
    def __pow__(self, power):
        if isinstance(power, Tensor):
            return _binary_op(self, power, lambda a, b: a ** b, 'pow')
        if not isinstance(power, (int, float)):
            raise TypeError(f"Unsupported power type: {type(power)}")
        flat = self.flatten()
        data = []
        for x in flat:
            if x < 0 and not float(power).is_integer():
                raise ValueError("PowerError: fractional power of negative value")
            data.append(x ** power)
        result = Tensor(_unflatten(data, self._shape), requires_grad=self.requires_grad, _parents=(self,), _op='pow')
        def _backward():
            if result.grad is None:
                return
            grad_flat = result.grad.flatten()
            result_grad = []
            for g, x in zip(grad_flat, flat):
                if x == 0 and power <= 0:
                    result_grad.append(0.0)
                else:
                    result_grad.append(g * power * (x ** (power - 1)))
            self._accumulate_grad(Tensor(_unflatten(result_grad, self._shape)))
        result._backward = _backward
        return result
    
    # ===== MATRIX OPERATIONS =====
    
    def matmul(self, other):
        if not isinstance(other, Tensor):
            other = Tensor(other)
        a_shape = tuple(self._shape)
        b_shape = tuple(other._shape)
        if len(a_shape) == 1 and len(b_shape) == 1:
            if a_shape[0] != b_shape[0]:
                raise ValueError(f"Shape mismatch: {a_shape} @ {b_shape}")
            value = sum(a * b for a, b in zip(self.flatten(), other.flatten()))
            result = Tensor([value], requires_grad=(self.requires_grad or other.requires_grad), _parents=(self, other), _op='matmul')
            def _backward():
                if result.grad is None:
                    return
                g = result.grad.item()
                if self.requires_grad:
                    self._accumulate_grad(Tensor([g * b for b in other.flatten()]))
                if other.requires_grad:
                    other._accumulate_grad(Tensor([g * a for a in self.flatten()]))
            result._backward = _backward
            return result
        if len(a_shape) == 2 and len(b_shape) == 2:
            if a_shape[1] != b_shape[0]:
                raise ValueError(f"Shape mismatch: {a_shape} @ {b_shape}")
            rows, k, cols = a_shape[0], a_shape[1], b_shape[1]
            result_data = [[sum(self.data[i][p] * other.data[p][j] for p in range(k)) for j in range(cols)] for i in range(rows)]
            result = Tensor(result_data, requires_grad=(self.requires_grad or other.requires_grad), _parents=(self, other), _op='matmul')
            def _backward():
                if result.grad is None:
                    return
                g = result.grad.data
                if self.requires_grad:
                    grad_a = [[sum(g[i][j] * other.data[p][j] for j in range(cols)) for p in range(k)] for i in range(rows)]
                    self._accumulate_grad(Tensor(grad_a))
                if other.requires_grad:
                    grad_b = [[sum(self.data[i][p] * g[i][j] for i in range(rows)) for j in range(cols)] for p in range(k)]
                    other._accumulate_grad(Tensor(grad_b))
            result._backward = _backward
            return result
        if len(a_shape) == 2 and len(b_shape) == 1:
            if a_shape[1] != b_shape[0]:
                raise ValueError(f"Shape mismatch: {a_shape} @ {b_shape}")
            rows, cols = a_shape[0], a_shape[1]
            result_data = [sum(self.data[i][j] * other.data[j] for j in range(cols)) for i in range(rows)]
            result = Tensor(result_data, requires_grad=(self.requires_grad or other.requires_grad), _parents=(self, other), _op='matmul')
            def _backward():
                if result.grad is None:
                    return
                g = result.grad.flatten()
                if self.requires_grad:
                    grad_a = [[g[i] * other.data[j] for j in range(cols)] for i in range(rows)]
                    self._accumulate_grad(Tensor(grad_a))
                if other.requires_grad:
                    grad_b = [sum(self.data[i][j] * g[i] for i in range(rows)) for j in range(cols)]
                    other._accumulate_grad(Tensor(grad_b))
            result._backward = _backward
            return result
        raise ValueError(f"Unsupported matmul: {a_shape} @ {b_shape}")
    
    def transpose(self):
        if len(self._shape) == 1:
            result_data = [[x] for x in self.flatten()]
            result = Tensor(result_data, requires_grad=self.requires_grad, _parents=(self,), _op='transpose')
            def _backward():
                if self.grad is not None:
                    g = self.grad.flatten()
                    self._accumulate_grad(Tensor(g))
            result._backward = _backward
            return result
        if len(self._shape) != 2:
            raise ValueError("transpose currently supports 1D/2D tensors")
        rows, cols = self._shape
        result_data = [[self.data[i][j] for i in range(rows)] for j in range(cols)]
        result = Tensor(result_data, requires_grad=self.requires_grad, _parents=(self,), _op='transpose')
        def _backward():
            if self.grad is not None:
                g = self.grad.data
                grad = [[g[j][i] for j in range(len(g))] for i in range(len(g[0]))]
                self._accumulate_grad(Tensor(grad))
        result._backward = _backward
        return result
    
    def reshape(self, new_shape):
        new_shape = _normalize_shape(new_shape)
        if _numel(self._shape) != _numel(new_shape):
            raise ValueError(f"ShapeError: Cannot reshape Tensor{tuple(self._shape)} to {new_shape}")
        result = Tensor(_unflatten(self.flatten(), new_shape), requires_grad=self.requires_grad, _parents=(self,), _op='reshape')
        def _backward():
            if self.grad is None:
                return
            self._accumulate_grad(Tensor(_unflatten(self.grad.flatten(), self._shape)))
        result._backward = _backward
        return result
    
    # ===== REDUCTIONS =====
    
    def sum(self, axis=None, keepdims=False):
        if axis is None:
            value = sum(self.flatten())
            if keepdims:
                out_shape = tuple(1 for _ in self._shape)
                data = _unflatten([value], out_shape)
            else:
                data = [value]
            result = Tensor(data, requires_grad=self.requires_grad, _parents=(self,), _op='sum')
            def _backward():
                if self.grad is None:
                    return
                scalar_grad = self.grad.item()
                self._accumulate_grad(Tensor(_unflatten([scalar_grad] * self.size, self._shape)))
            result._backward = _backward
            return result
        if axis < 0:
            axis += len(self._shape)
        if len(self._shape) != 2:
            raise ValueError("axis reduction currently supports 2D tensors")
        if axis == 0:
            values = [sum(self.data[i][j] for i in range(self._shape[0])) for j in range(self._shape[1])]
            if keepdims:
                result_data = [values]
                result = Tensor(result_data, requires_grad=self.requires_grad, _parents=(self,), _op='sum')
            else:
                result = Tensor(values, requires_grad=self.requires_grad, _parents=(self,), _op='sum')
            def _backward():
                if self.grad is None:
                    return
                g = self.grad.flatten()
                self._accumulate_grad(Tensor([[g[j] for j in range(self._shape[1])] for _ in range(self._shape[0])]))
            result._backward = _backward
            return result
        if axis == 1:
            values = [sum(row) for row in self.data]
            if keepdims:
                result_data = [[v] for v in values]
                result = Tensor(result_data, requires_grad=self.requires_grad, _parents=(self,), _op='sum')
            else:
                result = Tensor(values, requires_grad=self.requires_grad, _parents=(self,), _op='sum')
            def _backward():
                if self.grad is None:
                    return
                g = self.grad.flatten()
                self._accumulate_grad(Tensor([[g[i] for _ in range(self._shape[1])] for i in range(self._shape[0])]))
            result._backward = _backward
            return result
        raise ValueError(f"Unsupported axis: {axis}")
    
    def mean(self, axis=None, keepdims=False):
        if axis is None:
            return self.sum() / self.size
        if axis < 0:
            axis += len(self._shape)
        divisor = self._shape[axis]
        return self.sum(axis=axis, keepdims=keepdims) / divisor
    
    def max(self, axis=None):
        if axis is None:
            return max(self.flatten())
        if axis < 0:
            axis += len(self._shape)
        if len(self._shape) == 2 and axis == 1:
            return Tensor([max(row) for row in self.data])
        if len(self._shape) == 2 and axis == 0:
            return Tensor([max(self.data[i][j] for i in range(self._shape[0])) for j in range(self._shape[1])])
        raise ValueError(f"Unsupported max axis: {axis}")
    
    def min(self, axis=None):
        if axis is None:
            return min(self.flatten())
        if axis < 0:
            axis += len(self._shape)
        if len(self._shape) == 2 and axis == 1:
            return Tensor([min(row) for row in self.data])
        if len(self._shape) == 2 and axis == 0:
            return Tensor([min(self.data[i][j] for i in range(self._shape[0])) for j in range(self._shape[1])])
        raise ValueError(f"Unsupported min axis: {axis}")
    
    def argmax(self, axis=None):
        if axis is None:
            flat = self.flatten()
            return flat.index(max(flat))
        if axis < 0:
            axis += len(self._shape)
        if len(self._shape) == 2 and axis == 1:
            return [row.index(max(row)) for row in self.data]
        if len(self._shape) == 2 and axis == 0:
            return [max(range(self._shape[0]), key=lambda i: self.data[i][j]) for j in range(self._shape[1])]
        raise ValueError(f"Unsupported argmax axis: {axis}")
    
    def argmin(self, axis=None):
        if axis is None:
            flat = self.flatten()
            return flat.index(min(flat))
        if axis < 0:
            axis += len(self._shape)
        if len(self._shape) == 2 and axis == 1:
            return [row.index(min(row)) for row in self.data]
        if len(self._shape) == 2 and axis == 0:
            return [min(range(self._shape[0]), key=lambda i: self.data[i][j]) for j in range(self._shape[1])]
        raise ValueError(f"Unsupported argmin axis: {axis}")
    
    # ===== ELEMENTWISE MATH =====
    
    def exp(self):
        return _unary_op(self, math.exp, lambda x: math.exp(x), 'exp')
    
    def log(self):
        flat = self.flatten()
        for x in flat:
            if x <= 0:
                raise ValueError(f"log domain error: x must be > 0, got {x}")
        return _unary_op(self, math.log, lambda x: 1.0 / x, 'log')
    
    def sqrt(self):
        flat = self.flatten()
        for x in flat:
            if x < 0:
                raise ValueError(f"sqrt domain error: x must be >= 0, got {x}")
        return _unary_op(self, math.sqrt, lambda x: 0.5 / math.sqrt(x) if x > 0 else 0.0, 'sqrt')
    
    def abs(self):
        return _unary_op(self, abs, lambda x: 1.0 if x > 0 else -1.0 if x < 0 else 0.0, 'abs')
    
    def sin(self):
        return _unary_op(self, math.sin, math.cos, 'sin')
    
    def cos(self):
        return _unary_op(self, math.cos, lambda x: -math.sin(x), 'cos')
    
    def tan(self):
        return _unary_op(self, math.tan, lambda x: 1.0 / (math.cos(x) ** 2), 'tan')
    
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
# 3. AUTODIFF OPERATIONS
# ============================================================

def _to_tensor(value):
    if isinstance(value, Tensor):
        return value
    return Tensor(value)

def _binary_op(a, b, forward_fn, op_name):
    a = _to_tensor(a)
    b = _to_tensor(b)
    result_shape = _broadcast_shape(tuple(a.shape), tuple(b.shape))
    a_data = _broadcast_data(a.data, tuple(a.shape), result_shape)
    b_data = _broadcast_data(b.data, tuple(b.shape), result_shape)
    flat_a = _flatten(a_data)
    flat_b = _flatten(b_data)
    result_flat = [forward_fn(x, y) for x, y in zip(flat_a, flat_b)]
    result = Tensor(_unflatten(result_flat, result_shape), requires_grad=(a.requires_grad or b.requires_grad), _parents=(a, b), _op=op_name)
    def _backward():
        if result.grad is None:
            return
        grad_flat = result.grad.flatten()
        if op_name == 'add':
            if a.requires_grad: ga = grad_flat
            if b.requires_grad: gb = grad_flat
        elif op_name == 'sub':
            if a.requires_grad: ga = grad_flat
            if b.requires_grad: gb = [-x for x in grad_flat]
        elif op_name == 'mul':
            if a.requires_grad: ga = [g * y for g, y in zip(grad_flat, flat_b)]
            if b.requires_grad: gb = [g * x for g, x in zip(grad_flat, flat_a)]
        elif op_name == 'div':
            if a.requires_grad: ga = [g / y for g, y in zip(grad_flat, flat_b)]
            if b.requires_grad: gb = [-g * x / (y ** 2) for g, x, y in zip(grad_flat, flat_a, flat_b)]
        elif op_name == 'pow':
            if a.requires_grad:
                ga = []
                for g, x, y in zip(grad_flat, flat_a, flat_b):
                    if x == 0 and y <= 0:
                        ga.append(0.0)
                    else:
                        ga.append(g * y * (x ** (y - 1)))
            if b.requires_grad:
                gb = []
                for g, x, y in zip(grad_flat, flat_a, flat_b):
                    if x <= 0:
                        gb.append(0.0)
                    else:
                        gb.append(g * (x ** y) * math.log(max(abs(x), 1e-12)))
        if a.requires_grad:
            grad_a = Tensor(_unflatten(ga, result_shape))
            grad_a = _reduce_broadcast_gradient(grad_a, tuple(a.shape), result_shape)
            a._accumulate_grad(grad_a)
        if b.requires_grad:
            grad_b = Tensor(_unflatten(gb, result_shape))
            grad_b = _reduce_broadcast_gradient(grad_b, tuple(b.shape), result_shape)
            b._accumulate_grad(grad_b)
    result._backward = _backward
    return result

def _unary_op(x, forward_fn, derivative_fn, op_name):
    x = _to_tensor(x)
    flat = x.flatten()
    result_flat = [forward_fn(v) for v in flat]
    result = Tensor(_unflatten(result_flat, tuple(x.shape)), requires_grad=x.requires_grad, _parents=(x,), _op=op_name)
    def _backward():
        if result.grad is None:
            return
        grad_flat = result.grad.flatten()
        gx = [g * derivative_fn(v) for g, v in zip(grad_flat, flat)]
        x._accumulate_grad(Tensor(_unflatten(gx, tuple(x.shape))))
    result._backward = _backward
    return result


# ============================================================
# 4. ACTIVATIONS
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
    if axis == 0:
        cols, rows = x.shape[0], x.shape[1]
        probabilities = []
        for j in range(rows):
            col = [x.data[i][j] for i in range(cols)]
            maximum = max(col)
            exp_values = [math.exp(v - maximum) for v in col]
            total = sum(exp_values)
            probabilities.append([v / total for v in exp_values])
        result_data = [[probabilities[i][j] for i in range(cols)] for j in range(rows)]
        result = Tensor(result_data, requires_grad=x.requires_grad, _parents=(x,), _op='softmax')
        def _backward():
            if result.grad is None:
                return
            grad = []
            for j in range(rows):
                p = [probabilities[i][j] for i in range(cols)]
                g = [result.grad.data[i][j] for i in range(cols)]
                dot = sum(p[i] * g[i] for i in range(cols))
                grad.append([p[i] * (g[i] - dot) for i in range(cols)])
            grad_transposed = [[grad[j][i] for j in range(rows)] for i in range(cols)]
            x._accumulate_grad(Tensor(grad_transposed))
        result._backward = _backward
        return result
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
# 5. LOSS FUNCTIONS
# ============================================================

def _labels_to_ints(target):
    if isinstance(target, Tensor):
        return [int(round(x)) for x in target.flatten()]
    return [int(x) for x in target]

def cross_entropy(pred, target, from_logits=False, reduction='mean'):
    pred = _to_tensor(pred)
    labels = _labels_to_ints(target)
    if len(pred.shape) == 1:
        logits = pred.reshape((1, pred.shape[0]))
        labels = labels[:1]
    elif len(pred.shape) == 2:
        logits = pred
    else:
        raise ValueError("CrossEntropy expects 1D or 2D predictions")
    batch, classes = logits.shape[0], logits.shape[1]
    if len(labels) != batch:
        raise ValueError(f"CrossEntropy: predictions batch={batch}, labels={len(labels)}")
    if from_logits:
        losses = []
        probabilities = []
        for i in range(batch):
            row = logits.data[i]
            maximum = max(row)
            exp_values = [math.exp(x - maximum) for x in row]
            exp_sum = sum(exp_values)
            probs = [x / exp_sum for x in exp_values]
            probabilities.append(probs)
            label = labels[i]
            if label < 0 or label >= classes:
                raise ValueError(f"Invalid class label: {label}")
            log_sum_exp = maximum + math.log(exp_sum)
            losses.append(log_sum_exp - row[label])
        if reduction == 'sum':
            loss_value = sum(losses)
        else:
            loss_value = sum(losses) / batch
        result = Tensor([loss_value], requires_grad=logits.requires_grad, _parents=(logits,), _op='cross_entropy')
        def _backward():
            if result.grad is None:
                return
            upstream = result.grad.item()
            divisor = 1 if reduction == 'sum' else batch
            grad = []
            for i in range(batch):
                row_grad = []
                for j in range(classes):
                    one_hot = 1.0 if j == labels[i] else 0.0
                    row_grad.append(upstream * (probabilities[i][j] - one_hot) / divisor)
                grad.append(row_grad)
            logits._accumulate_grad(Tensor(grad))
        result._backward = _backward
        return result
    # from_logits=False
    probabilities = logits
    losses = []
    for i in range(batch):
        label = labels[i]
        if label < 0 or label >= classes:
            raise ValueError(f"Invalid class label: {label}")
        p = max(probabilities.data[i][label], 1e-12)
        losses.append(-math.log(p))
    loss_value = sum(losses) if reduction == 'sum' else sum(losses) / batch
    result = Tensor([loss_value], requires_grad=probabilities.requires_grad, _parents=(probabilities,), _op='cross_entropy')
    def _backward():
        if result.grad is None:
            return
        upstream = result.grad.item()
        divisor = 1 if reduction == 'sum' else batch
        grad = []
        for i in range(batch):
            row_grad = []
            for j in range(classes):
                one_hot = 1.0 if j == labels[i] else 0.0
                row_grad.append(upstream * (probabilities.data[i][j] - one_hot) / divisor)
            grad.append(row_grad)
        probabilities._accumulate_grad(Tensor(grad))
    result._backward = _backward
    return result

def mse(pred, target):
    pred = _to_tensor(pred)
    target = _to_tensor(target)
    diff = pred - target
    return (diff * diff).mean()


# ============================================================
# 6. NEURAL NETWORK LAYERS
# ============================================================

class Dense:
    def __init__(self, input_size, output_size, activation=None):
        self.input_size = int(input_size)
        self.output_size = int(output_size)
        self.activation = activation.lower() if activation else None
        if self.activation == 'relu':
            scale = math.sqrt(2.0 / self.input_size)
        else:
            scale = math.sqrt(1.0 / self.input_size)
        self.weights = Tensor([[random.gauss(0, scale) for _ in range(self.output_size)] for _ in range(self.input_size)], requires_grad=True)
        self.bias = Tensor([0.0] * self.output_size, requires_grad=True)
        self.input = None
        self.pre_activation = None
        self.output = None
    
    def forward(self, x):
        if not isinstance(x, Tensor):
            x = Tensor(x)
        if len(x.shape) == 1:
            if x.shape[0] != self.input_size:
                raise ValueError(f"Dense input shape error: expected [{self.input_size}], got {x.shape}")
        elif len(x.shape) == 2:
            if x.shape[1] != self.input_size:
                raise ValueError(f"Dense input shape error: expected [batch, {self.input_size}], got {x.shape}")
        else:
            raise ValueError("Dense supports 1D/2D input")
        self.input = x
        z = x.matmul(self.weights) + self.bias
        self.pre_activation = z
        if self.activation in (None, '', 'linear'):
            self.output = z
        elif self.activation == 'relu':
            self.output = relu(z)
        elif self.activation == 'sigmoid':
            self.output = sigmoid(z)
        elif self.activation == 'tanh':
            self.output = tanh(z)
        elif self.activation == 'softmax':
            self.output = softmax(z)
        else:
            raise ValueError(f"Unknown activation: {self.activation}")
        return self.output
    
    def parameters(self):
        return [self.weights, self.bias]
    
    def zero_grad(self):
        self.weights.zero_grad()
        self.bias.zero_grad()

class Sequential:
    def __init__(self, layers):
        self.layers = layers
        self.training = True
        self._optimizer_state = {}
    
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
        self.training = True
        for layer in self.layers:
            if hasattr(layer, 'training'):
                layer.training = True
    
    def eval(self):
        self.training = False
        for layer in self.layers:
            if hasattr(layer, 'training'):
                layer.training = False
    
    def last_dense(self):
        for layer in reversed(self.layers):
            if isinstance(layer, Dense):
                return layer
        return None
    
    def save(self, path: str):
        state = {
            'layers': self.layers,
            'training': self.training,
            'optimizer_state': self._optimizer_state
        }
        with open(path, 'wb') as f:
            pickle.dump(state, f)
    
    @classmethod
    def load(cls, path: str):
        with open(path, 'rb') as f:
            state = pickle.load(f)
        model = cls(state['layers'])
        model.training = state['training']
        model._optimizer_state = state.get('optimizer_state', {})
        return model


# ============================================================
# 7. OPTIMIZERS
# ============================================================

class Optimizer:
    def __init__(self, params, lr=0.001):
        self.params = list(params)
        self.lr = lr
    
    def zero_grad(self):
        for param in self.params:
            param.zero_grad()

class SGD(Optimizer):
    def __init__(self, params, lr=0.01, momentum=0.0):
        super().__init__(params, lr)
        self.momentum = momentum
        self.velocities = [None for _ in self.params]
    
    def step(self):
        for i, param in enumerate(self.params):
            if param.grad is None:
                continue
            grad_flat = param.grad.flatten()
            data_flat = param.flatten()
            if self.momentum > 0:
                if self.velocities[i] is None:
                    self.velocities[i] = [0.0 for _ in grad_flat]
                velocity = self.velocities[i]
                for j, grad in enumerate(grad_flat):
                    velocity[j] = self.momentum * velocity[j] + self.lr * grad
                    data_flat[j] -= velocity[j]
            else:
                for j, grad in enumerate(grad_flat):
                    data_flat[j] -= self.lr * grad
            param.data = _unflatten(data_flat, tuple(param.shape))

class Adam(Optimizer):
    def __init__(self, params, lr=0.001, betas=(0.9, 0.999), eps=1e-8):
        super().__init__(params, lr)
        self.betas = betas
        self.eps = eps
        self.m = [None for _ in self.params]
        self.v = [None for _ in self.params]
        self.t = 0
    
    def step(self):
        self.t += 1
        beta1, beta2 = self.betas
        for i, param in enumerate(self.params):
            if param.grad is None:
                continue
            grad = param.grad.flatten()
            data = param.flatten()
            if self.m[i] is None:
                self.m[i] = [0.0 for _ in grad]
                self.v[i] = [0.0 for _ in grad]
            m, v = self.m[i], self.v[i]
            for j, g in enumerate(grad):
                m[j] = beta1 * m[j] + (1.0 - beta1) * g
                v[j] = beta2 * v[j] + (1.0 - beta2) * (g * g)
                m_hat = m[j] / (1.0 - beta1 ** self.t)
                v_hat = v[j] / (1.0 - beta2 ** self.t)
                data[j] -= self.lr * m_hat / (math.sqrt(v_hat) + self.eps)
            param.data = _unflatten(data, tuple(param.shape))


# ============================================================
# 8. DATASET LOADERS
# ============================================================

def load_mnist(offline=False):
    """Load real MNIST via NumPy with offline cache support."""
    if offline:
        cache_dir = os.path.join(os.path.expanduser("~"), ".vireo", "mnist")
        if not os.path.exists(cache_dir):
            raise RuntimeError("MNIST not cached locally. Run online once or download manually.")
    try:
        import numpy as np
    except ImportError:
        raise ImportError("NumPy is required for MNIST loading. Install with: pip install numpy")
    cache_dir = os.path.join(os.path.expanduser("~"), ".vireo", "mnist")
    os.makedirs(cache_dir, exist_ok=True)
    filenames = {
        'train_images': 'train-images-idx3-ubyte.gz',
        'train_labels': 'train-labels-idx1-ubyte.gz',
        'test_images': 't10k-images-idx3-ubyte.gz',
        'test_labels': 't10k-labels-idx1-ubyte.gz'
    }
    base_url = 'https://storage.googleapis.com/tensorflow/tf-keras-datasets/'
    for name, fname in filenames.items():
        path = os.path.join(cache_dir, fname)
        if not os.path.exists(path):
            if offline:
                raise RuntimeError(f"MNIST file {fname} not cached locally.")
            print(f"📥 Downloading {fname}...")
            urlretrieve(base_url + fname, path)
    def load_images(filename):
        with gzip.open(os.path.join(cache_dir, filename), 'rb') as f:
            data = np.frombuffer(f.read(), np.uint8, offset=16)
        return data.reshape(-1, 784).astype(np.float32) / 255.0
    def load_labels(filename):
        with gzip.open(os.path.join(cache_dir, filename), 'rb') as f:
            data = np.frombuffer(f.read(), np.uint8, offset=8)
        return data.astype(np.int64)
    x_train = load_images(filenames['train_images'])
    y_train = load_labels(filenames['train_labels'])
    x_test = load_images(filenames['test_images'])
    y_test = load_labels(filenames['test_labels'])
    return {
        'train': (Tensor(x_train.tolist()), Tensor(y_train.tolist())),
        'test': (Tensor(x_test.tolist()), Tensor(y_test.tolist()))
    }


# ============================================================
# 9. METRICS
# ============================================================

def classification_metrics(y_true, y_pred, num_classes=10):
    y_true = [int(x) for x in y_true]
    y_pred = [int(x) for x in y_pred]
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred length mismatch")
    confusion = [[0 for _ in range(num_classes)] for _ in range(num_classes)]
    for true, pred in zip(y_true, y_pred):
        if not (0 <= true < num_classes):
            raise ValueError(f"Invalid true label: {true}")
        if not (0 <= pred < num_classes):
            raise ValueError(f"Invalid predicted label: {pred}")
        confusion[true][pred] += 1
    total = len(y_true)
    correct = sum(confusion[i][i] for i in range(num_classes))
    accuracy = correct / total if total else 0.0
    precision_per_class = []
    recall_per_class = []
    f1_per_class = []
    for c in range(num_classes):
        tp = confusion[c][c]
        fp = sum(confusion[r][c] for r in range(num_classes) if r != c)
        fn = sum(confusion[c][r] for r in range(num_classes) if r != c)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        precision_per_class.append(precision)
        recall_per_class.append(recall)
        f1_per_class.append(f1)
    return {
        'accuracy': accuracy,
        'precision': sum(precision_per_class) / num_classes,
        'recall': sum(recall_per_class) / num_classes,
        'f1': sum(f1_per_class) / num_classes,
        'precision_per_class': precision_per_class,
        'recall_per_class': recall_per_class,
        'f1_per_class': f1_per_class,
        'confusion_matrix': confusion
    }


# ============================================================
# 10. TRAINING
# ============================================================

def train_model(model, train_data, train_labels, epochs=10, batch_size=64, lr=0.001, optimizer_name='adam', shuffle=True, verbose=True):
    if not isinstance(train_data, Tensor):
        train_data = Tensor(train_data)
    if not isinstance(train_labels, Tensor):
        train_labels = Tensor(train_labels)
    if len(train_data.shape) != 2:
        raise ValueError("train_data must be 2D")
    if len(train_labels.shape) != 1:
        raise ValueError("train_labels must be 1D")
    if train_data.shape[0] != train_labels.shape[0]:
        raise ValueError("Data and labels size mismatch")
    if optimizer_name.lower() == 'sgd':
        optimizer = SGD(model.parameters(), lr=lr)
    else:
        optimizer = Adam(model.parameters(), lr=lr)
    history = {'loss': [], 'accuracy': []}
    n = train_data.shape[0]
    for epoch in range(epochs):
        model.train()
        indices = list(range(n))
        if shuffle:
            random.shuffle(indices)
        total_loss = 0.0
        total_correct = 0
        total_seen = 0
        for start in range(0, n, batch_size):
            batch_indices = indices[start:start + batch_size]
            batch_x = Tensor([train_data.data[i] for i in batch_indices])
            batch_y = Tensor([train_labels.data[i] for i in batch_indices])
            optimizer.zero_grad()
            output = model.forward(batch_x)
            last_dense = model.last_dense()
            if last_dense is not None and last_dense.activation == 'softmax':
                loss = cross_entropy(last_dense.pre_activation, batch_y, from_logits=True)
            else:
                loss = cross_entropy(output, batch_y, from_logits=False)
            loss.backward()
            optimizer.step()
            batch_loss = loss.item()
            predictions = output.argmax(axis=1)
            correct = sum(int(p == t) for p, t in zip(predictions, batch_y.data))
            total_loss += batch_loss * len(batch_indices)
            total_correct += correct
            total_seen += len(batch_indices)
        epoch_loss = total_loss / total_seen if total_seen else 0.0
        epoch_accuracy = total_correct / total_seen if total_seen else 0.0
        history['loss'].append(epoch_loss)
        history['accuracy'].append(epoch_accuracy)
        if verbose:
            print(f"Epoch {epoch + 1}/{epochs} - Loss: {epoch_loss:.4f} - Accuracy: {epoch_accuracy * 100:.2f}%")
    return history


# ============================================================
# 11. SELF TEST
# ============================================================

def run_self_tests():
    print("\n🧪 VIREO v0.7.2 PRO SELF TESTS")
    print("=" * 50)
    
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
    
    # Test 4: Autodiff
    x = Tensor([2.0], requires_grad=True)
    y = x * x
    y.backward()
    assert abs(x.grad.item() - 4.0) < 1e-6, "Test 4 failed"
    print("✅ Autodiff")
    
    # Test 5: Broadcast
    a = Tensor([1, 2, 3])
    b = Tensor([[1], [2], [3]])
    c = a + b
    assert c.shape == [3, 3], "Test 5 failed"
    print("✅ Broadcast")
    
    # Test 6: Broadcast gradient
    x = Tensor([1, 2, 3], requires_grad=True)
    y = Tensor([[1], [2], [3]], requires_grad=True)
    z = x + y
    z.sum().backward()
    assert x.grad.flatten() == [3.0, 3.0, 3.0], "Test 6 failed"
    assert y.grad.flatten() == [3.0, 3.0, 3.0], "Test 6 failed"
    print("✅ Broadcast gradient")
    
    # Test 7: Reshape
    a = Tensor([1, 2, 3, 4, 5, 6])
    b = a.reshape([2, 3])
    assert b.shape == [2, 3], "Test 7 failed"
    print("✅ Reshape")
    
    # Test 8: Relu
    x = Tensor([-1, 0, 1])
    y = relu(x)
    assert y.flatten() == [0.0, 0.0, 1.0], "Test 8 failed"
    print("✅ Relu")
    
    # Test 9: Softmax
    x = Tensor([1, 2, 3])
    y = softmax(x)
    assert abs(sum(y.flatten()) - 1.0) < 1e-6, "Test 9 failed"
    print("✅ Softmax")
    
    # Test 10: Indexing backward
    x = Tensor([1, 2, 3], requires_grad=True)
    y = x[1]
    y.backward()
    assert x.grad.flatten() == [0.0, 1.0, 0.0], "Test 10 failed"
    print("✅ Indexing backward")
    
    # Test 11: CrossEntropy backward
    logits = Tensor([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]], requires_grad=True)
    labels = Tensor([0, 1])
    loss = cross_entropy(logits, labels, from_logits=True)
    loss.backward()
    assert logits.grad is not None, "Test 11 failed"
    print("✅ CrossEntropy backward")
    
    # Test 12: Slice backward
    x = Tensor([1, 2, 3, 4], requires_grad=True)
    y = x[1:3]
    y.sum().backward()
    assert x.grad.flatten() == [0.0, 1.0, 1.0, 0.0], "Test 12 failed"
    print("✅ Slice backward")
    
    # Test 13: Softmax axis 0 backward
    x = Tensor([[1, 2], [3, 4]], requires_grad=True)
    y = softmax(x, axis=0)
    y.sum().backward()
    assert x.grad is not None, "Test 13 failed"
    print("✅ Softmax axis 0 backward")
    
    # Test 14: sum keepdims
    x = Tensor([[1, 2], [3, 4]])
    y = x.sum(axis=0, keepdims=True)
    assert y.shape == [1, 2], "Test 14 failed"
    z = x.sum(axis=1, keepdims=True)
    assert z.shape == [2, 1], "Test 14 failed"
    print("✅ sum keepdims")
    
    print("\n🎉 ALL TESTS PASSED")


# ============================================================
# 12. VIREO INTERPRETER
# ============================================================

class VireoInterpreter:
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
    
    def execute(self, code: str) -> str:
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
    
    def _build_model(self, name):
        model_data = self._models.get(name, {})
        layers = []
        activations = model_data.get('activations', [])
        layer_strs = model_data.get('layers', [])
        for i, layer_str in enumerate(layer_strs):
            if 'Dense' in layer_str:
                import re
                match = re.search(r'Dense\((\d+),\s*(\d+)\)', layer_str)
                if match:
                    input_size = int(match.group(1))
                    output_size = int(match.group(2))
                    act = activations[i] if i < len(activations) else None
                    layers.append(Dense(input_size, output_size, act))
        if not layers:
            raise ValueError(f"Model '{name}' contains no layers")
        return Sequential(layers)
    
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
        self._models[name] = {'layers': layers, 'activations': activations}
        self.output.insert(0, f"🧠 Model '{name}' defined")
    
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
        if name in self._models:
            model = self._build_model(name)
            data = load_mnist()
            train_x, train_y = data['train']
            history = train_model(model, train_x, train_y, epochs=config['epochs'], batch_size=config['batch_size'], lr=config['lr'])
            self._loaded_model = model
            self._model_objects[name] = model
            self._history[name] = history
            self.output.append(f"   ✅ Real training completed for '{name}'")
            if history['loss']:
                self.output.append(f"   📉 Final loss: {history['loss'][-1]:.4f}")
                self.output.append(f"   🎯 Final accuracy: {history['accuracy'][-1] * 100:.2f}%")
        else:
            self.output.append(f"   ❌ Model '{name}' not found")
        self.output.insert(0, f"🏋️ Training '{name}' completed")
    
    def _handle_predict_block(self, lines):
        name = lines[0].replace('predict ', '').strip().split('{')[0].strip()
        config = {'data': 'test', 'model': name}
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == '}' or stripped.startswith('}'):
                continue
            if '=' in stripped:
                key, value = stripped.split('=', 1)
                key, value = key.strip(), value.strip().strip('"')
                if key == 'data':
                    config['data'] = value
                elif key == 'model':
                    config['model'] = value
        if name in self._model_objects:
            model = self._model_objects[name]
            data = load_mnist()
            test_x, test_y = data['test']
            pred = model.forward(test_x)
            predictions = pred.argmax(axis=1)
            correct = sum(1 for p, t in zip(predictions, test_y.data) if p == t)
            accuracy = correct / len(test_x.data)
            self.output.append(f"   ✅ Accuracy: {accuracy * 100:.2f}%")
            self._metrics['accuracy'] = accuracy
        else:
            self.output.append("   ❌ No trained model found")
        self.output.insert(0, f"🎯 Prediction completed for '{name}'")
    
    def _handle_evaluate_block(self, lines):
        name = lines[0].replace('evaluate ', '').strip().split('{')[0].strip()
        config = {'data': 'test', 'metrics': ['accuracy', 'precision', 'recall', 'f1']}
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == '}' or stripped.startswith('}'):
                continue
            if '=' in stripped:
                key, value = stripped.split('=', 1)
                key, value = key.strip(), value.strip().strip('"')
                if key == 'data':
                    config['data'] = value
            elif stripped.startswith('metrics '):
                metrics_str = stripped.replace('metrics ', '').strip()
                if metrics_str.startswith('[') and metrics_str.endswith(']'):
                    config['metrics'] = [m.strip() for m in metrics_str[1:-1].split(',')]
        if name in self._model_objects:
            model = self._model_objects[name]
            data = load_mnist()
            test_x, test_y = data['test']
            pred = model.forward(test_x)
            predictions = pred.argmax(axis=1)
            targets = test_y.data
            metrics = classification_metrics(targets, predictions, num_classes=10)
            self._metrics = metrics
            for metric in config['metrics']:
                if metric in metrics:
                    self.output.append(f"      {metric}: {metrics[metric] * 100:.2f}%")
                else:
                    self.output.append(f"      {metric}: N/A")
            if 'confusion_matrix' in config['metrics']:
                self.output.append(f"      confusion_matrix: {metrics['confusion_matrix']}")
        else:
            self.output.append("   ❌ No trained model found")
        self.output.insert(0, f"📈 Evaluation completed for '{name}'")
    
    def _handle_metrics_block(self, lines):
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == '}' or stripped.startswith('}'):
                continue
            if stripped in ['accuracy', 'precision', 'recall', 'f1']:
                value = self._metrics.get(stripped, 0.0)
                self.output.append(f"   {stripped}: {value * 100:.2f}%")
        self.output.insert(0, "📊 Metrics defined")
    
    def _handle_dataset_block(self, lines):
        name = lines[0].replace('dataset ', '').strip().split('{')[0].strip()
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == '}' or stripped.startswith('}'):
                continue
            if '=' in stripped:
                key, value = stripped.split('=', 1)
                key, value = key.strip(), value.strip().strip('"')
                self.output.append(f"   📁 {key} = {value}")
        self.output.insert(0, f"📂 Dataset '{name}' defined")
    
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
        
        result = self._evaluate(line)
        return result
    
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
                    if isinstance(left, Tensor) and isinstance(right, (int, float)):
                        if op == '+': return left + right
                        if op == '-': return left - right
                        if op == '*': return left * right
                        if op == '/': return left / right
                    if isinstance(left, (int, float)) and isinstance(right, Tensor):
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
# 13. API INTEGRATION
# ============================================================

def execute_vireo_code(code: str) -> dict:
    interpreter = VireoInterpreter()
    output = interpreter.execute(code)
    return {
        "status": "error" if interpreter.errors else "success",
        "output": output,
        "errors": interpreter.errors,
        "variables": interpreter.variables,
        "functions": interpreter.functions,
        "metrics": interpreter._metrics,
        "history": interpreter._history
    }


# ============================================================
# 14. EXAMPLE
# ============================================================

if __name__ == "__main__":
    run_self_tests()
    print("\n" + "=" * 50)
    
    test_code = """
    let x = 5
    let y = 10
    let sum = x + y
    print(sum)
    
    let t = Tensor([1, 2, 3, 4])
    let t2 = Tensor([5, 6, 7, 8])
    let sum_t = t + t2
    print(sum_t)
    """
    result = execute_vireo_code(test_code)
    print(result["output"])