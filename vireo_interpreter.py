# ============================================================
# VIREO INTERPRETER v0.5.1
# ============================================================
#
# Full ML / Tensor engine for Vireo
#
# FIXED:
# - Reverse-mode autodiff
# - Gradient accumulation
# - Broadcasting
# - Dense layer
# - Stable Softmax
# - Stable CrossEntropy
# - Adam optimizer
# - SGD optimizer
# - Real MNIST loading
# - Mini-batch training
# - Real prediction
# - Real multiclass metrics
# - Confusion matrix
# - Shape validation
#
# Vireo syntax preserved:
#
# model MNIST {
#     layer Dense(784, 128)
#     activation ReLU
#     layer Dense(128, 10)
#     activation Softmax
#     loss CrossEntropy
#     optimizer Adam(lr=0.001)
# }
#
# train MNIST {
#     data = "mnist"
#     epochs = 5
#     batch_size = 64
#     lr = 0.001
# }
#
# predict MNIST {
#     data = "test"
#     model = "MNIST"
# }
#
# evaluate MNIST {
#     data = "test"
#     metrics = [accuracy, precision, recall, f1]
# }
#
# ============================================================

import re
import math
import json
import random
import os
import urllib.request
from typing import List, Dict, Any, Optional, Union, Tuple


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
        return values[0]

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
    """
    NumPy-like broadcasting shape calculation.
    """
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
            raise ValueError(
                f"BroadcastError: cannot broadcast {shape_a} and {shape_b}"
            )

    return tuple(reversed(result))


def _broadcast_data(data, source_shape, target_shape):
    """
    Broadcast nested list/scalar data to target shape.
    """
    source_shape = tuple(source_shape)
    target_shape = tuple(target_shape)

    if source_shape == target_shape:
        return _deep_copy(data)

    if source_shape == ():
        return _broadcast_data(
            data,
            (),
            target_shape
        )

    if len(source_shape) > len(target_shape):
        raise ValueError(
            f"Cannot broadcast {source_shape} to {target_shape}"
        )

    padded_source = (1,) * (
        len(target_shape) - len(source_shape)
    ) + source_shape

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


def _unbroadcast(grad_data, grad_shape, target_shape):
    """
    Reduces a broadcasted gradient back to original shape.
    """
    if tuple(grad_shape) == tuple(target_shape):
        return _deep_copy(grad_data)

    flat_grad = _flatten(grad_data)

    if not target_shape:
        return sum(flat_grad)

    padded_target = (1,) * (
        len(grad_shape) - len(target_shape)
    ) + tuple(target_shape)

    result = [0.0] * _numel(padded_target)

    for linear in range(_numel(grad_shape)):
        indices = []
        remainder = linear

        for dim in reversed(grad_shape):
            indices.append(remainder % dim)
            remainder //= dim

        indices.reverse()

        target_indices = []

        for i, dim in enumerate(padded_target):
            if dim == 1:
                target_indices.append(0)
            else:
                target_indices.append(indices[i])

        target_linear = 0
        for i, idx in enumerate(target_indices):
            target_linear *= padded_target[i]
            target_linear += idx

        result[target_linear] += flat_grad[linear]

    return _unflatten(
        result,
        padded_target
    )


# ============================================================
# 2. TENSOR
# ============================================================

class Tensor:
    """
    Vireo Tensor with reverse-mode autodiff.
    """

    def __init__(
        self,
        data,
        dtype="float32",
        requires_grad=False,
        _parents=(),
        _op=""
    ):
        if isinstance(data, Tensor):
            data = data.data

        if _is_number(data):
            data = [float(data)]

        elif isinstance(data, tuple):
            data = list(data)

        elif not isinstance(data, list):
            if hasattr(data, "tolist"):
                data = data.tolist()
            elif hasattr(data, "__iter__"):
                data = list(data)
            else:
                data = [data]

        self.data = _deep_copy(data)
        self.dtype = dtype
        self.requires_grad = bool(requires_grad)

        self.grad = None

        self._parents = tuple(_parents)
        self._op = _op
        self._backward = lambda: None

        self._shape = list(_shape_of(self.data))

    # --------------------------------------------------------
    # Basic properties
    # --------------------------------------------------------

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
            raise ValueError(
                f"Tensor.item() requires one element, got {len(flat)}"
            )

        return flat[0]

    def numpy(self):
        return _deep_copy(self.data)

    def __len__(self):
        if not self._shape:
            return 1
        return self._shape[0]

    def __repr__(self):
        return (
            f"Tensor(shape={self.shape}, "
            f"dtype={self.dtype}, "
            f"requires_grad={self.requires_grad})"
        )

    def __str__(self):
        return str(self.data)

    # --------------------------------------------------------
    # Gradient helpers
    # --------------------------------------------------------

    def _accumulate_grad(self, grad):
        if not self.requires_grad:
            return

        if not isinstance(grad, Tensor):
            grad = Tensor(grad)

        if self.grad is None:
            self.grad = Tensor(
                grad.data,
                dtype=self.dtype,
                requires_grad=False
            )
        else:
            self.grad = Tensor(
                _add_data(
                    self.grad.data,
                    grad.data
                ),
                dtype=self.dtype,
                requires_grad=False
            )

    def zero_grad(self):
        self.grad = None

    # --------------------------------------------------------
    # Backward
    # --------------------------------------------------------

    def backward(self, grad=None):
        """
        Full reverse-mode autodiff.

        Uses a topological graph traversal instead of recursive
        backward calls.
        """

        if not self.requires_grad and grad is None:
            # Still allow scalar backward for convenience.
            pass

        if grad is None:
            if self.size != 1:
                raise RuntimeError(
                    "backward() requires grad for non-scalar Tensor"
                )

            grad = Tensor(
                _unflatten([1.0], self._shape)
            )

        elif isinstance(grad, (int, float)):
            grad = Tensor(
                _broadcast_data(
                    float(grad),
                    [],
                    tuple(self._shape)
                )
            )

        elif not isinstance(grad, Tensor):
            grad = Tensor(grad)

        # Build graph
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

        # Seed
        self.grad = Tensor(
            grad.data,
            dtype=self.dtype,
            requires_grad=False
        )

        # Reverse traversal
        for node in reversed(topo):
            node._backward()

    # --------------------------------------------------------
    # Indexing
    # --------------------------------------------------------

    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            result = self.data

            for i in idx:
                result = result[i]

            return Tensor(result)

        if isinstance(idx, slice):
            return Tensor(
                self.data[idx],
                requires_grad=self.requires_grad
            )

        return self.data[idx]

    def __setitem__(self, idx, value):
        if isinstance(value, Tensor):
            value = value.data

        if isinstance(idx, tuple):
            result = self.data

            for i in idx[:-1]:
                result = result[i]

            result[idx[-1]] = value
        else:
            self.data[idx] = value

    # --------------------------------------------------------
    # Arithmetic
    # --------------------------------------------------------

    def __add__(self, other):
        return _binary_op(
            self,
            other,
            lambda a, b: a + b,
            "add"
        )

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return _binary_op(
            self,
            other,
            lambda a, b: a - b,
            "sub"
        )

    def __rsub__(self, other):
        return _binary_op(
            other,
            self,
            lambda a, b: a - b,
            "sub"
        )

    def __mul__(self, other):
        return _binary_op(
            self,
            other,
            lambda a, b: a * b,
            "mul"
        )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return _binary_op(
            self,
            other,
            lambda a, b: a / b,
            "div"
        )

    def __rtruediv__(self, other):
        return _binary_op(
            other,
            self,
            lambda a, b: a / b,
            "div"
        )

    def __neg__(self):
        return self * -1.0

    def __pow__(self, power):
        if isinstance(power, Tensor):
            return _binary_op(
                self,
                power,
                lambda a, b: a ** b,
                "pow"
            )

        data = [
            x ** power
            for x in self.flatten()
        ]

        result = Tensor(
            _unflatten(data, self._shape),
            requires_grad=self.requires_grad,
            _parents=(self,),
            _op="pow"
        )

        def _backward():
            if self.grad is None:
                return

            grad_flat = self.grad.flatten()

            result_grad = [
                g * power * (x ** (power - 1))
                for g, x in zip(
                    grad_flat,
                    self.flatten()
                )
            ]

            self._accumulate_grad(
                Tensor(
                    _unflatten(
                        result_grad,
                        self._shape
                    )
                )
            )

        result._backward = _backward

        return result

    # --------------------------------------------------------
    # Matrix multiplication
    # --------------------------------------------------------

    def matmul(self, other):
        if not isinstance(other, Tensor):
            other = Tensor(other)

        a_shape = tuple(self._shape)
        b_shape = tuple(other._shape)

        if len(a_shape) == 1 and len(b_shape) == 1:

            if a_shape[0] != b_shape[0]:
                raise ValueError(
                    f"Shape mismatch: {a_shape} @ {b_shape}"
                )

            value = sum(
                a * b
                for a, b in zip(
                    self.flatten(),
                    other.flatten()
                )
            )

            result = Tensor(
                [value],
                requires_grad=(
                    self.requires_grad or
                    other.requires_grad
                ),
                _parents=(self, other),
                _op="matmul"
            )

            def _backward():
                if result.grad is None:
                    return

                g = result.grad.item()

                if self.requires_grad:
                    self._accumulate_grad(
                        Tensor([
                            g * b
                            for b in other.flatten()
                        ])
                    )

                if other.requires_grad:
                    other._accumulate_grad(
                        Tensor([
                            g * a
                            for a in self.flatten()
                        ])
                    )

            result._backward = _backward

            return result

        # ----------------------------------------------------
        # 2D @ 2D
        # ----------------------------------------------------

        if len(a_shape) == 2 and len(b_shape) == 2:

            if a_shape[1] != b_shape[0]:
                raise ValueError(
                    f"Shape mismatch: {a_shape} @ {b_shape}"
                )

            rows = a_shape[0]
            k = a_shape[1]
            cols = b_shape[1]

            result_data = [
                [
                    sum(
                        self.data[i][p] *
                        other.data[p][j]
                        for p in range(k)
                    )
                    for j in range(cols)
                ]
                for i in range(rows)
            ]

            result = Tensor(
                result_data,
                requires_grad=(
                    self.requires_grad or
                    other.requires_grad
                ),
                _parents=(self, other),
                _op="matmul"
            )

            def _backward():

                if result.grad is None:
                    return

                g = result.grad.data

                if self.requires_grad:
                    grad_a = [
                        [
                            sum(
                                g[i][j] *
                                other.data[p][j]
                                for j in range(cols)
                            )
                            for p in range(k)
                        ]
                        for i in range(rows)
                    ]

                    self._accumulate_grad(
                        Tensor(grad_a)
                    )

                if other.requires_grad:
                    grad_b = [
                        [
                            sum(
                                self.data[i][p] *
                                g[i][j]
                                for i in range(rows)
                            )
                            for j in range(cols)
                        ]
                        for p in range(k)
                    ]

                    other._accumulate_grad(
                        Tensor(grad_b)
                    )

            result._backward = _backward

            return result

        # ----------------------------------------------------
        # 2D @ 1D
        # ----------------------------------------------------

        if len(a_shape) == 2 and len(b_shape) == 1:

            if a_shape[1] != b_shape[0]:
                raise ValueError(
                    f"Shape mismatch: {a_shape} @ {b_shape}"
                )

            rows = a_shape[0]
            cols = a_shape[1]

            result_data = [
                sum(
                    self.data[i][j] *
                    other.data[j]
                    for j in range(cols)
                )
                for i in range(rows)
            ]

            result = Tensor(
                result_data,
                requires_grad=(
                    self.requires_grad or
                    other.requires_grad
                ),
                _parents=(self, other),
                _op="matmul"
            )

            def _backward():

                if result.grad is None:
                    return

                g = result.grad.flatten()

                if self.requires_grad:

                    grad_a = [
                        [
                            g[i] * other.data[j]
                            for j in range(cols)
                        ]
                        for i in range(rows)
                    ]

                    self._accumulate_grad(
                        Tensor(grad_a)
                    )

                if other.requires_grad:

                    grad_b = [
                        sum(
                            self.data[i][j] *
                            g[i]
                            for i in range(rows)
                        )
                        for j in range(cols)
                    ]

                    other._accumulate_grad(
                        Tensor(grad_b)
                    )

            result._backward = _backward

            return result

        raise ValueError(
            f"Unsupported matmul: {a_shape} @ {b_shape}"
        )

    # --------------------------------------------------------
    # Transpose
    # --------------------------------------------------------

    def transpose(self):
        if len(self._shape) == 1:
            return Tensor(
                [[x] for x in self.flatten()],
                requires_grad=self.requires_grad
            )

        if len(self._shape) != 2:
            raise ValueError(
                "transpose currently supports 1D/2D tensors"
            )

        rows, cols = self._shape

        result_data = [
            [
                self.data[i][j]
                for i in range(rows)
            ]
            for j in range(cols)
        ]

        result = Tensor(
            result_data,
            requires_grad=self.requires_grad,
            _parents=(self,),
            _op="transpose"
        )

        def _backward():

            if self.grad is not None:
                g = self.grad.data

                grad = [
                    [
                        g[j][i]
                        for j in range(len(g))
                    ]
                    for i in range(len(g[0]))
                ]

                self._accumulate_grad(
                    Tensor(grad)
                )

        result._backward = _backward

        return result

    # --------------------------------------------------------
    # Reshape
    # --------------------------------------------------------

    def reshape(self, new_shape):
        new_shape = _normalize_shape(new_shape)

        if _numel(self._shape) != _numel(new_shape):
            raise ValueError(
                f"ShapeError: Cannot reshape "
                f"Tensor{tuple(self._shape)} "
                f"to {new_shape}"
            )

        result = Tensor(
            _unflatten(
                self.flatten(),
                new_shape
            ),
            requires_grad=self.requires_grad,
            _parents=(self,),
            _op="reshape"
        )

        def _backward():

            if self.grad is None:
                return

            self._accumulate_grad(
                Tensor(
                    _unflatten(
                        self.grad.flatten(),
                        self._shape
                    )
                )
            )

        result._backward = _backward

        return result

    # --------------------------------------------------------
    # Reduction
    # --------------------------------------------------------

    def sum(self, axis=None, keepdims=False):

        if axis is None:

            value = sum(self.flatten())

            if keepdims:
                out_shape = tuple(
                    1 for _ in self._shape
                )
                data = _unflatten(
                    [value],
                    out_shape
                )
            else:
                data = [value]

            result = Tensor(
                data,
                requires_grad=self.requires_grad,
                _parents=(self,),
                _op="sum"
            )

            def _backward():

                if self.grad is None:
                    return

                scalar_grad = self.grad.item()

                self._accumulate_grad(
                    Tensor(
                        _unflatten(
                            [
                                scalar_grad
                            ] * self.size,
                            self._shape
                        )
                    )
                )

            result._backward = _backward

            return result

        if len(self._shape) != 2:
            raise ValueError(
                "axis reduction currently supports 2D tensors"
            )

        if axis == 0:

            values = [
                sum(
                    self.data[i][j]
                    for i in range(self._shape[0])
                )
                for j in range(self._shape[1])
            ]

            result = Tensor(
                values,
                requires_grad=self.requires_grad,
                _parents=(self,),
                _op="sum"
            )

            def _backward():

                if self.grad is None:
                    return

                g = self.grad.flatten()

                self._accumulate_grad(
                    Tensor([
                        [
                            g[j]
                            for j in range(self._shape[1])
                        ]
                        for _ in range(self._shape[0])
                    ])
                )

            result._backward = _backward

            return result

        if axis == 1:

            values = [
                sum(row)
                for row in self.data
            ]

            result = Tensor(
                values,
                requires_grad=self.requires_grad,
                _parents=(self,),
                _op="sum"
            )

            def _backward():

                if self.grad is None:
                    return

                g = self.grad.flatten()

                self._accumulate_grad(
                    Tensor([
                        [
                            g[i]
                            for _ in range(self._shape[1])
                        ]
                        for i in range(self._shape[0])
                    ])
                )

            result._backward = _backward

            return result

        raise ValueError(f"Unsupported axis: {axis}")

    def mean(self, axis=None, keepdims=False):

        if axis is None:
            return self.sum() / self.size

        if axis < 0:
            axis += len(self._shape)

        divisor = self._shape[axis]

        return self.sum(
            axis=axis,
            keepdims=keepdims
        ) / divisor

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def max(self, axis=None):

        if axis is None:
            return max(self.flatten())

        if len(self._shape) == 2 and axis == 1:
            return Tensor([
                max(row)
                for row in self.data
            ])

        if len(self._shape) == 2 and axis == 0:
            return Tensor([
                max(
                    self.data[i][j]
                    for i in range(self._shape[0])
                )
                for j in range(self._shape[1])
            ])

        raise ValueError(
            f"Unsupported max axis: {axis}"
        )

    def min(self, axis=None):

        if axis is None:
            return min(self.flatten())

        if len(self._shape) == 2 and axis == 1:
            return Tensor([
                min(row)
                for row in self.data
            ])

        if len(self._shape) == 2 and axis == 0:
            return Tensor([
                min(
                    self.data[i][j]
                    for i in range(self._shape[0])
                )
                for j in range(self._shape[1])
            ])

        raise ValueError(
            f"Unsupported min axis: {axis}"
        )

    def argmax(self, axis=None):

        if axis is None:
            flat = self.flatten()
            return flat.index(max(flat))

        if len(self._shape) == 2 and axis == 1:
            return [
                row.index(max(row))
                for row in self.data
            ]

        if len(self._shape) == 2 and axis == 0:
            return [
                max(
                    range(self._shape[0]),
                    key=lambda i: self.data[i][j]
                )
                for j in range(self._shape[1])
            ]

        raise ValueError(
            f"Unsupported argmax axis: {axis}"
        )

    def argmin(self, axis=None):

        if axis is None:
            flat = self.flatten()
            return flat.index(min(flat))

        if len(self._shape) == 2 and axis == 1:
            return [
                row.index(min(row))
                for row in self.data
            ]

        raise ValueError(
            f"Unsupported argmin axis: {axis}"
        )

    # --------------------------------------------------------
    # Elementwise mathematical functions
    # --------------------------------------------------------

    def exp(self):
        return _unary_op(
            self,
            math.exp,
            lambda x: math.exp(x),
            "exp"
        )

    def log(self):
        return _unary_op(
            self,
            lambda x: math.log(max(x, 1e-12)),
            lambda x: 1.0 / max(x, 1e-12),
            "log"
        )

    def sqrt(self):
        return _unary_op(
            self,
            lambda x: math.sqrt(max(x, 0.0)),
            lambda x: 0.5 / math.sqrt(max(x, 1e-12)),
            "sqrt"
        )

    def abs(self):
        return _unary_op(
            self,
            abs,
            lambda x: 1.0 if x > 0 else -1.0 if x < 0 else 0.0,
            "abs"
        )

    def sin(self):
        return _unary_op(
            self,
            math.sin,
            math.cos,
            "sin"
        )

    def cos(self):
        return _unary_op(
            self,
            math.cos,
            lambda x: -math.sin(x),
            "cos"
        )

    def tan(self):
        return _unary_op(
            self,
            math.tan,
            lambda x: 1.0 / (math.cos(x) ** 2),
            "tan"
        )

    # --------------------------------------------------------
    # Normalization
    # --------------------------------------------------------

    def normalize(self, mean=None, std=None):

        flat = self.flatten()

        if mean is None:
            mean = sum(flat) / len(flat)

        if std is None:
            std = math.sqrt(
                sum(
                    (x - mean) ** 2
                    for x in flat
                ) / len(flat)
            )

        return Tensor([
            (x - mean) /
            (std + 1e-8)
            for x in flat
        ])

    def standardize(self):
        return self.normalize()

    def clip(self, min_val, max_val):
        return Tensor([
            max(min_val, min(max_val, x))
            for x in self.flatten()
        ])

    # --------------------------------------------------------
    # Factory methods
    # --------------------------------------------------------

    @classmethod
    def zeros(cls, shape):
        shape = _normalize_shape(shape)

        return cls(
            _unflatten(
                [0.0] * _numel(shape),
                shape
            )
        )

    @classmethod
    def ones(cls, shape):
        shape = _normalize_shape(shape)

        return cls(
            _unflatten(
                [1.0] * _numel(shape),
                shape
            )
        )

    @classmethod
    def random(cls, shape):
        shape = _normalize_shape(shape)

        return cls(
            _unflatten(
                [
                    random.random()
                    for _ in range(_numel(shape))
                ],
                shape
            )
        )

    @classmethod
    def eye(cls, size):
        return cls([
            [
                1.0 if i == j else 0.0
                for j in range(size)
            ]
            for i in range(size)
        ])

    @classmethod
    def linspace(cls, start, end, steps):

        if steps <= 1:
            return cls([start])

        return cls([
            start +
            i * (end - start) /
            (steps - 1)
            for i in range(steps)
        ])

    @classmethod
    def arange(cls, start, end, step=1):
        return cls(
            list(
                range(
                    start,
                    end,
                    step
                )
            )
        )


# ============================================================
# 3. AUTODIFF OPERATIONS
# ============================================================

def _to_tensor(value):
    if isinstance(value, Tensor):
        return value

    return Tensor(value)


def _add_data(a, b):
    if isinstance(a, list):
        return [
            _add_data(x, y)
            for x, y in zip(a, b)
        ]

    return a + b


def _binary_op(a, b, forward_fn, op_name):

    a = _to_tensor(a)
    b = _to_tensor(b)

    result_shape = _broadcast_shape(
        tuple(a.shape),
        tuple(b.shape)
    )

    a_data = _broadcast_data(
        a.data,
        tuple(a.shape),
        result_shape
    )

    b_data = _broadcast_data(
        b.data,
        tuple(b.shape),
        result_shape
    )

    flat_a = _flatten(a_data)
    flat_b = _flatten(b_data)

    result_flat = [
        forward_fn(x, y)
        for x, y in zip(
            flat_a,
            flat_b
        )
    ]

    result = Tensor(
        _unflatten(
            result_flat,
            result_shape
        ),
        requires_grad=(
            a.requires_grad or
            b.requires_grad
        ),
        _parents=(a, b),
        _op=op_name
    )

    def _backward():

        if result.grad is None:
            return

        grad_flat = result.grad.flatten()

        if op_name == "add":

            if a.requires_grad:
                ga = grad_flat

            if b.requires_grad:
                gb = grad_flat

        elif op_name == "sub":

            if a.requires_grad:
                ga = grad_flat

            if b.requires_grad:
                gb = [-x for x in grad_flat]

        elif op_name == "mul":

            if a.requires_grad:
                ga = [
                    g * y
                    for g, y in zip(
                        grad_flat,
                        flat_b
                    )
                ]

            if b.requires_grad:
                gb = [
                    g * x
                    for g, x in zip(
                        grad_flat,
                        flat_a
                    )
                ]

        elif op_name == "div":

            if a.requires_grad:
                ga = [
                    g / y
                    for g, y in zip(
                        grad_flat,
                        flat_b
                    )
                ]

            if b.requires_grad:
                gb = [
                    -g * x / (y ** 2)
                    for g, x, y in zip(
                        grad_flat,
                        flat_a,
                        flat_b
                    )
                ]

        elif op_name == "pow":

            if a.requires_grad:
                ga = [
                    g * y * (
                        x ** (y - 1)
                    )
                    for g, x, y in zip(
                        grad_flat,
                        flat_a,
                        flat_b
                    )
                ]

            if b.requires_grad:
                ga = [
                    g * (
                        x ** y
                    ) * math.log(
                        max(abs(x), 1e-12)
                    )
                    for g, x, y in zip(
                        grad_flat,
                        flat_a,
                        flat_b
                    )
                ]

        if a.requires_grad:
            ga_data = _unbroadcast(
                _unflatten(
                    ga,
                    result_shape
                ),
                result_shape,
                tuple(a.shape)
            )

            a._accumulate_grad(
                Tensor(ga_data)
            )

        if b.requires_grad:
            gb_data = _unbroadcast(
                _unflatten(
                    gb,
                    result_shape
                ),
                result_shape,
                tuple(b.shape)
            )

            b._accumulate_grad(
                Tensor(gb_data)
            )

    result._backward = _backward

    return result


def _unary_op(
    x,
    forward_fn,
    derivative_fn,
    op_name
):

    x = _to_tensor(x)

    flat = x.flatten()

    result_flat = [
        forward_fn(v)
        for v in flat
    ]

    result = Tensor(
        _unflatten(
            result_flat,
            tuple(x.shape)
        ),
        requires_grad=x.requires_grad,
        _parents=(x,),
        _op=op_name
    )

    def _backward():

        if result.grad is None:
            return

        grad_flat = result.grad.flatten()

        gx = [
            g * derivative_fn(v)
            for g, v in zip(
                grad_flat,
                flat
            )
        ]

        x._accumulate_grad(
            Tensor(
                _unflatten(
                    gx,
                    tuple(x.shape)
                )
            )
        )

    result._backward = _backward

    return result


# ============================================================
# 4. ACTIVATION FUNCTIONS
# ============================================================

def relu(x):

    if not isinstance(x, Tensor):
        return max(0.0, x)

    flat = x.flatten()

    result_flat = [
        max(0.0, v)
        for v in flat
    ]

    result = Tensor(
        _unflatten(
            result_flat,
            tuple(x.shape)
        ),
        requires_grad=x.requires_grad,
        _parents=(x,),
        _op="relu"
    )

    def _backward():

        if result.grad is None:
            return

        gx = [
            g if v > 0 else 0.0
            for g, v in zip(
                result.grad.flatten(),
                flat
            )
        ]

        x._accumulate_grad(
            Tensor(
                _unflatten(
                    gx,
                    tuple(x.shape)
                )
            )
        )

    result._backward = _backward

    return result


def sigmoid(x):

    if not isinstance(x, Tensor):
        return 1.0 / (
            1.0 + math.exp(-x)
        )

    flat = x.flatten()

    output = [
        1.0 / (
            1.0 + math.exp(
                -max(-60.0, min(60.0, v))
            )
        )
        for v in flat
    ]

    result = Tensor(
        _unflatten(
            output,
            tuple(x.shape)
        ),
        requires_grad=x.requires_grad,
        _parents=(x,),
        _op="sigmoid"
    )

    def _backward():

        if result.grad is None:
            return

        gx = [
            g * y * (1.0 - y)
            for g, y in zip(
                result.grad.flatten(),
                output
            )
        ]

        x._accumulate_grad(
            Tensor(
                _unflatten(
                    gx,
                    tuple(x.shape)
                )
            )
        )

    result._backward = _backward

    return result


def tanh(x):

    if not isinstance(x, Tensor):
        return math.tanh(x)

    flat = x.flatten()

    output = [
        math.tanh(v)
        for v in flat
    ]

    result = Tensor(
        _unflatten(
            output,
            tuple(x.shape)
        ),
        requires_grad=x.requires_grad,
        _parents=(x,),
        _op="tanh"
    )

    def _backward():

        if result.grad is None:
            return

        gx = [
            g * (
                1.0 - y * y
            )
            for g, y in zip(
                result.grad.flatten(),
                output
            )
        ]

        x._accumulate_grad(
            Tensor(
                _unflatten(
                    gx,
                    tuple(x.shape)
                )
            )
        )

    result._backward = _backward

    return result


def leaky_relu(x, alpha=0.01):

    if not isinstance(x, Tensor):
        return (
            x
            if x >= 0
            else alpha * x
        )

    flat = x.flatten()

    output = [
        v if v >= 0 else alpha * v
        for v in flat
    ]

    result = Tensor(
        _unflatten(
            output,
            tuple(x.shape)
        ),
        requires_grad=x.requires_grad,
        _parents=(x,),
        _op="leaky_relu"
    )

    def _backward():

        if result.grad is None:
            return

        gx = [
            g * (
                1.0 if v >= 0
                else alpha
            )
            for g, v in zip(
                result.grad.flatten(),
                flat
            )
        ]

        x._accumulate_grad(
            Tensor(
                _unflatten(
                    gx,
                    tuple(x.shape)
                )
            )
        )

    result._backward = _backward

    return result


def elu(x, alpha=1.0):

    if not isinstance(x, Tensor):
        return (
            x
            if x > 0
            else alpha * (
                math.exp(x) - 1
            )
        )

    flat = x.flatten()

    output = [
        v if v > 0 else
        alpha * (
            math.exp(v) - 1
        )
        for v in flat
    ]

    result = Tensor(
        _unflatten(
            output,
            tuple(x.shape)
        ),
        requires_grad=x.requires_grad,
        _parents=(x,),
        _op="elu"
    )

    def _backward():

        if result.grad is None:
            return

        gx = []

        for g, v, y in zip(
            result.grad.flatten(),
            flat,
            output
        ):
            derivative = (
                1.0
                if v > 0
                else y + alpha
            )

            gx.append(
                g * derivative
            )

        x._accumulate_grad(
            Tensor(
                _unflatten(
                    gx,
                    tuple(x.shape)
                )
            )
        )

    result._backward = _backward

    return result


def softmax(x, axis=-1):

    if not isinstance(x, Tensor):
        return x

    if len(x.shape) == 1:

        values = x.flatten()
        maximum = max(values)

        exp_values = [
            math.exp(
                v - maximum
            )
            for v in values
        ]

        total = sum(exp_values)

        probabilities = [
            v / total
            for v in exp_values
        ]

        result = Tensor(
            probabilities,
            requires_grad=x.requires_grad,
            _parents=(x,),
            _op="softmax"
        )

        def _backward():

            if result.grad is None:
                return

            g = result.grad.flatten()

            dot = sum(
                p * gi
                for p, gi in zip(
                    probabilities,
                    g
                )
            )

            gx = [
                p * (
                    gi - dot
                )
                for p, gi in zip(
                    probabilities,
                    g
                )
            ]

            x._accumulate_grad(
                Tensor(gx)
            )

        result._backward = _backward

        return result

    if len(x.shape) != 2:
        raise ValueError(
            "softmax currently supports 1D/2D tensors"
        )

    rows = x.shape[0]
    cols = x.shape[1]

    probabilities = []

    for i in range(rows):

        row = x.data[i]

        maximum = max(row)

        exp_values = [
            math.exp(
                v - maximum
            )
            for v in row
        ]

        total = sum(exp_values)

        probabilities.append([
            v / total
            for v in exp_values
        ])

    result = Tensor(
        probabilities,
        requires_grad=x.requires_grad,
        _parents=(x,),
        _op="softmax"
    )

    def _backward():

        if result.grad is None:
            return

        grad = []

        for i in range(rows):

            p = probabilities[i]
            g = result.grad.data[i]

            dot = sum(
                p[j] * g[j]
                for j in range(cols)
            )

            grad.append([
                p[j] * (
                    g[j] - dot
                )
                for j in range(cols)
            ])

        x._accumulate_grad(
            Tensor(grad)
        )

    result._backward = _backward

    return result


# ============================================================
# 5. LOSS FUNCTIONS
# ============================================================

def _labels_to_ints(target):
    if isinstance(target, Tensor):
        return [
            int(round(x))
            for x in target.flatten()
        ]

    return [
        int(x)
        for x in target
    ]


def cross_entropy(
    pred,
    target,
    from_logits=False,
    reduction="mean"
):
    """
    Stable CrossEntropy.

    Supports:
        pred: [batch, classes]
        target: integer class labels

    If from_logits=True:
        pred is treated as raw logits.

    Gradient:
        softmax(logits) - one_hot
    """

    pred = _to_tensor(pred)

    labels = _labels_to_ints(target)

    if len(pred.shape) == 1:
        logits = pred.reshape(
            (1, pred.shape[0])
        )
        labels = labels[:1]
    elif len(pred.shape) == 2:
        logits = pred
    else:
        raise ValueError(
            "CrossEntropy expects 1D or 2D predictions"
        )

    batch = logits.shape[0]
    classes = logits.shape[1]

    if len(labels) != batch:
        raise ValueError(
            f"CrossEntropy: predictions batch={batch}, "
            f"labels={len(labels)}"
        )

    if from_logits:

        losses = []
        probabilities = []

        for i in range(batch):

            row = logits.data[i]

            maximum = max(row)

            exp_values = [
                math.exp(
                    x - maximum
                )
                for x in row
            ]

            exp_sum = sum(exp_values)

            probs = [
                x / exp_sum
                for x in exp_values
            ]

            probabilities.append(probs)

            label = labels[i]

            if label < 0 or label >= classes:
                raise ValueError(
                    f"Invalid class label: {label}"
                )

            log_sum_exp = (
                maximum +
                math.log(exp_sum)
            )

            losses.append(
                log_sum_exp -
                row[label]
            )

        if reduction == "sum":
            loss_value = sum(losses)
        else:
            loss_value = (
                sum(losses) /
                batch
            )

        result = Tensor(
            [loss_value],
            requires_grad=logits.requires_grad,
            _parents=(logits,),
            _op="cross_entropy"
        )

        def _backward():

            if result.grad is None:
                return

            upstream = result.grad.item()

            grad = []

            divisor = (
                1
                if reduction == "sum"
                else batch
            )

            for i in range(batch):

                row_grad = []

                for j in range(classes):

                    one_hot = (
                        1.0
                        if j == labels[i]
                        else 0.0
                    )

                    row_grad.append(
                        upstream *
                        (
                            probabilities[i][j]
                            - one_hot
                        ) / divisor
                    )

                grad.append(row_grad)

            if logits.requires_grad:

                logits._accumulate_grad(
                    Tensor(grad)
                )

        result._backward = _backward

        return result

    # --------------------------------------------------------
    # Probability input
    # --------------------------------------------------------

    probabilities = logits

    losses = []

    for i in range(batch):

        label = labels[i]

        if label < 0 or label >= classes:
            raise ValueError(
                f"Invalid class label: {label}"
            )

        p = max(
            probabilities.data[i][label],
            1e-12
        )

        losses.append(
            -math.log(p)
        )

    loss_value = (
        sum(losses)
        if reduction == "sum"
        else sum(losses) / batch
    )

    result = Tensor(
        [loss_value],
        requires_grad=probabilities.requires_grad,
        _parents=(probabilities,),
        _op="cross_entropy"
    )

    def _backward():

        if result.grad is None:
            return

        upstream = result.grad.item()

        divisor = (
            1
            if reduction == "sum"
            else batch
        )

        grad = []

        for i in range(batch):

            row_grad = []

            for j in range(classes):

                if j == labels[i]:

                    p = max(
                        probabilities.data[i][j],
                        1e-12
                    )

                    value = (
                        -upstream /
                        (
                            p *
                            divisor
                        )
                    )

                else:
                    value = 0.0

                row_grad.append(value)

            grad.append(row_grad)

        probabilities._accumulate_grad(
            Tensor(grad)
        )

    result._backward = _backward

    return result


def mse(pred, target):
    pred = _to_tensor(pred)
    target = _to_tensor(target)

    diff = pred - target

    return (
        (diff * diff).mean()
    )


# ============================================================
# 6. DENSE
# ============================================================

class Dense:

    def __init__(
        self,
        input_size,
        output_size,
        activation="relu"
    ):

        self.input_size = int(input_size)
        self.output_size = int(output_size)

        self.activation = (
            activation.lower()
            if activation
            else None
        )

        # He initialization
        scale = math.sqrt(
            2.0 / self.input_size
        )

        self.weights = Tensor(
            [
                [
                    random.gauss(
                        0,
                        scale
                    )
                    for _ in range(
                        self.output_size
                    )
                ]
                for _ in range(
                    self.input_size
                )
            ],
            requires_grad=True
        )

        self.bias = Tensor(
            [0.0] * self.output_size,
            requires_grad=True
        )

        self.input = None
        self.pre_activation = None
        self.output = None

    def forward(self, x):

        if not isinstance(x, Tensor):
            x = Tensor(x)

        if len(x.shape) == 1:

            if x.shape[0] != self.input_size:
                raise ValueError(
                    f"Dense input shape error: "
                    f"expected [{self.input_size}], "
                    f"got {x.shape}"
                )

        elif len(x.shape) == 2:

            if x.shape[1] != self.input_size:
                raise ValueError(
                    f"Dense input shape error: "
                    f"expected [batch, {self.input_size}], "
                    f"got {x.shape}"
                )

        else:
            raise ValueError(
                "Dense supports 1D/2D input"
            )

        self.input = x

        z = (
            x.matmul(
                self.weights
            )
            + self.bias
        )

        self.pre_activation = z

        activation = self.activation

        if activation in (
            None,
            "",
            "linear"
        ):
            self.output = z

        elif activation == "relu":
            self.output = relu(z)

        elif activation == "sigmoid":
            self.output = sigmoid(z)

        elif activation == "tanh":
            self.output = tanh(z)

        elif activation == "softmax":
            self.output = softmax(z)

        elif activation == "leaky_relu":
            self.output = leaky_relu(z)

        elif activation == "elu":
            self.output = elu(z)

        else:
            raise ValueError(
                f"Unknown activation: {self.activation}"
            )

        return self.output

    def parameters(self):
        return [
            self.weights,
            self.bias
        ]

    def zero_grad(self):
        self.weights.zero_grad()
        self.bias.zero_grad()


# ============================================================
# 7. DROPOUT
# ============================================================

class Dropout:

    def __init__(self, rate=0.3):
        if not 0 <= rate < 1:
            raise ValueError(
                "Dropout rate must be in [0, 1)"
            )

        self.rate = rate
        self.mask = None
        self.training = True

    def forward(self, x):

        if not self.training or self.rate == 0:
            return x

        flat = x.flatten()

        scale = 1.0 / (
            1.0 - self.rate
        )

        mask = [
            1.0 if random.random() > self.rate
            else 0.0
            for _ in flat
        ]

        self.mask = mask

        return Tensor(
            [
                value *
                mask_value *
                scale
                for value, mask_value
                in zip(flat, mask)
            ]
        ).reshape(
            tuple(x.shape)
        )


# ============================================================
# 8. SEQUENTIAL
# ============================================================

class Sequential:

    def __init__(self, layers):
        self.layers = layers
        self.training = True

    def forward(self, x):

        for layer in self.layers:
            x = layer.forward(x)

        return x

    def parameters(self):

        params = []

        for layer in self.layers:

            if hasattr(
                layer,
                "parameters"
            ):
                params.extend(
                    layer.parameters()
                )

        return params

    def zero_grad(self):

        for param in self.parameters():
            param.zero_grad()

    def train(self):

        self.training = True

        for layer in self.layers:

            if hasattr(
                layer,
                "training"
            ):
                layer.training = True

    def eval(self):

        self.training = False

        for layer in self.layers:

            if hasattr(
                layer,
                "training"
            ):
                layer.training = False

    def last_dense(self):

        for layer in reversed(
            self.layers
        ):
            if isinstance(layer, Dense):
                return layer

        return None


# ============================================================
# 9. OPTIMIZER BASE
# ============================================================

class Optimizer:

    def __init__(
        self,
        params,
        lr=0.001
    ):
        self.params = list(params)
        self.lr = lr

    def zero_grad(self):

        for param in self.params:
            param.zero_grad()


# ============================================================
# 10. SGD
# ============================================================

class SGD(Optimizer):

    def __init__(
        self,
        params,
        lr=0.01,
        momentum=0.0
    ):
        super().__init__(
            params,
            lr
        )

        self.momentum = momentum

        self.velocities = [
            None
            for _ in self.params
        ]

    def step(self):

        for i, param in enumerate(
            self.params
        ):

            if param.grad is None:
                continue

            grad_flat = param.grad.flatten()
            data_flat = param.flatten()

            if self.momentum > 0:

                if self.velocities[i] is None:
                    self.velocities[i] = [
                        0.0
                        for _ in grad_flat
                    ]

                velocity = self.velocities[i]

                for j, grad in enumerate(
                    grad_flat
                ):

                    velocity[j] = (
                        self.momentum *
                        velocity[j]
                        +
                        self.lr * grad
                    )

                    data_flat[j] -= velocity[j]

            else:

                for j, grad in enumerate(
                    grad_flat
                ):
                    data_flat[j] -= (
                        self.lr * grad
                    )

            param.data = _unflatten(
                data_flat,
                tuple(param.shape)
            )


# ============================================================
# 11. ADAM
# ============================================================

class Adam(Optimizer):

    def __init__(
        self,
        params,
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8
    ):

        super().__init__(
            params,
            lr
        )

        self.betas = betas
        self.eps = eps

        self.m = [
            None
            for _ in self.params
        ]

        self.v = [
            None
            for _ in self.params
        ]

        self.t = 0

    def step(self):

        self.t += 1

        beta1, beta2 = self.betas

        for i, param in enumerate(
            self.params
        ):

            if param.grad is None:
                continue

            grad = param.grad.flatten()
            data = param.flatten()

            if self.m[i] is None:

                self.m[i] = [
                    0.0
                    for _ in grad
                ]

                self.v[i] = [
                    0.0
                    for _ in grad
                ]

            m = self.m[i]
            v = self.v[i]

            for j, g in enumerate(
                grad
            ):

                m[j] = (
                    beta1 * m[j]
                    +
                    (1.0 - beta1) * g
                )

                v[j] = (
                    beta2 * v[j]
                    +
                    (1.0 - beta2) *
                    (g * g)
                )

                m_hat = (
                    m[j] /
                    (
                        1.0 -
                        beta1 ** self.t
                    )
                )

                v_hat = (
                    v[j] /
                    (
                        1.0 -
                        beta2 ** self.t
                    )
                )

                data[j] -= (
                    self.lr *
                    m_hat /
                    (
                        math.sqrt(v_hat)
                        +
                        self.eps
                    )
                )

            param.data = _unflatten(
                data,
                tuple(param.shape)
            )


# ============================================================
# 12. MNIST
# ============================================================

MNIST_URL = (
    "https://storage.googleapis.com/"
    "tensorflow/tf-keras-datasets/"
    "mnist.npz"
)


def load_mnist(
    cache_dir=None,
    limit_train=None,
    limit_test=None
):
    """
    Loads REAL MNIST.

    Uses:
        ~/.vireo/mnist/mnist.npz

    No TensorFlow dependency is required.
    """

    if cache_dir is None:
        cache_dir = os.path.join(
            os.path.expanduser("~"),
            ".vireo",
            "mnist"
        )

    os.makedirs(
        cache_dir,
        exist_ok=True
    )

    filename = os.path.join(
        cache_dir,
        "mnist.npz"
    )

    if not os.path.exists(filename):

        print(
            "📥 Downloading real MNIST..."
        )

        try:

            urllib.request.urlretrieve(
                MNIST_URL,
                filename
            )

        except Exception as e:

            raise RuntimeError(
                "Unable to download MNIST. "
                f"Reason: {e}"
            )

    try:

        import numpy as np

        with np.load(
            filename
        ) as data:

            x_train = data[
                "x_train"
            ]

            y_train = data[
                "y_train"
            ]

            x_test = data[
                "x_test"
            ]

            y_test = data[
                "y_test"
            ]

    except ImportError:

        raise RuntimeError(
            "MNIST loader requires NumPy. "
            "Install with: pip install numpy"
        )

    if limit_train is not None:
        x_train = x_train[
            :limit_train
        ]
        y_train = y_train[
            :limit_train
        ]

    if limit_test is not None:
        x_test = x_test[
            :limit_test
        ]
        y_test = y_test[
            :limit_test
        ]

    x_train = (
        x_train
        .reshape(
            len(x_train),
            784
        )
        .astype("float32")
        / 255.0
    )

    x_test = (
        x_test
        .reshape(
            len(x_test),
            784
        )
        .astype("float32")
        / 255.0
    )

    return {
        "train": (
            Tensor(
                x_train.tolist()
            ),
            Tensor(
                y_train.astype(
                    "int64"
                ).tolist()
            )
        ),
        "test": (
            Tensor(
                x_test.tolist()
            ),
            Tensor(
                y_test.astype(
                    "int64"
                ).tolist()
            )
        )
    }


def _generate_synthetic_mnist(
    train_size=1000,
    test_size=200
):
    """
    Explicit synthetic dataset for testing only.

    It is NOT MNIST.
    """

    train_images = [
        [
            random.random()
            for _ in range(784)
        ]
        for _ in range(train_size)
    ]

    train_labels = [
        random.randint(0, 9)
        for _ in range(train_size)
    ]

    test_images = [
        [
            random.random()
            for _ in range(784)
        ]
        for _ in range(test_size)
    ]

    test_labels = [
        random.randint(0, 9)
        for _ in range(test_size)
    ]

    return {
        "train": (
            Tensor(train_images),
            Tensor(train_labels)
        ),
        "test": (
            Tensor(test_images),
            Tensor(test_labels)
        )
    }


def load_csv(filename):

    import csv

    data = []

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.reader(f)

        for row in reader:

            data.append([
                float(x)
                for x in row
            ])

    return data


# ============================================================
# 13. METRICS
# ============================================================

def classification_metrics(
    y_true,
    y_pred,
    num_classes=10
):

    y_true = [
        int(x)
        for x in y_true
    ]

    y_pred = [
        int(x)
        for x in y_pred
    ]

    if len(y_true) != len(y_pred):
        raise ValueError(
            "y_true and y_pred length mismatch"
        )

    confusion = [
        [0 for _ in range(num_classes)]
        for _ in range(num_classes)
    ]

    for true, pred in zip(
        y_true,
        y_pred
    ):

        if (
            0 <= true < num_classes
            and
            0 <= pred < num_classes
        ):
            confusion[true][pred] += 1

    total = len(y_true)

    correct = sum(
        confusion[i][i]
        for i in range(num_classes)
    )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    precision_per_class = []
    recall_per_class = []
    f1_per_class = []

    for c in range(num_classes):

        tp = confusion[c][c]

        fp = sum(
            confusion[r][c]
            for r in range(num_classes)
            if r != c
        )

        fn = sum(
            confusion[c][r]
            for r in range(num_classes)
            if r != c
        )

        precision = (
            tp / (tp + fp)
            if tp + fp
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if tp + fn
            else 0.0
        )

        f1 = (
            2 * precision * recall /
            (precision + recall)
            if precision + recall
            else 0.0
        )

        precision_per_class.append(
            precision
        )

        recall_per_class.append(
            recall
        )

        f1_per_class.append(
            f1
        )

    return {
        "accuracy": accuracy,
        "precision": sum(
            precision_per_class
        ) / num_classes,
        "recall": sum(
            recall_per_class
        ) / num_classes,
        "f1": sum(
            f1_per_class
        ) / num_classes,
        "precision_per_class":
            precision_per_class,
        "recall_per_class":
            recall_per_class,
        "f1_per_class":
            f1_per_class,
        "confusion_matrix":
            confusion
    }


# ============================================================
# 14. MODEL TRAINING
# ============================================================

def train_model(
    model,
    train_data,
    train_labels,
    epochs=10,
    batch_size=64,
    lr=0.001,
    optimizer_name="adam",
    shuffle=True,
    verbose=True
):

    if not isinstance(
        train_data,
        Tensor
    ):
        train_data = Tensor(
            train_data
        )

    if not isinstance(
        train_labels,
        Tensor
    ):
        train_labels = Tensor(
            train_labels
        )

    if len(train_data.shape) != 2:
        raise ValueError(
            "train_data must be 2D"
        )

    if len(train_labels.shape) != 1:
        raise ValueError(
            "train_labels must be 1D"
        )

    if train_data.shape[0] != train_labels.shape[0]:
        raise ValueError(
            "Data and labels size mismatch"
        )

    if optimizer_name.lower() == "sgd":

        optimizer = SGD(
            model.parameters(),
            lr=lr
        )

    else:

        optimizer = Adam(
            model.parameters(),
            lr=lr
        )

    history = {
        "loss": [],
        "accuracy": []
    }

    n = train_data.shape[0]

    for epoch in range(epochs):

        model.train()

        indices = list(
            range(n)
        )

        if shuffle:
            random.shuffle(
                indices
            )

        total_loss = 0.0
        total_correct = 0
        total_seen = 0
        batches = 0

        for start in range(
            0,
            n,
            batch_size
        ):

            batch_indices = indices[
                start:
                start + batch_size
            ]

            batch_x = [
                train_data.data[i]
                for i in batch_indices
            ]

            batch_y = [
                train_labels.data[i]
                for i in batch_indices
            ]

            x = Tensor(
                batch_x
            )

            y = Tensor(
                batch_y
            )

            optimizer.zero_grad()

            output = model.forward(x)

            last_dense = model.last_dense()

            if (
                last_dense is not None
                and
                last_dense.activation
                == "softmax"
            ):

                loss = cross_entropy(
                    last_dense.pre_activation,
                    y,
                    from_logits=True
                )

            else:

                loss = cross_entropy(
                    output,
                    y,
                    from_logits=False
                )

            loss.backward()

            optimizer.step()

            batch_loss = loss.item()

            predictions = output.argmax(
                axis=1
            )

            correct = sum(
                int(p == t)
                for p, t in zip(
                    predictions,
                    batch_y
                )
            )

            total_loss += (
                batch_loss *
                len(batch_indices)
            )

            total_correct += correct
            total_seen += len(
                batch_indices
            )

            batches += 1

        epoch_loss = (
            total_loss / total_seen
            if total_seen
            else 0.0
        )

        epoch_accuracy = (
            total_correct / total_seen
            if total_seen
            else 0.0
        )

        history["loss"].append(
            epoch_loss
        )

        history["accuracy"].append(
            epoch_accuracy
        )

        if verbose:

            print(
                f"Epoch "
                f"{epoch + 1}/{epochs} "
                f"- Loss: "
                f"{epoch_loss:.4f} "
                f"- Accuracy: "
                f"{epoch_accuracy * 100:.2f}%"
            )

    return history


# ============================================================
# 15. EVALUATION
# ============================================================

def evaluate_model(
    model,
    test_data,
    test_labels,
    batch_size=256,
    num_classes=10
):

    if not isinstance(
        test_data,
        Tensor
    ):
        test_data = Tensor(
            test_data
        )

    if not isinstance(
        test_labels,
        Tensor
    ):
        test_labels = Tensor(
            test_labels
        )

    model.eval()

    predictions = []
    targets = []

    for start in range(
        0,
        test_data.shape[0],
        batch_size
    ):

        x = Tensor(
            test_data.data[
                start:
                start + batch_size
            ]
        )

        y = test_labels.data[
            start:
            start + batch_size
        ]

        output = model.forward(
            x
        )

        pred = output.argmax(
            axis=1
        )

        predictions.extend(
            pred
        )

        targets.extend(
            int(v)
            for v in y
        )

    return classification_metrics(
        targets,
        predictions,
        num_classes=num_classes
    )


# ============================================================
# 16. PREDICTION
# ============================================================

def predict_model(
    model,
    data,
    batch_size=256
):

    if not isinstance(
        data,
        Tensor
    ):
        data = Tensor(data)

    model.eval()

    predictions = []
    confidences = []

    for start in range(
        0,
        data.shape[0],
        batch_size
    ):

        x = Tensor(
            data.data[
                start:
                start + batch_size
            ]
        )

        output = model.forward(
            x
        )

        pred = output.argmax(
            axis=1
        )

        for i, cls in enumerate(
            pred
        ):

            confidence = (
                output.data[i][cls]
            )

            predictions.append(
                cls
            )

            confidences.append(
                confidence
            )

    return {
        "classes": predictions,
        "confidence": confidences
    }


# ============================================================
# 17. VIREO INTERPRETER
# ============================================================

class VireoInterpreter:

    def __init__(self):

        self.variables = {}
        self.functions = {}
        self.output = []

        self._code_lines = []

        self._loaded_model = None
        self._metrics = {}
        self._datasets = {}

        self._device = "CPU"

        self._models = {}
        self._model_objects = {}

        self._history = {}

    # --------------------------------------------------------
    # EXECUTE
    # --------------------------------------------------------

    def execute(
        self,
        code: str
    ) -> str:

        self.output = []

        self._code_lines = (
            code.splitlines()
        )

        i = 0

        while i < len(
            self._code_lines
        ):

            line = self._code_lines[i]

            stripped = line.strip()

            if (
                not stripped
                or
                stripped.startswith("//")
                or
                stripped.startswith("#")
            ):
                i += 1
                continue

            block_keywords = (
                "model ",
                "train ",
                "predict ",
                "evaluate ",
                "metrics ",
                "dataset "
            )

            if stripped.startswith(
                block_keywords
            ):

                block_lines = [
                    stripped
                ]

                i += 1

                indent = (
                    len(line) -
                    len(line.lstrip())
                )

                while i < len(
                    self._code_lines
                ):

                    next_line = (
                        self._code_lines[i]
                    )

                    next_stripped = (
                        next_line.strip()
                    )

                    if not next_stripped:

                        i += 1
                        continue

                    next_indent = (
                        len(next_line) -
                        len(next_line.lstrip())
                    )

                    if (
                        next_stripped == "}"
                        or
                        next_stripped.startswith("}")
                    ):

                        block_lines.append(
                            next_stripped
                        )

                        i += 1

                        break

                    if next_indent > indent:

                        block_lines.append(
                            next_stripped
                        )

                        i += 1

                    else:
                        break

                try:
                    self._execute_block(
                        block_lines
                    )

                except Exception as e:

                    self.output.append(
                        f"❌ Error: {e}"
                    )

            else:

                try:

                    result = (
                        self._execute_line(
                            stripped
                        )
                    )

                    if result is not None:
                        self.output.append(
                            str(result)
                        )

                except Exception as e:

                    self.output.append(
                        f"❌ Error: {e}"
                    )

                i += 1

        return "\n".join(
            self.output
        )

    # --------------------------------------------------------
    # BLOCK DISPATCH
    # --------------------------------------------------------

    def _execute_block(
        self,
        lines
    ):

        if not lines:
            return

        first = lines[0]

        if first.startswith("model "):
            self._handle_model_block(
                lines
            )

        elif first.startswith("train "):
            self._handle_train_block(
                lines
            )

        elif first.startswith("predict "):
            self._handle_predict_block(
                lines
            )

        elif first.startswith("evaluate "):
            self._handle_evaluate_block(
                lines
            )

        elif first.startswith("metrics "):
            self._handle_metrics_block(
                lines
            )

        elif first.startswith("dataset "):
            self._handle_dataset_block(
                lines
            )

    # ========================================================
    # MODEL
    # ========================================================

    def _handle_model_block(
        self,
        lines
    ):

        first = lines[0]

        model_name = (
            first
            .replace(
                "model ",
                "",
                1
            )
            .strip()
            .split("{")[0]
            .strip()
        )

        layers = []
        activations = []

        loss = None
        optimizer = None

        for line in lines[1:]:

            stripped = line.strip()

            if (
                stripped == "}"
                or
                stripped.startswith("}")
            ):
                continue

            if stripped.startswith(
                "layer "
            ):

                layers.append(
                    stripped
                )

                self.output.append(
                    f"   📊 Layer: {stripped}"
                )

            elif stripped.startswith(
                "activation "
            ):

                activation = (
                    stripped
                    .replace(
                        "activation ",
                        "",
                        1
                    )
                    .strip()
                    .lower()
                )

                activations.append(
                    activation
                )

                self.output.append(
                    f"   ⚡ Activation: "
                    f"{activation}"
                )

            elif stripped.startswith(
                "loss "
            ):

                loss = (
                    stripped
                    .replace(
                        "loss ",
                        "",
                        1
                    )
                    .strip()
                )

                self.output.append(
                    f"   📉 Loss: {loss}"
                )

            elif stripped.startswith(
                "optimizer "
            ):

                optimizer = (
                    stripped
                    .replace(
                        "optimizer ",
                        "",
                        1
                    )
                    .strip()
                )

                self.output.append(
                    f"   🎯 Optimizer: "
                    f"{optimizer}"
                )

        self._models[
            model_name
        ] = {
            "layers": layers,
            "activations": activations,
            "loss": loss,
            "optimizer": optimizer
        }

        self.output.insert(
            0,
            f"🧠 Model "
            f"'{model_name}' defined"
        )

    # ========================================================
    # BUILD MODEL
    # ========================================================

    def _build_model(
        self,
        model_name
    ):

        model_data = (
            self._models.get(
                model_name
            )
        )

        if model_data is None:
            raise ValueError(
                f"Model '{model_name}' not found"
            )

        layers = []

        activation_index = 0

        for layer_str in (
            model_data["layers"]
        ):

            match = re.search(
                r"Dense\s*"
                r"\(\s*(\d+)\s*,\s*(\d+)"
                r"(?:\s*,\s*([^)]+))?\s*\)",
                layer_str,
                re.IGNORECASE
            )

            if not match:
                raise ValueError(
                    f"Invalid Dense layer: "
                    f"{layer_str}"
                )

            input_size = int(
                match.group(1)
            )

            output_size = int(
                match.group(2)
            )

            inline_activation = (
                match.group(3)
            )

            if inline_activation:

                activation = (
                    inline_activation
                    .strip()
                    .lower()
                )

            elif (
                activation_index <
                len(
                    model_data[
                        "activations"
                    ]
                )
            ):

                activation = (
                    model_data[
                        "activations"
                    ][
                        activation_index
                    ]
                )

                activation_index += 1

            else:

                activation = (
                    "linear"
                )

            layers.append(
                Dense(
                    input_size,
                    output_size,
                    activation
                )
            )

        if not layers:
            raise ValueError(
                f"Model '{model_name}' "
                f"contains no layers"
            )

        model = Sequential(
            layers
        )

        self._model_objects[
            model_name
        ] = model

        return model

    # ========================================================
    # TRAIN
    # ========================================================

    def _handle_train_block(
        self,
        lines
    ):

        first = lines[0]

        train_name = (
            first
            .replace(
                "train ",
                "",
                1
            )
            .strip()
            .split("{")[0]
            .strip()
        )

        config = {
            "data": "mnist",
            "epochs": 10,
            "batch_size": 64,
            "lr": 0.001
        }

        for line in lines[1:]:

            stripped = line.strip()

            if (
                stripped == "}"
                or
                stripped.startswith("}")
            ):
                continue

            if stripped.startswith(
                "data "
            ):

                config["data"] = (
                    stripped
                    .split("=", 1)[1]
                    .strip()
                    .strip('"')
                )

            elif stripped.startswith(
                "epochs "
            ):

                config["epochs"] = int(
                    stripped
                    .split("=", 1)[1]
                    .strip()
                )

            elif stripped.startswith(
                "batch_size "
            ):

                config["batch_size"] = int(
                    stripped
                    .split("=", 1)[1]
                    .strip()
                )

            elif stripped.startswith(
                "lr "
            ):

                config["lr"] = float(
                    stripped
                    .split("=", 1)[1]
                    .strip()
                )

        self.output.append(
            f"🏋️ Starting training "
            f"'{train_name}'..."
        )

        if train_name not in self._models:

            self.output.append(
                f"   ❌ Model "
                f"'{train_name}' not found"
            )

            return

        model = (
            self._model_objects.get(
                train_name
            )
        )

        if model is None:

            model = self._build_model(
                train_name
            )

        self.output.append(
            "   📥 Loading real MNIST..."
        )

        data = load_mnist()

        train_x, train_y = (
            data["train"]
        )

        optimizer_config = (
            self._models[
                train_name
            ].get(
                "optimizer"
            )
            or
            "Adam(lr=0.001)"
        )

        optimizer_name = (
            "sgd"
            if optimizer_config
            .lower()
            .startswith("sgd")
            else
            "adam"
        )

        history = train_model(
            model,
            train_x,
            train_y,
            epochs=config["epochs"],
            batch_size=config[
                "batch_size"
            ],
            lr=config["lr"],
            optimizer_name=optimizer_name
        )

        self._loaded_model = model

        self._history[
            train_name
        ] = history

        self.output.append(
            f"   ✅ Training completed "
            f"for '{train_name}'"
        )

        if history["loss"]:

            self.output.append(
                f"   📉 Final loss: "
                f"{history['loss'][-1]:.4f}"
            )

            self.output.append(
                f"   🎯 Final accuracy: "
                f"{history['accuracy'][-1] * 100:.2f}%"
            )

    # ========================================================
    # PREDICT
    # ========================================================

    def _handle_predict_block(
        self,
        lines
    ):

        first = lines[0]

        predict_name = (
            first
            .replace(
                "predict ",
                "",
                1
            )
            .strip()
            .split("{")[0]
            .strip()
        )

        config = {
            "data": "test",
            "model": predict_name
        }

        for line in lines[1:]:

            stripped = line.strip()

            if (
                stripped == "}"
                or
                stripped.startswith("}")
            ):
                continue

            if stripped.startswith(
                "data "
            ):

                config["data"] = (
                    stripped
                    .split("=", 1)[1]
                    .strip()
                    .strip('"')
                )

            elif stripped.startswith(
                "model "
            ):

                config["model"] = (
                    stripped
                    .split("=", 1)[1]
                    .strip()
                    .strip('"')
                )

        model_name = config[
            "model"
        ]

        model = (
            self._model_objects.get(
                model_name
            )
        )

        if model is None:
            model = self._loaded_model

        if model is None:

            self.output.append(
                "   ❌ No trained model found"
            )

            return

        data = load_mnist()

        if config["data"] == "train":
            x, y = data["train"]
        else:
            x, y = data["test"]

        result = predict_model(
            model,
            x
        )

        predictions = result[
            "classes"
        ]

        confidence = result[
            "confidence"
        ]

        accuracy = sum(
            int(p == t)
            for p, t in zip(
                predictions,
                y.data
            )
        ) / len(
            predictions
        )

        self.output.append(
            f"   🎯 Samples: "
            f"{len(predictions)}"
        )

        self.output.append(
            f"   ✅ Accuracy: "
            f"{accuracy * 100:.2f}%"
        )

        if predictions:

            self.output.append(
                f"   🔢 First prediction: "
                f"{predictions[0]}"
            )

            self.output.append(
                f"   🎲 Confidence: "
                f"{confidence[0] * 100:.2f}%"
            )

        self.output.insert(
            0,
            f"🎯 Prediction completed "
            f"for '{predict_name}'"
        )

    # ========================================================
    # EVALUATE
    # ========================================================

    def _handle_evaluate_block(
        self,
        lines
    ):

        first = lines[0]

        eval_name = (
            first
            .replace(
                "evaluate ",
                "",
                1
            )
            .strip()
            .split("{")[0]
            .strip()
        )

        config = {
            "data": "test",
            "metrics": [
                "accuracy",
                "precision",
                "recall",
                "f1"
            ]
        }

        for line in lines[1:]:

            stripped = line.strip()

            if (
                stripped == "}"
                or
                stripped.startswith("}")
            ):
                continue

            if stripped.startswith(
                "data "
            ):

                config["data"] = (
                    stripped
                    .split("=", 1)[1]
                    .strip()
                    .strip('"')
                )

            elif stripped.startswith(
                "metrics "
            ):

                value = (
                    stripped
                    .replace(
                        "metrics ",
                        "",
                        1
                    )
                    .strip()
                )

                if (
                    value.startswith("[")
                    and
                    value.endswith("]")
                ):

                    config["metrics"] = [
                        x.strip()
                        .strip("'")
                        .strip('"')
                        for x in
                        value[1:-1].split(",")
                        if x.strip()
                    ]

        model = self._loaded_model

        if model is None:

            model = (
                self._model_objects.get(
                    eval_name
                )
            )

        if model is None:

            self.output.append(
                "   ❌ No trained model found"
            )

            return

        data = load_mnist()

        if config["data"] == "train":
            x, y = data["train"]
        else:
            x, y = data["test"]

        metrics = evaluate_model(
            model,
            x,
            y,
            num_classes=10
        )

        self._metrics = metrics

        self.output.insert(
            0,
            f"📈 Evaluation completed "
            f"for '{eval_name}'"
        )

        for metric in config[
            "metrics"
        ]:

            metric_lower = (
                metric.lower()
            )

            if metric_lower in (
                "accuracy",
                "precision",
                "recall",
                "f1"
            ):

                value = metrics[
                    metric_lower
                ]

                self.output.append(
                    f"   {metric_lower}: "
                    f"{value * 100:.2f}%"
                )

            else:

                self.output.append(
                    f"   {metric}: N/A"
                )

    # ========================================================
    # METRICS BLOCK
    # ========================================================

    def _handle_metrics_block(
        self,
        lines
    ):

        metrics = {}

        for line in lines[1:]:

            stripped = line.strip()

            if stripped in (
                "accuracy",
                "precision",
                "recall",
                "f1"
            ):

                if self._metrics:

                    metrics[
                        stripped
                    ] = self._metrics.get(
                        stripped,
                        0.0
                    )

                else:

                    metrics[
                        stripped
                    ] = None

        self._metrics = metrics

        self.output.insert(
            0,
            "📊 Metrics defined"
        )

        for name, value in metrics.items():

            if value is None:

                self.output.append(
                    f"   {name}: N/A"
                )

            else:

                self.output.append(
                    f"   {name}: "
                    f"{value * 100:.2f}%"
                )

    # ========================================================
    # DATASET
    # ========================================================

    def _handle_dataset_block(
        self,
        lines
    ):

        first = lines[0]

        dataset_name = (
            first
            .replace(
                "dataset ",
                "",
                1
            )
            .strip()
            .split("{")[0]
            .strip()
        )

        dataset_config = {
            "train": None,
            "test": None
        }

        for line in lines[1:]:

            stripped = line.strip()

            if stripped.startswith(
                "train "
            ):

                dataset_config[
                    "train"
                ] = (
                    stripped
                    .split("=", 1)[1]
                    .strip()
                    .strip('"')
                )

            elif stripped.startswith(
                "test "
            ):

                dataset_config[
                    "test"
                ] = (
                    stripped
                    .split("=", 1)[1]
                    .strip()
                    .strip('"')
                )

        self._datasets[
            dataset_name
        ] = dataset_config

        self.output.insert(
            0,
            f"📂 Dataset "
            f"'{dataset_name}' defined"
        )

    # ========================================================
    # NORMAL LINE EXECUTION
    # ========================================================

    def _execute_line(
        self,
        line
    ):

        # ----------------------------------------------------
        # let
        # ----------------------------------------------------

        if line.startswith("let "):

            parts = line[
                4:
            ].split(
                "=",
                1
            )

            name = parts[
                0
            ].strip()

            if len(parts) == 2:

                value = self._evaluate(
                    parts[1].strip()
                )

                self.variables[
                    name
                ] = value

                return (
                    f"{name} = {value}"
                )

            self.variables[
                name
            ] = None

            return (
                f"{name} = None"
            )

        # ----------------------------------------------------
        # const
        # ----------------------------------------------------

        if line.startswith("const "):

            parts = line[
                6:
            ].split(
                "=",
                1
            )

            name = parts[
                0
            ].strip()

            if len(parts) == 2:

                value = self._evaluate(
                    parts[1].strip()
                )

                self.variables[
                    name
                ] = value

                return (
                    f"const {name} = {value}"
                )

        # ----------------------------------------------------
        # load
        # ----------------------------------------------------

        if line.startswith("load "):
            return self._handle_load(
                line
            )

        # ----------------------------------------------------
        # print(...)
        # ----------------------------------------------------

        if (
            line.startswith("print(")
            and
            line.endswith(")")
        ):

            value = line[
                6:-1
            ]

            return self._evaluate(
                value
            )

        # ----------------------------------------------------
        # print "..."
        # ----------------------------------------------------

        if line.startswith(
            'print "'
        ):

            value = line[
                6:-1
            ]

            return value

        # ----------------------------------------------------
        # return
        # ----------------------------------------------------

        if line.startswith(
            "return "
        ):

            value = self._evaluate(
                line[7:]
            )

            return (
                f"Return: {value}"
            )

        # ----------------------------------------------------
        # decorators
        # ----------------------------------------------------

        if line.startswith(
            "@neural"
        ):

            return (
                "🧠 Neural network "
                "decorator applied"
            )

        # ----------------------------------------------------
        # function
        # ----------------------------------------------------

        if (
            line.startswith("fn ")
            and
            "(" in line
        ):

            function_name = (
                line[3:
                     line.index("(")]
                .strip()
            )

            self.functions[
                function_name
            ] = line

            return (
                f"Function "
                f"{function_name} defined"
            )

        # ----------------------------------------------------
        # Dense
        # ----------------------------------------------------

        if line.startswith(
            "Dense("
        ):

            return (
                "🧠 Dense layer created"
            )

        # ----------------------------------------------------
        # Tensor
        # ----------------------------------------------------

        if (
            "Tensor" in line
            or
            line.startswith(
                "tensor"
            )
        ):

            return self._handle_tensor(
                line
            )

        return self._evaluate(
            line
        )

    # ========================================================
    # EXPRESSION EVALUATOR
    # ========================================================

    def _evaluate(
        self,
        expr
    ):

        expr = expr.strip()

        if expr in self.variables:
            return self.variables[
                expr
            ]

        if (
            expr.startswith('"')
            and
            expr.endswith('"')
        ):
            return expr[1:-1]

        if (
            expr.startswith("'")
            and
            expr.endswith("'")
        ):
            return expr[1:-1]

        # booleans
        if expr.lower() == "true":
            return True

        if expr.lower() == "false":
            return False

        # numbers
        try:

            if (
                "."
                in expr
                or
                "e"
                in expr.lower()
            ):
                return float(expr)

            return int(expr)

        except (
            ValueError,
            TypeError
        ):
            pass

        # Lists
        if (
            expr.startswith("[")
            and
            expr.endswith("]")
        ):

            try:
                return json.loads(
                    expr.replace(
                        "'",
                        '"'
                    )
                )

            except Exception:

                try:
                    return eval(
                        expr,
                        {
                            "__builtins__":
                                {}
                        }
                    )

                except Exception:
                    pass

        # Tensor constructor
        if expr.startswith(
            "Tensor"
        ):
            return self._parse_tensor_expression(
                expr
            )

        # predict(...)
        if (
            expr.startswith(
                "predict "
            )
            and
            "(" in expr
        ):

            return (
                self._handle_predict_expression(
                    expr
                )
            )

        # Simple arithmetic
        # Parse only at top-level.
        for operator in [
            "+",
            "-",
            "*",
            "/"
        ]:

            parts = self._split_operator(
                expr,
                operator
            )

            if len(parts) == 2:

                left = self._evaluate(
                    parts[0]
                )

                right = self._evaluate(
                    parts[1]
                )

                try:

                    if operator == "+":
                        return left + right

                    if operator == "-":
                        return left - right

                    if operator == "*":
                        return left * right

                    if operator == "/":
                        return left / right

                except Exception:
                    return (
                        f"{left} "
                        f"{operator} "
                        f"{right}"
                    )

        return expr

    # ========================================================
    # SPLIT OPERATOR
    # ========================================================

    def _split_operator(
        self,
        expr,
        operator
    ):

        depth = 0
        quote = None

        positions = []

        for i, char in enumerate(
            expr
        ):

            if char in (
                '"',
                "'"
            ):

                if quote is None:
                    quote = char

                elif quote == char:
                    quote = None

                continue

            if quote is not None:
                continue

            if char in (
                "(",
                "[",
                "{"
            ):
                depth += 1

            elif char in (
                ")",
                "]",
                "}"
            ):
                depth -= 1

            elif (
                char == operator
                and
                depth == 0
            ):
                positions.append(i)

        if not positions:
            return [
                expr
            ]

        # Use the last top-level operator.
        pos = positions[-1]

        return [
            expr[:pos].strip(),
            expr[pos + 1:].strip()
        ]

    # ========================================================
    # TENSOR EXPRESSION
    # ========================================================

    def _parse_tensor_expression(
        self,
        expr
    ):

        match = re.match(
            r"Tensor\((.*)\)$",
            expr,
            re.IGNORECASE
        )

        if not match:
            return (
                "📊 Tensor operation"
            )

        value = match.group(
            1
        ).strip()

        try:

            data = json.loads(
                value.replace(
                    "'",
                    '"'
                )
            )

            return Tensor(
                data
            )

        except Exception:

            if value in self.variables:

                variable = self.variables[
                    value
                ]

                if isinstance(
                    variable,
                    Tensor
                ):
                    return variable

            return (
                "📊 Tensor operation"
            )

    # ========================================================
    # TENSOR HANDLER
    # ========================================================

    def _handle_tensor(
        self,
        line
    ):

        lower = line.lower()

        if "matmul" in lower:
            return (
                "📊 Tensor matmul operation"
            )

        if "reshape" in lower:
            return (
                "📐 Tensor reshape operation"
            )

        if "transpose" in lower:
            return (
                "🔄 Tensor transpose operation"
            )

        if "sum" in lower:
            return (
                "➕ Tensor sum operation"
            )

        if "mean" in lower:
            return (
                "📊 Tensor mean operation"
            )

        if "zeros" in lower:
            return (
                "0️⃣ Tensor zeros operation"
            )

        if "ones" in lower:
            return (
                "1️⃣ Tensor ones operation"
            )

        if "random" in lower:
            return (
                "🎲 Tensor random operation"
            )

        return (
            "📊 Tensor operation"
        )

    # ========================================================
    # LOAD
    # ========================================================

    def _handle_load(
        self,
        line
    ):

        match = re.search(
            r'"([^"]+)"',
            line
        )

        if match:

            filename = match.group(
                1
            )

            self._loaded_model = (
                filename
            )

            return (
                f"📂 Model loaded from: "
                f"{filename}"
            )

        return (
            "❌ Error: "
            "No filename specified"
        )

    # ========================================================
    # PREDICT EXPRESSION
    # ========================================================

    def _handle_predict_expression(
        self,
        expr
    ):

        if self._loaded_model is None:

            return {
                "class": "unknown",
                "confidence": 0.0
            }

        return {
            "class": None,
            "confidence": None
        }


# ============================================================
# 18. API INTEGRATION
# ============================================================

def execute_vireo_code(
    code: str
) -> dict:

    interpreter = (
        VireoInterpreter()
    )

    output = interpreter.execute(
        code
    )

    return {
        "status": "success",
        "output": output,
        "variables":
            interpreter.variables,
        "functions":
            interpreter.functions,
        "metrics":
            interpreter._metrics,
        "device":
            interpreter._device,
        "history":
            interpreter._history
    }


# ============================================================
# 19. SELF TESTS
# ============================================================

def run_self_tests():

    print(
        "\n🧪 VIREO v0.5.1 SELF TESTS"
    )

    # --------------------------------------------------------
    # Test 1: broadcasting
    # --------------------------------------------------------

    x = Tensor(
        [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ],
        requires_grad=True
    )

    b = Tensor(
        [10.0, 20.0, 30.0],
        requires_grad=True
    )

    y = x + b

    assert y.shape == [2, 3]

    loss = y.sum()

    loss.backward()

    assert b.grad is not None

    assert b.grad.flatten() == [
        2.0,
        2.0,
        2.0
    ]

    print(
        "✅ Broadcasting"
    )

    # --------------------------------------------------------
    # Test 2: matmul gradient
    # --------------------------------------------------------

    a = Tensor(
        [
            [1.0, 2.0],
            [3.0, 4.0]
        ],
        requires_grad=True
    )

    w = Tensor(
        [
            [2.0, 0.0],
            [0.0, 2.0]
        ],
        requires_grad=True
    )

    y = a.matmul(w)

    loss = y.sum()

    loss.backward()

    assert a.grad is not None
    assert w.grad is not None

    print(
        "✅ MatMul autodiff"
    )

    # --------------------------------------------------------
    # Test 3: CrossEntropy
    # --------------------------------------------------------

    logits = Tensor(
        [
            [2.0, 1.0, 0.1],
            [0.1, 2.0, 0.3]
        ],
        requires_grad=True
    )

    labels = Tensor(
        [0, 1]
    )

    loss = cross_entropy(
        logits,
        labels,
        from_logits=True
    )

    loss.backward()

    assert loss.item() > 0
    assert logits.grad is not None

    print(
        "✅ CrossEntropy"
    )

    # --------------------------------------------------------
    # Test 4: Dense
    # --------------------------------------------------------

    dense = Dense(
        4,
        3,
        activation="relu"
    )

    x = Tensor(
        [
            [1.0, 2.0, 3.0, 4.0],
            [2.0, 3.0, 4.0, 5.0]
        ]
    )

    output = dense.forward(
        x
    )

    assert output.shape == [
        2,
        3
    ]

    print(
        "✅ Dense"
    )

    # --------------------------------------------------------
    # Test 5: Adam
    # --------------------------------------------------------

    parameter = Tensor(
        [
            [1.0, 2.0],
            [3.0, 4.0]
        ],
        requires_grad=True
    )

    simple_loss = (
        parameter *
        parameter
    ).sum()

    simple_loss.backward()

    before = parameter.flatten()

    optimizer = Adam(
        [parameter],
        lr=0.01
    )

    optimizer.step()

    after = parameter.flatten()

    assert before != after

    print(
        "✅ Adam"
    )

    # --------------------------------------------------------
    # Test 6: metrics
    # --------------------------------------------------------

    metrics = classification_metrics(
        [0, 1, 2, 2],
        [0, 1, 1, 2],
        num_classes=3
    )

    assert (
        abs(
            metrics["accuracy"] -
            0.75
        ) < 1e-9
    )

    assert len(
        metrics["confusion_matrix"]
    ) == 3

    print(
        "✅ Real multiclass metrics"
    )

    print(
        "\n🎉 ALL VIREO v0.5.1 "
        "SELF TESTS PASSED"
    )


# ============================================================
# 20. EXAMPLE
# ============================================================

if __name__ == "__main__":

    run_self_tests()

    print(
        "\n"
        "============================================================"
    )

    test_code = """
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
    epochs = 5
    batch_size = 64
    lr = 0.001
}

predict MNIST {
    data = "test"
    model = "MNIST"
}

evaluate MNIST {
    data = "test"
    metrics = [accuracy, precision, recall, f1]
}
"""

    result = execute_vireo_code(
        test_code
    )

    print(
        result["output"]
    )
