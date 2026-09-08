"""
Vireo Specialized Agents Package

Provides specialized agent implementations for different roles in the A2A protocol:

1. GuardianAgent - Protocol enforcement, security, and audit
2. NegotiatorAgent - Contract negotiation and agreement
3. ExecutorAgent - Task execution and workflow management
4. VerifierAgent - Result verification and validation

These agents work together to create a complete multi-agent system with:
- Security and trust management
- Negotiation and contracting
- Task execution and coordination
- Verification and quality assurance

Usage Examples:
--------------
# Create a Guardian agent for security
from protocol.agents import GuardianAgent, GuardianConfig

guardian_config = GuardianConfig(
    name="SecurityGuardian",
    enforce_protocol=True,
    enforce_signatures=True,
    rate_limit=100
)
guardian = GuardianAgent(guardian_config)
await guardian.start()

# Create a Negotiator agent
from protocol.agents import NegotiatorAgent, NegotiatorConfig

negotiator_config = NegotiatorConfig(
    name="ContractNegotiator",
    max_rounds=10,
    strategy="collaborative"
)
negotiator = NegotiatorAgent(negotiator_config)
await negotiator.start()

# Create an Executor agent
from protocol.agents import ExecutorAgent, ExecutorConfig

executor_config = ExecutorConfig(
    name="TaskExecutor",
    concurrent_tasks=5,
    enable_retry=True
)
executor = ExecutorAgent(executor_config)
await executor.start()

# Create a Verifier agent
from protocol.agents import VerifierAgent, VerifierConfig

verifier_config = VerifierConfig(
    name="ResultVerifier",
    require_multiple_verifiers=2,
    verification_threshold=0.8
)
verifier = VerifierAgent(verifier_config)
await verifier.start()
"""

# Guardian Agent
from .guardian_agent import (
    GuardianAgent,
    GuardianConfig,
)

# Negotiator Agent
from .negotiator_agent import (
    NegotiatorAgent,
    NegotiatorConfig,
)

# Executor Agent
from .executor_agent import (
    ExecutorAgent,
    ExecutorConfig,
)

# Verifier Agent
from .verifier_agent import (
    VerifierAgent,
    VerifierConfig,
)

# Agent Factory
from typing import Dict, Any, Type, Union
import logging

logger = logging.getLogger(__name__)

# Registry of available agent types
AGENT_REGISTRY: Dict[str, Type] = {
    "guardian": GuardianAgent,
    "negotiator": NegotiatorAgent,
    "executor": ExecutorAgent,
    "verifier": VerifierAgent,
}


class AgentFactory:
    """
    Factory for creating specialized agents.
    
    Provides a unified interface for creating different types of agents
    with their specific configurations.
    """
    
    @staticmethod
    def create_agent(
        agent_type: str,
        config: Union[Dict[str, Any], GuardianConfig, NegotiatorConfig, ExecutorConfig, VerifierConfig],
        **kwargs
    ) -> Union[GuardianAgent, NegotiatorAgent, ExecutorAgent, VerifierAgent]:
        """
        Create an agent of the specified type.
        
        Args:
            agent_type: Type of agent to create ('guardian', 'negotiator', 'executor', 'verifier')
            config: Configuration for the agent (dict or specific config class)
            **kwargs: Additional arguments to pass to the agent constructor
            
        Returns:
            An instance of the requested agent type
            
        Raises:
            ValueError: If agent_type is unknown
        """
        agent_type = agent_type.lower()
        
        if agent_type not in AGENT_REGISTRY:
            raise ValueError(
                f"Unknown agent type: {agent_type}. "
                f"Available types: {list(AGENT_REGISTRY.keys())}"
            )
        
        agent_class = AGENT_REGISTRY[agent_type]
        
        # Create config if dict was provided
        if isinstance(config, dict):
            # Get the appropriate config class
            config_class = AgentFactory._get_config_class(agent_type)
            config = config_class(**config)
        
        # Create agent
        agent = agent_class(config, **kwargs)
        logger.info(f"Created {agent_type} agent: {agent.id}")
        return agent
    
    @staticmethod
    def _get_config_class(agent_type: str) -> Type:
        """Get the configuration class for an agent type."""
        config_map = {
            "guardian": GuardianConfig,
            "negotiator": NegotiatorConfig,
            "executor": ExecutorConfig,
            "verifier": VerifierConfig,
        }
        return config_map.get(agent_type, dict)
    
    @staticmethod
    def register_agent_type(name: str, agent_class: Type) -> None:
        """
        Register a custom agent type.
        
        Args:
            name: Name of the agent type
            agent_class: Agent class
        """
        AGENT_REGISTRY[name.lower()] = agent_class
        logger.info(f"Registered agent type: {name}")
    
    @staticmethod
    def list_agent_types() -> List[str]:
        """List all registered agent types."""
        return list(AGENT_REGISTRY.keys())
    
    @staticmethod
    def get_agent_info(agent_type: str) -> Dict[str, Any]:
        """
        Get information about an agent type.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Dictionary with agent information
        """
        agent_type = agent_type.lower()
        
        if agent_type not in AGENT_REGISTRY:
            return {"error": f"Unknown agent type: {agent_type}"}
        
        agent_class = AGENT_REGISTRY[agent_type]
        
        return {
            "type": agent_type,
            "class": agent_class.__name__,
            "module": agent_class.__module__,
            "config_class": AgentFactory._get_config_class(agent_type).__name__,
            "description": {
                "guardian": "Protocol enforcement, security, and audit",
                "negotiator": "Contract negotiation and agreement",
                "executor": "Task execution and workflow management",
                "verifier": "Result verification and validation",
            }.get(agent_type, "Unknown description"),
        }


# Convenience functions for quick agent creation

def create_guardian(
    name: str = "GuardianAgent",
    enforce_protocol: bool = True,
    enforce_signatures: bool = True,
    rate_limit: int = 100,
    **kwargs
) -> GuardianAgent:
    """
    Quickly create a Guardian agent with default settings.
    
    Args:
        name: Agent name
        enforce_protocol: Enforce protocol compliance
        enforce_signatures: Enforce message signatures
        rate_limit: Rate limit per minute
        **kwargs: Additional configuration
        
    Returns:
        GuardianAgent instance
    """
    config = GuardianConfig(
        name=name,
        enforce_protocol=enforce_protocol,
        enforce_signatures=enforce_signatures,
        rate_limit=rate_limit,
        **kwargs
    )
    return GuardianAgent(config)


def create_negotiator(
    name: str = "NegotiatorAgent",
    strategy: str = "collaborative",
    max_rounds: int = 10,
    **kwargs
) -> NegotiatorAgent:
    """
    Quickly create a Negotiator agent with default settings.
    
    Args:
        name: Agent name
        strategy: Negotiation strategy ('collaborative', 'competitive', 'principled')
        max_rounds: Maximum negotiation rounds
        **kwargs: Additional configuration
        
    Returns:
        NegotiatorAgent instance
    """
    config = NegotiatorConfig(
        name=name,
        strategy=strategy,
        max_rounds=max_rounds,
        **kwargs
    )
    return NegotiatorAgent(config)


def create_executor(
    name: str = "ExecutorAgent",
    concurrent_tasks: int = 5,
    enable_retry: bool = True,
    **kwargs
) -> ExecutorAgent:
    """
    Quickly create an Executor agent with default settings.
    
    Args:
        name: Agent name
        concurrent_tasks: Maximum concurrent tasks
        enable_retry: Enable retry on failure
        **kwargs: Additional configuration
        
    Returns:
        ExecutorAgent instance
    """
    config = ExecutorConfig(
        name=name,
        concurrent_tasks=concurrent_tasks,
        enable_retry=enable_retry,
        **kwargs
    )
    return ExecutorAgent(config)


def create_verifier(
    name: str = "VerifierAgent",
    require_multiple_verifiers: int = 1,
    verification_threshold: float = 0.8,
    **kwargs
) -> VerifierAgent:
    """
    Quickly create a Verifier agent with default settings.
    
    Args:
        name: Agent name
        require_multiple_verifiers: Number of verifiers required
        verification_threshold: Threshold for verification pass
        **kwargs: Additional configuration
        
    Returns:
        VerifierAgent instance
    """
    config = VerifierConfig(
        name=name,
        require_multiple_verifiers=require_multiple_verifiers,
        verification_threshold=verification_threshold,
        **kwargs
    )
    return VerifierAgent(config)


def create_agent_system(
    guardian_config: Optional[Dict[str, Any]] = None,
    negotiator_config: Optional[Dict[str, Any]] = None,
    executor_config: Optional[Dict[str, Any]] = None,
    verifier_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Agent]:
    """
    Create a complete multi-agent system with all specialized agents.
    
    Args:
        guardian_config: Configuration for Guardian agent
        negotiator_config: Configuration for Negotiator agent
        executor_config: Configuration for Executor agent
        verifier_config: Configuration for Verifier agent
        
    Returns:
        Dictionary of created agents
    """
    agents = {}
    
    # Default configurations
    guardian_config = guardian_config or {"name": "GuardianAgent"}
    negotiator_config = negotiator_config or {"name": "NegotiatorAgent"}
    executor_config = executor_config or {"name": "ExecutorAgent"}
    verifier_config = verifier_config or {"name": "VerifierAgent"}
    
    # Create agents using factory
    agents["guardian"] = AgentFactory.create_agent("guardian", guardian_config)
    agents["negotiator"] = AgentFactory.create_agent("negotiator", negotiator_config)
    agents["executor"] = AgentFactory.create_agent("executor", executor_config)
    agents["verifier"] = AgentFactory.create_agent("verifier", verifier_config)
    
    logger.info("Created complete multi-agent system")
    return agents


# Version
__version__ = "3.0.0"


# Exports
__all__ = [
    # Agent classes
    'GuardianAgent',
    'GuardianConfig',
    'NegotiatorAgent',
    'NegotiatorConfig',
    'ExecutorAgent',
    'ExecutorConfig',
    'VerifierAgent',
    'VerifierConfig',
    
    # Factory
    'AgentFactory',
    'AGENT_REGISTRY',
    
    # Convenience functions
    'create_guardian',
    'create_negotiator',
    'create_executor',
    'create_verifier',
    'create_agent_system',
    
    # Version
    '__version__',
]