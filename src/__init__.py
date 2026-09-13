# [file name]: src/__init__.py
# ============================================================
# VIREO SOURCE CODE - MAIN PACKAGE
# ============================================================
"""
Vireo Source Code Package

This package contains the core implementation of Vireo:
- compiler: JIT compilation and GPU support
- crypto: Cryptographic primitives (Ed25519, DID, Trust)
- transport: Distributed transport (Redis, Kafka)
- onnx: ONNX import/export
"""

from .compiler import VireoJIT, jit_compile, GPUSupport, gpu_accelerate
from .crypto import Ed25519Crypto, DIDManager, TrustManager
from .transport import RedisEventBus, KafkaEventBus
from .onnx import export_to_onnx, import_from_onnx

__version__ = "1.4.3"

__all__ = [
    # Compiler
    "VireoJIT",
    "jit_compile",
    "GPUSupport",
    "gpu_accelerate",
    # Crypto
    "Ed25519Crypto",
    "DIDManager",
    "TrustManager",
    # Transport
    "RedisEventBus",
    "KafkaEventBus",
    # ONNX
    "export_to_onnx",
    "import_from_onnx",
]