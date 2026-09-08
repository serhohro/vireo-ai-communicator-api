# core/config.py
"""Vireo core configuration."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class Config:
    """Vireo configuration."""
    
    # Server
    port: int = 5000
    debug: bool = True
    secret_key: str = "vireo-v3-secret-key"
    
    # Database
    redis_url: str = "redis://localhost:6379"
    
    # Security
    auth_secret_key: str = "vireo-auth-secret-key"
    jwt_secret: str = "vireo-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60
    
    # LLM Providers
    mistral_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Features
    enable_wasm: bool = True
    enable_rust: bool = False
    enable_formal_verification: bool = True
    enable_mcp: bool = True
    enable_websocket: bool = True
    
    # Paths
    models_dir: str = "models/"
    keys_dir: str = "keys/"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return getattr(self, key, default)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            port=int(os.getenv("PORT", 5000)),
            debug=os.getenv("DEBUG", "True").lower() == "true",
            secret_key=os.getenv("SECRET_KEY", "vireo-v3-secret-key"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            auth_secret_key=os.getenv("AUTH_SECRET_KEY", "vireo-auth-secret-key"),
            jwt_secret=os.getenv("JWT_SECRET", "vireo-jwt-secret"),
            mistral_api_key=os.getenv("MISTRAL_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

_config: Optional[Config] = None

def get_config() -> Config:
    """Get configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config

def reload_config():
    """Reload configuration."""
    global _config
    _config = Config.from_env()