# ============================================================
# VIREO RUNTIME CONTEXT
# Управління контекстом виконання
# ============================================================

import threading
import time
from typing import Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass, field
from contextvars import ContextVar as ContextVarType
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RuntimeContext:
    """
    Контекст виконання Vireo.
    
    Містить:
    - Змінні контексту
    - Метадані
    - Налаштування
    - Статистику
    """
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    stats: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[float] = field(default_factory=time.time)
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = time.time()

    def get(self, key: str, default: Any = None) -> Any:
        """Отримує змінну контексту."""
        with self._lock:
            return self.variables.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Встановлює змінну контексту."""
        with self._lock:
            self.variables[key] = value
            logger.debug(f"Context variable set: {key} = {value}")

    def delete(self, key: str) -> bool:
        """Видаляє змінну контексту."""
        with self._lock:
            if key in self.variables:
                del self.variables[key]
                return True
            return False

    def has(self, key: str) -> bool:
        """Перевіряє наявність змінної."""
        with self._lock:
            return key in self.variables

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Отримує метадані."""
        with self._lock:
            return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        """Встановлює метадані."""
        with self._lock:
            self.metadata[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """Отримує налаштування."""
        with self._lock:
            return self.config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Встановлює налаштування."""
        with self._lock:
            self.config[key] = value

    def increment_stats(self, key: str, delta: int = 1) -> int:
        """Збільшує статистику."""
        with self._lock:
            current = self.stats.get(key, 0)
            self.stats[key] = current + delta
            return self.stats[key]

    def get_stats(self, key: str, default: Any = 0) -> Any:
        """Отримує статистику."""
        with self._lock:
            return self.stats.get(key, default)

    def get_elapsed(self) -> float:
        """Отримує час роботи."""
        return time.time() - self.start_time

    def snapshot(self) -> Dict[str, Any]:
        """Створює знімок контексту."""
        with self._lock:
            return {
                "variables": self.variables.copy(),
                "metadata": self.metadata.copy(),
                "config": self.config.copy(),
                "stats": self.stats.copy(),
                "elapsed": self.get_elapsed(),
            }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        """Відновлює контекст зі знімка."""
        with self._lock:
            self.variables = snapshot.get("variables", {}).copy()
            self.metadata = snapshot.get("metadata", {}).copy()
            self.config = snapshot.get("config", {}).copy()
            self.stats = snapshot.get("stats", {}).copy()

    def clear(self) -> None:
        """Очищає контекст."""
        with self._lock:
            self.variables.clear()
            self.metadata.clear()
            self.config.clear()
            self.stats.clear()
            self.start_time = time.time()

    def __repr__(self) -> str:
        return f"RuntimeContext(variables={len(self.variables)}, metadata={len(self.metadata)}, stats={len(self.stats)})"


class ContextVar(Generic[T]):
    """
    Безпечна змінна контексту.
    
    Використовує Python contextvars для потокобезпеки.
    """
    
    def __init__(self, name: str, default: Optional[T] = None):
        self._var = ContextVarType(name, default=default)
        self._name = name
    
    def get(self) -> T:
        """Отримує значення."""
        return self._var.get()
    
    def set(self, value: T) -> None:
        """Встановлює значення."""
        self._var.set(value)
    
    def reset(self, token) -> None:
        """Скидає значення."""
        self._var.reset(token)
    
    @property
    def name(self) -> str:
        return self._name


class ContextManager:
    """
    Менеджер контексту.
    
    Управляє глобальним і локальними контекстами.
    """
    
    def __init__(self):
        self._global_context = RuntimeContext()
        self._local_contexts: Dict[str, RuntimeContext] = {}
        self._lock = threading.RLock()
    
    def get_global(self) -> RuntimeContext:
        """Отримує глобальний контекст."""
        return self._global_context
    
    def create_local(self, name: str) -> RuntimeContext:
        """Створює локальний контекст."""
        with self._lock:
            context = RuntimeContext()
            self._local_contexts[name] = context
            logger.debug(f"Local context created: {name}")
            return context
    
    def get_local(self, name: str) -> Optional[RuntimeContext]:
        """Отримує локальний контекст."""
        with self._lock:
            return self._local_contexts.get(name)
    
    def delete_local(self, name: str) -> bool:
        """Видаляє локальний контекст."""
        with self._lock:
            if name in self._local_contexts:
                del self._local_contexts[name]
                logger.debug(f"Local context deleted: {name}")
                return True
            return False
    
    def list_locals(self) -> List[str]:
        """Список локальних контекстів."""
        with self._lock:
            return list(self._local_contexts.keys())
    
    def clear(self) -> None:
        """Очищає всі контексти."""
        with self._lock:
            self._global_context.clear()
            self._local_contexts.clear()


# ============================================================
# ГЛОБАЛЬНИЙ КОНТЕКСТ
# ============================================================

_default_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Отримує глобальний менеджер контексту."""
    global _default_context_manager
    if _default_context_manager is None:
        _default_context_manager = ContextManager()
    return _default_context_manager


def get_context() -> RuntimeContext:
    """Отримує глобальний контекст."""
    return get_context_manager().get_global()


def set_context(context: RuntimeContext) -> None:
    """Встановлює глобальний контекст."""
    get_context_manager()._global_context = context


def reset_context() -> None:
    """Скидає глобальний контекст."""
    get_context().clear()


def create_local_context(name: str) -> RuntimeContext:
    """Створює локальний контекст."""
    return get_context_manager().create_local(name)


def get_local_context(name: str) -> Optional[RuntimeContext]:
    """Отримує локальний контекст."""
    return get_context_manager().get_local(name)