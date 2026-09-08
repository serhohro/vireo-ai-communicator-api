# ============================================================
# VIREO JIT COMPILER
# Just-In-Time компіляція через LLVM
# ============================================================
#
# Компоненти:
#   - LLVMBackend: LLVM IR генерація та компіляція
#   - TensorOps: Оптимізація тензорних операцій
#   - Autograd: Автоматичне диференціювання
#   - Optimizer: Оптимізація графів
#
# ============================================================

from .llvm_backend import (
    LLVMBackend,
    LLVMCompiler,
    LLVMConfig,
    compile_to_llvm,
    optimize_ir,
    compile_to_native,
)

from .tensor_ops import (
    TensorOps,
    TensorOptimizer,
    fuse_operations,
    optimize_tensor_graph,
)

from .autograd import (
    Autograd,
    Variable,
    Function,
    GradFn,
    Tensor,
    autograd_enabled,
)

from .optimizer import (
    GraphOptimizer,
    OptimizerPass,
    PassManager,
    ConstantFolding,
    DeadCodeElimination,
    CommonSubexpressionElimination,
)

__version__ = "3.0.0"
__all__ = [
    "LLVMBackend",
    "LLVMCompiler",
    "LLVMConfig",
    "compile_to_llvm",
    "optimize_ir",
    "compile_to_native",
    "TensorOps",
    "TensorOptimizer",
    "fuse_operations",
    "optimize_tensor_graph",
    "Autograd",
    "Variable",
    "Function",
    "GradFn",
    "Tensor",
    "autograd_enabled",
    "GraphOptimizer",
    "OptimizerPass",
    "PassManager",
    "ConstantFolding",
    "DeadCodeElimination",
    "CommonSubexpressionElimination",
]

__author__ = "Serhii (serhohro)"
__license__ = "Apache 2.0"