# 🇪🇺 European LLM Guide for Vireo v3.0.0

**Version:** 3.0.0  
**Last Updated:** 2026-09-06  
**Compliance:** GDPR · EU AI Act · Data Sovereignty

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Supported Providers](#2-supported-providers)
3. [Installation & Setup](#3-installation--setup)
4. [Basic Usage](#4-basic-usage)
5. [Provider Selection](#5-provider-selection)
6. [Advanced Usage](#6-advanced-usage)
7. [Data Sovereignty](#7-data-sovereignty)
8. [EU AI Act Compliance](#8-eu-ai-act-compliance)
9. [Cost Management](#9-cost-management)
10. [Troubleshooting](#10-troubleshooting)
11. [Future Providers](#11-future-providers)

---

## 1. Overview

### Why European LLMs?

Vireo v3.0.0 provides first-class support for European LLM providers to ensure:

- **🇪🇺 Data Sovereignty** — Data stays in Europe
- **📜 GDPR Compliance** — Full compliance with EU regulations
- **⚖️ AI Act Ready** — Compliant with EU AI Act
- **🔐 Privacy First** — No data sharing with non-EU
- **💶 Cost Optimization** — Competitive European pricing

### Vireo's Commitment

> *"Vireo supports European AI independence! 🌿🇪🇺"*

---

## 2. Supported Providers

### 2.1 Current Providers (v3.0.0)

| Provider | Country | Models | Status | EU Hosted |
|----------|---------|--------|--------|-----------|
| **Mistral AI** | 🇫🇷 France | mistral-tiny, mistral-small, mistral-medium, mistral-large, open-mistral-7b, open-mistral-8x7b | ✅ | ✅ |
| **Aleph Alpha** | 🇩🇪 Germany | luminous-base, luminous-extended, luminous-supreme, luminous-control | ✅ | ✅ |
| **Cohere** | 🇨🇭 Switzerland | command, command-light, command-r, embed-multilingual | ✅ | ✅ |
| **Stability AI** | 🇬🇧 UK | stablelm-zephyr-3b, stablelm-tuned-alpha-7b | ✅ | ✅ |
| **DeepL** | 🇩🇪 Germany | deepL-pro, deepL-ultra | 🆕 New | ✅ |
| **Hugging Face EU** | 🇫🇷 France | mistral-7b, llama-3-8b, zephyr-7b | 🆕 New | ✅ |

### 2.2 Coming Soon

| Provider | Country | Expected |
|----------|---------|----------|
| **LightOn** | 🇫🇷 France | Q4 2026 |
| **Cradle** | 🇳🇱 Netherlands | Q1 2027 |
| **Mistral Large 3** | 🇫🇷 France | Q4 2026 |
| **German AI** | 🇩🇪 Germany | Q1 2027 |

---

## 3. Installation & Setup

### 3.1 Install Dependencies

```bash
# Install European LLM support
pip install vireo[eu-llm]

# Or manually
pip install mistralai python-dotenv requests
3.2 Configure Environment
bash
# .env file
# Mistral AI (🇫🇷 France)
MISTRAL_API_KEY=your-mistral-key

# Aleph Alpha (🇩🇪 Germany)
ALEPH_ALPHA_API_KEY=your-aleph-alpha-key

# Cohere (🇨🇭 Switzerland)
COHERE_API_KEY=your-cohere-key

# Stability AI (🇬🇧 UK)
STABILITY_AI_API_KEY=your-stability-key

# DeepL (🇩🇪 Germany)
DEEPL_API_KEY=your-deepl-key

# Default European provider
DEFAULT_EU_LLM=mistral
DEFAULT_EU_MODEL=mistral-large-latest

# Data residency
EU_DATA_RESIDENCY=strict  # strict | flexible | any
EU_ALLOWED_REGIONS=eu-west-1,eu-central-1,eu-north-1
3.3 Verify Setup
python
from protocol.llm_provider_eu import EULLMProviderFactory

# Initialize
EULLMProviderFactory.initialize()

# Check available providers
providers = EULLMProviderFactory.get_all_providers()
print(f"✅ Available European providers: {providers}")

# Test connection
for name in providers:
    provider = EULLMProviderFactory.get_provider(name)
    status = provider.health_check()
    print(f"{name}: {'✅' if status else '❌'}")
4. Basic Usage
4.1 Simple Generation
python
from protocol.llm_provider_eu import EULLMProviderFactory

# Initialize
EULLMProviderFactory.initialize()

# Get Mistral (French provider)
provider = EULLMProviderFactory.get_provider("mistral")

# Generate
response = provider.generate(
    prompt="What are the benefits of European AI sovereignty?",
    model="mistral-large-latest",
    max_tokens=500,
    temperature=0.7
)

print(f"🇫🇷 Mistral AI:")
print(response.text)
print(f"Tokens: {response.tokens_used}")
print(f"Cost: €{response.cost_eur:.4f}")
4.2 Chat Completion
python
from protocol.llm_provider_eu import EULLMProviderFactory

# Initialize
EULLMProviderFactory.initialize()

# Get Aleph Alpha (German provider)
provider = EULLMProviderFactory.get_provider("aleph_alpha")

# Chat
response = provider.chat(
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant for European businesses."},
        {"role": "user", "content": "Explain GDPR compliance for AI systems."}
    ],
    model="luminous-extended",
    max_tokens=500
)

print(f"🇩🇪 Aleph Alpha:")
print(response.text)
4.3 Streaming
python
from protocol.llm_provider_eu import EULLMProviderFactory

provider = EULLMProviderFactory.get_provider("mistral")

# Stream response
for chunk in provider.stream(
    prompt="Write a poem about European AI",
    model="mistral-medium",
    max_tokens=200
):
    print(chunk, end="", flush=True)
5. Provider Selection
5.1 Automatic Selection
python
from protocol.llm_provider_eu import EULLMProviderFactory

# Automatically select best provider
provider = EULLMProviderFactory.get_best_provider(
    task="chat",
    required_capabilities=["code_generation", "reasoning"],
    max_cost=0.01,  # EUR
    preferred_region="Germany"
)

response = provider.generate("Write Python code for a REST API")
5.2 Region-Based Selection
python
from protocol.llm_provider_eu import EULLMProviderFactory

# French providers
french_providers = EULLMProviderFactory.get_providers_by_region("France")
print(f"🇫🇷 French providers: {french_providers}")

# German providers
german_providers = EULLMProviderFactory.get_providers_by_region("Germany")
print(f"🇩🇪 German providers: {german_providers}")

# Swiss providers
swiss_providers = EULLMProviderFactory.get_providers_by_region("Switzerland")
print(f"🇨🇭 Swiss providers: {swiss_providers}")
5.3 Capability-Based Selection
python
from protocol.llm_provider_eu import EULLMProviderFactory

# Code generation
provider = EULLMProviderFactory.get_provider_by_capability("code_generation")
print(f"Best for code: {provider.name}")

# Multilingual
provider = EULLMProviderFactory.get_provider_by_capability("multilingual")
print(f"Best for multilingual: {provider.name}")

# Reasoning
provider = EULLMProviderFactory.get_provider_by_capability("reasoning")
print(f"Best for reasoning: {provider.name}")
6. Advanced Usage
6.1 Multi-Provider Ensemble
python
from protocol.llm_provider_eu import EULLMProviderFactory
import asyncio

async def ensemble_generation(prompt: str):
    """Query multiple European providers in parallel."""
    providers = [
        "mistral",
        "aleph_alpha", 
        "cohere",
        "stability"
    ]
    
    tasks = []
    for name in providers:
        provider = EULLMProviderFactory.get_provider(name)
        if provider:
            tasks.append(asyncio.to_thread(
                provider.generate, prompt, 200
            ))
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    results = []
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            continue
        results.append({
            "provider": providers[i],
            "text": response.text,
            "tokens": response.tokens_used,
            "cost_eur": response.cost_eur
        })
    
    return results

# Use
results = asyncio.run(ensemble_generation(
    "What is the EU AI Act and how does it affect AI development?"
))

for result in results:
    print(f"{result['provider']}: {result['text'][:100]}...")
    print(f"Cost: €{result['cost_eur']:.4f}")
6.2 Fallback Strategy
python
from protocol.llm_provider_eu import EULLMProviderFactory

def generate_with_fallback(prompt: str, max_retries: int = 3):
    """Try multiple providers if one fails."""
    providers = ["mistral", "cohere", "aleph_alpha", "stability"]
    
    for attempt in range(max_retries):
        for name in providers:
            try:
                provider = EULLMProviderFactory.get_provider(name)
                if provider and provider.health_check():
                    response = provider.generate(prompt, max_tokens=200)
                    return response.text
            except Exception as e:
                print(f"⚠️ {name} failed: {e}")
                continue
        
        print(f"🔄 Retry {attempt + 1}/{max_retries}")
    
    raise RuntimeError("All European providers failed")

# Use
text = generate_with_fallback("Explain European AI sovereignty")
print(f"✅ Result: {text[:200]}...")
6.3 Provider Ranking
python
from protocol.llm_provider_eu import EULLMProviderFactory

def rank_providers(prompt: str, criteria: str = "quality"):
    """Rank European providers for a specific prompt."""
    providers = EULLMProviderFactory.get_all_providers()
    results = []
    
    for name in providers:
        provider = EULLMProviderFactory.get_provider(name)
        if not provider:
            continue
        
        start = time.time()
        try:
            response = provider.generate(prompt, max_tokens=100)
            results.append({
                "provider": name,
                "response": response.text,
                "time": time.time() - start,
                "tokens": response.tokens_used,
                "cost": response.cost_eur
            })
        except Exception:
            continue
    
    if criteria == "quality":
        # Sort by tokens (proxy for quality)
        results.sort(key=lambda x: x["tokens"], reverse=True)
    elif criteria == "speed":
        results.sort(key=lambda x: x["time"])
    elif criteria == "cost":
        results.sort(key=lambda x: x["cost"])
    
    return results

# Rank
rankings = rank_providers(
    "Write a summary of European AI regulation",
    criteria="quality"
)

for i, result in enumerate(rankings[:3]):
    print(f"{i+1}. {result['provider']} — {result['time']:.2f}s, €{result['cost']:.4f}")
7. Data Sovereignty
7.1 Data Residency
python
from protocol.llm_provider_eu import DataResidencyManager

# Initialize
residency = DataResidencyManager()

# Check provider data residency
for name in ["mistral", "aleph_alpha", "cohere"]:
    location = residency.get_data_location(name)
    print(f"{name}: {location}")

# Set strict residency
residency.set_policy("strict")
data = residency.process_sensitive_data(user_data)
7.2 GDPR Compliance
python
from protocol.llm_provider_eu import GDPRCompliance

# Initialize
gdpr = GDPRCompliance()

# Check compliance
for name in ["mistral", "aleph_alpha"]:
    compliant = gdpr.is_compliant(name)
    print(f"{name}: {'✅' if compliant else '❌'}")

# Delete user data (Right to be forgotten)
gdpr.delete_user_data(user_id="user-123")

# Export user data (Data portability)
data = gdpr.export_user_data(user_id="user-123")
7.3 EU Cloud Providers
python
# Preferred EU cloud providers
EU_CLOUDS = {
    "mistral": ["AWS-eu-west-1", "AWS-eu-central-1"],
    "aleph_alpha": ["Azure-Germany", "AWS-eu-central-1"],
    "cohere": ["AWS-eu-west-1"],
    "stability": ["AWS-eu-west-2"]
}

def get_provider_cloud(provider_name: str):
    return EU_CLOUDS.get(provider_name, ["Unknown"])

# Check
clouds = get_provider_cloud("mistral")
print(f"🇫🇷 Mistral runs on: {clouds}")
8. EU AI Act Compliance
8.1 Risk Assessment
python
from protocol.llm_provider_eu import AIActCompliance

# Initialize
aiact = AIActCompliance()

# Assess provider risk
for name in ["mistral", "aleph_alpha", "cohere"]:
    risk = aiact.assess_risk(name)
    print(f"{name}: {risk.level}")
    print(f"  Compliance: {risk.compliance_score}%")
    print(f"  Status: {risk.status}")
8.2 Transparency Requirements
python
from protocol.llm_provider_eu import AITransparency

# Initialize
transparency = AITransparency()

# Get transparency report
for name in ["mistral", "aleph_alpha"]:
    report = transparency.get_report(name)
    print(f"{name}:")
    print(f"  Model cards: {'✅' if report.model_cards else '❌'}")
    print(f"  Explainability: {report.explainability_score}%")
    print(f"  Audit trail: {'✅' if report.audit_trail else '❌'}")
8.3 Human Oversight
python
from protocol.llm_provider_eu import HumanOversight

oversight = HumanOversight()

# Enable human oversight
oversight.enable(
    provider="mistral",
    threshold=0.85,  # Confidence threshold
    reviewer="human-reviewer@company.com"
)

# Get oversight logs
logs = oversight.get_logs(start_date="2026-09-01")
print(f"{len(logs)} oversight events")
9. Cost Management
9.1 Pricing Comparison
Provider	Model	Cost per 1K tokens (EUR)
Mistral	mistral-tiny	€0.00025
Mistral	mistral-small	€0.00050
Mistral	mistral-medium	€0.00100
Mistral	mistral-large	€0.00200
Aleph Alpha	luminous-base	€0.00030
Aleph Alpha	luminous-extended	€0.00080
Aleph Alpha	luminous-supreme	€0.00200
Cohere	command	€0.00050
Cohere	command-r	€0.00150
Stability	stablelm-3b	€0.00020
Stability	stablelm-7b	€0.00050
9.2 Cost Tracking
python
from protocol.llm_provider_eu import CostTracker

# Initialize
tracker = CostTracker()

# Track costs
def track_and_generate(provider_name, prompt):
    provider = EULLMProviderFactory.get_provider(provider_name)
    response = provider.generate(prompt, max_tokens=200)
    
    # Track
    tracker.track(
        provider=provider_name,
        model=response.model,
        tokens=response.tokens_used,
        cost_eur=response.cost_eur
    )
    
    return response.text

# Get monthly report
report = tracker.get_monthly_report()
print(f"Total cost (EUR): €{report.total_cost:.2f}")
print(f"Total tokens: {report.total_tokens}")
print(f"By provider: {report.by_provider}")
9.3 Budget Limits
python
from protocol.llm_provider_eu import BudgetManager

# Initialize
budget = BudgetManager()

# Set budgets
budget.set_limit(
    provider="mistral",
    monthly_limit=100.00  # EUR
)

budget.set_limit(
    provider="aleph_alpha",
    monthly_limit=50.00
)

# Check usage
for name in ["mistral", "aleph_alpha"]:
    usage = budget.get_usage(name)
    print(f"{name}: €{usage.current:.2f} / €{usage.limit:.2f}")
    if usage.exceeded:
        print(f"⚠️ Budget exceeded for {name}!")
10. Troubleshooting
10.1 Common Issues
API Key Missing
text
Error: MistralProvider requires API key
Solution: Set MISTRAL_API_KEY environment variable

Rate Limiting
text
Error: Rate limit exceeded
Solution: Implement exponential backoff

python
def generate_with_backoff(provider, prompt):
    import time
    for attempt in range(5):
        try:
            return provider.generate(prompt)
        except RateLimitError:
            wait = 2 ** attempt
            print(f"⏳ Waiting {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Rate limit exhausted")
Provider Unavailable
text
Error: Provider unavailable
Solution: Use fallback providers

python
def get_provider_with_fallback(name):
    try:
        return EULLMProviderFactory.get_provider(name)
    except ProviderUnavailableError:
        # Try another European provider
        alternatives = ["cohere", "aleph_alpha"]
        for alt in alternatives:
            try:
                return EULLMProviderFactory.get_provider(alt)
            except:
                continue
        raise RuntimeError("No European providers available")
10.2 Performance Optimization
python
# Use async for parallel requests
async def generate_parallel(prompts):
    providers = ["mistral", "aleph_alpha", "cohere"]
    tasks = []
    
    for prompt in prompts:
        for name in providers:
            provider = EULLMProviderFactory.get_provider(name)
            if provider:
                tasks.append(asyncio.to_thread(
                    provider.generate, prompt, 100
                ))
    
    responses = await asyncio.gather(*tasks)
    return responses

# Use caching
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generate(prompt: str, provider: str = "mistral"):
    provider_obj = EULLMProviderFactory.get_provider(provider)
    return provider_obj.generate(prompt, max_tokens=100)
11. Future Providers
11.1 Planned European Providers
Provider	Country	Expected	Status
LightOn	🇫🇷 France	Q4 2026	📅 In discussion
Cradle	🇳🇱 Netherlands	Q1 2027	📅 Planned
German AI	🇩🇪 Germany	Q1 2027	📅 Planned
Mistral Large 3	🇫🇷 France	Q4 2026	📅 Beta
European GPT	🇪🇺 EU	Q3 2027	📅 Planned
11.2 How to Request a Provider
python
# Submit a request for a new European provider
from protocol.llm_provider_eu import ProviderRequest

request = ProviderRequest(
    name="New EU Provider",
    country="France",
    website="https://example.com",
    api_docs="https://example.com/api",
    capabilities=["chat", "code", "embedding"],
    reason="Need additional European AI capabilities"
)

EULLMProviderFactory.submit_request(request)
11.3 Community Contributions
python
# Custom European provider implementation
class CustomEUProvider(EULLMProvider):
    def __init__(self):
        super().__init__()
        self.name = "Custom EU AI"
        self.country = "France"
        self.models = ["custom-7b", "custom-13b"]
        self.is_eu_hosted = True
    
    def generate(self, prompt, **kwargs):
        # Implementation
        pass
    
    def health_check(self):
        return True

# Register
EULLMProviderFactory.register_provider("custom_eu", CustomEUProvider())
📚 Additional Resources
SECURITY_GUIDE.md — Security with EU providers

PROTOCOL.md — Protocol specification

TUTORIAL.md — Complete tutorial

GOVERNANCE.md — Governance model

🇪🇺 Quick Commands
bash
# Check EU providers
python -c "from protocol.llm_provider_eu import EULLMProviderFactory; EULLMProviderFactory.initialize(); print(EULLMProviderFactory.get_all_providers())"

# Test EU providers
vireo test-eu-providers

# Check GDPR compliance
vireo gdpr-check --provider mistral

# AI Act assessment
vireo ai-act --provider aleph_alpha

# Cost report
vireo eu-cost-report --month 2026-09
🌿 Vireo v3.0.0 — European LLM Guide