# ============================================================
# VIREO VISION EXTENSION
# ============================================================
"""
Computer Vision extension for Vireo.

Provides:
- Vision model loading and inference
- Image classification
- Object detection
- Image segmentation
"""

from .models import (
    VisionModel,
    ImageClassifier,
    ObjectDetector,
    ImageSegmenter,
    load_vision_model,
    list_vision_models,
)

__all__ = [
    'VisionModel',
    'ImageClassifier',
    'ObjectDetector',
    'ImageSegmenter',
    'load_vision_model',
    'list_vision_models',
]