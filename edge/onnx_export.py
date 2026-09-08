# ============================================================
# VIREO ONNX EXPORTER
# Експорт моделей в ONNX
# ============================================================

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class ONNXConfig:
    """Конфігурація ONNX."""
    opset_version: int = 13
    enable_optimization: bool = True
    input_names: List[str] = field(default_factory=list)
    output_names: List[str] = field(default_factory=list)
    dynamic_axes: Dict[str, Any] = field(default_factory=dict)
    verbose: bool = False


class ONNXExporter:
    """
    Експортер в ONNX.
    
    Експортує моделі в ONNX формат.
    """
    
    def __init__(self, config: Optional[ONNXConfig] = None):
        self.config = config or ONNXConfig()
    
    def export(self, model, sample_input: Any, path: str) -> bool:
        """
        Експортує модель в ONNX.
        
        Args:
            model: Модель
            sample_input: Зразок входу
            path: Шлях для збереження
            
        Returns:
            bool: True якщо успішно        """
        try:
            import torch
            
            input_names = self.config.input_names or ["input"]
            output_names = self.config.output_names or ["output"]
            
            torch.onnx.export(
                model,
                sample_input,
                path,
                opset_version=self.config.opset_version,
                input_names=input_names,
                output_names=output_names,
                dynamic_axes=self.config.dynamic_axes,
                verbose=self.config.verbose,
            )
            
            logger.info(f"Model exported to ONNX: {path}")
            return True
        except Exception as e:
            logger.error(f"ONNX export failed: {e}")
            return False
    
    def load(self, path: str) -> Optional[Any]:
        """
        Завантажує ONNX модель.
        
        Args:
            path: Шлях до ONNX файлу
            
        Returns:
            Any: ONNX модель
        """
        try:
            import onnx
            import onnxruntime as ort
            
            onnx_model = onnx.load(path)
            onnx.checker.check_model(onnx_model)
            
            session = ort.InferenceSession(path)
            return session
        except Exception as e:
            logger.error(f"ONNX load failed: {e}")
            return None


def export_to_onnx(model, sample_input: Any, path: str, config: Optional[ONNXConfig] = None) -> bool:
    """Зручна функція для експорту в ONNX."""
    exporter = ONNXExporter(config)
    return exporter.export(model, sample_input, path)


def load_onnx(path: str) -> Optional[Any]:
    """Зручна функція для завантаження ONNX."""
    exporter = ONNXExporter()
    return exporter.load(path)