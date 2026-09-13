# [file name]: src/transport/__init__.py
# ============================================================
# VIREO TRANSPORT PACKAGE
# ============================================================
"""
Distributed transport for Vireo.

Provides:
- Redis transport (pub/sub)
- Kafka transport (event streaming)
"""

from .redis import RedisEventBus
from .kafka import KafkaEventBus

__all__ = [
    "RedisEventBus",
    "KafkaEventBus",
]