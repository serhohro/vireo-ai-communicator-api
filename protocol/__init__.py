# ============================================================
# VIREO PROTOCOL MODULE - AI-to-AI Communication Protocol
# ============================================================

from .config import LLMConfig
from .llm_provider import LLMProvider, create_llm_provider
from .llm_agent import LLMAgent
from .agent import Agent
from .message import Message, make_message
from .intent import Intent
from .state import DialogueState, DialogueStateMachine, InvalidTransition
from .capabilities import CapabilityRegistry, Capability
from .trust import TrustManager, Identity, Permission, verify, attach_signature
from .contract import Contract, Proposal, create_default_contract
from .conflict import ContextStore, ConflictStrategy, ConflictError
from .runtime_bridge import RuntimeBridge, real_vireo_executor, create_runtime_bridge

# Transport
from .transport.base import Transport, Handler
from .transport.in_memory import InMemoryEventBus

__all__ = [
    # Config
    'LLMConfig',
    # LLM
    'LLMProvider',
    'create_llm_provider',
    'LLMAgent',
    # Agent
    'Agent',
    # Message
    'Message',
    'make_message',
    # Intent
    'Intent',
    # State
    'DialogueState',
    'DialogueStateMachine',
    'InvalidTransition',
    # Capabilities
    'CapabilityRegistry',
    'Capability',
    # Trust
    'TrustManager',
    'Identity',
    'Permission',
    'verify',
    'attach_signature',
    # Contract
    'Contract',
    'Proposal',
    'create_default_contract',
    # Conflict
    'ContextStore',
    'ConflictStrategy',
    'ConflictError',
    # Runtime
    'RuntimeBridge',
    'real_vireo_executor',
    'create_runtime_bridge',
    # Transport
    'Transport',
    'Handler',
    'InMemoryEventBus'
]