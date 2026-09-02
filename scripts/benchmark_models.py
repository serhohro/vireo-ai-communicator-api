#!/usr/bin/env python3
"""Benchmark Vireo performance

Usage:
    python scripts/benchmark_models.py [--iterations N] [--output OUTPUT]
"""

import sys
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
import statistics

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent.base import BaseAgent
from core.agent.registry import AgentRegistry
from core.contract.contract import Contract, Terms, Obligation
from core.execution.runner import ExecutionRunner
from core.verification.verifier import Verifier


class BenchmarkAgent(BaseAgent):
    """Simple agent for benchmarking"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.register_capability("echo", self.echo)
        self.register_capability("compute", self.compute)
        self.register_capability("sleep", self.sleep)
    
    def echo(self, message: str) -> str:
        return message
    
    def compute(self, a: float, b: float, operation: str = "add") -> float:
        ops = {
            "add": lambda: a + b,
            "sub": lambda: a - b,
            "mul": lambda: a * b,
            "div": lambda: a / b if b != 0 else 0
        }
        return ops.get(operation, lambda: 0)()
    
    def sleep(self, seconds: float) -> str:
        time.sleep(seconds)
        return f"Slept for {seconds}s"
    
    def start(self):
        pass
    
    def stop(self):
        pass


def benchmark_capability_execution(iterations: int = 100) -> Dict[str, Any]:
    """Benchmark capability execution"""
    print(f"🏃 Benchmarking capability execution ({iterations} iterations)...")
    
    agent = BenchmarkAgent("benchmark")
    registry = AgentRegistry()
    registry.register(agent)
    
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        result = agent.execute("compute", {"a": 10, "b": 5, "operation": "add"})
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        "name": "capability_execution",
        "iterations": iterations,
        "avg_time_ms": statistics.mean(times) * 1000,
        "min_time_ms": min(times) * 1000,
        "max_time_ms": max(times) * 1000,
        "std_dev_ms": statistics.stdev(times) * 1000,
    }


def benchmark_contract_execution(iterations: int = 50) -> Dict[str, Any]:
    """Benchmark contract execution"""
    print(f"🏃 Benchmarking contract execution ({iterations} iterations)...")
    
    agent1 = BenchmarkAgent("agent1")
    agent2 = BenchmarkAgent("agent2")
    
    registry = AgentRegistry()
    registry.register(agent1)
    registry.register(agent2)
    
    runner = ExecutionRunner()
    runner.register_executor("compute", agent1.compute)
    runner.register_executor("echo", agent2.echo)
    
    times = []
    
    for _ in range(iterations):
        contract = Contract(
            contract_id=f"benchmark_{_+1}",
            parties=["agent1", "agent2"],
            terms=Terms(max_tokens=100, timeout_sec=10),
            obligations={
                "agent1": Obligation(
                    action="compute",
                    input={"a": 10, "b": 5, "operation": "add"}
                ),
                "agent2": Obligation(
                    action="echo",
                    input={"message": "$ref.agent1.result"}
                )
            }
        )
        
        start = time.perf_counter()
        result = runner.execute_contract(contract)
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        "name": "contract_execution",
        "iterations": iterations,
        "avg_time_ms": statistics.mean(times) * 1000,
        "min_time_ms": min(times) * 1000,
        "max_time_ms": max(times) * 1000,
        "std_dev_ms": statistics.stdev(times) * 1000,
    }


def benchmark_verification(iterations: int = 50) -> Dict[str, Any]:
    """Benchmark verification"""
    print(f"🏃 Benchmarking verification ({iterations} iterations)...")
    
    verifier = Verifier()
    
    times = []
    
    for _ in range(iterations):
        contract = Contract(
            contract_id=f"verify_{_+1}",
            parties=["agent1", "agent2"],
            terms=Terms(max_tokens=100),
            obligations={
                "agent1": Obligation(action="compute", input={}),
                "agent2": Obligation(action="echo", input={})
            },
            signatures={"agent1": "sig1", "agent2": "sig2"}
        )
        
        results = {
            "agent1": {"success": True, "result": {"value": 15}},
            "agent2": {"success": True, "result": {"message": "done"}}
        }
        
        start = time.perf_counter()
        result = verifier.verify_contract(contract, results)
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        "name": "verification",
        "iterations": iterations,
        "avg_time_ms": statistics.mean(times) * 1000,
        "min_time_ms": min(times) * 1000,
        "max_time_ms": max(times) * 1000,
        "std_dev_ms": statistics.stdev(times) * 1000,
    }


def run_benchmarks(iterations: int = 50) -> Dict[str, Any]:
    """Run all benchmarks"""
    print("\n" + "="*60)
    print("🔬 Vireo Performance Benchmark")
    print("="*60 + "\n")
    
    results = []
    
    # Capability execution
    results.append(benchmark_capability_execution(iterations))
    
    # Contract execution
    results.append(benchmark_contract_execution(iterations // 2))
    
    # Verification
    results.append(benchmark_verification(iterations // 2))
    
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": "2.0.1",
        "iterations": iterations,
        "results": results
    }


def format_results(results: Dict[str, Any]) -> str:
    """Format results for display"""
    output = []
    output.append("📊 Benchmark Results")
    output.append("="*60)
    output.append(f"Timestamp: {results['timestamp']}")
    output.append(f"Version: {results['version']}")
    output.append(f"Iterations: {results['iterations']}")
    output.append("")
    output.append("-"*60)
    
    for result in results["results"]:
        output.append(f"\n🔹 {result['name'].replace('_', ' ').title()}:")
        output.append(f"   Average: {result['avg_time_ms']:.2f} ms")
        output.append(f"   Min: {result['min_time_ms']:.2f} ms")
        output.append(f"   Max: {result['max_time_ms']:.2f} ms")
        output.append(f"   Std Dev: {result['std_dev_ms']:.2f} ms")
    
    output.append("")
    output.append("="*60)
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Benchmark Vireo performance")
    parser.add_argument("--iterations", type=int, default=50, help="Number of iterations")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    results = run_benchmarks(args.iterations)
    
    if args.json:
        print(json.dumps(results, indent=2))
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
    else:
        print(format_results(results))
        if args.output:
            with open(args.output, 'w') as f:
                f.write(format_results(results))


if __name__ == "__main__":
    main()