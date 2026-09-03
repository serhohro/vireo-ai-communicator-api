# ============================================================
# VIREO EDGE EXTENSION
# ============================================================
"""
Edge optimization for Vireo.

Provides:
- Model quantization
- ONNX export
- Raspberry Pi optimization
- Lightweight runtime
"""

from .quantize import quantize_model, QuantizationConfig
from .onnx_export import export_to_onnx, ONNXConfig
from .raspberry_pi import optimize_for_pi, PiConfig

__all__ = [
    'quantize_model',
    'QuantizationConfig',
    'export_to_onnx',
    'ONNXConfig',
    'optimize_for_pi',
    'PiConfig',
]