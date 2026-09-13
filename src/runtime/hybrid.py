# [file name]: src/runtime/hybrid.py
# ============================================================
# VIREO HYBRID RUNTIME — Vireo DSL → PyTorch/ONNX
# ============================================================
"""
Hybrid runtime for Vireo.

Converts Vireo DSL to:
- PyTorch models
- ONNX format
- NumPy code (fallback)
"""

import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("vireo.runtime.hybrid")


def vireo_to_pytorch(vireo_code: str, input_shape: Optional[List[int]] = None) -> Any:
    """
    Конвертує Vireo модель у PyTorch Sequential.
    
    Args:
        vireo_code: Vireo код моделі
        input_shape: Форма вхідних даних (опціонально)
        
    Returns:
        torch.nn.Sequential: PyTorch модель
    """
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        logger.warning("PyTorch not installed, returning dict")
        return {"error": "PyTorch not installed", "code": vireo_code}
    
    layers = []
    lines = vireo_code.strip().split('\n')
    model_name = "Model"
    
    # Знаходимо назву моделі
    for line in lines:
        if 'model' in line and '{' in line:
            model_name = line.replace('model', '').strip().split('{')[0].strip()
            break
    
    # Парсинг шарів
    for line in lines:
        line = line.strip()
        
        # Пропускаємо порожні рядки та коментарі
        if not line or line.startswith('//') or line.startswith('#'):
            continue
        
        # Парсинг Dense(784, 128)
        if 'Dense' in line:
            match = re.search(r'Dense\((\d+),\s*(\d+)\)', line)
            if match:
                in_features = int(match.group(1))
                out_features = int(match.group(2))
                layers.append(nn.Linear(in_features, out_features))
                logger.debug(f"Added Dense({in_features}, {out_features})")
        
        # Парсинг activation ReLU
        elif 'activation' in line:
            act = line.replace('activation', '').strip()
            if act == 'ReLU' or act == 'relu':
                layers.append(nn.ReLU())
                logger.debug("Added ReLU")
            elif act == 'Softmax' or act == 'softmax':
                layers.append(nn.Softmax(dim=1))
                logger.debug("Added Softmax")
            elif act == 'Sigmoid' or act == 'sigmoid':
                layers.append(nn.Sigmoid())
                logger.debug("Added Sigmoid")
            elif act == 'Tanh' or act == 'tanh':
                layers.append(nn.Tanh())
                logger.debug("Added Tanh")
        
        # Парсинг Dropout
        elif 'Dropout' in line:
            match = re.search(r'Dropout\(([\d.]+)\)', line)
            if match:
                p = float(match.group(1))
                layers.append(nn.Dropout(p))
                logger.debug(f"Added Dropout({p})")
        
        # Парсинг BatchNorm
        elif 'BatchNorm' in line:
            # Потрібно знати кількість каналів
            match = re.search(r'BatchNorm\((\d+)\)', line)
            if match:
                num_features = int(match.group(1))
                layers.append(nn.BatchNorm1d(num_features))
                logger.debug(f"Added BatchNorm({num_features})")
        
        # Парсинг Flatten
        elif 'Flatten' in line:
            layers.append(nn.Flatten())
            logger.debug("Added Flatten")
    
    if not layers:
        logger.warning("No layers found in Vireo code")
        return {"error": "No layers found", "code": vireo_code}
    
    # Створюємо Sequential модель
    model = nn.Sequential(*layers)
    logger.info(f"✅ Converted Vireo model '{model_name}' to PyTorch")
    
    return model


def vireo_to_onnx(vireo_code: str, path: str, input_shape: List[int] = [1, 784]) -> bool:
    """
    Конвертує Vireo модель в ONNX та зберігає у файл.
    
    Args:
        vireo_code: Vireo код моделі
        path: Шлях для збереження ONNX файлу
        input_shape: Форма вхідних даних
        
    Returns:
        bool: True якщо успішно
    """
    try:
        import torch
        import onnx
    except ImportError:
        logger.warning("PyTorch or ONNX not installed")
        return False
    
    # Конвертуємо в PyTorch
    model = vireo_to_pytorch(vireo_code)
    if isinstance(model, dict) and "error" in model:
        return False
    
    # Створюємо dummy input
    dummy_input = torch.randn(*input_shape)
    
    # Експортуємо в ONNX
    torch.onnx.export(
        model,
        dummy_input,
        path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    logger.info(f"✅ ONNX model exported to {path}")
    return True


def vireo_to_numpy(vireo_code: str) -> Dict[str, Any]:
    """
    Конвертує Vireo модель у структуру NumPy.
    
    Args:
        vireo_code: Vireo код моделі
        
    Returns:
        Dict: Опис моделі для NumPy
    """
    layers = []
    lines = vireo_code.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//') or line.startswith('#'):
            continue
        
        layer_info = {"type": "unknown", "params": {}}
        
        if 'Dense' in line:
            match = re.search(r'Dense\((\d+),\s*(\d+)\)', line)
            if match:
                layer_info["type"] = "Dense"
                layer_info["params"]["in_features"] = int(match.group(1))
                layer_info["params"]["out_features"] = int(match.group(2))
                layers.append(layer_info)
        
        elif 'activation' in line:
            act = line.replace('activation', '').strip()
            layer_info["type"] = "Activation"
            layer_info["params"]["activation"] = act
            layers.append(layer_info)
        
        elif 'Dropout' in line:
            match = re.search(r'Dropout\(([\d.]+)\)', line)
            if match:
                layer_info["type"] = "Dropout"
                layer_info["params"]["p"] = float(match.group(1))
                layers.append(layer_info)
        
        elif 'Flatten' in line:
            layer_info["type"] = "Flatten"
            layers.append(layer_info)
    
    return {
        "layers": layers,
        "num_layers": len(layers)
    }


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    # Приклад Vireo коду
    code = """
    model MNIST {
        layer Dense(784, 128)
        activation ReLU
        layer Dense(128, 10)
        activation Softmax
    }
    """
    
    # Конвертація в PyTorch
    model = vireo_to_pytorch(code)
    print(f"PyTorch model: {model}")
    
    # Конвертація в NumPy опис
    numpy_model = vireo_to_numpy(code)
    print(f"NumPy model: {numpy_model}")