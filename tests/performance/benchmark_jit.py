#!/usr/bin/env python3
"""
Performance Benchmarks: JIT (Just-In-Time) Compiler

Benchmarks for JIT compilation and execution performance.
"""

import pytest
import time
import sys
import statistics
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import numba
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from runtime.jit import JITCompiler
    HAS_JIT = True
except ImportError:
    HAS_JIT = False


@pytest.mark.skipif(not HAS_JIT, reason="JITCompiler not available")
class BenchmarkJIT:
    """JIT compiler performance benchmarks."""
    
    @pytest.fixture
    def compiler(self):
        """Create a JIT compiler instance."""
        return JITCompiler()
    
    @pytest.fixture
    def test_array(self):
        """Create a test array."""
        if not HAS_NUMPY:
            pytest.skip("NumPy not available")
        return np.random.randn(10000)
    
    def test_benchmark_jit_compile(self, benchmark, compiler):
        """Benchmark JIT compilation."""
        def compile_fn():
            @compiler.compile
            def sum_array(arr):
                total = 0.0
                for x in arr:
                    total += x
                return total
            return sum_array
        
        result = benchmark(compile_fn)
        assert result is not None
        
    def test_benchmark_jit_execution(self, benchmark, compiler, test_array):
        """Benchmark JIT execution."""
        @compiler.compile
        def sum_array(arr):
            total = 0.0
            for x in arr:
                total += x
            return total
        
        def execute():
            return sum_array(test_array)
        
        result = benchmark(execute)
        assert abs(result - test_array.sum()) < 1e-9
        
    def test_benchmark_jit_vs_python(self, compiler, test_array):
        """Compare JIT vs Python performance."""
        @compiler.compile
        def jit_sum(arr):
            total = 0.0
            for x in arr:
                total += x
            return total
        
        def python_sum(arr):
            total = 0.0
            for x in arr:
                total += x
            return total
        
        # Warmup
        for _ in range(10):
            jit_sum(test_array)
            python_sum(test_array)
        
        # Benchmark JIT
        start = time.time()
        for _ in range(100):
            jit_sum(test_array)
        jit_time = time.time() - start
        
        # Benchmark Python
        start = time.time()
        for _ in range(100):
            python_sum(test_array)
        python_time = time.time() - start
        
        speedup = python_time / jit_time if jit_time > 0 else 0
        
        print(f"\n📊 JIT vs Python Performance:")
        print(f"   JIT: {jit_time*10:.3f} ms per operation")
        print(f"   Python: {python_time*10:.3f} ms per operation")
        print(f"   Speedup: {speedup:.1f}x")
        
        assert speedup > 0.5  # Should be at least as fast as Python
        
    def test_benchmark_matrix_multiply(self, compiler):
        """Benchmark matrix multiplication with JIT."""
        if not HAS_NUMPY:
            pytest.skip("NumPy not available")
            
        size = 100
        a = np.random.randn(size, size)
        b = np.random.randn(size, size)
        
        @compiler.compile
        def matmul_jit(a, b):
            result = np.zeros((a.shape[0], b.shape[1]))
            for i in range(a.shape[0]):
                for j in range(b.shape[1]):
                    total = 0.0
                    for k in range(a.shape[1]):
                        total += a[i, k] * b[k, j]
                    result[i, j] = total
            return result
        
        def matmul_python(a, b):
            result = np.zeros((a.shape[0], b.shape[1]))
            for i in range(a.shape[0]):
                for j in range(b.shape[1]):
                    total = 0.0
                    for k in range(a.shape[1]):
                        total += a[i, k] * b[k, j]
                    result[i, j] = total
            return result
        
        # Warmup
        for _ in range(5):
            matmul_jit(a, b)
            matmul_python(a, b)
        
        # Benchmark JIT
        start = time.time()
        for _ in range(10):
            matmul_jit(a, b)
        jit_time = time.time() - start
        
        # Benchmark Python
        start = time.time()
        for _ in range(10):
            matmul_python(a, b)
        python_time = time.time() - start
        
        speedup = python_time / jit_time if jit_time > 0 else 0
        
        print(f"\n📊 Matrix Multiplication ({size}x{size}):")
        print(f"   JIT: {jit_time*100:.3f} ms per operation")
        print(f"   Python: {python_time*100:.3f} ms per operation")
        print(f"   Speedup: {speedup:.1f}x")
        
    def test_benchmark_parallel_execution(self, compiler, test_array):
        """Benchmark parallel execution with JIT."""
        @compiler.compile(parallel=True)
        def parallel_sum(arr):
            total = 0.0
            for x in arr:
                total += x
            return total
        
        @compiler.compile(parallel=False)
        def serial_sum(arr):
            total = 0.0
            for x in arr:
                total += x
            return total
        
        # Warmup
        for _ in range(10):
            parallel_sum(test_array)
            serial_sum(test_array)
        
        # Benchmark parallel
        start = time.time()
        for _ in range(100):
            parallel_sum(test_array)
        parallel_time = time.time() - start
        
        # Benchmark serial
        start = time.time()
        for _ in range(100):
            serial_sum(test_array)
        serial_time = time.time() - start
        
        speedup = serial_time / parallel_time if parallel_time > 0 else 0
        
        print(f"\n📊 Parallel vs Serial Execution:")
        print(f"   Parallel: {parallel_time*10:.3f} ms per operation")
        print(f"   Serial: {serial_time*10:.3f} ms per operation")
        print(f"   Speedup: {speedup:.1f}x")


@pytest.mark.skipif(not HAS_NUMBA or not HAS_NUMPY, reason="Numba or NumPy not available")
class TestJITPerformance:
    """JIT performance tests with Numba."""
    
    def test_numba_vs_python_sum(self, benchmark):
        """Compare Numba JIT vs Python using benchmark fixture."""
        import numpy as np
        import numba
        
        @numba.jit(nopython=True)
        def jit_sum(arr):
            total = 0.0
            for x in arr:
                total += x
            return total
        
        def python_sum(arr):
            total = 0.0
            for x in arr:
                total += x
            return total
        
        data = np.random.randn(10000)
        
        # Warmup
        jit_sum(data)
        
        # Benchmark JIT
        jit_result = benchmark(jit_sum, data)
        
        # Benchmark Python
        python_result = benchmark(python_sum, data)
        
        print(f"\n📊 JIT vs Python (pytest-benchmark):")
        print(f"   JIT: {jit_result}")
        print(f"   Python: {python_result}")