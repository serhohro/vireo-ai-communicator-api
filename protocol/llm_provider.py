"""LLM Provider for Vireo v2.0.1"""

from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import logging
import os
import json

logger = logging.getLogger(__name__)


class LLMResponse:
    """LLM response"""
    def __init__(self, text: str, tokens_used: int, cost_usd: float, model: str, provider: str):
        self.text = text
        self.tokens_used = tokens_used
        self.cost_usd = cost_usd
        self.model = model
        self.provider = provider


class LLMProvider(ABC):
    """Base LLM provider"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    def generate(self, prompt: str, model: str = "gpt-4", **kwargs) -> LLMResponse:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000)
            )
            
            return LLMResponse(
                text=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                cost_usd=self._estimate_cost(response.usage.total_tokens, model),
                model=model,
                provider="OpenAI"
            )
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        return self._models
    
    def _estimate_cost(self, tokens: int, model: str) -> float:
        rates = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.001
        }
        rate = rates.get(model, 0.01)
        return (tokens / 1000) * rate


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._models = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    
    def generate(self, prompt: str, model: str = "claude-3-sonnet", **kwargs) -> LLMResponse:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000)
            )
            
            return LLMResponse(
                text=response.content[0].text,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                cost_usd=self._estimate_cost(response.usage, model),
                model=model,
                provider="Anthropic"
            )
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        return self._models
    
    def _estimate_cost(self, usage, model: str) -> float:
        input_cost = usage.input_tokens * 0.000003
        output_cost = usage.output_tokens * 0.000015
        return input_cost + output_cost


class GoogleProvider(LLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self._models = ["gemini-pro", "gemini-pro-vision"]
    
    def generate(self, prompt: str, model: str = "gemini-pro", **kwargs) -> LLMResponse:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model_obj = genai.GenerativeModel(model)
            response = model_obj.generate_content(
                prompt,
                generation_config={
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_output_tokens": kwargs.get("max_tokens", 1000)
                }
            )
            
            return LLMResponse(
                text=response.text,
                tokens_used=len(response.text.split()),
                cost_usd=0.0001,
                model=model,
                provider="Google"
            )
        except Exception as e:
            logger.error(f"Google error: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        return self._models


class LLMProviderFactory:
    """Factory for LLM providers"""
    
    _providers: Dict[str, LLMProvider] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider: LLMProvider) -> None:
        cls._providers[name] = provider
    
    @classmethod
    def get_provider(cls, name: str) -> Optional[LLMProvider]:
        return cls._providers.get(name)
    
    @classmethod
    def get_all_providers(cls) -> List[str]:
        return list(cls._providers.keys())
    
    @classmethod
    def initialize(cls):
        if os.getenv("OPENAI_API_KEY"):
            cls.register_provider("openai", OpenAIProvider())
        if os.getenv("ANTHROPIC_API_KEY"):
            cls.register_provider("anthropic", AnthropicProvider())
        if os.getenv("GOOGLE_API_KEY"):
            cls.register_provider("google", GoogleProvider())


# Auto-initialize
LLMProviderFactory.initialize()