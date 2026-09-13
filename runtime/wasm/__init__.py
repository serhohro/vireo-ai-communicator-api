# ============================================================
# VIREO WASM RUNTIME
# WebAssembly підтримка
# ============================================================
#
# Компоненти:
#   - WASMCompiler: Компіляція в WASM
#   - WASMRuntime: Виконання WASM
#   - WASMModule: WASM модуль
#   - WASMInstance: Екземпляр WASM
#
# ============================================================

from .compiler import (
    WASMCompiler,
    compile_to_wasm,
    WASMConfig,
)

from .runtime import (
    WASMRuntime,
    WASMModule,
    WASMInstance,
    WASMResult,
)

from .bindings.python import (
    WASMPythonBinding,
    PythonWASMFunc,
)

from .bindings.typescript import (
    WASMTypeScriptBinding,
    TypeScriptWASMFunc,
)

__version__ = "3.0.0"
__all__ = [
    "WASMCompiler",
    "compile_to_wasm",
    "WASMConfig",
    "WASMRuntime",
    "WASMModule",
    "WASMInstance",
    "WASMResult",
    "WASMPythonBinding",
    "PythonWASMFunc",
    "WASMTypeScriptBinding",
    "TypeScriptWASMFunc",
]

__author__ = "Serhii (serhohro)"
__license__ = "Apache 2.0"