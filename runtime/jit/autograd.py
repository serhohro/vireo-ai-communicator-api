# ============================================================
# VIREO AUTOGRAD
# Автоматичне диференціювання
# ============================================================

from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field
import threading
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class Variable:
    """Змінна для автограда."""
    data: Any
    grad: Optional[Any] = None
    requires_grad: bool = False
    grad_fn: Optional['Function'] = None
    name: str = ""
    shape: Optional[List[int]] = None
    dtype: str = "float32"


class Function:
    """
    Базовий клас для функцій автограда.
    
    Визначає forward та backward прохід.
    """
    
    def __init__(self):
        self._saved_tensors: List[Variable] = []
        self._inputs: List[Variable] = []
        self._output: Optional[Variable] = None
    
    def forward(self, *inputs: Variable) -> Variable:
        """Прямий прохід."""
        raise NotImplementedError
    
    def backward(self, grad: Any) -> List[Any]:
        """Зворотний прохід."""
        raise NotImplementedError
    
    def save_for_backward(self, *tensors: Variable) -> None:
        """Зберігає тензори для зворотного проходу."""
        self._saved_tensors.extend(tensors)
    
    @property
    def saved_tensors(self) -> List[Variable]:
        return self._saved_tensors


class Add(Function):
    """Додавання."""
    
    def forward(self, a: Variable, b: Variable) -> Variable:
        self._inputs = [a, b]
        result = Variable(
            data=a.data + b.data,
            requires_grad=a.requires_grad or b.requires_grad,
            grad_fn=self if (a.requires_grad or b.requires_grad) else None,
        )
        return result
    
    def backward(self, grad: Any) -> List[Any]:
        return [grad, grad]


class Mul(Function):
    """Множення."""
    
    def forward(self, a: Variable, b: Variable) -> Variable:
        self._inputs = [a, b]
        self.save_for_backward(a, b)
        
        result = Variable(
            data=a.data * b.data,
            requires_grad=a.requires_grad or b.requires_grad,
            grad_fn=self if (a.requires_grad or b.requires_grad) else None,
        )
        return result
    
    def backward(self, grad: Any) -> List[Any]:
        a, b = self._saved_tensors
        return [grad * b.data, grad * a.data]


class MatMul(Function):
    """Матричне множення."""
    
    def forward(self, a: Variable, b: Variable) -> Variable:
        self._inputs = [a, b]
        self.save_for_backward(a, b)
        
        import numpy as np
        result = Variable(
            data=np.matmul(a.data, b.data),
            requires_grad=a.requires_grad or b.requires_grad,
            grad_fn=self if (a.requires_grad or b.requires_grad) else None,
        )
        return result
    
    def backward(self, grad: Any) -> List[Any]:
        import numpy as np
        a, b = self._saved_tensors
        grad_a = np.matmul(grad, b.data.T)
        grad_b = np.matmul(a.data.T, grad)
        return [grad_a, grad_b]


class ReLU(Function):
    """ReLU активація."""
    
    def forward(self, x: Variable) -> Variable:
        self._inputs = [x]
        self.save_for_backward(x)
        
        import numpy as np
        data = np.maximum(0, x.data)
        result = Variable(
            data=data,
            requires_grad=x.requires_grad,
            grad_fn=self if x.requires_grad else None,
        )
        return result
    
    def backward(self, grad: Any) -> List[Any]:
        import numpy as np
        x = self._saved_tensors[0]
        return [grad * (x.data > 0)]


class Sigmoid(Function):
    """Sigmoid активація."""
    
    def forward(self, x: Variable) -> Variable:
        self._inputs = [x]
        self.save_for_backward(x)
        
        import numpy as np
        data = 1 / (1 + np.exp(-x.data))
        result = Variable(
            data=data,
            requires_grad=x.requires_grad,
            grad_fn=self if x.requires_grad else None,
        )
        return result
    
    def backward(self, grad: Any) -> List[Any]:
        x = self._saved_tensors[0]
        import numpy as np
        sig = 1 / (1 + np.exp(-x.data))
        return [grad * sig * (1 - sig)]


class Autograd:
    """
    Система автоматичного диференціювання.
    
    Підтримує:
    - Прямий прохід
    - Зворотний прохід
    - Обчислення градієнтів
    - Граф обчислень
    """
    
    def __init__(self):
        self._enabled = True
        self._graph: List[Function] = []
        self._lock = threading.RLock()
    
    def enable(self) -> None:
        """Вмикає autograd."""
        with self._lock:
            self._enabled = True
    
    def disable(self) -> None:
        """Вимикає autograd."""
        with self._lock:
            self._enabled = False
    
    def is_enabled(self) -> bool:
        """Перевіряє чи включений autograd."""
        return self._enabled
    
    def record(self, fn: Function) -> None:
        """Записує функцію в граф."""
        if self._enabled:
            with self._lock:
                self._graph.append(fn)
    
    def backward(self, output: Variable) -> None:
        """
        Обчислює градієнти за допомогою зворотного проходу.
        
        Args:
            output: Вихідна змінна
        """
        if not output.requires_grad:
            return
        
        # Ініціалізуємо градієнт
        import numpy as np
        if output.grad is None:
            output.grad = np.ones_like(output.data)
        
        # Зворотний прохід
        grad = output.grad
        fn = output.grad_fn
        
        while fn is not None:
            grads = fn.backward(grad)
            
            # Оновлюємо градієнти для входів
            for i, input_var in enumerate(fn._inputs):
                if i < len(grads) and input_var.requires_grad:
                    if input_var.grad is None:
                        input_var.grad = grads[i]
                    else:
                        input_var.grad += grads[i]
            
            # Переходимо до наступної функції
            if fn._inputs and fn._inputs[0].grad_fn is not None:
                grad = fn._inputs[0].grad
                fn = fn._inputs[0].grad_fn
            else:
                fn = None
    
    def clear(self) -> None:
        """Очищає граф обчислень."""
        with self._lock:
            self._graph.clear()
    
    def get_graph(self) -> List[Function]:
        """Отримує граф обчислень."""
        with self._lock:
            return self._graph.copy()


# ============================================================
# ГЛОБАЛЬНИЙ АВТОГРАД
# ============================================================

_default_autograd: Optional[Autograd] = None


def get_autograd() -> Autograd:
    """Отримує глобальний автоград."""
    global _default_autograd
    if _default_autograd is None:
        _default_autograd = Autograd()
    return _default_autograd


def autograd_enabled() -> bool:
    """Перевіряє чи включений автоград."""
    return get_autograd().is_enabled()


# Класи для зручності
class Tensor(Variable):
    """Тензор з підтримкою автограда."""
    pass