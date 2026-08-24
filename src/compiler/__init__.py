# [file name]: src/compiler/__init__.py
# ============================================================
# VIREO COMPILER PACKAGE
# ============================================================
"""
Compiler module for Vireo.

Provides:
- JIT compilation via LLVM
- GPU acceleration via CUDA/ROCm/Metal
"""

from .jit import VireoJIT, jit_compile
from .gpu import GPUSupport, gpu_accelerate

__all__ = [
    "VireoJIT",
    "jit_compile",
    "GPUSupport",
    "gpu_accelerate",
]