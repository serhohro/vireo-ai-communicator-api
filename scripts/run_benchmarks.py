#!/usr/bin/env python3
"""
Vireo Performance Benchmarks

Runs comprehensive benchmarks for Vireo components including:
- Wire format serialization/deserialization
- Cryptography (signing/verification)
- Protocol state machine
- JIT compilation
- GPU operations
"""

import os
import sys
import time
import json
import statistics
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
import asyncio
import multiprocessing
from dataclasses import dataclass, field

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.crypto import ed25519, blake2b
    from core.protocol import Protocol, Message, State
    from core.wire_format import WireFormat
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    print("⚠️ Core modules not available. Running limited benchmarks.")

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import numba
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False


@dataclass
class BenchmarkResult:
    """Benchmark result."""
    name: str
    iterations: int
    times: List[float] = field(default_factory=list)
    min_time: float = 0.0
    max_time: float = 0.0
    mean_time: float = 0.0
    median_time: float = 0.0
    std_time: float = 0.0
    ops_per_second: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def compute_stats(self):
        """Compute statistics from times."""
        if not self.times:
            return
        
        self.min_time = min(self.times)
        self.max_time = max(self.times)
        self.mean_time = statistics.mean(self.times)
        self.median_time = statistics.median(self.times)
        self.std_time = statistics.stdev(self.times) if len(self.times) > 1 else 0.0
        self.ops_per_second = 1.0 / (self.mean_time / 1_000_000)  # ops per second


class BenchmarkRunner:
    """Run benchmarks for Vireo components."""
    
    def __init__(self, iterations: int = 1000, warmup: int = 100):
        self.iterations = iterations
        self.warmup = warmup
        self.results: List[BenchmarkResult] = []
        
    def run_benchmark(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        iterations: Optional[int] = None,
        warmup: Optional[int] = None
    ) -> BenchmarkResult:
        """Run a single benchmark."""
        if kwargs is None:
            kwargs = {}
        
        iterations = iterations or self.iterations
        warmup = warmup or self.warmup
        
        result = BenchmarkResult(name=name, iterations=iterations)
        
        # Warmup
        for _ in range(warmup):
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"⚠️ Warmup error for {name}: {e}")
                break
        
        # Benchmark
        for _ in range(iterations):
            start = time.perf_counter_ns()
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"⚠️ Benchmark error for {name}: {e}")
                continue
            end = time.perf_counter_ns()
            result.times.append(end - start)
        
        result.compute_stats()
        self.results.append(result)
        
        return result
    
    def run_wire_format_benchmarks(self):
        """Benchmark wire format operations."""
        print("\n📦 Wire Format Benchmarks")
        print("-" * 40)
        
        if not HAS_CORE:
            print("⚠️ Core module not available, skipping wire format benchmarks")
            return
        
        wire = WireFormat()
        
        # Test data
        test_data = {
            "version": "3.0.0",
            "type": "propose",
            "id": "msg_1234567890",
            "sender": "did:vireo:alice",
            "recipient": "did:vireo:bob",
            "timestamp": 1700000000,
            "nonce": "n_abcdef123",
            "payload": {
                "task": "analyze_code",
                "parameters": {
                    "language": "python",
                    "depth": "full",
                    "timeout": 300
                },
                "contract": {
                    "price": 100,
                    "deadline": "2024-12-31",
                    "terms": ["quality", "timeliness", "security"]
                }
            }
        }
        
        # Serialization benchmark
        result = self.run_benchmark(
            "wire_serialize",
            wire.serialize,
            (test_data,),
            iterations=5000
        )
        print(f"  ✓ Serialize: {result.ops_per_second:,.0f} ops/sec")
        
        # Deserialization benchmark
        serialized = wire.serialize(test_data)
        result = self.run_benchmark(
            "wire_deserialize",
            wire.deserialize,
            (serialized,),
            iterations=5000
        )
        print(f"  ✓ Deserialize: {result.ops_per_second:,.0f} ops/sec")
        
        # Roundtrip benchmark
        result = self.run_benchmark(
            "wire_roundtrip",
            lambda: wire.deserialize(wire.serialize(test_data)),
            iterations=2000
        )
        print(f"  ✓ Roundtrip: {result.ops_per_second:,.0f} ops/sec")
    
    def run_crypto_benchmarks(self):
        """Benchmark cryptographic operations."""
        print("\n🔐 Cryptographic Benchmarks")
        print("-" * 40)
        
        if not HAS_CORE:
            print("⚠️ Core module not available, skipping crypto benchmarks")
            return
        
        # Generate key pair
        keypair = ed25519.Ed25519.generate()
        private_key = keypair.private_key
        public_key = keypair.public_key
        
        test_data = b"Hello, Vireo! This is a test message for benchmarking."
        
        # Signing benchmark
        result = self.run_benchmark(
            "ed25519_sign",
            ed25519.Ed25519.sign,
            (test_data, private_key),
            iterations=2000
        )
        print(f"  ✓ Ed25519 Sign: {result.ops_per_second:,.0f} ops/sec")
        
        # Verification benchmark
        signature = ed25519.Ed25519.sign(test_data, private_key)
        result = self.run_benchmark(
            "ed25519_verify",
            ed25519.Ed25519.verify,
            (test_data, signature, public_key),
            iterations=2000
        )
        print(f"  ✓ Ed25519 Verify: {result.ops_per_second:,.0f} ops/sec")
        
        # BLAKE2b benchmark
        result = self.run_benchmark(
            "blake2b",
            blake2b.blake2b,
            (test_data,),
            iterations=10000
        )
        print(f"  ✓ BLAKE2b: {result.ops_per_second:,.0f} ops/sec")
        
        # Full roundtrip
        def crypto_roundtrip():
            sig = ed25519.Ed25519.sign(test_data, private_key)
            return ed25519.Ed25519.verify(test_data, sig, public_key)
        
        result = self.run_benchmark(
            "crypto_roundtrip",
            crypto_roundtrip,
            iterations=1000
        )
        print(f"  ✓ Crypto Roundtrip: {result.ops_per_second:,.0f} ops/sec")
    
    def run_protocol_benchmarks(self):
        """Benchmark protocol operations."""
        print("\n📋 Protocol Benchmarks")
        print("-" * 40)
        
        if not HAS_CORE:
            print("⚠️ Core module not available, skipping protocol benchmarks")
            return
        
        protocol = Protocol()
        
        # State transitions
        def state_transition():
            protocol.reset()
            protocol.process("propose", {"task": "test"})
            protocol.process("commit", {"accepted": True})
            protocol.process("execute", {"data": "test"})
            return protocol.get_state()
        
        result = self.run_benchmark(
            "protocol_transitions",
            state_transition,
            iterations=5000
        )
        print(f"  ✓ State Transitions: {result.ops_per_second:,.0f} ops/sec")
        
        # Message validation
        message = {
            "type": "propose",
            "version": "3.0.0",
            "sender": "did:vireo:alice",
            "recipient": "did:vireo:bob",
            "payload": {"task": "test"}
        }
        
        result = self.run_benchmark(
            "message_validation",
            protocol.validate_message,
            (message,),
            iterations=10000
        )
        print(f"  ✓ Message Validation: {result.ops_per_second:,.0f} ops/sec")
    
    def run_gpu_benchmarks(self):
        """Benchmark GPU operations if available."""
        print("\n🎮 GPU Benchmarks")
        print("-" * 40)
        
        if not HAS_TORCH:
            print("⚠️ PyTorch not available, skipping GPU benchmarks")
            return
        
        if not torch.cuda.is_available():
            print("⚠️ CUDA not available, skipping GPU benchmarks")
            return
        
        # Matrix multiplication
        sizes = [128, 256, 512, 1024]
        
        for size in sizes:
            a = torch.randn(size, size, device="cuda")
            b = torch.randn(size, size, device="cuda")
            
            def matmul():
                return a @ b
            
            result = self.run_benchmark(
                f"gpu_matmul_{size}x{size}",
                matmul,
                iterations=100
            )
            print(f"  ✓ Matmul {size}x{size}: {result.ops_per_second:,.0f} ops/sec")
        
        # Tensor operations
        tensor = torch.randn(1000, 1000, device="cuda")
        
        def tensor_ops():
            x = tensor + tensor
            y = x * 2
            z = y.sum()
            return z
        
        result = self.run_benchmark(
            "gpu_tensor_ops",
            tensor_ops,
            iterations=1000
        )
        print(f"  ✓ Tensor Ops: {result.ops_per_second:,.0f} ops/sec")
    
    def run_jit_benchmarks(self):
        """Benchmark JIT compilation if available."""
        print("\n⚡ JIT Benchmarks")
        print("-" * 40)
        
        if HAS_NUMBA:
            @numba.jit(nopython=True)
            def jit_sum(arr):
                total = 0
                for x in arr:
                    total += x
                return total
            
            import numpy as np
            data = np.random.randn(10000)
            
            result = self.run_benchmark(
                "jit_sum",
                jit_sum,
                (data,),
                iterations=10000
            )
            print(f"  ✓ JIT Sum: {result.ops_per_second:,.0f} ops/sec")
            
            # Python comparison
            def python_sum(arr):
                total = 0
                for x in arr:
                    total += x
                return total
            
            result = self.run_benchmark(
                "python_sum",
                python_sum,
                (data,),
                iterations=1000
            )
            print(f"  ✓ Python Sum: {result.ops_per_second:,.0f} ops/sec")
            print(f"  🚀 JIT Speedup: {result.ops_per_second / jit_result.ops_per_second:.1f}x")
        else:
            print("⚠️ Numba not available, skipping JIT benchmarks")
    
    def run_all(self):
        """Run all benchmarks."""
        print("=" * 60)
        print("🌿 Vireo Performance Benchmarks v3.0.0")
        print(f"   Iterations: {self.iterations}")
        print(f"   Warmup: {self.warmup}")
        print(f"   Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        self.run_wire_format_benchmarks()
        self.run_crypto_benchmarks()
        self.run_protocol_benchmarks()
        self.run_gpu_benchmarks()
        self.run_jit_benchmarks()
        
        self.save_results()
        self.print_summary()
    
    def save_results(self, output_file: Optional[str] = None):
        """Save benchmark results to JSON."""
        if output_file is None:
            output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "version": "3.0.0",
            "timestamp": datetime.now().isoformat(),
            "iterations": self.iterations,
            "warmup": self.warmup,
            "results": [
                {
                    "name": r.name,
                    "iterations": r.iterations,
                    "min_us": r.min_time / 1000 if r.min_time else 0,
                    "max_us": r.max_time / 1000 if r.max_time else 0,
                    "mean_us": r.mean_time / 1000 if r.mean_time else 0,
                    "median_us": r.median_time / 1000 if r.median_time else 0,
                    "std_us": r.std_time / 1000 if r.std_time else 0,
                    "ops_per_second": r.ops_per_second,
                    "metadata": r.metadata
                }
                for r in self.results
            ]
        }
        
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\n📊 Results saved to: {output_file}")
    
    def print_summary(self):
        """Print summary of results."""
        print("\n" + "=" * 60)
        print("📊 Benchmark Summary")
        print("=" * 60)
        print(f"{'Benchmark':<30} {'Ops/sec':>15} {'Mean (µs)':>15}")
        print("-" * 60)
        
        for r in sorted(self.results, key=lambda x: x.name):
            if r.ops_per_second > 0:
                print(f"{r.name:<30} {r.ops_per_second:>15,.0f} {r.mean_time/1000:>15.2f}")
    
    def get_results(self) -> List[BenchmarkResult]:
        """Get all benchmark results."""
        return self.results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Vireo performance benchmarks")
    parser.add_argument(
        "-i", "--iterations",
        type=int,
        default=1000,
        help="Number of iterations per benchmark"
    )
    parser.add_argument(
        "-w", "--warmup",
        type=int,
        default=100,
        help="Number of warmup iterations"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--benchmark",
        choices=["wire", "crypto", "protocol", "gpu", "jit", "all"],
        default="all",
        help="Specific benchmark to run"
    )
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner(iterations=args.iterations, warmup=args.warmup)
    
    if args.benchmark == "all":
        runner.run_all()
    else:
        print(f"Running {args.benchmark} benchmarks...")
        getattr(runner, f"run_{args.benchmark}_benchmarks")()
        runner.save_results(args.output)


if __name__ == "__main__":
    main()