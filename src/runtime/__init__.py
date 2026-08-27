# [file name]: src/runtime/__init__.py
# ============================================================
# VIREO RUNTIME PACKAGE
# ============================================================
"""
Hybrid runtime for Vireo.

Provides:
- Vireo DSL → PyTorch conversion
- Multi-backend execution
"""

from .hybrid import vireo_to_pytorch, vireo_to_onnx

__all__ = [
    "vireo_to_pytorch",
    "vireo_to_onnx",
]