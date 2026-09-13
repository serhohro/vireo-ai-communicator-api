# Vireo GPU Acceleration

Complete guide for GPU acceleration with Vireo.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [CUDA Support](#cuda-support)
4. [Metal Support](#metal-support)
5. [ROCm Support](#rocm-support)
6. [Tensor Operations](#tensor-operations)
7. [Model Training](#model-training)
8. [Performance Optimization](#performance-optimization)
9. [Benchmarking](#benchmarking)

---

## Overview

Vireo supports GPU acceleration through multiple backends:

| Backend | Platform | Hardware | Status |
|---------|----------|----------|--------|
| CUDA | NVIDIA | GPU | ✅ Stable |
| Metal | Apple | M1/M2/M3 | ✅ Stable |
| ROCm | AMD | GPU | ✅ Stable |
| CPU | Any | CPU | ✅ Stable |
| OpenCL | Any | Any | 🚧 Development |

### Performance Comparison
┌─────────────────────────────────────────────────────────────┐
│ PERFORMANCE │
│ Operations per second (higher is better) │
├─────────────────────────────────────────────────────────────┤
│ CPU: ████████░░░░░░░░░░░░░░░░░░░░░░░░░ 2000 │
│ CUDA A100: ████████████████████████████████ 10000 │
│ Metal M3: ██████████████████████████░░░░░░ 8000 │
│ ROCm MI250: ████████████████████████████████ 9500 │
└─────────────────────────────────────────────────────────────┘

text

---

## Installation

### CUDA Installation

```bash
# Install NVIDIA CUDA Toolkit
# For Ubuntu/Debian
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install cuda-toolkit-12-3

# Install Vireo with CUDA support
pip install vireo-ai[cuda]

# Or from source
export CUDA_HOME=/usr/local/cuda
pip install -e .[cuda]
Metal Installation (macOS)
bash
# macOS with Apple Silicon
pip install vireo-ai[metal]

# From source
export METAL=1
pip install -e .[metal]
ROCm Installation (AMD)
bash
# For Ubuntu/Debian with AMD GPU
wget https://repo.radeon.com/amdgpu-install/latest/ubuntu/jammy/amdgpu-install_6.0.60002-1_all.deb
sudo dpkg -i amdgpu-install_6.0.60002-1_all.deb
sudo amdgpu-install --usecase=rocm

# Install Vireo with ROCm support
pip install vireo-ai[rocm]

# From source
export ROCM_PATH=/opt/rocm
pip install -e .[rocm]
Verify Installation
python
from vireo.runtime.gpu import CUDA

cuda = CUDA()
print(f"CUDA available: {cuda.is_available()}")
print(f"GPU count: {cuda.device_count()}")
print(f"GPU name: {cuda.get_device_name(0)}")
CUDA Support
Basic Usage
python
from vireo.runtime.gpu import CUDA, Tensor

# Initialize CUDA
cuda = CUDA()

# Check GPU availability
print(f"GPU available: {cuda.is_available()}")
print(f"GPU count: {cuda.device_count()}")
print(f"GPU name: {cuda.get_device_name(0)}")

# Create tensor on GPU
tensor = Tensor(
    data=[[1, 2], [3, 4]],
    device="cuda:0"
)

# Move tensor to GPU
cpu_tensor = Tensor([[1, 2], [3, 4]])
gpu_tensor = cpu_tensor.to("cuda:0")

# GPU operations
result = gpu_tensor @ gpu_tensor.T
Memory Management
python
from vireo.runtime.gpu import CUDA

# Check memory usage
memory_info = CUDA.memory_stats()
print(f"Memory free: {memory_info['free'] / 1024**3:.2f} GB")
print(f"Memory used: {memory_info['used'] / 1024**3:.2f} GB")
print(f"Memory total: {memory_info['total'] / 1024**3:.2f} GB")

# Clear memory
CUDA.empty_cache()

# Set memory limit
CUDA.set_memory_limit(8 * 1024**3)  # 8 GB
Multi-GPU
python
from vireo.runtime.gpu import CUDA

# Use multiple GPUs
cuda = CUDA()

# Create models on different GPUs
model1 = create_model().to("cuda:0")
model2 = create_model().to("cuda:1")
model3 = create_model().to("cuda:2")

# Distributed training
cuda.distributed_training(
    models=[model1, model2, model3],
    data=dataset,
    method="data_parallel"
)
Metal Support
Basic Usage
python
from vireo.runtime.gpu import Metal, Tensor

# Initialize Metal
metal = Metal()

# Check availability
print(f"Metal available: {metal.is_available()}")

# Create tensor on Metal
tensor = Tensor(
    data=[[1, 2], [3, 4]],
    device="metal:0"
)

# Metal operations
result = tensor.metal_matmul(tensor.T)
Optimized for Apple Silicon
python
from vireo.runtime.gpu import Metal

# Use Apple Neural Engine (ANE)
metal = Metal(use_ane=True)

# Optimize for M-series chips
metal.set_optimization(
    precision="mixed",
    use_float16=True,
    use_ane_for_convolutions=True
)

# Profile performance
metal.profile({
    "matrix_size": 1024,
    "iterations": 100,
    "operation": "matmul"
})
ROCm Support
Basic Usage
python
from vireo.runtime.gpu import ROCm, Tensor

# Initialize ROCm
rocm = ROCm()

# Check availability
print(f"ROCm available: {rocm.is_available()}")
print(f"GPU count: {rocm.device_count()}")

# Create tensor on AMD GPU
tensor = Tensor(
    data=[[1, 2], [3, 4]],
    device="rocm:0"
)
Tensor Operations
Creating Tensors
python
from vireo.runtime.gpu import Tensor

# Create tensors
t1 = Tensor.zeros((3, 3), device="cuda")
t2 = Tensor.ones((2, 2), device="cuda")
t3 = Tensor.random((4, 4), device="cuda")
t4 = Tensor.eye(5, device="cuda")

# From numpy
import numpy as np
np_array = np.random.randn(100, 100)
t = Tensor.from_numpy(np_array, device="cuda")
Tensor Operations
python
# Basic operations
a = Tensor([[1, 2], [3, 4]], device="cuda")
b = Tensor([[5, 6], [7, 8]], device="cuda")

# Arithmetic
c = a + b
d = a - b
e = a * b
f = a / b

# Matrix operations
g = a @ b  # Matrix multiplication
h = a.T    # Transpose
i = a.inv()  # Inverse

# Reductions
sum_result = a.sum()
mean_result = a.mean()
max_result = a.max()
min_result = a.min()
std_result = a.std()

# Advanced
j = a.matmul(b)
k = a.det()
l = a.eig()
m = a.svd()
Tensor Transformations
python
# Reshape
reshaped = tensor.reshape((1, 9))

# Flatten
flattened = tensor.flatten()

# Transpose
transposed = tensor.T

# Slicing
slice1 = tensor[0:2, 0:2]
slice2 = tensor[:, 1:3]

# Concatenation
concat = Tensor.cat([t1, t2], dim=0)

# Stack
stacked = Tensor.stack([t1, t2, t3], dim=1)
Model Training
Training Setup
python
from vireo.runtime.gpu import CUDA, Trainer

# Setup GPU training
cuda = CUDA()
trainer = Trainer(
    device="cuda:0",
    precision="float16",
    gradient_checkpointing=True
)

# Define model
model = create_model().to("cuda:0")

# Training
trainer.train(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=100,
    learning_rate=0.001,
    optimizer="adam",
    loss="cross_entropy",
    checkpoint_dir="./checkpoints"
)
Distributed Training
python
from vireo.runtime.gpu import DistributedTrainer

# Setup distributed training
trainer = DistributedTrainer(
    world_size=4,  # 4 GPUs
    backend="nccl",
    sync_bn=True,
    gradient_accumulation_steps=4
)

# Train on multiple GPUs
trainer.train_distributed(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=100,
    distributed_method="ddp"  # Distributed Data Parallel
)
Mixed Precision Training
python
from vireo.runtime.gpu import MixedPrecisionTrainer

# Mixed precision training
trainer = MixedPrecisionTrainer(
    dtype="float16",
    loss_scaling="dynamic",
    amp_config={
        "opt_level": "O2",
        "cast_model_type": "float16",
        "patch_torch_functions": True
    }
)

# Train with mixed precision
trainer.train(
    model=model,
    train_loader=train_loader,
    epochs=50
)
Performance Optimization
Memory Optimization
python
# Use checkpointing
from vireo.runtime.gpu import checkpoint

def forward_with_checkpoint(self, x):
    # Use activation checkpointing
    output = checkpoint(self.layer1, x)
    output = checkpoint(self.layer2, output)
    return output

# Memory-efficient operations
from vireo.runtime.gpu import memory_efficient

@memory_efficient
def large_computation(x, y):
    # Operation with reduced memory usage
    return x @ y
Performance Profiling
python
from vireo.runtime.gpu import Profiler

# Profile GPU operations
profiler = Profiler(device="cuda:0")

@profiler.profile
def my_operation():
    # GPU operations
    pass

# Get profile results
results = profiler.get_results()
print(f"Total time: {results['total_time']:.3f}s")
print(f"Peak memory: {results['peak_memory'] / 1024**3:.2f} GB")
print(f"Flops: {results['flops'] / 1e9:.2f} GFLOPS")

# Visualize
profiler.visualize()
Kernel Optimization
python
from vireo.runtime.gpu import kernel

@kernel
def custom_kernel(input, output):
    # Custom CUDA/Metal/ROCm kernel
    idx = thread_idx.x + block_idx.x * block_dim.x
    
    if idx < input.size:
        output[idx] = input[idx] * 2 + 1

# Use custom kernel
result = custom_kernel(tensor, grid=(128,), block=(256,))
Benchmarking
Benchmark Script
python
# tests/performance/benchmark_gpu.py
import time
from vireo.runtime.gpu import CUDA, Tensor

def benchmark_gpu():
    cuda = CUDA()
    results = {}
    
    # Matrix multiplication
    sizes = [128, 512, 1024, 2048, 4096]
    for size in sizes:
        a = Tensor.random((size, size), device="cuda")
        b = Tensor.random((size, size), device="cuda")
        
        start = time.time()
        c = a @ b
        c.cpu()  # Synchronize
        elapsed = time.time() - start
        
        results[f"matmul_{size}"] = {
            "time": elapsed,
            "flops": (2 * size**3) / elapsed / 1e9
        }
    
    return results

if __name__ == "__main__":
    results = benchmark_gpu()
    for name, data in results.items():
        print(f"{name}: {data['time']:.3f}s, {data['flops']:.2f} GFLOPS")
GPU vs CPU Comparison
python
def compare_gpu_cpu():
    import time
    import numpy as np
    from vireo.runtime.gpu import Tensor
    
    size = 1000
    cpu_data = np.random.randn(size, size)
    gpu_data = Tensor.from_numpy(cpu_data, device="cuda")
    
    # CPU
    start = time.time()
    cpu_result = cpu_data @ cpu_data
    cpu_time = time.time() - start
    
    # GPU
    start = time.time()
    gpu_result = gpu_data @ gpu_data
    gpu_time = time.time() - start
    
    print(f"CPU: {cpu_time:.3f}s")
    print(f"GPU: {gpu_time:.3f}s")
    print(f"Speedup: {cpu_time / gpu_time:.1f}x")
🔗 Next Steps
WASM Guide

EU LLM Guide

Deployment Guide

API Reference