# ============================================================
# VIREO WASM RUNTIME
# Виконання WebAssembly
# ============================================================

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
import logging

logger = logging.getLogger(__name__)

try:
    import wasmtime
    WASMTIME_AVAILABLE = True
except ImportError:
    WASMTIME_AVAILABLE = False
    logger.warning("wasmtime not installed. WASM features disabled.")


@dataclass
class WASMResult:
    """Результат виконання WASM."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    duration: float = 0.0
    memory_used: int = 0


class WASMModule:
    """WASM модуль."""
    
    def __init__(self, wasm_bytes: bytes):
        self.wasm_bytes = wasm_bytes
        self.module: Optional['wasmtime.Module'] = None
        self._loaded = False
        self._available = WASMTIME_AVAILABLE
    
    def load(self) -> bool:
        """Завантажує модуль."""
        if not self._available:
            return False
        
        if self._loaded:
            return True
        
        try:
            engine = wasmtime.Engine()
            self.module = wasmtime.Module(engine, self.wasm_bytes)
            self._loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load WASM module: {e}")
            return False
    
    def get_module(self):
        """Отримує wasmtime модуль."""
        if not self._loaded:
            self.load()
        return self.module
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded


class WASMInstance:
    """Екземпляр WASM модуля."""
    
    def __init__(self, module: WASMModule):
        self.module = module
        self.instance: Optional['wasmtime.Instance'] = None
        self._instantiated = False
        self._available = WASMTIME_AVAILABLE
    
    def instantiate(self, imports: Optional[Dict[str, Any]] = None) -> bool:
        """Створює екземпляр модуля."""
        if not self._available:
            return False
        
        if self._instantiated:
            return True
        
        if not self.module.is_loaded:
            self.module.load()
        
        try:
            wasm_module = self.module.get_module()
            engine = wasmtime.Engine()
            store = wasmtime.Store(engine)
            
            # Створюємо екземпляр
            self.instance = wasmtime.Instance(store, wasm_module, [])
            self._instantiated = True
            return True
        except Exception as e:
            logger.error(f"Failed to instantiate WASM: {e}")
            return False
    
    def call(self, func_name: str, *args) -> Optional[Any]:
        """Викликає функцію."""
        if not self._instantiated:
            if not self.instantiate():
                return None
        
        try:
            func = getattr(self.instance, func_name)
            return func(*args)
        except Exception as e:
            logger.error(f"Failed to call WASM function: {e}")
            return None
    
    @property
    def is_instantiated(self) -> bool:
        return self._instantiated


class WASMRuntime:
    """
    WASM виконавець.
    
    Виконує WASM модулі.
    """
    
    def __init__(self):
        self._modules: Dict[str, WASMModule] = {}
        self._instances: Dict[str, WASMInstance] = {}
        self._available = WASMTIME_AVAILABLE
        self._context = {}
    
    def load_module(self, name: str, wasm_bytes: bytes) -> bool:
        """Завантажує WASM модуль."""
        if name in self._modules:
            return True
        
        module = WASMModule(wasm_bytes)
        if module.load():
            self._modules[name] = module
            return True
        return False
    
    def instantiate(self, name: str, imports: Optional[Dict[str, Any]] = None) -> bool:
        """Створює екземпляр модуля."""
        if name not in self._modules:
            return False
        
        if name in self._instances:
            return True
        
        instance = WASMInstance(self._modules[name])
        if instance.instantiate(imports):
            self._instances[name] = instance
            return True
        return False
    
    def call(self, name: str, func_name: str, *args) -> Optional[Any]:
        """Викликає функцію в модулі."""
        if name not in self._instances:
            if not self.instantiate(name):
                return None
        
        return self._instances[name].call(func_name, *args)
    
    def is_available(self) -> bool:
        """Перевіряє доступність WASM."""
        return self._available