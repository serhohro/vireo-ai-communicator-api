# ============================================================
# VIREO PROTOCOL MODULE — AI-to-AI Communication Protocol
# ============================================================

from .config import LLMConfig
from .llm_provider import (
    LLMProvider,
    create_llm_provider,
    OllamaProvider,
    GeminiProvider,
    OpenAIProvider,
    ClaudeProvider,
    MistralProvider,
    get_provider,
    AVAILABLE_PROVIDERS,
    AVAILABLE_MODELS,
)
from .llm_provider_eu import (
    OllamaOptimizedProvider,
    HuggingFaceProvider,
    BLOOMProvider,
    OpenChatProvider,
    get_eu_provider,
    EU_MODELS,
)
from .llm_agent import LLMAgent
from .agent import Agent
from .message import Message, make_message
from .intent import Intent
from .state import DialogueState, DialogueStateMachine, InvalidTransition
from .capabilities import CapabilityRegistry, Capability
from .trust import TrustBootstrap, TrustManager, verify, attach_signature
from .contract import Contract, Proposal, create_default_contract
from .conflict import ContextStore, ConflictStrategy, ConflictError
from .runtime_bridge import RuntimeBridge, real_vireo_executor, create_runtime_bridge
from .agents import (
    RoleAgent,
    AgentRole,
    MasterAgent,
    GuardianAgent,
    create_role_agent,
    ROLES,
)

# Transport
from .transport.base import Transport, Handler
from .transport.in_memory import InMemoryEventBus

__all__ = [
    # Config
    'LLMConfig',
    
    # LLM Providers
    'LLMProvider',
    'create_llm_provider',
    'OllamaProvider',
    'GeminiProvider',
    'OpenAIProvider',
    'ClaudeProvider',
    'MistralProvider',
    'get_provider',
    'AVAILABLE_PROVIDERS',
    'AVAILABLE_MODELS',
    
    # 🆕 EU LLM Providers
    'OllamaOptimizedProvider',
    'HuggingFaceProvider',
    'BLOOMProvider',
    'OpenChatProvider',
    'get_eu_provider',
    'EU_MODELS',
    
    # LLM Agent
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
    'TrustBootstrap',
    'TrustManager',
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
    
    # Agents
    'RoleAgent',
    'AgentRole',
    'MasterAgent',
    'GuardianAgent',
    'create_role_agent',
    'ROLES',
    
    # Transport
    'Transport',
    'Handler',
    'InMemoryEventBus',
]