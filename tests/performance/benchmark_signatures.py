#!/usr/bin/env python3
"""
Performance Benchmarks: Signatures

Benchmarks for cryptographic signature operations.
"""

import pytest
import time
import sys
import statistics
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from core.crypto import ed25519, blake2b
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    print("⚠️ Core modules not available, running limited benchmarks")


class BenchmarkSignatures:
    """Signature performance benchmarks."""
    
    @pytest.fixture
    def key_pair(self):
        """Generate a key pair for benchmarks."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
        return ed25519.Ed25519.generate()
    
    @pytest.fixture
    def test_data(self):
        """Create test data for benchmarks."""
        return b"Hello, Vireo! This is a test message for signature benchmarking." * 10
    
    def test_benchmark_key_generation(self, benchmark):
        """Benchmark key pair generation."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        def generate():
            return ed25519.Ed25519.generate()
        
        result = benchmark(generate)
        assert result is not None
        assert len(result.private_key) == 32
        assert len(result.public_key) == 32
        
    def test_benchmark_signing(self, benchmark, key_pair, test_data):
        """Benchmark signing."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        def sign():
            return ed25519.Ed25519.sign(test_data, key_pair.private_key)
        
        result = benchmark(sign)
        assert len(result) == 64
        
    def test_benchmark_verification(self, benchmark, key_pair, test_data):
        """Benchmark verification."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        signature = ed25519.Ed25519.sign(test_data, key_pair.private_key)
        
        def verify():
            return ed25519.Ed25519.verify(test_data, signature, key_pair.public_key)
        
        result = benchmark(verify)
        assert result is True
        
    def test_benchmark_blake2b(self, benchmark, test_data):
        """Benchmark BLAKE2b hashing."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        def hash_data():
            return blake2b.blake2b(test_data)
        
        result = benchmark(hash_data)
        assert len(result) == 32
        
    def test_benchmark_blake2b_64(self, benchmark, test_data):
        """Benchmark BLAKE2b with 64-byte digest."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        def hash_64():
            return blake2b.blake2b(test_data, digest_size=64)
        
        result = benchmark(hash_64)
        assert len(result) == 64
        
    def test_benchmark_sign_verify_roundtrip(self, benchmark, key_pair, test_data):
        """Benchmark full sign/verify roundtrip."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        def roundtrip():
            sig = ed25519.Ed25519.sign(test_data, key_pair.private_key)
            return ed25519.Ed25519.verify(test_data, sig, key_pair.public_key)
        
        result = benchmark(roundtrip)
        assert result is True
        
    def test_benchmark_concurrent_signing(self, key_pair, test_data):
        """Benchmark concurrent signing."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        import concurrent.futures
        import time
        
        def sign_worker():
            return ed25519.Ed25519.sign(test_data, key_pair.private_key)
        
        # Run concurrent signing
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(sign_worker) for _ in range(100)]
            results = [f.result() for f in futures]
        signing_time = time.time() - start
        
        # Verify all signatures
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(
                    ed25519.Ed25519.verify,
                    test_data,
                    sig,
                    key_pair.public_key
                )
                for sig in results
            ]
            verify_results = [f.result() for f in futures]
        verify_time = time.time() - start
        
        assert all(verify_results)
        
        print(f"\n📊 Concurrent Signature Benchmarks:")
        print(f"   Sign 100 ops: {signing_time:.3f}s ({100/signing_time:.1f} ops/sec)")
        print(f"   Verify 100 ops: {verify_time:.3f}s ({100/verify_time:.1f} ops/sec)")
        
    def test_benchmark_different_sizes(self, key_pair):
        """Benchmark signing different message sizes."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        sizes = [64, 256, 1024, 4096, 16384]
        results = {}
        
        for size in sizes:
            data = b"X" * size
            start = time.time()
            for _ in range(100):
                sig = ed25519.Ed25519.sign(data, key_pair.private_key)
                ed25519.Ed25519.verify(data, sig, key_pair.public_key)
            elapsed = time.time() - start
            results[size] = elapsed / 100
        
        print(f"\n📊 Message Size Benchmarks:")
        for size, avg in results.items():
            print(f"   {size} bytes: {avg*1000:.3f} ms per operation")
            
        assert results[64] < results[16384]  # Larger messages take slightly longer


class TestSignaturePerformance:
    """Signature performance tests with pytest-benchmark."""
    
    def test_key_gen_performance(self, benchmark):
        """Test key generation performance."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        benchmark(ed25519.Ed25519.generate)
        
    def test_sign_performance(self, benchmark):
        """Test signing performance."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        key_pair = ed25519.Ed25519.generate()
        data = b"Test data for signing performance"
        
        benchmark(ed25519.Ed25519.sign, data, key_pair.private_key)
        
    def test_verify_performance(self, benchmark):
        """Test verification performance."""
        if not HAS_CORE:
            pytest.skip("Core modules not available")
            
        key_pair = ed25519.Ed25519.generate()
        data = b"Test data for verification performance"
        signature = ed25519.Ed25519.sign(data, key_pair.private_key)
        
        benchmark(ed25519.Ed25519.verify, data, signature, key_pair.public_key)