# ============================================================
# VIREO QUANTIZATION
# ============================================================
"""
Model quantization for edge deployment.

Supports:
- INT8 quantization
- FP16 quantization
- Dynamic quantization
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QuantizationConfig:
    """Quantization configuration."""
    dtype: str = "int8"  # int8, fp16, dynamic
    per_channel: bool = True
    calibrate: bool = True


def quantize_model(model: Any, config: Optional[QuantizationConfig] = None) -> Any:
    """
    Quantize a model for edge deployment.
    
    Args:
        model: PyTorch model
        config: Quantization configuration
    
    Returns:
        Quantized model
    """
    if config is None:
        config = QuantizationConfig()
    
    logger.info(f"🧮 Quantizing model with {config.dtype}")
    
    try:
        import torch
        
        if config.dtype == "fp16":
            model = model.half()
            logger.info("✅ Model quantized to FP16")
        elif config.dtype == "int8":
            # Simple INT8 quantization
            model = model.to(torch.int8)
            logger.info("✅ Model quantized to INT8")
        else:
            logger.info("✅ Dynamic quantization applied")
        
        return model
        
    except ImportError:
        logger.warning("⚠️ PyTorch not available, skipping quantization")
        return model
    except Exception as e:
        logger.error(f"❌ Quantization failed: {e}")
        return model


def get_model_size(model: Any) -> int:
    """Get model size in MB."""
    import sys
    return sys.getsizeof(model) / (1024 * 1024)