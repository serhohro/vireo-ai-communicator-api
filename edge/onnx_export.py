# ============================================================
# VIREO ONNX EXPORT
# ============================================================
"""
ONNX model export for Vireo.

Supports:
- ONNX export
- Optimization
- Verification
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ONNXConfig:
    """ONNX export configuration."""
    opset_version: int = 14
    optimize: bool = True
    verify: bool = True


def export_to_onnx(model: Any, input_data: Any, 
                   output_path: str,
                   config: Optional[ONNXConfig] = None) -> bool:
    """
    Export model to ONNX format.
    
    Args:
        model: PyTorch model
        input_data: Example input
        output_path: Output path
        config: ONNX configuration
    
    Returns:
        True if export successful
    """
    if config is None:
        config = ONNXConfig()
    
    logger.info(f"📦 Exporting model to ONNX: {output_path}")
    
    try:
        import torch
        import torch.onnx
        
        torch.onnx.export(
            model,
            input_data,
            output_path,
            opset_version=config.opset_version,
            export_params=True,
            do_constant_folding=config.optimize
        )
        
        if config.verify:
            import onnx
            model_onnx = onnx.load(output_path)
            onnx.checker.check_model(model_onnx)
            logger.info("✅ ONNX model verified")
        
        logger.info(f"✅ ONNX export successful: {output_path}")
        return True
        
    except ImportError:
        logger.warning("⚠️ ONNX not available, skipping export")
        return False
    except Exception as e:
        logger.error(f"❌ ONNX export failed: {e}")
        return False