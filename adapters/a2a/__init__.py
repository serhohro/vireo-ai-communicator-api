# ============================================================
# VIREO A2A ADAPTER
# ============================================================
"""
A2A (Agent-to-Agent) adapter for Vireo.

Provides:
- A2A protocol compatibility
- Agent discovery
- Task delegation
- Message translation
"""

from .adapter import A2AAdapter, A2AAgent, A2AMessage

__all__ = [
    'A2AAdapter',
    'A2AAgent',
    'A2AMessage',
]