# ============================================================
# VIREO LLM CONFIGURATION
# ============================================================

import os
from typing import List, Dict, Any

# Спроба завантажити .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class LLMConfig:
    # ============================================================
    # ЗАГАЛЬНІ
    # ============================================================
    PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    MODE = os.getenv("LLM_MODE", "auto")
    
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
    
    # ============================================================
    # 1. OLLAMA
    # ============================================================
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:latest")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    
    # ============================================================
    # 2. CLAUDE (Anthropic)
    # ============================================================
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20241022")
    
    # ============================================================
    # 3. OPENAI
    # ============================================================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # ============================================================
    # 4. GOOGLE GEMINI
    # ============================================================
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    # ============================================================
    # 5. MISTRAL AI
    # ============================================================
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    
    # ============================================================
    # ПЕРЕВІРКА ДОСТУПНОСТІ
    # ============================================================
    
    @classmethod
    def is_ollama_available(cls) -> bool:
        try:
            import requests
            response = requests.get(f"{cls.OLLAMA_HOST}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @classmethod
    def is_claude_available(cls) -> bool:
        return bool(cls.ANTHROPIC_API_KEY)
    
    @classmethod
    def is_openai_available(cls) -> bool:
        return bool(cls.OPENAI_API_KEY)
    
    @classmethod
    def is_gemini_available(cls) -> bool:
        return bool(cls.GOOGLE_API_KEY)
    
    @classmethod
    def is_mistral_available(cls) -> bool:
        return bool(cls.MISTRAL_API_KEY)
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        providers = []
        if cls.is_ollama_available():
            providers.append("ollama")
        if cls.is_claude_available():
            providers.append("claude")
        if cls.is_openai_available():
            providers.append("openai")
        if cls.is_gemini_available():
            providers.append("gemini")
        if cls.is_mistral_available():
            providers.append("mistral")
        return providers
    
    @classmethod
    def get_provider_status(cls) -> Dict[str, Any]:
        return {
            "ollama": {
                "available": cls.is_ollama_available(),
                "model": cls.OLLAMA_MODEL,
                "free": True,
                "cost": "Безкоштовно"
            },
            "gemini": {
                "available": cls.is_gemini_available(),
                "model": cls.GEMINI_MODEL,
                "free": True,
                "cost": "Безкоштовно (60 зап/хв)"
            },
            "claude": {
                "available": cls.is_claude_available(),
                "model": cls.CLAUDE_MODEL,
                "free": False,
                "cost": "~$0.0015/запит"
            },
            "openai": {
                "available": cls.is_openai_available(),
                "model": cls.OPENAI_MODEL,
                "free": False,
                "cost": "~$0.002/запит"
            },
            "mistral": {
                "available": cls.is_mistral_available(),
                "model": cls.MISTRAL_MODEL,
                "free": False,
                "cost": "~$0.001/запит"
            }
        }