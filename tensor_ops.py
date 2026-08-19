# ============================================================
# VIREO TENSOR OPERATIONS v1.0.0
# Розширена бібліотека тензорних операцій
# ============================================================

import math
import random
from typing import List, Union, Optional, Tuple

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
    
    @property
    def ndim(self):
        """Кількість вимірів"""
        return len(self.shape)
    
    def __repr__(self):
        return f"Tensor({self.data}, shape={self.shape}, dtype={self.dtype})"
    
    # ============================================================
    # АРИФМЕТИЧНІ ОПЕРАЦІЇ
    # ============================================================
    
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
    
    def __pow__(self, other):
        if isinstance(other, Tensor):
            if self.shape != other.shape:
                raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
            return Tensor([a ** b for a, b in zip(self.data, other.data)])
        return Tensor([x ** other for x in self.data])
    
    # ============================================================
    # МАТРИЧНІ ОПЕРАЦІЇ
    # ============================================================
    
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
    
    # ============================================================
    # СТАТИСТИЧНІ ОПЕРАЦІЇ
    # ============================================================
    
    def sum(self, axis=None):
        """Сума"""
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
        """Середнє"""
        s = self.sum(axis)
        if isinstance(s, Tensor):
            if axis is None:
                return s / self.size
            return Tensor([v / self.shape[axis] for v in s.data])
        return s / self.size
    
    def std(self, axis=None):
        """Стандартне відхилення"""
        mean_val = self.mean(axis)
        if axis is None:
            if isinstance(mean_val, Tensor):
                mean_val = mean_val.data[0]
            squared_diff = [(x - mean_val) ** 2 for x in self.flatten()]
            return math.sqrt(sum(squared_diff) / len(squared_diff))
        return self
    
    def var(self, axis=None):
        """Дисперсія"""
        std_val = self.std(axis)
        return std_val ** 2
    
    def max(self, axis=None):
        """Максимум"""
        if axis is None:
            def _max(d):
                if isinstance(d, list):
                    return max(_max(item) for item in d)
                return d
            return _max(self.data)
        
        if axis == 0 and len(self.shape) == 2:
            result = []
            for col in range(self.shape[1]):
                result.append(max(row[col] for row in self.data))
            return Tensor(result)
        if axis == 1 and len(self.shape) == 2:
            return Tensor([max(row) for row in self.data])
        return self
    
    def min(self, axis=None):
        """Мінімум"""
        if axis is None:
            def _min(d):
                if isinstance(d, list):
                    return min(_min(item) for item in d)
                return d
            return _min(self.data)
        return self
    
    def argmax(self, axis=None):
        """Індекс максимуму"""
        if axis is None:
            flat = self.flatten()
            return flat.index(max(flat))
        if axis == 1 and len(self.shape) == 2:
            return [row.index(max(row)) for row in self.data]
        return self
    
    def argmin(self, axis=None):
        """Індекс мінімуму"""
        if axis is None:
            flat = self.flatten()
            return flat.index(min(flat))
        return self
    
    # ============================================================
    # НОРМАЛІЗАЦІЯ
    # ============================================================
    
    def normalize(self, mean=None, std=None):
        """Нормалізація"""
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
        """Стандартизація (Z-score)"""
        return self.normalize()
    
    def clip(self, min_val, max_val):
        """Обмеження значень"""
        return Tensor([max(min_val, min(max_val, x)) for x in self.flatten()])
    
    # ============================================================
    # ПОБІТОВІ ОПЕРАЦІЇ
    # ============================================================
    
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
    
    # ============================================================
    # КОНВЕРСІЯ
    # ============================================================
    
    def to_list(self):
        return self.data
    
    def to_numpy(self):
        """Конвертація в NumPy (емуляція)"""
        return self.data
    
    # ============================================================
    # СТВОРЕННЯ ТЕНЗОРІВ
    # ============================================================
    
    @classmethod
    def zeros(cls, shape):
        data = [[0.0 for _ in range(shape[1])] for _ in range(shape[0])]
        return cls(data)
    
    @classmethod
    def ones(cls, shape):
        data = [[1.0 for _ in range(shape[1])] for _ in range(shape[0])]
        return cls(data)
    
    @classmethod
    def random(cls, shape):
        data = [[random.random() for _ in range(shape[1])] for _ in range(shape[0])]
        return cls(data)
    
    @classmethod
    def eye(cls, size):
        data = [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]
        return cls(data)
    
    @classmethod
    def linspace(cls, start, end, steps):
        data = [start + i * (end - start) / (steps - 1) for i in range(steps)]
        return cls(data)
    
    @classmethod
    def arange(cls, start, end, step=1):
        data = list(range(start, end, step))
        return cls(data)


# ============================================================
# ФУНКЦІЇ ДЛЯ ТЕНЗОРІВ
# ============================================================

def tensor_add(a, b):
    return a + b

def tensor_sub(a, b):
    return a - b

def tensor_mul(a, b):
    return a * b

def tensor_div(a, b):
    return a / b

def tensor_matmul(a, b):
    return a.matmul(b)

def tensor_transpose(a):
    return a.transpose()

def tensor_reshape(a, shape):
    return a.reshape(shape)

def tensor_flatten(a):
    return a.flatten()

def tensor_sum(a, axis=None):
    return a.sum(axis)

def tensor_mean(a, axis=None):
    return a.mean(axis)

def tensor_max(a, axis=None):
    return a.max(axis)

def tensor_min(a, axis=None):
    return a.min(axis)

def tensor_argmax(a, axis=None):
    return a.argmax(axis)

def tensor_argmin(a, axis=None):
    return a.argmin(axis)

def tensor_normalize(a, mean=None, std=None):
    return a.normalize(mean, std)

def tensor_standardize(a):
    return a.standardize()

def tensor_clip(a, min_val, max_val):
    return a.clip(min_val, max_val)

def tensor_abs(a):
    return a.abs()

def tensor_sqrt(a):
    return a.sqrt()

def tensor_exp(a):
    return a.exp()

def tensor_log(a):
    return a.log()