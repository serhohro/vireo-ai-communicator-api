"""
Vireo EU Models — європейські LLM провайдери
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ============================================================
# ЄВРОПЕЙСЬКІ МОДЕЛІ
# ============================================================

EUROPEAN_MODELS = {
    "mistral": {
        "name": "Mistral 7B",
        "provider": "Mistral AI",
        "country": "France",
        "type": "cloud",
        "license": "Apache 2.0",
        "url": "https://mistral.ai"
    },
    "bloom": {
        "name": "BLOOM",
        "provider": "Hugging Face",
        "country": "France",
        "type": "local",
        "license": "Responsible AI",
        "url": "https://huggingface.co/bigscience/bloom"
    },
    "openchat": {
        "name": "OpenChat",
        "provider": "LAION",
        "country": "Germany",
        "type": "local",
        "license": "MIT",
        "url": "https://openchat.de"
    },
    "gpt4all": {
        "name": "GPT-4All",
        "provider": "Nomic AI",
        "country": "EU",
        "type": "local",
        "license": "MIT",
        "url": "https://gpt4all.io"
    }
}

class EuropeanModelProvider:
    """Провайдер для європейських LLM."""
    
    def __init__(self, model_name: str):
        if model_name not in EUROPEAN_MODELS:
            raise ValueError(f"Unknown European model: {model_name}")
        
        self.model_info = EUROPEAN_MODELS[model_name]
        self.model_name = model_name
        self.country = self.model_info["country"]
    
    def get_info(self) -> Dict[str, Any]:
        """Отримати інформацію про модель."""
        return {
            "name": self.model_name,
            "provider": self.model_info["provider"],
            "country": self.model_info["country"],
            "type": self.model_info["type"],
            "license": self.model_info["license"]
        }
    
    def is_european(self) -> bool:
        """Перевірити, чи модель європейська."""
        return True
    
    def get_country(self) -> str:
        """Отримати країну походження."""
        return self.country