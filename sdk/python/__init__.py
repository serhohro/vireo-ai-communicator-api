# ============================================================
# VIREO PYTHON SDK
# ============================================================
"""
Vireo Python SDK — client library for interacting with Vireo agents.

Provides:
- VireoClient: Main client for agent communication
- Agent management
- Contract creation and validation
- Message handling
"""

from .client import (
    VireoClient,
    AgentInfo,
    Message,
    Contract,
    create_contract,
    DEFAULT_CONTRACT,
)

__all__ = [
    'VireoClient',
    'AgentInfo',
    'Message',
    'Contract',
    'create_contract',
    'DEFAULT_CONTRACT',
]