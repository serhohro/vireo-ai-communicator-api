# ============================================================
# VIREO NLP EXTENSION
# ============================================================
"""
Natural Language Processing extension for Vireo.

Provides:
- Text embedding models (BERT)
- Text generation models (GPT-2)
- Text classification
- Named entity recognition
"""

from .models import (
    NLPModel,
    TextEmbedder,
    TextGenerator,
    TextClassifier,
    load_nlp_model,
    list_nlp_models,
)

__all__ = [
    'NLPModel',
    'TextEmbedder',
    'TextGenerator',
    'TextClassifier',
    'load_nlp_model',
    'list_nlp_models',
]