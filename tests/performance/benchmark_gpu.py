#!/usr/bin/env python3
"""
Performance Benchmarks: GPU

Benchmarks for GPU acceleration performance.
"""

import pytest
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    from runtime.gpu import CUDA, Metal, ROCm
    HAS_GPU = True
except ImportError:
    HAS_GPU = False


@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch not available")
@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
class BenchmarkGPU:
    """GPU performance benchmarks."""
    
    @pytest.fixture
    def device(self):
        """Get CUDA device."""
        return torch.device("cuda")
    
    @pytest.fixture
    def cpu_device(self):
        """Get CPU device."""
        return torch.device("cpu")
    
    def test_benchmark_gpu_vs_cpu_matmul(self, device, cpu_device):
        """Benchmark matrix multiplication on GPU vs CPU."""
        sizes = [128, 256, 512, 1024]
        results = {}
        
        for size in sizes:
            a = torch.randn(size, size)
            b = torch.randn(size, size)
            
            # CPU
            start = time.time()
            for _ in range(10):
                torch.matmul(a, b)
            cpu_time = time.time() - start
            
            # GPU
            a_gpu = a.to(device)
            b_gpu = b.to(device)
            
            # Warmup
            for _ in range(5):
                torch.matmul(a_gpu, b_gpu)
            
            start = time.time()
            for _ in range(10):
                torch.matmul(a_gpu, b_gpu)
            gpu_time = time.time() - start
            
            speedup = cpu_time / gpu_time if gpu_time > 0 else 0
            results[size] = {"cpu": cpu_time, "gpu": gpu_time, "speedup": speedup}
        
        print(f"\n📊 GPU vs CPU Matrix Multiplication:")
        print(f"{'Size':<8} {'CPU (ms)':<12} {'GPU (ms)':<12} {'Speedup':<10}")
        print("-" * 50)
        for size, result in results.items():
            print(f"{size:<8} {result['cpu']*100:.2f}     {result['gpu']*100:.2f}     {result['speedup']:.1f}x")
            
        # GPU should be faster for larger matrices
        assert results[1024]["speedup"] > 1.0
        
    def test_benchmark_gpu_tensor_ops(self, device, cpu_device):
        """Benchmark tensor operations on GPU vs CPU."""
        size = 10000
        
        # CPU
        a_cpu = torch.randn(size, size)
        b_cpu = torch.randn(size, size)
        
        start = time.time()
        for _ in range(5):
            c_cpu = a_cpu + b_cpu
            d_cpu = c_cpu * 2
            e_cpu = d_cpu.sum()
        cpu_time = time.time() - start
        
        # GPU
        a_gpu = torch.randn(size, size, device=device)
        b_gpu = torch.randn(size, size, device=device)
        
        # Warmup
        for _ in range(3):
            c_gpu = a_gpu + b_gpu
            d_gpu = c_gpu * 2
            e_gpu = d_gpu.sum()
        
        start = time.time()
        for _ in range(5):
            c_gpu = a_gpu + b_gpu
            d_gpu = c_gpu * 2
            e_gpu = d_gpu.sum()
        gpu_time = time.time() - start
        
        speedup = cpu_time / gpu_time if gpu_time > 0 else 0
        
        print(f"\n📊 GPU Tensor Operations:")
        print(f"   CPU: {cpu_time*200:.3f} ms per operation")
        print(f"   GPU: {gpu_time*200:.3f} ms per operation")
        print(f"   Speedup: {speedup:.1f}x")
        
    def test_benchmark_gpu_memory_transfer(self, device):
        """Benchmark CPU-GPU memory transfer."""
        sizes = [1024, 10240, 102400, 1024000]
        results = {}
        
        for size in sizes:
            # CPU to GPU
            cpu_data = torch.randn(size)
            
            start = time.time()
            for _ in range(10):
                gpu_data = cpu_data.to(device)
            cpu_to_gpu = time.time() - start
            
            # GPU to CPU
            gpu_data = torch.randn(size, device=device)
            
            start = time.time()
            for _ in range(10):
                cpu_data = gpu_data.cpu()
            gpu_to_cpu = time.time() - start
            
            results[size] = {
                "cpu_to_gpu": cpu_to_gpu / 10 * 1000,
                "gpu_to_cpu": gpu_to_cpu / 10 * 1000
            }
        
        print(f"\n📊 GPU Memory Transfer (ms per operation):")
        print(f"{'Size':<12} {'CPU→GPU (ms)':<15} {'GPU→CPU (ms)':<15}")
        print("-" * 45)
        for size, result in results.items():
            print(f"{size:<12} {result['cpu_to_gpu']:.3f}        {result['gpu_to_cpu']:.3f}")
            
    def test_benchmark_gpu_batch_processing(self, device):
        """Benchmark batch processing on GPU."""
        batch_sizes = [1, 8, 32, 64, 128]
        results = {}
        
        for batch_size in batch_sizes:
            data = torch.randn(batch_size, 1000, 1000)
            
            # CPU
            cpu_data = data
            start = time.time()
            for _ in range(3):
                result_cpu = torch.matmul(cpu_data, cpu_data.transpose(1, 2))
            cpu_time = time.time() - start
            
            # GPU
            gpu_data = data.to(device)
            
            # Warmup
            for _ in range(2):
                torch.matmul(gpu_data, gpu_data.transpose(1, 2))
            
            start = time.time()
            for _ in range(3):
                result_gpu = torch.matmul(gpu_data, gpu_data.transpose(1, 2))
            gpu_time = time.time() - start
            
            speedup = cpu_time / gpu_time if gpu_time > 0 else 0
            results[batch_size] = {"cpu": cpu_time, "gpu": gpu_time, "speedup": speedup}
        
        print(f"\n📊 GPU Batch Processing:")
        print(f"{'Batch':<8} {'CPU (ms)':<12} {'GPU (ms)':<12} {'Speedup':<10}")
        print("-" * 50)
        for batch_size, result in results.items():
            print(f"{batch_size:<8} {result['cpu']*333:.2f}     {result['gpu']*333:.2f}     {result['speedup']:.1f}x")


@pytest.mark.skipif(not HAS_GPU, reason="GPU runtime not available")
class TestGPUPerformance:
    """GPU performance tests."""
    
    def test_gpu_available(self):
        """Test that GPU is available."""
        import torch
        assert torch.cuda.is_available() is True
        
    def test_gpu_device_count(self):
        """Test GPU device count."""
        import torch
        count = torch.cuda.device_count()
        assert count > 0
        print(f"\n📊 Available GPUs: {count}")
        for i in range(count):
            print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")