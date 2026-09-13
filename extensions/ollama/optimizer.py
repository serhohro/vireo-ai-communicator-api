# ============================================================
# OLLAMA OPTIMIZER
# ============================================================
"""
Ollama optimization and management for Vireo.

Provides:
- GPU detection and optimization
- Model caching
- Auto-download
- Performance monitoring
"""

import os
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import lru_cache

logger = logging.getLogger(__name__)


class OllamaOptimizer:
    """Optimizer for Ollama models."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.models_dir = Path.home() / ".ollama" / "models"
        self.cache = {}
    
    def check_gpu(self) -> bool:
        """Check if GPU is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information."""
        if not self.check_gpu():
            return {"available": False}
        
        try:
            import torch
            return {
                "available": True,
                "count": torch.cuda.device_count(),
                "name": torch.cuda.get_device_name(0),
                "memory_mb": torch.cuda.get_device_properties(0).total_memory / 1e6,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def optimize_model(self, model_name: str) -> Dict[str, Any]:
        """Optimize model settings."""
        gpu_info = self.get_gpu_info()
        
        result = {
            "model": model_name,
            "optimized": False,
            "gpu_available": gpu_info.get("available", False),
            "recommendations": []
        }
        
        if gpu_info.get("available"):
            result["recommendations"].append("✅ GPU available — use 'num_gpu=1'")
            if gpu_info.get("memory_mb", 0) < 4000:
                result["recommendations"].append("⚠️ Limited VRAM — use smaller model (e.g., phi3:mini)")
        else:
            result["recommendations"].append("⚠️ No GPU — use smaller models")
        
        # Model-specific recommendations
        if "70b" in model_name and not gpu_info.get("available"):
            result["recommendations"].append("❌ 70B model requires GPU with 16GB+ VRAM")
        elif "70b" in model_name and gpu_info.get("available"):
            result["recommendations"].append("⚠️ 70B model requires 16GB+ VRAM")
        
        result["optimized"] = True
        return result
    
    @lru_cache(maxsize=100)
    def generate(self, prompt: str, model: str, **kwargs) -> str:
        """Generate with caching."""
        import requests
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_gpu": 1 if self.check_gpu() else 0,
                **kwargs
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return f"Error: {e}"
    
    def download_model(self, model_name: str) -> bool:
        """Download a model."""
        try:
            import requests
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"model": model_name},
                timeout=600
            )
            response.raise_for_status()
            logger.info(f"✅ Downloaded {model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {model_name}: {e}")
            return False
    
    def list_local_models(self) -> List[str]:
        """List locally available models."""
        try:
            import requests
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            return [m["name"] for m in response.json().get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def clear_cache(self):
        """Clear generation cache."""
        self.cache = {}
        self.generate.cache_clear()
        logger.info("✅ Ollama cache cleared")


class OllamaCache:
    """Cache for Ollama responses."""
    
    def __init__(self, cache_dir: str = "cache/ollama"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str) -> Optional[str]:
        """Get cached response."""
        cache_file = self.cache_dir / f"{hash(key)}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                return data.get("response")
            except:
                return None
        return None
    
    def set(self, key: str, value: str):
        """Cache a response."""
        cache_file = self.cache_dir / f"{hash(key)}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump({"response": value, "timestamp": time.time()}, f)
        except:
            pass
    
    def clear(self):
        """Clear cache."""
        import shutil
        shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("✅ Ollama cache cleared")