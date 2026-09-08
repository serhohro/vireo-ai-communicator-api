# ============================================================
# VIREO LANGUAGE EXTENSIONS
# ============================================================
# ML, Tensor, Vision, NLP
# ============================================================

# ============================================================
# GRAMMAR (зберігається в .py файлах)
# ============================================================

from .ml import ml_grammar, MLParser
from .tensor import tensor_grammar, TensorParser
from .vision import vision_grammar, VisionParser
from .nlp import nlp_grammar, NLPParser

# ============================================================
# ЕКСПОРТИ
# ============================================================

__all__ = [
    # Grammars
    "ml_grammar",
    "tensor_grammar",
    "vision_grammar",
    "nlp_grammar",
    # Parsers
    "MLParser",
    "TensorParser",
    "VisionParser",
    "NLPParser",
]