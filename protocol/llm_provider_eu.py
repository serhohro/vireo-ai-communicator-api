"""European LLM Providers for Vireo v2.0.1

Supports European AI providers for data sovereignty and compliance.
"""

from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import logging
import os
import json
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """LLM response"""
    text: str
    tokens_used: int
    cost_usd: float
    model: str
    provider: str
    metadata: Dict[str, Any]


class EuropeanLLMProvider(ABC):
    """Base class for European LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def region(self) -> str:
        pass


class MistralProvider(EuropeanLLMProvider):
    """Mistral AI provider (France)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.base_url = "https://api.mistral.ai/v1"
        self._models = ["mistral-tiny", "mistral-small", "mistral-medium", "mistral-large"]
        self._region = "France"
        self._logger = logging.getLogger(__name__)
    
    @property
    def provider_name(self) -> str:
        return "Mistral"
    
    @property
    def region(self) -> str:
        return self._region
    
    def get_available_models(self) -> List[str]:
        return self._models
    
    def generate(self, prompt: str, model: str = "mistral-medium", **kwargs) -> LLMResponse:
        """Generate text using Mistral AI"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return LLMResponse(
                text=result["choices"][0]["message"]["content"],
                tokens_used=result["usage"]["total_tokens"],
                cost_usd=self._estimate_cost(result["usage"]["total_tokens"], model),
                model=model,
                provider=self.provider_name,
                metadata=result
            )
        except Exception as e:
            self._logger.error(f"Mistral API error: {e}")
            raise
    
    def _estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost based on model"""
        rates = {
            "mistral-tiny": 0.00025,
            "mistral-small": 0.0005,
            "mistral-medium": 0.001,
            "mistral-large": 0.002,
        }
        rate = rates.get(model, 0.001)
        return (tokens / 1000) * rate


class AlephAlphaProvider(EuropeanLLMProvider):
    """Aleph Alpha provider (Germany)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALEPH_ALPHA_API_KEY")
        self.base_url = "https://api.aleph-alpha.com"
        self._models = ["luminous-base", "luminous-extended", "luminous-supreme"]
        self._region = "Germany"
        self._logger = logging.getLogger(__name__)
    
    @property
    def provider_name(self) -> str:
        return "Aleph Alpha"
    
    @property
    def region(self) -> str:
        return self._region
    
    def get_available_models(self) -> List[str]:
        return self._models
    
    def generate(self, prompt: str, model: str = "luminous-base", **kwargs) -> LLMResponse:
        """Generate text using Aleph Alpha"""
        url = f"{self.base_url}/complete"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "prompt": prompt,
            "maximum_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return LLMResponse(
                text=result["completions"][0]["completion"],
                tokens_used=result["usage"]["total_tokens"],
                cost_usd=self._estimate_cost(result["usage"]["total_tokens"], model),
                model=model,
                provider=self.provider_name,
                metadata=result
            )
        except Exception as e:
            self._logger.error(f"Aleph Alpha API error: {e}")
            raise
    
    def _estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost based on model"""
        rates = {
            "luminous-base": 0.0003,
            "luminous-extended": 0.0008,
            "luminous-supreme": 0.002,
        }
        rate = rates.get(model, 0.0005)
        return (tokens / 1000) * rate


class CohereProvider(EuropeanLLMProvider):
    """Cohere provider (UK/Switzerland)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        self.base_url = "https://api.cohere.ai/v1"
        self._models = ["command", "command-light", "command-nightly"]
        self._region = "Switzerland"
        self._logger = logging.getLogger(__name__)
    
    @property
    def provider_name(self) -> str:
        return "Cohere"
    
    @property
    def region(self) -> str:
        return self._region
    
    def get_available_models(self) -> List[str]:
        return self._models
    
    def generate(self, prompt: str, model: str = "command", **kwargs) -> LLMResponse:
        """Generate text using Cohere"""
        url = f"{self.base_url}/generate"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return LLMResponse(
                text=result["generations"][0]["text"],
                tokens_used=result["meta"]["billed_units"]["input_tokens"] + 
                           result["meta"]["billed_units"]["output_tokens"],
                cost_usd=self._estimate_cost(result),
                model=model,
                provider=self.provider_name,
                metadata=result
            )
        except Exception as e:
            self._logger.error(f"Cohere API error: {e}")
            raise
    
    def _estimate_cost(self, result: Dict) -> float:
        """Estimate cost from result"""
        units = result["meta"]["billed_units"]
        input_tokens = units.get("input_tokens", 0)
        output_tokens = units.get("output_tokens", 0)
        return ((input_tokens + output_tokens) / 1000) * 0.0005


class StabilityAIProvider(EuropeanLLMProvider):
    """Stability AI provider (UK)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("STABILITY_AI_API_KEY")
        self.base_url = "https://api.stability.ai/v1"
        self._models = ["stablelm-zephyr-3b"]
        self._region = "United Kingdom"
        self._logger = logging.getLogger(__name__)
    
    @property
    def provider_name(self) -> str:
        return "Stability AI"
    
    @property
    def region(self) -> str:
        return self._region
    
    def get_available_models(self) -> List[str]:
        return self._models
    
    def generate(self, prompt: str, model: str = "stablelm-zephyr-3b", **kwargs) -> LLMResponse:
        """Generate text using Stability AI"""
        url = f"{self.base_url}/generation/{model}/text"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "text_prompts": [{"text": prompt}],
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return LLMResponse(
                text=result["choices"][0]["text"],
                tokens_used=len(result["choices"][0]["text"].split()),
                cost_usd=0.0,  # Not publicly available
                model=model,
                provider=self.provider_name,
                metadata=result
            )
        except Exception as e:
            self._logger.error(f"Stability AI API error: {e}")
            raise


class EULLMProviderFactory:
    """Factory for European LLM providers"""
    
    _providers: Dict[str, EuropeanLLMProvider] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider: EuropeanLLMProvider) -> None:
        cls._providers[name] = provider
    
    @classmethod
    def get_provider(cls, name: str) -> Optional[EuropeanLLMProvider]:
        return cls._providers.get(name)
    
    @classmethod
    def get_all_providers(cls) -> List[str]:
        return list(cls._providers.keys())
    
    @classmethod
    def get_providers_by_region(cls, region: str) -> List[EuropeanLLMProvider]:
        return [p for p in cls._providers.values() if p.region == region]
    
    @classmethod
    def initialize(cls):
        """Initialize all European providers"""
        # Check if API keys are available
        if os.getenv("MISTRAL_API_KEY"):
            cls.register_provider("mistral", MistralProvider())
        if os.getenv("ALEPH_ALPHA_API_KEY"):
            cls.register_provider("aleph_alpha", AlephAlphaProvider())
        if os.getenv("COHERE_API_KEY"):
            cls.register_provider("cohere", CohereProvider())
        if os.getenv("STABILITY_AI_API_KEY"):
            cls.register_provider("stability_ai", StabilityAIProvider())
        
        logger.info(f"Initialized {len(cls._providers)} European LLM providers")


# Auto-initialize
EULLMProviderFactory.initialize()