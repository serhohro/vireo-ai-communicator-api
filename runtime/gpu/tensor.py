# ============================================================
# VIREO GPU TENSOR
# Тензорні операції на GPU
# ============================================================

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
import logging

from .cuda import is_cuda_available, get_cuda_devices
from .metal import is_metal_available, get_metal_devices
from .rocm import is_rocm_available, get_rocm_devices

logger = logging.getLogger(__name__)


class GPUType(Enum):
    """Типи GPU."""
    NONE = "none"
    CUDA = "cuda"
    METAL = "metal"
    ROCM = "rocm"


@dataclass
class GPUDevice:
    """GPU пристрій."""
    id: int
    name: str
    type: GPUType
    memory: int = 0
    compute_capability: str = ""
    available: bool = True


@dataclass
class GPUContext:
    """GPU контекст."""
    device: GPUDevice
    context: Optional[Any] = None
    streams: List[Any] = field(default_factory=list)


class GPUTensor:
    """
    Тензор на GPU.
    
    Підтримує:
    - Створення на GPU
    - Переміщення між CPU/GPU
    - Базові операції
    """
    
    def __init__(self, data: Any, device: Optional[GPUDevice] = None):
        self._data = data
        self._device = device or self._get_default_device()
        self._on_gpu = False
        self._gpu_data = None
    
    def _get_default_device(self) -> GPUDevice:
        """Отримує пристрій за замовчуванням."""
        if is_cuda_available():
            devices = get_cuda_devices()
            if devices:
                return GPUDevice(
                    id=devices[0]["id"],
                    name=devices[0]["name"],
                    type=GPUType.CUDA,
                    memory=devices[0]["memory"],
                )
        elif is_metal_available():
            devices = get_metal_devices()
            if devices:
                return GPUDevice(
                    id=devices[0]["id"],
                    name=devices[0]["name"],
                    type=GPUType.METAL,
                )
        elif is_rocm_available():
            devices = get_rocm_devices()
            if devices:
                return GPUDevice(
                    id=devices[0]["id"],
                    name=devices[0]["name"],
                    type=GPUType.ROCM,
                    memory=devices[0]["memory"],
                )
        
        return GPUDevice(id=0, name="CPU", type=GPUType.NONE)
    
    def to_gpu(self) -> 'GPUTensor':
        """Переміщує тензор на GPU."""
        if self._device.type == GPUType.NONE:
            logger.warning("No GPU available")
            return self
        
        try:
            import torch
            self._gpu_data = torch.tensor(self._data).cuda()
            self._on_gpu = True
            return self
        except Exception as e:
            logger.error(f"Failed to move to GPU: {e}")
            return self
    
    def to_cpu(self) -> 'GPUTensor':
        """Переміщує тензор на CPU."""
        if self._gpu_data is not None:
            self._data = self._gpu_data.cpu().numpy()
            self._gpu_data = None
            self._on_gpu = False
        return self
    
    @property
    def data(self) -> Any:
        """Отримує дані тензора."""
        if self._on_gpu and self._gpu_data is not None:
            return self._gpu_data
        return self._data
    
    @property
    def device(self) -> GPUDevice:
        """Отримує пристрій."""
        return self._device
    
    @property
    def on_gpu(self) -> bool:
        """Перевіряє чи тензор на GPU."""
        return self._on_gpu
    
    def __repr__(self) -> str:
        return f"GPUTensor(device={self._device.type.value}, on_gpu={self._on_gpu})"


def to_gpu(data: Any, device: Optional[GPUDevice] = None) -> GPUTensor:
    """Переміщує дані на GPU."""
    tensor = GPUTensor(data, device)
    return tensor.to_gpu()


def to_cpu(tensor: GPUTensor) -> Any:
    """Переміщує тензор на CPU."""
    return tensor.to_cpu().data


def is_gpu_available() -> bool:
    """Перевіряє доступність GPU."""
    return is_cuda_available() or is_metal_available() or is_rocm_available()


def get_gpu_type() -> GPUType:
    """Отримує тип доступного GPU."""
    if is_cuda_available():
        return GPUType.CUDA
    elif is_metal_available():
        return GPUType.METAL
    elif is_rocm_available():
        return GPUType.ROCM
    return GPUType.NONE