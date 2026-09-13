# [file name]: src/onnx/__init__.py
# ============================================================
# VIREO ONNX PACKAGE
# ============================================================
"""
ONNX integration for Vireo.

Provides:
- Export Vireo models to ONNX
- Import ONNX models to Vireo
"""

from .export import export_to_onnx
from .import import import_from_onnx

__all__ = [
    "export_to_onnx",
    "import_from_onnx",
]