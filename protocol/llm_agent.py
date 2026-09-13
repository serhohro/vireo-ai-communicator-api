"""
Vireo LLM Agent v3.1 — inherits Agent, uses real providers.

Honest behavior:
- If provider is configured, makes real call.
- If not, returns structured "mock" response with explicit status.
"""

import os
from typing import Optional

from protocol.agent import Agent


class LLMAgent(Agent):
    """
    Agent backed by an LLM provider.

    Supported providers (based on configured API keys):
    - ollama (local, no key)
    - mistral, aleph_alpha, cohere
    - openai, claude, gemini, qwen, deepseek
    """

    def __init__(
        self,
        agent_id: str,
        private_key_hex: str,
        public_key_hex: str,
        provider: str,
        model_name: Optional[str] = None,
        name: Optional[str] = None,
    ):
        super().__init__(agent_id, private_key_hex, public_key_hex, name=name)
        self.provider = provider
        self.model_name = model_name or self._default_model(provider)

    @staticmethod
    def _default_model(provider: str) -> str:
        return {
            "ollama": "llama3",
            "mistral": "mistral-large-latest",
            "aleph_alpha": "luminous-base",
            "cohere": "command-r-plus",
            "openai": "gpt-4o-mini",
            "claude": "claude-3-5-sonnet-20241022",
            "gemini": "gemini-1.5-pro",
            "qwen": "qwen-max",
            "deepseek": "deepseek-chat",
        }.get(provider, "unknown")

    def is_configured(self) -> bool:
        env_map = {
            "ollama": None,
            "mistral": "MISTRAL_API_KEY",
            "aleph_alpha": "ALEPH_ALPHA_API_KEY",
            "cohere": "COHERE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "qwen": "QWEN_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        env = env_map.get(self.provider)
        if env is None:
            return True   # ollama needs no key
        return bool(os.getenv(env, ""))

    def generate(self, prompt: str) -> dict:
        """
        Generate a response.

        Returns:
            {"status": "ok"|"mock"|"error", "response": str, ...}
        """
        if not self.is_configured():
            return {
                "status": "mock",
                "provider": self.provider,
                "model": self.model_name,
                "response": f"[mock] Provider '{self.provider}' not configured. "
                            f"Set API key to enable real calls.",
            }

        if self.provider == "ollama":
            return self._call_ollama(prompt)
        return self._call_remote(prompt)

    def _call_ollama(self, prompt: str) -> dict:
        import json
        import urllib.request
        from core.config import config

        url = f"{config.OLLAMA_URL}/api/generate"
        body = json.dumps({
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
            return {
                "status": "ok",
                "provider": "ollama",
                "model": self.model_name,
                "response": result.get("response", ""),
            }
        except Exception as e:
            return {
                "status": "error",
                "provider": "ollama",
                "error": str(e),
            }

    def _call_remote(self, prompt: str) -> dict:
        """Remote provider calls — implement per provider in future versions."""
        return {
            "status": "error",
            "provider": self.provider,
            "error": f"Remote call for '{self.provider}' not yet implemented. "
                     f"See docs/API_REFERENCE.md.",
        }