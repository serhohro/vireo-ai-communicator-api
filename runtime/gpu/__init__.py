# ============================================================
# VIREO GPU ACCELERATION
# GPU підтримка (CUDA, Metal, ROCm)
# ============================================================
#
# Компоненти:
#   - CUDAExecutor: NVIDIA CUDA
#   - MetalExecutor: Apple Metal
#   - ROCmExecutor: AMD ROCm
#   - GPUDevice: Управління пристроями
#   - GPUTensor: Тензорні операції на GPU
#
# ============================================================

from .cuda import (
    CUDAExecutor,
    CUDAContext,
    CUDAKernel,
    is_cuda_available,
    get_cuda_devices,
)

from .metal import (
    MetalExecutor,
    MetalContext,
    MetalKernel,
    is_metal_available,
    get_metal_devices,
)

from .rocm import (
    ROCmExecutor,
    ROCmContext,
    ROCmKernel,
    is_rocm_available,
    get_rocm_devices,
)

from .tensor import (
    GPUTensor,
    GPUType,
    GPUDevice,
    GPUContext,
    to_gpu,
    to_cpu,
    is_gpu_available,
    get_gpu_type,
)

__version__ = "3.0.0"
__all__ = [
    "CUDAExecutor",
    "CUDAContext",
    "CUDAKernel",
    "is_cuda_available",
    "get_cuda_devices",
    "MetalExecutor",
    "MetalContext",
    "MetalKernel",
    "is_metal_available",
    "get_metal_devices",
    "ROCmExecutor",
    "ROCmContext",
    "ROCmKernel",
    "is_rocm_available",
    "get_rocm_devices",
    "GPUTensor",
    "GPUType",
    "GPUDevice",
    "GPUContext",
    "to_gpu",
    "to_cpu",
    "is_gpu_available",
    "get_gpu_type",
]

__author__ = "Serhii (serhohro)"
__license__ = "Apache 2.0"