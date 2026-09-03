#!/usr/bin/env python3
# ============================================================
# VIREO MODEL BENCHMARK
# ============================================================
"""
Benchmark script for Vireo models.

Measures:
- Model loading time
- Inference speed
- Memory usage
- Token throughput
- CPU/GPU utilization
"""

import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class BenchmarkResult:
    """Benchmark result for a model."""
    model_name: str
    provider: str
    load_time_ms: float
    inference_time_ms: float
    tokens_per_second: float
    memory_used_mb: float
    success: bool
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results."""
    timestamp: str
    version: str
    results: List[BenchmarkResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "version": self.version,
            "results": [
                {
                    "model": r.model_name,
                    "provider": r.provider,
                    "load_time_ms": r.load_time_ms,
                    "inference_time_ms": r.inference_time_ms,
                    "tokens_per_second": r.tokens_per_second,
                    "memory_used_mb": r.memory_used_mb,
                    "success": r.success,
                    "error": r.error,
                    "details": r.details
                }
                for r in self.results
            ]
        }


# ============================================================
# BENCHMARK FUNCTIONS
# ============================================================

def get_memory_usage() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    except ImportError:
        return 0.0


def benchmark_load(model_name: str, provider: str = "ollama") -> Dict[str, Any]:
    """Benchmark model loading."""
    start_memory = get_memory_usage()
    start_time = time.perf_counter()
    
    try:
        if provider == "ollama":
            # Test Ollama model loading
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model_name, "prompt": "test", "stream": False},
                timeout=10
            )
            loaded = response.status_code == 200
        elif provider == "huggingface":
            # Test Hugging Face model loading
            from transformers import AutoModel
            model = AutoModel.from_pretrained(model_name)
            loaded = model is not None
        else:
            loaded = False
        
        load_time = (time.perf_counter() - start_time) * 1000
        end_memory = get_memory_usage()
        
        return {
            "success": loaded,
            "load_time_ms": load_time,
            "memory_mb": end_memory - start_memory,
            "error": None if loaded else "Failed to load model"
        }
    except Exception as e:
        return {
            "success": False,
            "load_time_ms": (time.perf_counter() - start_time) * 1000,
            "memory_mb": 0,
            "error": str(e)
        }


def benchmark_inference(model_name: str, provider: str = "ollama", 
                        prompt: str = "Hello, who are you?") -> Dict[str, Any]:
    """Benchmark model inference."""
    start_memory = get_memory_usage()
    start_time = time.perf_counter()
    
    try:
        if provider == "ollama":
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model_name, "prompt": prompt, "stream": False},
                timeout=60
            )
            if response.status_code == 200:
                result = response.json().get("response", "")
                tokens = len(result.split())
                inference_time = (time.perf_counter() - start_time) * 1000
                end_memory = get_memory_usage()
                
                return {
                    "success": True,
                    "inference_time_ms": inference_time,
                    "tokens": tokens,
                    "tokens_per_second": tokens / (inference_time / 1000) if inference_time > 0 else 0,
                    "memory_mb": end_memory - start_memory,
                    "error": None
                }
        elif provider == "huggingface":
            from transformers import pipeline
            pipe = pipeline("text-generation", model=model_name)
            result = pipe(prompt, max_new_tokens=50)
            inference_time = (time.perf_counter() - start_time) * 1000
            tokens = len(result[0]["generated_text"].split())
            
            return {
                "success": True,
                "inference_time_ms": inference_time,
                "tokens": tokens,
                "tokens_per_second": tokens / (inference_time / 1000) if inference_time > 0 else 0,
                "memory_mb": 0,
                "error": None
            }
        
        return {
            "success": False,
            "inference_time_ms": (time.perf_counter() - start_time) * 1000,
            "tokens": 0,
            "tokens_per_second": 0,
            "memory_mb": 0,
            "error": f"Unsupported provider: {provider}"
        }
    except Exception as e:
        return {
            "success": False,
            "inference_time_ms": (time.perf_counter() - start_time) * 1000,
            "tokens": 0,
            "tokens_per_second": 0,
            "memory_mb": 0,
            "error": str(e)
        }


def run_benchmark(model_name: str, provider: str = "ollama") -> BenchmarkResult:
    """Run full benchmark for a model."""
    logger.info(f"🧪 Benchmarking {model_name} ({provider})...")
    
    load_result = benchmark_load(model_name, provider)
    if not load_result["success"]:
        return BenchmarkResult(
            model_name=model_name,
            provider=provider,
            load_time_ms=load_result["load_time_ms"],
            inference_time_ms=0,
            tokens_per_second=0,
            memory_used_mb=load_result["memory_mb"],
            success=False,
            error=load_result["error"]
        )
    
    inference_result = benchmark_inference(model_name, provider)
    
    return BenchmarkResult(
        model_name=model_name,
        provider=provider,
        load_time_ms=load_result["load_time_ms"],
        inference_time_ms=inference_result["inference_time_ms"],
        tokens_per_second=inference_result.get("tokens_per_second", 0),
        memory_used_mb=load_result["memory_mb"] + inference_result.get("memory_mb", 0),
        success=inference_result["success"],
        error=inference_result.get("error"),
        details={
            "tokens": inference_result.get("tokens", 0)
        }
    )


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Benchmark Vireo models")
    parser.add_argument("--models", nargs="+", help="Models to benchmark")
    parser.add_argument("--all", action="store_true", help="Benchmark all models")
    parser.add_argument("--provider", default="ollama", help="Provider to use")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Default models
    default_models = [
        "llama3:8b",
        "mistral:7b",
        "phi3:mini",
        "qwen2.5-coder:latest"
    ]
    
    if args.all:
        models = default_models
    elif args.models:
        models = args.models
    else:
        models = default_models
    
    logger.info("=" * 60)
    logger.info("🚀 VIREO MODEL BENCHMARK")
    logger.info("=" * 60)
    logger.info(f"📋 Models: {', '.join(models)}")
    logger.info(f"📡 Provider: {args.provider}")
    logger.info("=" * 60)
    
    results = []
    for model in models:
        logger.info(f"\n🔍 Benchmarking {model}...")
        try:
            result = run_benchmark(model, args.provider)
            results.append(result)
            
            # Print summary
            if result.success:
                logger.info(f"  ✅ {model}")
                logger.info(f"     Load time: {result.load_time_ms:.2f}ms")
                logger.info(f"     Inference: {result.inference_time_ms:.2f}ms")
                logger.info(f"     Tokens/s: {result.tokens_per_second:.2f}")
                logger.info(f"     Memory: {result.memory_used_mb:.2f}MB")
            else:
                logger.error(f"  ❌ {model}: {result.error}")
        except Exception as e:
            logger.error(f"  ❌ {model}: {e}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 BENCHMARK SUMMARY")
    logger.info("=" * 60)
    
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    logger.info(f"✅ Successful: {len(successful)}")
    logger.info(f"❌ Failed: {len(failed)}")
    
    if successful:
        avg_load = sum(r.load_time_ms for r in successful) / len(successful)
        avg_inference = sum(r.inference_time_ms for r in successful) / len(successful)
        avg_tokens = sum(r.tokens_per_second for r in successful) / len(successful)
        avg_memory = sum(r.memory_used_mb for r in successful) / len(successful)
        
        logger.info(f"\n📊 Average metrics:")
        logger.info(f"   Load time: {avg_load:.2f}ms")
        logger.info(f"   Inference: {avg_inference:.2f}ms")
        logger.info(f"   Tokens/s: {avg_tokens:.2f}")
        logger.info(f"   Memory: {avg_memory:.2f}MB")
    
    # Save results
    if args.output:
        suite = BenchmarkSuite(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            version="2.0.2",
            results=results
        )
        
        with open(args.output, "w") as f:
            json.dump(suite.to_dict(), f, indent=2)
        logger.info(f"\n💾 Results saved to {args.output}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Benchmark complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()