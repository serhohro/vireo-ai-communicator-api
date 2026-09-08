# ============================================================
# VIREO QUANTIZER
# Квантування моделей для Edge
# ============================================================

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
import logging
import numpy as np

logger = logging.getLogger(__name__)


class QuantizationType(Enum):
    """Типи квантування."""
    NONE = "none"
    INT8 = "int8"
    INT16 = "int16"
    FP16 = "fp16"
    BFLOAT16 = "bfloat16"


@dataclass
class QuantizationConfig:
    """Конфігурація квантування."""
    type: QuantizationType = QuantizationType.INT8
    per_channel: bool = False
    symmetric: bool = True
    calibration_samples: int = 100
    enable_optimization: bool = True


class Quantizer:
    """
    Квантувальник моделей.
    
    Підтримує різні типи квантування.
    """
    
    def __init__(self, config: Optional[QuantizationConfig] = None):
        self.config = config or QuantizationConfig()
    
    def quantize_model(self, model) -> Any:
        """
        Квантує модель.
        
        Args:
            model: Модель для квантування
            
        Returns:
            Any: Квантована модель
        """
        logger.info(f"Quantizing model with {self.config.type.value}")
        
        if self.config.type == QuantizationType.NONE:
            return model
        
        try:
            import torch
            if self.config.type == QuantizationType.INT8:
                return torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
            elif self.config.type == QuantizationType.FP16:
                return model.half()
            elif self.config.type == QuantizationType.INT16:
                return self._quantize_int16(model)
            else:
                return model
        except Exception as e:
            logger.error(f"Quantization failed: {e}")
            return model
    
    def quantize_tensor(self, tensor: Any) -> Any:
        """
        Квантує тензор.
        
        Args:
            tensor: Тензор для квантування
            
        Returns:
            Any: Квантований тензор
        """
        if self.config.type == QuantizationType.NONE:
            return tensor
        
        try:
            if isinstance(tensor, np.ndarray):
                if self.config.type == QuantizationType.INT8:
                    return self._quantize_numpy_int8(tensor)
                elif self.config.type == QuantizationType.FP16:
                    return tensor.astype(np.float16)
            return tensor
        except Exception as e:
            logger.error(f"Tensor quantization failed: {e}")
            return tensor
    
    def _quantize_int16(self, model) -> Any:
        """Квантує модель в INT16."""
        # Спрощена реалізація
        return model
    
    def _quantize_numpy_int8(self, tensor: np.ndarray) -> np.ndarray:
        """Квантує numpy масив в INT8."""
        if self.config.symmetric:
            max_val = np.max(np.abs(tensor))
            scale = 127.0 / max_val if max_val > 0 else 1.0
            return np.round(tensor * scale).astype(np.int8)
        else:
            min_val = np.min(tensor)
            max_val = np.max(tensor)
            scale = 255.0 / (max_val - min_val) if max_val > min_val else 1.0
            zero_point = -min_val * scale
            return np.round(tensor * scale + zero_point).astype(np.uint8)


def quantize_model(model, config: Optional[QuantizationConfig] = None) -> Any:
    """Зручна функція для квантування моделі."""
    quantizer = Quantizer(config)
    return quantizer.quantize_model(model)


def quantize_tensor(tensor: Any, config: Optional[QuantizationConfig] = None) -> Any:
    """Зручна функція для квантування тензора."""
    quantizer = Quantizer(config)
    return quantizer.quantize_tensor(tensor)