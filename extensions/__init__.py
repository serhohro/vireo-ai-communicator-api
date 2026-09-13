# ============================================================
# VIREO EXTENSIONS MODULE
# ============================================================
"""
Vireo Extensions — optional components for specialized tasks.

This module contains optional extensions for Vireo:
- ml: Machine learning models (pretrained, ONNX)
- vision: Computer vision models
- nlp: Natural language processing models
- ollama: Ollama optimization and caching

These extensions are optional and can be installed separately.
"""

from . import ml
from . import vision
from . import nlp
from . import ollama

__all__ = [
    'ml',
    'vision',
    'nlp',
    'ollama',
]