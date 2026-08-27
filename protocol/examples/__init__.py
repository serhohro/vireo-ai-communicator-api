# [file name]: examples/__init__.py
# ============================================================
# VIREO EXAMPLES PACKAGE
# Приклади коду на мові Vireo
# ============================================================
"""
Vireo Examples Package

This package contains example Vireo code files (.v) that demonstrate
various features of the Vireo language:

- weather_prediction.v     — Weather prediction with 2 models
- financial_prediction.v   — Financial market prediction with 4 models
- multi_agent_medical.v    — Multi-agent medical system
- negotiation_weather.v    — Agent negotiation protocol for weather

Usage:
    python vireo_interpreter.py examples/weather_prediction.v
    python api_server.py   # then use /interpreter endpoint
"""

__all__ = []

# ============================================================
# META INFORMATION
# ============================================================

__version__ = "1.4.0"
__author__ = "Serhii (serhohro)"
__description__ = "Vireo language examples"

# ============================================================
# FILE LIST (для документації)
# ============================================================

EXAMPLES = [
    "weather_prediction.v",
    "financial_prediction.v", 
    "multi_agent_medical.v",
    "negotiation_weather.v",
]

EXAMPLES_DESCRIPTIONS = {
    "weather_prediction.v": "Weather prediction with TemperatureModel and PrecipitationModel",
    "financial_prediction.v": "Financial market prediction with 4 models (Market, Trend, Risk, Portfolio)",
    "multi_agent_medical.v": "Multi-agent medical system with Vision, NLP, Analyst, Guardian agents",
    "negotiation_weather.v": "Agent negotiation protocol for weather prediction with contracts",
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def list_examples():
    """Повертає список доступних прикладів."""
    return EXAMPLES

def get_example_description(filename: str) -> str:
    """Повертає опис прикладу за ім'ям файлу."""
    return EXAMPLES_DESCRIPTIONS.get(filename, "No description available")

def get_example_path(filename: str) -> str:
    """Повертає повний шлях до файлу прикладу."""
    import os
    return os.path.join(os.path.dirname(__file__), filename)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("📁 Vireo Examples:")
    print("=" * 40)
    for ex in EXAMPLES:
        desc = get_example_description(ex)
        print(f"   {ex}")
        print(f"      {desc}")
    print("=" * 40)
    print(f"\nTotal: {len(EXAMPLES)} examples")