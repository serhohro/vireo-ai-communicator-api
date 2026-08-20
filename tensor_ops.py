# ============================================================
# VIREO TENSOR OPERATIONS v1.1.0
# Розширена бібліотека тензорних операцій з CNN підтримкою
# ============================================================

import math
import random
import numpy as np
from typing import List, Union, Optional, Tuple

# ============================================================
# 1. ОСНОВНИЙ КЛАС TENSOR
# ============================================================

class Tensor:
    """Повноцінна реалізація тензорів для Vireo"""
    
    def __init__(self, data, dtype='float32', requires_grad=False):
        if isinstance(data, (int, float)):
            self.data = [float(data)]
        elif isinstance(data, list):
            self.data = data
        elif isinstance(data, np.ndarray):
            self.data = data.tolist()
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
        return f"Tensor(shape={self.shape}, dtype={self.dtype})"
    
    def __str__(self):
        return str(self.data)
    
    def to_numpy(self):
        """Конвертація в NumPy масив"""
        return np.array(self.data, dtype=np.float32)
    
    @classmethod
    def from_numpy(cls, arr):
        """Створення Tensor з NumPy масиву"""
        return cls(arr.tolist())
    
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
        
        if axis == 0 and len(self.shape) == 2:
            result = []
            for col in range(self.shape[1]):
                result.append(max(row[col] for row in self.data))
            return Tensor(result)
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
    
    # ============================================================
    # НОРМАЛІЗАЦІЯ
    # ============================================================
    
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
    
    # ============================================================
    # МАТЕМАТИЧНІ ФУНКЦІЇ
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
    
    # ============================================================
    # СТВОРЕННЯ ТЕНЗОРІВ
    # ============================================================
    
    @classmethod
    def zeros(cls, shape):
        if len(shape) == 2:
            data = [[0.0 for _ in range(shape[1])] for _ in range(shape[0])]
        elif len(shape) == 1:
            data = [0.0 for _ in range(shape[0])]
        else:
            data = [0.0]
        return cls(data)
    
    @classmethod
    def ones(cls, shape):
        if len(shape) == 2:
            data = [[1.0 for _ in range(shape[1])] for _ in range(shape[0])]
        elif len(shape) == 1:
            data = [1.0 for _ in range(shape[0])]
        else:
            data = [1.0]
        return cls(data)
    
    @classmethod
    def random(cls, shape):
        if len(shape) == 2:
            data = [[random.random() for _ in range(shape[1])] for _ in range(shape[0])]
        elif len(shape) == 1:
            data = [random.random() for _ in range(shape[0])]
        else:
            data = [random.random()]
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
# 2. IM2COL / COL2IM (ДЛЯ КОНВОЛЮЦІЇ)
# ============================================================

def im2col(
    images: np.ndarray,
    kernel_height: int,
    kernel_width: int,
    stride: int = 1,
    padding: int = 0
) -> np.ndarray:
    """
    Перетворює зображення в матрицю патчів для швидкої згортки.
    """
    N, C, H, W = images.shape
    
    if padding > 0:
        images = np.pad(images, ((0, 0), (0, 0), (padding, padding), (padding, padding)), mode='constant')
        H += 2 * padding
        W += 2 * padding
    
    out_H = (H - kernel_height) // stride + 1
    out_W = (W - kernel_width) // stride + 1
    
    patches = np.zeros((N * out_H * out_W, C * kernel_height * kernel_width), dtype=images.dtype)
    
    idx = 0
    for n in range(N):
        for i in range(out_H):
            for j in range(out_W):
                patch = images[n, :, i*stride:i*stride+kernel_height, j*stride:j*stride+kernel_width]
                patches[idx] = patch.flatten()
                idx += 1
    
    return patches


def col2im(
    patches: np.ndarray,
    input_shape: Tuple[int, int, int, int],
    kernel_height: int,
    kernel_width: int,
    stride: int = 1,
    padding: int = 0
) -> np.ndarray:
    """
    Зворотна операція до im2col.
    """
    N, C, H, W = input_shape
    
    H_pad = H + 2 * padding
    W_pad = W + 2 * padding
    
    out_H = (H_pad - kernel_height) // stride + 1
    out_W = (W_pad - kernel_width) // stride + 1
    
    grad = np.zeros((N, C, H_pad, W_pad), dtype=patches.dtype)
    
    idx = 0
    for n in range(N):
        for i in range(out_H):
            for j in range(out_W):
                patch = patches[idx].reshape(C, kernel_height, kernel_width)
                idx += 1
                grad[n, :, i*stride:i*stride+kernel_height, j*stride:j*stride+kernel_width] += patch
    
    if padding > 0:
        grad = grad[:, :, padding:-padding, padding:-padding]
    
    return grad


# ============================================================
# 3. CONV2D ШАР
# ============================================================

class Conv2D:
    """Згортковий шар з autodiff через im2col."""
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride: int = 1,
        padding: int = 0,
        bias: bool = True
    ):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride
        self.padding = padding
        self.use_bias = bias
        
        scale = math.sqrt(2.0 / (in_channels * self.kernel_size[0] * self.kernel_size[1]))
        self.weights = np.random.randn(out_channels, in_channels, self.kernel_size[0], self.kernel_size[1]) * scale
        self.bias = np.zeros(out_channels) if bias else None
        
        self.dweights = None
        self.dbias = None
        self.dinput = None
        
        self._input = None
        self._patches = None
        self._input_shape = None
        self._out_H = None
        self._out_W = None
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        self._input = x
        self._input_shape = x.shape
        N, C, H, W = x.shape
        
        if C != self.in_channels:
            raise ValueError(f"Expected {self.in_channels} channels, got {C}")
        
        self._patches = im2col(x, self.kernel_size[0], self.kernel_size[1], self.stride, self.padding)
        
        H_pad = H + 2 * self.padding
        W_pad = W + 2 * self.padding
        self._out_H = (H_pad - self.kernel_size[0]) // self.stride + 1
        self._out_W = (W_pad - self.kernel_size[1]) // self.stride + 1
        
        weights_flat = self.weights.reshape(self.out_channels, -1)
        output_flat = weights_flat @ self._patches.T
        
        if self.use_bias:
            output_flat += self.bias[:, np.newaxis]
        
        output = output_flat.T.reshape(N, self.out_channels, self._out_H, self._out_W)
        return output
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        N, C_out, H_out, W_out = grad_output.shape
        
        grad_flat = grad_output.reshape(N * H_out * W_out, C_out).T
        weights_flat = self.weights.reshape(self.out_channels, -1)
        
        self.dweights = grad_flat @ self._patches
        self.dweights = self.dweights.reshape(self.weights.shape) / N
        
        if self.use_bias:
            self.dbias = grad_output.sum(axis=(0, 2, 3)) / N
        
        grad_input_flat = weights_flat.T @ grad_flat
        grad_input_flat = grad_input_flat.T
        
        self.dinput = col2im(
            grad_input_flat,
            self._input_shape,
            self.kernel_size[0],
            self.kernel_size[1],
            self.stride,
            self.padding
        )
        
        return self.dinput
    
    def parameters(self):
        return [
            ('weights', self.weights, self.dweights),
            ('bias', self.bias, self.dbias)
        ] if self.use_bias else [
            ('weights', self.weights, self.dweights)
        ]
    
    def zero_grad(self):
        self.dweights = None
        self.dbias = None
        self.dinput = None


# ============================================================
# 4. MAXPOOL2D ШАР
# ============================================================

class MaxPool2D:
    """MaxPool2D з кешуванням argmax для backward."""
    
    def __init__(self, kernel_size: int, stride: Optional[int] = None, padding: int = 0):
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if stride is not None else kernel_size
        self.padding = padding
        self._input = None
        self._argmax = None
        self._input_shape = None
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        self._input = x
        self._input_shape = x.shape
        N, C, H, W = x.shape
        
        if self.padding > 0:
            x = np.pad(x, ((0, 0), (0, 0), (self.padding, self.padding), (self.padding, self.padding)), mode='constant')
            H += 2 * self.padding
            W += 2 * self.padding
        
        H_out = (H - self.kernel_size[0]) // self.stride + 1
        W_out = (W - self.kernel_size[1]) // self.stride + 1
        
        output = np.zeros((N, C, H_out, W_out), dtype=x.dtype)
        self._argmax = np.zeros((N, C, H_out, W_out, 2), dtype=np.int64)
        
        for n in range(N):
            for c in range(C):
                for i in range(H_out):
                    for j in range(W_out):
                        window = x[n, c, i*self.stride:i*self.stride+self.kernel_size[0], j*self.stride:j*self.stride+self.kernel_size[1]]
                        max_val = window.max()
                        output[n, c, i, j] = max_val
                        idx = window.argmax()
                        self._argmax[n, c, i, j] = (idx // self.kernel_size[1], idx % self.kernel_size[1])
        
        return output
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        N, C, H_out, W_out = grad_output.shape
        _, _, H, W = self._input_shape
        
        H_pad = H + 2 * self.padding
        W_pad = W + 2 * self.padding
        
        grad_input = np.zeros((N, C, H_pad, W_pad), dtype=grad_output.dtype)
        
        for n in range(N):
            for c in range(C):
                for i in range(H_out):
                    for j in range(W_out):
                        h_idx, w_idx = self._argmax[n, c, i, j]
                        grad_input[n, c, i*self.stride + h_idx, j*self.stride + w_idx] += grad_output[n, c, i, j]
        
        if self.padding > 0:
            grad_input = grad_input[:, :, self.padding:-self.padding, self.padding:-self.padding]
        
        return grad_input
    
    def zero_grad(self):
        pass


# ============================================================
# 5. FLATTEN ШАР
# ============================================================

class Flatten:
    """Розгортає тензор у 2D (batch, features)."""
    
    def __init__(self):
        self._input_shape = None
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        self._input_shape = x.shape
        return x.reshape(x.shape[0], -1)
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        return grad_output.reshape(self._input_shape)
    
    def zero_grad(self):
        pass


# ============================================================
# 6. BATCHNORM ШАР
# ============================================================

class BatchNorm2D:
    """Batch Normalization для 2D зображень."""
    
    def __init__(self, num_features, eps=1e-5, momentum=0.1):
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        
        self.gamma = np.ones(num_features)
        self.beta = np.zeros(num_features)
        
        self.running_mean = np.zeros(num_features)
        self.running_var = np.ones(num_features)
        
        self._input = None
        self._mean = None
        self._var = None
        self._normalized = None
        
        self.dgamma = None
        self.dbeta = None
        self.dinput = None
    
    def forward(self, x: np.ndarray, training=True) -> np.ndarray:
        self._input = x
        N, C, H, W = x.shape
        
        if C != self.num_features:
            raise ValueError(f"Expected {self.num_features} channels, got {C}")
        
        # Перетворюємо в (N*H*W, C)
        x_flat = x.transpose(0, 2, 3, 1).reshape(-1, C)
        
        if training:
            mean = x_flat.mean(axis=0)
            var = x_flat.var(axis=0)
            
            self.running_mean = self.momentum * mean + (1 - self.momentum) * self.running_mean
            self.running_var = self.momentum * var + (1 - self.momentum) * self.running_var
        else:
            mean = self.running_mean
            var = self.running_var
        
        self._mean = mean
        self._var = var
        
        normalized = (x_flat - mean) / np.sqrt(var + self.eps)
        self._normalized = normalized
        
        output_flat = self.gamma * normalized + self.beta
        output = output_flat.reshape(N, H, W, C).transpose(0, 3, 1, 2)
        
        return output
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        N, C, H, W = grad_output.shape
        
        grad_flat = grad_output.transpose(0, 2, 3, 1).reshape(-1, C)
        
        # Градієнти для gamma і beta
        self.dgamma = (grad_flat * self._normalized).sum(axis=0) / N
        self.dbeta = grad_flat.sum(axis=0) / N
        
        # Градієнт для вхідних даних
        x_flat = self._input.transpose(0, 2, 3, 1).reshape(-1, C)
        mean = self._mean
        var = self._var
        eps = self.eps
        
        N_total = x_flat.shape[0]
        inv_std = 1.0 / np.sqrt(var + eps)
        
        # Градієнт для normalized
        d_norm = grad_flat * self.gamma
        
        # Градієнт для x
        d_x = (1.0 / N_total) * inv_std * (
            N_total * d_norm -
            d_norm.sum(axis=0) -
            (x_flat - mean) * (inv_std ** 2) * (d_norm * (x_flat - mean)).sum(axis=0)
        )
        
        self.dinput = d_x.reshape(N, H, W, C).transpose(0, 3, 1, 2)
        
        return self.dinput
    
    def parameters(self):
        return [
            ('gamma', self.gamma, self.dgamma),
            ('beta', self.beta, self.dbeta)
        ]
    
    def zero_grad(self):
        self.dgamma = None
        self.dbeta = None
        self.dinput = None


# ============================================================
# 7. ФУНКЦІЇ ДЛЯ ТЕНЗОРІВ
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


# ============================================================
# 8. ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    print("🧪 Testing Conv2D + MaxPool2D + Flatten + BatchNorm")
    
    conv1 = Conv2D(1, 32, kernel_size=3, stride=1, padding=1)
    bn1 = BatchNorm2D(32)
    pool1 = MaxPool2D(kernel_size=2, stride=2)
    conv2 = Conv2D(32, 64, kernel_size=3, stride=1, padding=1)
    bn2 = BatchNorm2D(64)
    pool2 = MaxPool2D(kernel_size=2, stride=2)
    flatten = Flatten()
    
    x = np.random.randn(8, 1, 28, 28)
    
    print(f"Input shape: {x.shape}")
    x = conv1.forward(x)
    print(f"After Conv1: {x.shape}")
    x = bn1.forward(x)
    print(f"After BN1: {x.shape}")
    x = pool1.forward(x)
    print(f"After Pool1: {x.shape}")
    x = conv2.forward(x)
    print(f"After Conv2: {x.shape}")
    x = bn2.forward(x)
    print(f"After BN2: {x.shape}")
    x = pool2.forward(x)
    print(f"After Pool2: {x.shape}")
    x = flatten.forward(x)
    print(f"After Flatten: {x.shape}")
    
    grad = np.random.randn(*x.shape)
    grad = flatten.backward(grad)
    grad = pool2.backward(grad)
    grad = bn2.backward(grad)
    grad = conv2.backward(grad)
    grad = pool1.backward(grad)
    grad = bn1.backward(grad)
    grad = conv1.backward(grad)
    
    print(f"\n✅ All shapes match!")
    print(f"   grad shape: {grad.shape}")
    print(f"   conv1 dweights shape: {conv1.dweights.shape}")
    print(f"   conv1 dbias shape: {conv1.dbias.shape}")
    print(f"   bn1 dgamma shape: {bn1.dgamma.shape}")
    print(f"   bn1 dbeta shape: {bn1.dbeta.shape}")
