"""
Vireo Protocol Package

A2A (Agent-to-Agent) protocol implementation for secure AI communication.

This package provides:
- Agent base classes and implementations
- Specialized agents (Guardian, Negotiator, Executor, Verifier)
- Transport layer adapters (Redis, WebSocket, gRPC, HTTP)
- Capability management and discovery
"""

from .agent import Agent, BaseAgent, AgentConfig
from .llm_agent import LLMAgent, LLMConfig
from .capabilities import Capability, CapabilityRegistry, CapabilityManager

from .agents import (
    GuardianAgent,
    NegotiatorAgent,
    ExecutorAgent,
    VerifierAgent,
    AgentFactory,
)

from .transport import (
    Transport,
    TransportFactory,
    RedisTransport,
    WebSocketTransport,
    GRPCTransport,
    HTTPTransport,
)

__all__ = [
    # Agent base
    'Agent',
    'BaseAgent',
    'AgentConfig',
    
    # LLM Agent
    'LLMAgent',
    'LLMConfig',
    
    # Capabilities
    'Capability',
    'CapabilityRegistry',
    'CapabilityManager',
    
    # Specialized agents
    'GuardianAgent',
    'NegotiatorAgent',
    'ExecutorAgent',
    'VerifierAgent',
    'AgentFactory',
    
    # Transport
    'Transport',
    'TransportFactory',
    'RedisTransport',
    'WebSocketTransport',
    'GRPCTransport',
    'HTTPTransport',
]

__version__ = '3.0.0'