"""
Vireo Core Configuration v3.1
"""

import os
from pathlib import Path


class Config:
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    NONCE_DB_PATH = os.getenv("VIREO_NONCE_DB", str(BASE_DIR / "nonces.db"))
    DID_REGISTRY_PATH = os.getenv("VIREO_DID_REGISTRY", str(BASE_DIR / "did_registry.json"))

    # Wire
    WIRE_MAGIC = b"VIRE"
    WIRE_VERSION = 0x0301
    MAX_PAYLOAD_SIZE = 16 * 1024 * 1024   # 16 MB

    # Nonce
    NONCE_TTL_SEC = 24 * 3600             # 24h
    MAX_CLOCK_SKEW_MS = 5 * 60 * 1000     # ±5 min
    NONCE_BYTES = 16

    # Crypto
    HASH_DIGEST_SIZE = 32                 # BLAKE2b-256
    ED25519_SIG_BYTES = 64

    # Server
    HOST = os.getenv("VIREO_HOST", "0.0.0.0")
    PORT = int(os.getenv("VIREO_PORT", "5000"))

    # LLM
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    ALEPH_ALPHA_API_KEY = os.getenv("ALEPH_ALPHA_API_KEY", "")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

    # Compliance
    COMPLIANCE_MODE = os.getenv("VIREO_COMPLIANCE_MODE", "strict")  # strict | dev


config = Config()