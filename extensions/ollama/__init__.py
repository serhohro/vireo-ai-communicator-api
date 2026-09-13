# ============================================================
# VIREO OLLAMA EXTENSION
# ============================================================
"""
Ollama extension for Vireo.

Provides:
- Ollama model optimization
- Response caching
- GPU detection and configuration
- Auto-download of models

This extension optimizes Ollama for Vireo agent coordination.
"""

from .optimizer import OllamaOptimizer, OllamaCache
from .cache import OllamaCacheManager

__all__ = [
    'OllamaOptimizer',
    'OllamaCache',
    'OllamaCacheManager',
]


# ============================================================
# VERSION INFO
# ============================================================

__version__ = "2.0.2"
__description__ = "Ollama extension for Vireo AI-to-AI communication"