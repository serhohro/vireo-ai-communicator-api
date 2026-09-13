# ============================================================
# VIREO RUNTIME MODULE
# Vireo Runtime v3.0.0
# ============================================================
#
# Components:
#   - Executor: Code execution engine
#   - Context: Runtime context management
#   - Registry: Component registration
#   - JIT: LLVM-based JIT compilation
#   - GPU: CUDA/Metal/ROCm acceleration
#   - WASM: WebAssembly runtime
#   - Edge: Edge device optimization
#
# Usage:
#   from runtime import Executor, RuntimeContext, Registry
#   from runtime.jit import JITCompiler
#   from runtime.gpu import GPUExecutor
#
# ============================================================

__version__ = "3.0.0"
__author__ = "Serhii (serhohro)"
__license__ = "Apache 2.0"

# ============================================================
# CORE MODULES
# ============================================================

from .executor import (
    Executor,
    ExecutionResult,
    ExecutionStatus,
    ExecutionMode,
    execute,
    execute_async,
)

from .context import (
    RuntimeContext,
    ContextManager,
    ContextVar,
    get_context,
    set_context,
    reset_context,
)

from .registry import (
    Registry,
    ComponentRegistry,
    ComponentType,
    ComponentInfo,
    register_component,
    get_component,
    list_components,
)

# ============================================================
# JIT MODULE
# ============================================================

try:
    from .jit import (
        JITCompiler,
        JITConfig,
        LLVMBackend,
        optimize_ir,
        compile_to_machine,
    )
except ImportError:
    pass

# ============================================================
# GPU MODULE
# ============================================================

try:
    from .gpu import (
        GPUExecutor,
        GPUDevice,
        GPUType,
        CUDAExecutor,
        MetalExecutor,
        ROCmExecutor,
    )
except ImportError:
    pass

# ============================================================
# WASM MODULE
# ============================================================

try:
    from .wasm import (
        WASMRuntime,
        WASMCompiler,
        WASMModule,
        WASMInstance,
    )
except ImportError:
    pass

# ============================================================
# EDGE MODULE
# ============================================================

try:
    from .edge import (
        EdgeExecutor,
        EdgeDevice,
        Quantizer,
        ONNXExporter,
        RaspberryPiExecutor,
        MobileExecutor,
    )
except ImportError:
    pass

# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    # Core
    "Executor",
    "ExecutionResult",
    "ExecutionStatus",
    "ExecutionMode",
    "execute",
    "execute_async",
    "RuntimeContext",
    "ContextManager",
    "ContextVar",
    "get_context",
    "set_context",
    "reset_context",
    "Registry",
    "ComponentRegistry",
    "ComponentType",
    "ComponentInfo",
    "register_component",
    "get_component",
    "list_components",
    # JIT
    "JITCompiler",
    "JITConfig",
    "LLVMBackend",
    "optimize_ir",
    "compile_to_machine",
    # GPU
    "GPUExecutor",
    "GPUDevice",
    "GPUType",
    "CUDAExecutor",
    "MetalExecutor",
    "ROCmExecutor",
    # WASM
    "WASMRuntime",
    "WASMCompiler",
    "WASMModule",
    "WASMInstance",
    # Edge
    "EdgeExecutor",
    "EdgeDevice",
    "Quantizer",
    "ONNXExporter",
    "RaspberryPiExecutor",
    "MobileExecutor",
]

# ============================================================
# VERSION INFO
# ============================================================

def get_version() -> str:
    return __version__

def get_info() -> dict:
    return {
        "name": "Vireo Runtime",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "features": [
            "JIT compilation (LLVM)",
            "GPU acceleration (CUDA/Metal/ROCm)",
            "WebAssembly runtime",
            "Edge device optimization",
            "Tensor operations",
            "Autograd",
            "Multi-threading",
        ],
    }

# ============================================================
# INITIALIZATION
# ============================================================

def _check_dependencies():
    """Check for optional dependencies."""
    missing = []
    
    try:
        import llvmlite  # noqa
    except ImportError:
        missing.append("llvmlite (JIT)")
    
    try:
        import torch  # noqa
    except ImportError:
        missing.append("torch (GPU)")
    
    try:
        import wasmtime  # noqa
    except ImportError:
        missing.append("wasmtime (WASM)")
    
    if missing:
        print(f"⚠️ Missing optional dependencies: {', '.join(missing)}")

_check_dependencies()

if __name__ == "__main__":
    print(f"Vireo Runtime v{__version__}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print()
    print("Available modules:")
    for module in __all__:
        if not module.startswith("_"):
            print(f"  - {module}")