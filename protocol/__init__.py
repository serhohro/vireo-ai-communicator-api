"""
Vireo Protocol Agents v3.1

Application-level agents built on top of core protocol:
- Agent          — base agent (DID, Ed25519, state machine)
- LLMAgent       — agent backed by an LLM provider
- Capability     — capability descriptor

Specialized agents live in `protocol.agents`:
- GuardianAgent
- NegotiatorAgent
- ExecutorAgent
- VerifierAgent
"""

from .agent import Agent
from .llm_agent import LLMAgent
from .capabilities import Capability

# Re-export specialized agents for convenience
from .agents import (
    GuardianAgent,
    NegotiatorAgent,
    ExecutorAgent,
    VerifierAgent,
)

__all__ = [
    # Base
    "Agent",
    "LLMAgent",
    "Capability",

    # Specialized
    "GuardianAgent",
    "NegotiatorAgent",
    "ExecutorAgent",
    "VerifierAgent",
]

__version__ = "3.1.0"