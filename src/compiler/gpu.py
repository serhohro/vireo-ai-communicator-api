# [file name]: src/compiler/gpu.py
# ============================================================
# GPU SUPPORT FOR VIREO
# ============================================================
"""
GPU acceleration for Vireo.

Provides:
- CUDA backend for NVIDIA GPUs
- ROCm support for AMD GPUs
- Metal support for Apple Silicon
- Automatic device detection
"""

import os
import logging
from typing import Optional, Any, Union
from enum import Enum

logger = logging.getLogger("vireo.compiler.gpu")


class GPUDevice(str, Enum):
    """Доступні GPU пристрої."""
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    METAL = "metal"
    TPU = "tpu"


class GPUSupport:
    """Підтримка GPU для Vireo."""
    
    def __init__(self):
        self.device = self._detect_gpu()
        self._cuda_available = False
        self._rocm_available = False
        self._metal_available = False
        
        self._init_backends()
    
    def _init_backends(self):
        """Ініціалізує доступні GPU бекенди."""
        # Перевіряємо CUDA
        try:
            import cupy
            self._cuda_available = cupy.cuda.is_available()
            if self._cuda_available:
                logger.info("✅ CUDA available")
        except ImportError:
            pass
        
        # Перевіряємо ROCm
        try:
            import torch
            if torch.cuda.is_available() and "AMD" in torch.cuda.get_device_name(0):
                self._rocm_available = True
                logger.info("✅ ROCm available")
        except ImportError:
            pass
        
        # Перевіряємо Metal
        try:
            import torch
            if torch.backends.mps.is_available():
                self._metal_available = True
                logger.info("✅ Metal available")
        except ImportError:
            pass
    
    def _detect_gpu(self) -> GPUDevice:
        """Визначає доступний GPU."""
        # Перевіряємо CUDA
        try:
            import cupy
            if cupy.cuda.is_available():
                return GPUDevice.CUDA
        except:
            pass
        
        # Перевіряємо ROCm
        try:
            import torch
            if torch.cuda.is_available() and "AMD" in torch.cuda.get_device_name(0):
                return GPUDevice.ROCM
        except:
            pass
        
        # Перевіряємо Metal
        try:
            import torch
            if torch.backends.mps.is_available():
                return GPUDevice.METAL
        except:
            pass
        
        return GPUDevice.CPU
    
    def accelerate(self, tensor: Any, device: Optional[GPUDevice] = None) -> Any:
        """
        Переносить тензор на GPU.
        
        Args:
            tensor: Вхідний тензор
            device: Цільовий пристрій (якщо None - використовує визначений)
            
        Returns:
            Тензор на GPU
        """
        target = device or self.device
        
        if target == GPUDevice.CUDA and self._cuda_available:
            import cupy as cp
            return cp.array(tensor)
        
        elif target == GPUDevice.ROCM and self._rocm_available:
            import torch
            return torch.tensor(tensor).to("cuda")
        
        elif target == GPUDevice.METAL and self._metal_available:
            import torch
            return torch.tensor(tensor).to("mps")
        
        return tensor
    
    def get_device_info(self) -> dict:
        """Повертає інформацію про пристрій."""
        info = {
            "device": self.device.value,
            "cuda_available": self._cuda_available,
            "rocm_available": self._rocm_available,
            "metal_available": self._metal_available,
        }
        
        if self._cuda_available:
            import cupy
            info["cuda_version"] = cupy.__version__
            info["cuda_devices"] = cupy.cuda.runtime.getDeviceCount()
        
        return info


def gpu_accelerate(func):
    """
    Декоратор для GPU прискорення.
    
    Usage:
        @gpu_accelerate
        def my_model(data):
            return dense(data, 128)
    """
    def wrapper(*args, **kwargs):
        gpu = GPUSupport()
        if gpu.device != GPUDevice.CPU:
            logger.info(f"🚀 Running on {gpu.device.value}")
            # Перенесення на GPU
            new_args = []
            for arg in args:
                if hasattr(arg, "data"):
                    new_args.append(gpu.accelerate(arg))
                else:
                    new_args.append(arg)
            return func(*new_args, **kwargs)
        return func(*args, **kwargs)
    return wrapper


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    gpu = GPUSupport()
    print("📊 GPU Info:", gpu.get_device_info())