# ============================================================
# LAYER 2 <-> LAYER 3 BRIDGE
# ============================================================

import logging
import time
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger("vireo.protocol.runtime_bridge")


def real_vireo_executor(code: str) -> Dict[str, Any]:
    """Реальний виконавець Vireo коду."""
    try:
        from vireo_interpreter import execute_vireo_code
        result = execute_vireo_code(code)
        return result
    except ImportError:
        return {
            "status": "error",
            "errors": ["VireoInterpreter not found"],
            "output": "",
            "variables": {},
            "models": {}
        }
    except Exception as e:
        return {
            "status": "error",
            "errors": [str(e)],
            "output": "",
            "variables": {},
            "models": {}
        }


class RuntimeBridge:
    def __init__(self, executor: Optional[Callable] = None, cache_enabled: bool = False):
        self.executor = executor or real_vireo_executor
        self.cache_enabled = cache_enabled
        self._cache: Dict[str, Any] = {}
    
    def run(self, code: str) -> Any:
        if self.cache_enabled:
            cache_key = hashlib.md5(code.encode()).hexdigest()
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        result = self.executor(code)
        
        if self.cache_enabled:
            self._cache[cache_key] = result
        
        return result


def create_runtime_bridge(**kwargs) -> RuntimeBridge:
    return RuntimeBridge(**kwargs)