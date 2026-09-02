# Vireo Core Package
# Version: 2.0.1

from .agent.base import BaseAgent
from .agent.registry import AgentRegistry
from .protocol.state import ProtocolState, StateMachine
from .protocol.message import Message, MessageType
from .contract.contract import Contract, Terms, Obligation
from .contract.validator import ContractValidator
from .capability.registry import CapabilityRegistry
from .identity.key_manager import KeyManager
from .identity.trust_bootstrap import TrustBootstrapProtocol
from .execution.runner import ExecutionRunner
from .verification.verifier import Verifier

__all__ = [
    # Agent
    'BaseAgent',
    'AgentRegistry',
    # Protocol
    'ProtocolState',
    'StateMachine',
    'Message',
    'MessageType',
    # Contract
    'Contract',
    'Terms',
    'Obligation',
    'ContractValidator',
    # Capability
    'CapabilityRegistry',
    # Identity
    'KeyManager',
    'TrustBootstrapProtocol',
    # Execution
    'ExecutionRunner',
    # Verification
    'Verifier',
]

__version__ = "2.0.1"