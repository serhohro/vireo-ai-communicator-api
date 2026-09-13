# ============================================================
# OLLAMA CACHE
# ============================================================
"""
Ollama caching utilities.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from functools import lru_cache

class OllamaCacheManager:
    """Manage Ollama cache with TTL support."""
    
    def __init__(self, cache_dir: str = "cache/ollama", ttl_seconds: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
    
    def _get_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key from prompt, model, and parameters."""
        import json
        data = {
            "prompt": prompt,
            "model": model,
            "params": kwargs
        }
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def get(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        """Get cached response."""
        key = self._get_cache_key(prompt, model, **kwargs)
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                
                # Check TTL
                if time.time() - data.get("timestamp", 0) > self.ttl_seconds:
                    return None
                
                return data.get("response")
            except:
                return None
        
        return None
    
    def set(self, prompt: str, model: str, response: str, **kwargs):
        """Cache a response."""
        key = self._get_cache_key(prompt, model, **kwargs)
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            with open(cache_file, "w") as f:
                json.dump({
                    "response": response,
                    "timestamp": time.time(),
                    "prompt": prompt[:100],
                    "model": model
                }, f)
        except:
            pass
    
    def clear(self):
        """Clear all cache."""
        import shutil
        shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files)
        
        return {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
        }