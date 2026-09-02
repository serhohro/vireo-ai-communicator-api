markdown
# 🇪🇺 European LLM Guide for Vireo

**Version:** 2.0.1  
**Last Updated:** 2026-01-15

---

## Overview

Vireo supports multiple European LLM providers to ensure data sovereignty and compliance with EU regulations (GDPR, AI Act).

## Supported Providers

| Provider | Country | Models | Status |
|----------|---------|--------|--------|
| **Mistral AI** | 🇫🇷 France | mistral-tiny, mistral-small, mistral-medium, mistral-large | ✅ |
| **Aleph Alpha** | 🇩🇪 Germany | luminous-base, luminous-extended, luminous-supreme | ✅ |
| **Cohere** | 🇨🇭 Switzerland | command, command-light, command-nightly | ✅ |
| **Stability AI** | 🇬🇧 UK | stablelm-zephyr-3b | ✅ |
| **LightOn** | 🇫🇷 France | (coming soon) | 📅 |

## Setup

### 1. Get API Keys

```bash
# Mistral AI
export MISTRAL_API_KEY="your-key-here"

# Aleph Alpha
export ALEPH_ALPHA_API_KEY="your-key-here"

# Cohere
export COHERE_API_KEY="your-key-here"

# Stability AI
export STABILITY_AI_API_KEY="your-key-here"
2. Update .env
bash
# .env
MISTRAL_API_KEY=your-key-here
ALEPH_ALPHA_API_KEY=your-key-here
COHERE_API_KEY=your-key-here
STABILITY_AI_API_KEY=your-key-here

# Default provider
DEFAULT_EU_LLM=mistral
Usage
Basic Usage
python
from protocol.llm_provider_eu import MistralProvider, EULLMProviderFactory

# Initialize providers
EULLMProviderFactory.initialize()

# Get Mistral provider
provider = EULLMProviderFactory.get_provider("mistral")

# Generate text
response = provider.generate(
    prompt="What is the capital of Germany?",
    model="mistral-medium",
    max_tokens=100
)

print(response.text)
print(f"Tokens: {response.tokens_used}")
print(f"Cost: ${response.cost_usd:.4f}")
Multiple Providers
python
from protocol.llm_provider_eu import (
    MistralProvider, AlephAlphaProvider, CohereProvider,
    EULLMProviderFactory
)

# Get all providers
providers = EULLMProviderFactory.get_all_providers()
print(f"Available providers: {providers}")

# Compare responses
prompt = "Explain quantum computing in simple terms"

for name in providers:
    provider = EULLMProviderFactory.get_provider(name)
    response = provider.generate(prompt, max_tokens=200)
    print(f"\n{name.upper()}:")
    print(response.text[:100] + "...")
Provider Selection
python
from protocol.llm_provider_eu import EULLMProviderFactory

def select_provider(region: str):
    providers = EULLMProviderFactory.get_providers_by_region(region)
    if providers:
        return providers[0]
    return None

# Get French provider
french_provider = select_provider("France")
if french_provider:
    response = french_provider.generate("Hello, world!")
Configuration
Provider Configuration
python
# Custom configuration
provider = MistralProvider()
provider._region = "France"
provider._models = ["mistral-small", "mistral-medium"]

# Or using factory
EULLMProviderFactory.register_provider(
    "custom_mistral",
    MistralProvider()
)
Fallback Strategy
python
def generate_with_fallback(prompt: str) -> str:
    providers = ["mistral", "cohere", "aleph_alpha"]
    
    for name in providers:
        try:
            provider = EULLMProviderFactory.get_provider(name)
            if provider:
                response = provider.generate(prompt, max_tokens=100)
                return response.text
        except Exception:
            continue
    
    raise RuntimeError("All providers failed")
Compliance
GDPR Compliance
All European providers are:

✅ GDPR compliant

✅ Data stored in EU

✅ No data sharing with non-EU

✅ Right to deletion

AI Act Compliance
European providers:

✅ Transparent

✅ Explainable

✅ Auditable

✅ Human oversight capable

Cost Estimation
Provider Costs
Provider	Model	Cost per 1K tokens
Mistral	mistral-tiny	$0.00025
Mistral	mistral-small	$0.00050
Mistral	mistral-medium	$0.00100
Mistral	mistral-large	$0.00200
Aleph Alpha	luminous-base	$0.00030
Aleph Alpha	luminous-extended	$0.00080
Aleph Alpha	luminous-supreme	$0.00200
Cohere	command	$0.00050
Cost Tracking
python
from protocol.llm_provider_eu import LLMResponse

def track_cost(response: LLMResponse):
    print(f"Provider: {response.provider}")
    print(f"Model: {response.model}")
    print(f"Tokens: {response.tokens_used}")
    print(f"Cost: ${response.cost_usd:.4f}")
Troubleshooting
Common Issues
API Key Missing

text
Error: MistralProvider requires API key
Solution: Set MISTRAL_API_KEY environment variable
Rate Limiting

text
Error: Rate limit exceeded
Solution: Implement exponential backoff
Invalid Model

text
Error: Model not found
Solution: Check available models with get_available_models()
Example: Multi-Provider Chat
python
import asyncio
from protocol.llm_provider_eu import EULLMProviderFactory

async def multi_provider_chat():
    EULLMProviderFactory.initialize()
    
    prompt = "What are the benefits of European AI sovereignty?"
    
    # Run in parallel
    tasks = []
    for name in EULLMProviderFactory.get_all_providers():
        provider = EULLMProviderFactory.get_provider(name)
        if provider:
            tasks.append(asyncio.to_thread(
                provider.generate, prompt, 200
            ))
    
    responses = await asyncio.gather(*tasks)
    
    for response in responses:
        print(f"\n{response.provider} ({response.model}):")
        print(response.text[:150] + "...")

asyncio.run(multi_provider_chat())
Future Providers
Planned European providers:

🇫🇷 LightOn — French startup, API coming soon

🇩🇪 DeepL — German translation + AI

🇳🇱 Cradle — Dutch protein design AI

Vireo supports European AI independence! 🌿🇪🇺