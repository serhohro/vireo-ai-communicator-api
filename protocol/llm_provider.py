# [file name]: protocol/llm_provider.py
# ============================================================
# LLM PROVIDER - ПІДТРИМКА ВСІХ ПРОВАЙДЕРІВ
# Ollama | Claude | OpenAI | Gemini | Mistral
# ============================================================

import json
import logging
from typing import Optional, Dict, Any, List

from .config import LLMConfig

logger = logging.getLogger("vireo.llm_provider")


class LLMProvider:
    """Універсальний LLM провайдер."""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or LLMConfig.PROVIDER
        self._clients = {}
        self._initialized = {}
        self._init_all_providers()
    
    def _init_all_providers(self):
        """Ініціалізує всі доступні провайдери."""
        # Ollama
        self._init_ollama()
        
        # Claude
        if LLMConfig.is_claude_available():
            self._init_claude()
        
        # OpenAI
        if LLMConfig.is_openai_available():
            self._init_openai()
        
        # Gemini
        if LLMConfig.is_gemini_available():
            self._init_gemini()
        
        # Mistral
        if LLMConfig.is_mistral_available():
            self._init_mistral()
    
    def _init_ollama(self):
        """Ініціалізація Ollama."""
        try:
            import ollama
            self._clients['ollama'] = ollama.Client(
                host=LLMConfig.OLLAMA_HOST
            )
            self._initialized['ollama'] = True
            logger.info(f"✅ Ollama client initialized (model: {LLMConfig.OLLAMA_MODEL})")
        except Exception as e:
            logger.warning(f"⚠️ Ollama initialization error: {e}")
            self._initialized['ollama'] = False
    
    def _init_claude(self):
        try:
            import anthropic
            self._clients['claude'] = anthropic.Anthropic(
                api_key=LLMConfig.ANTHROPIC_API_KEY
            )
            self._initialized['claude'] = True
            logger.info("✅ Claude client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Claude error: {e}")
            self._initialized['claude'] = False
    
    def _init_openai(self):
        try:
            from openai import OpenAI
            self._clients['openai'] = OpenAI(
                api_key=LLMConfig.OPENAI_API_KEY
            )
            self._initialized['openai'] = True
            logger.info("✅ OpenAI client initialized")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI error: {e}")
            self._initialized['openai'] = False
    
    def _init_gemini(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=LLMConfig.GOOGLE_API_KEY)
            self._clients['gemini'] = genai
            self._initialized['gemini'] = True
            logger.info("✅ Gemini client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Gemini error: {e}")
            self._initialized['gemini'] = False
    
    def _init_mistral(self):
        try:
            from mistralai.client import MistralClient
            self._clients['mistral'] = MistralClient(
                api_key=LLMConfig.MISTRAL_API_KEY
            )
            self._initialized['mistral'] = True
            logger.info("✅ Mistral client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Mistral error: {e}")
            self._initialized['mistral'] = False
    
    def is_available(self, provider: Optional[str] = None) -> bool:
        provider = provider or self.provider
        return self._initialized.get(provider, False)
    
    def get_available_providers(self) -> List[str]:
        return [p for p in self._initialized if self._initialized[p]]
    
    def generate(self, system_prompt: str, user_prompt: str, task: Optional[str] = None,
                 max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Генерує відповідь через обраного провайдера."""
        
        # Проста реалізація для Ollama
        if self.provider == "ollama" or self.is_available("ollama"):
            return self._generate_ollama(system_prompt, user_prompt, max_tokens, temperature)
        
        # Якщо Ollama недоступний, пробуємо інші
        for p in ["claude", "openai", "gemini", "mistral"]:
            if self.is_available(p):
                generators = {
                    "claude": self._generate_claude,
                    "openai": self._generate_openai,
                    "gemini": self._generate_gemini,
                    "mistral": self._generate_mistral
                }
                return generators[p](system_prompt, user_prompt, max_tokens, temperature)
        
        return {
            "status": "error",
            "message": "No LLM providers available",
            "content": "Vireo is running but no LLM is available. Please check your configuration."
        }
    
    def _generate_ollama(self, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        if not self.is_available("ollama"):
            raise Exception("Ollama not available")
        
        client = self._clients["ollama"]
        response = client.chat(
            model=LLMConfig.OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={
                "num_predict": max_tokens,
                "temperature": temperature
            }
        )
        
        return {
            "status": "success",
            "content": response["message"]["content"],
            "provider": "ollama",
            "model": LLMConfig.OLLAMA_MODEL
        }
    
    def _generate_claude(self, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        client = self._clients["claude"]
        response = client.messages.create(
            model=LLMConfig.CLAUDE_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        content = "".join(block.text for block in response.content if block.type == "text")
        return {"status": "success", "content": content, "provider": "claude", "model": LLMConfig.CLAUDE_MODEL}
    
    def _generate_openai(self, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        client = self._clients["openai"]
        response = client.chat.completions.create(
            model=LLMConfig.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return {"status": "success", "content": response.choices[0].message.content, "provider": "openai", "model": LLMConfig.OPENAI_MODEL}
    
    def _generate_gemini(self, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        genai = self._clients["gemini"]
        model = genai.GenerativeModel(model_name=LLMConfig.GEMINI_MODEL, system_instruction=system_prompt)
        response = model.generate_content(user_prompt, generation_config={"temperature": temperature, "max_output_tokens": max_tokens})
        return {"status": "success", "content": response.text, "provider": "gemini", "model": LLMConfig.GEMINI_MODEL}
    
    def _generate_mistral(self, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        from mistralai.models.chat_completion import ChatMessage
        client = self._clients["mistral"]
        response = client.chat(
            model=LLMConfig.MISTRAL_MODEL,
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt)
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return {"status": "success", "content": response.choices[0].message.content, "provider": "mistral", "model": LLMConfig.MISTRAL_MODEL}
    
    def generate_json(self, system_prompt: str, user_prompt: str, task: Optional[str] = None,
                      max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Генерує і парсить JSON відповідь."""
        result = self.generate(system_prompt, user_prompt, task, max_tokens, temperature)
        
        if result.get("status") == "error":
            return result
        
        content = result.get("content", "")
        
        # Очищення від markdown
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        
        try:
            data = json.loads(cleaned)
            return {"status": "success", "data": data, "raw": content}
        except:
            return {"status": "error", "message": "JSON parse error", "raw": content}


def create_llm_provider(provider: Optional[str] = None) -> LLMProvider:
    return LLMProvider(provider)