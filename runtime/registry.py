# ============================================================
# VIREO RUNTIME REGISTRY
# Реєстрація компонентів
# ============================================================

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Type, Callable, List, Tuple
import threading
import logging

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Типи компонентів."""
    EXECUTOR = "executor"
    CONTEXT = "context"
    JIT = "jit"
    GPU = "gpu"
    WASM = "wasm"
    EDGE = "edge"
    AGENT = "agent"
    PROTOCOL = "protocol"
    TRANSPORT = "transport"
    CRYPTO = "crypto"
    STORAGE = "storage"
    CUSTOM = "custom"


@dataclass
class ComponentInfo:
    """Інформація про компонент."""
    name: str
    type: ComponentType
    version: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    instance: Optional[Any] = None
    factory: Optional[Callable] = None
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "enabled": self.enabled,
        }


class Registry:
    """
    Реєстр компонентів Vireo.
    
    Підтримує:
    - Реєстрацію компонентів
    - Отримання компонентів
    - Залежності
    - Життєвий цикл
    """
    
    def __init__(self):
        self._components: Dict[str, ComponentInfo] = {}
        self._instances: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(f"{__name__}.Registry")
    
    def register(
        self,
        name: str,
        component_type: ComponentType,
        instance: Optional[Any] = None,
        factory: Optional[Callable] = None,
        version: str = "1.0.0",
        description: str = "",
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Реєструє компонент.
        
        Args:
            name: Ім'я компонента
            component_type: Тип компонента
            instance: Екземпляр компонента
            factory: Фабрика для створення
            version: Версія
            description: Опис
            dependencies: Залежності
            metadata: Метадані
        """
        with self._lock:
            if name in self._components:
                self._logger.warning(f"Component '{name}' already registered, overwriting")
            
            info = ComponentInfo(
                name=name,
                type=component_type,
                version=version,
                description=description,
                dependencies=dependencies or [],
                metadata=metadata or {},
                instance=instance,
                factory=factory,
                enabled=True,
            )
            
            self._components[name] = info
            
            if instance is not None:
                self._instances[name] = instance
                self._logger.info(f"Component '{name}' registered with instance")
            elif factory is not None:
                self._logger.info(f"Component '{name}' registered with factory")
            else:
                self._logger.info(f"Component '{name}' registered (lazy)")
    
    def register_instance(
        self,
        name: str,
        instance: Any,
        component_type: ComponentType = ComponentType.CUSTOM,
        version: str = "1.0.0",
        description: str = "",
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Реєструє екземпляр компонента."""
        self.register(
            name=name,
            component_type=component_type,
            instance=instance,
            version=version,
            description=description,
            dependencies=dependencies,
            metadata=metadata,
        )
    
    def register_factory(
        self,
        name: str,
        factory: Callable,
        component_type: ComponentType = ComponentType.CUSTOM,
        version: str = "1.0.0",
        description: str = "",
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Реєструє фабрику компонента."""
        self.register(
            name=name,
            component_type=component_type,
            factory=factory,
            version=version,
            description=description,
            dependencies=dependencies,
            metadata=metadata,
        )
    
    def get(self, name: str, auto_init: bool = True) -> Optional[Any]:
        """
        Отримує компонент.
        
        Args:
            name: Ім'я компонента
            auto_init: Автоматично ініціалізувати
            
        Returns:
            Any: Екземпляр компонента або None
        """
        with self._lock:
            # Перевіряємо чи вже створено
            if name in self._instances:
                return self._instances[name]
            
            # Отримуємо інформацію
            info = self._components.get(name)
            if info is None:
                self._logger.error(f"Component '{name}' not found")
                return None
            
            if not info.enabled:
                self._logger.warning(f"Component '{name}' is disabled")
                return None
            
            if auto_init:
                return self._init_component(name)
            
            return None
    
    def _init_component(self, name: str) -> Any:
        """Ініціалізує компонент."""
        info = self._components.get(name)
        if info is None:
            return None
        
        # Перевіряємо залежності
        for dep in info.dependencies:
            if dep not in self._instances:
                self._logger.info(f"Initializing dependency: {dep}")
                self._init_component(dep)
        
        # Створюємо екземпляр
        if info.instance is not None:
            instance = info.instance
        elif info.factory is not None:
            try:
                instance = info.factory()
            except Exception as e:
                self._logger.error(f"Failed to create component '{name}': {e}")
                return None
        else:
            self._logger.error(f"No instance or factory for component '{name}'")
            return None
        
        self._instances[name] = instance
        self._logger.info(f"Component '{name}' initialized")
        return instance
    
    def get_info(self, name: str) -> Optional[ComponentInfo]:
        """Отримує інформацію про компонент."""
        with self._lock:
            return self._components.get(name)
    
    def list_components(self, component_type: Optional[ComponentType] = None) -> List[ComponentInfo]:
        """Список зареєстрованих компонентів."""
        with self._lock:
            if component_type is None:
                return list(self._components.values())
            return [c for c in self._components.values() if c.type == component_type]
    
    def list_names(self) -> List[str]:
        """Список імен компонентів."""
        with self._lock:
            return list(self._components.keys())
    
    def unregister(self, name: str) -> bool:
        """Видаляє компонент."""
        with self._lock:
            if name in self._components:
                del self._components[name]
                if name in self._instances:
                    del self._instances[name]
                self._logger.info(f"Component '{name}' unregistered")
                return True
            return False
    
    def enable(self, name: str) -> bool:
        """Вмикає компонент."""
        with self._lock:
            info = self._components.get(name)
            if info is None:
                return False
            info.enabled = True
            self._logger.info(f"Component '{name}' enabled")
            return True
    
    def disable(self, name: str) -> bool:
        """Вимикає компонент."""
        with self._lock:
            info = self._components.get(name)
            if info is None:
                return False
            info.enabled = False
            if name in self._instances:
                del self._instances[name]
            self._logger.info(f"Component '{name}' disabled")
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримує статистику."""
        with self._lock:
            return {
                "total_components": len(self._components),
                "active_instances": len(self._instances),
                "enabled": sum(1 for c in self._components.values() if c.enabled),
                "disabled": sum(1 for c in self._components.values() if not c.enabled),
                "by_type": {
                    t.value: sum(1 for c in self._components.values() if c.type == t)
                    for t in ComponentType
                },
            }
    
    def clear(self) -> None:
        """Очищає реєстр."""
        with self._lock:
            self._components.clear()
            self._instances.clear()
            self._logger.info("Registry cleared")


# ============================================================
# ГЛОБАЛЬНИЙ РЕЄСТР
# ============================================================

_default_registry: Optional[Registry] = None


def get_registry() -> Registry:
    """Отримує глобальний реєстр."""
    global _default_registry
    if _default_registry is None:
        _default_registry = Registry()
    return _default_registry


def register_component(
    name: str,
    component_type: ComponentType,
    instance: Optional[Any] = None,
    factory: Optional[Callable] = None,
    version: str = "1.0.0",
    description: str = "",
    dependencies: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Реєструє компонент у глобальному реєстрі."""
    get_registry().register(
        name=name,
        component_type=component_type,
        instance=instance,
        factory=factory,
        version=version,
        description=description,
        dependencies=dependencies,
        metadata=metadata,
    )


def get_component(name: str, auto_init: bool = True) -> Optional[Any]:
    """Отримує компонент з глобального реєстру."""
    return get_registry().get(name, auto_init=auto_init)


def list_components(component_type: Optional[ComponentType] = None) -> List[ComponentInfo]:
    """Список компонентів з глобального реєстру."""
    return get_registry().list_components(component_type)