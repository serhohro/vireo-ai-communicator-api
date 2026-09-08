"""
Vireo Capability Management

Defines capabilities for AI agents and provides registry and discovery.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Set, Union
from enum import Enum

logger = logging.getLogger(__name__)


class CapabilityType(Enum):
    """Types of capabilities."""
    # AI/ML
    TEXT_GENERATION = "text-generation"
    CODE_ANALYSIS = "code-analysis"
    IMAGE_PROCESSING = "image-processing"
    DATA_ANALYSIS = "data-analysis"
    ML_TRAINING = "ml-training"
    INFERENCE = "inference"
    
    # Communication
    NEGOTIATION = "negotiation"
    CONTRACT = "contract"
    ESCROW = "escrow"
    ARBITRATION = "arbitration"
    
    # Security
    VERIFICATION = "verification"
    AUDIT = "audit"
    ENCRYPTION = "encryption"
    
    # System
    COMPUTATION = "computation"
    STORAGE = "storage"
    NETWORK = "network"
    MONITORING = "monitoring"
    
    # Specialized
    MEDICAL = "medical"
    LEGAL = "legal"
    FINANCIAL = "financial"
    EDUCATIONAL = "educational"


@dataclass
class Capability:
    """Agent capability definition."""
    
    name: str
    type: Union[CapabilityType, str]
    description: str = ""
    version: str = "1.0.0"
    config: Dict[str, Any] = field(default_factory=dict)
    required_permissions: List[str] = field(default_factory=list)
    cost: Optional[float] = None
    estimated_time: Optional[float] = None
    
    @classmethod
    def create(
        cls,
        name: str,
        type: Union[CapabilityType, str],
        **kwargs
    ) -> "Capability":
        """Create a new capability."""
        if isinstance(type, CapabilityType):
            type = type.value
        return cls(name=name, type=type, **kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type if isinstance(self.type, str) else self.type.value,
            "description": self.description
                def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type if isinstance(self.type, str) else self.type.value,
            "description": self.description,
            "version": self.version,
            "config": self.config,
            "required_permissions": self.required_permissions,
            "cost": self.cost,
            "estimated_time": self.estimated_time,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Capability":
        """Create from dictionary."""
        return cls(**data)


class CapabilityRegistry:
    """
    Registry for agent capabilities.
    Manages capability registration, discovery, and matching.
    """
    
    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        self._agent_capabilities: Dict[str, Set[str]] = {}
        self._capability_agents: Dict[str, Set[str]] = {}
    
    def register_capability(self, agent_id: str, capability: Capability) -> None:
        """
        Register a capability for an agent.
        
        Args:
            agent_id: ID of the agent
            capability: Capability to register
        """
        cap_id = capability.name
        
        # Store capability
        if cap_id not in self._capabilities:
            self._capabilities[cap_id] = capability
        
        # Link to agent
        if agent_id not in self._agent_capabilities:
            self._agent_capabilities[agent_id] = set()
        self._agent_capabilities[agent_id].add(cap_id)
        
        # Link capability to agent
        if cap_id not in self._capability_agents:
            self._capability_agents[cap_id] = set()
        self._capability_agents[cap_id].add(agent_id)
        
        logger.debug(f"Registered capability {cap_id} for agent {agent_id}")
    
    def unregister_capability(self, agent_id: str, capability_name: str) -> bool:
        """
        Unregister a capability.
        
        Args:
            agent_id: ID of the agent
            capability_name: Name of the capability
            
        Returns:
            True if unregistered, False otherwise
        """
        if agent_id not in self._agent_capabilities:
            return False
        
        if capability_name not in self._agent_capabilities[agent_id]:
            return False
        
        # Remove from agent
        self._agent_capabilities[agent_id].remove(capability_name)
        
        # Remove from capability agents
        if capability_name in self._capability_agents:
            self._capability_agents[capability_name].discard(agent_id)
        
        # Clean up empty sets
        if not self._agent_capabilities[agent_id]:
            del self._agent_capabilities[agent_id]
        
        if capability_name in self._capability_agents and not self._capability_agents[capability_name]:
            del self._capability_agents[capability_name]
            if capability_name in self._capabilities:
                del self._capabilities[capability_name]
        
        logger.debug(f"Unregistered capability {capability_name} for agent {agent_id}")
        return True
    
    def get_capability(self, capability_name: str) -> Optional[Capability]:
        """Get a capability by name."""
        return self._capabilities.get(capability_name)
    
    def get_agent_capabilities(self, agent_id: str) -> List[Capability]:
        """Get all capabilities for an agent."""
        if agent_id not in self._agent_capabilities:
            return []
        
        caps = []
        for cap_name in self._agent_capabilities[agent_id]:
            cap = self._capabilities.get(cap_name)
            if cap:
                caps.append(cap)
        return caps
    
    def get_agents_with_capability(self, capability_name: str) -> List[str]:
        """Get all agents that have a specific capability."""
        if capability_name not in self._capability_agents:
            return []
        return list(self._capability_agents[capability_name])
    
    def find_agents_by_capabilities(
        self,
        required_capabilities: List[str],
        optional_capabilities: List[str] = None,
        min_match: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Find agents that match required capabilities.
        
        Args:
            required_capabilities: List of required capability names
            optional_capabilities: List of optional capability names
            min_match: Minimum number of required capabilities to match
            
        Returns:
            List of agent IDs with match scores
        """
        results = []
        optional_caps = optional_capabilities or []
        
        for agent_id, caps in self._agent_capabilities.items():
            # Check required capabilities
            required_matches = [c for c in required_capabilities if c in caps]
            if len(required_matches) < min_match:
                continue
            
            # Check optional capabilities
            optional_matches = [c for c in optional_caps if c in caps]
            
            # Calculate score
            score = len(required_matches) + (len(optional_matches) * 0.5)
            match_ratio = len(required_matches) / len(required_capabilities) if required_capabilities else 1.0
            
            results.append({
                "agent_id": agent_id,
                "score": score,
                "match_ratio": match_ratio,
                "matched_required": required_matches,
                "matched_optional": optional_matches,
                "capabilities": list(caps),
            })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def list_capabilities(self) -> List[str]:
        """List all registered capability names."""
        return list(self._capabilities.keys())
    
    def list_agents(self) -> List[str]:
        """List all registered agent IDs."""
        return list(self._agent_capabilities.keys())
    
    def clear(self) -> None:
        """Clear all registrations."""
        self._capabilities.clear()
        self._agent_capabilities.clear()
        self._capability_agents.clear()


class CapabilityManager:
    """
    Manager for agent capabilities.
    Handles capability discovery, matching, and negotiation.
    """
    
    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self.registry = registry or CapabilityRegistry()
        self._pending_matches: Dict[str, Dict[str, Any]] = {}
    
    def register(self, agent_id: str, capability: Capability) -> None:
        """Register a capability."""
        self.registry.register_capability(agent_id, capability)
    
    def unregister(self, agent_id: str, capability_name: str) -> bool:
        """Unregister a capability."""
        return self.registry.unregister_capability(agent_id, capability_name)
    
    def get_capabilities(self, agent_id: str) -> List[Capability]:
        """Get capabilities for an agent."""
        return self.registry.get_agent_capabilities(agent_id)
    
    def find_match(
        self,
        agent_id: str,
        required_capabilities: List[str],
        optional_capabilities: List[str] = None,
        min_match: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Find matching agents for capabilities.
        
        Args:
            agent_id: ID of the requesting agent
            required_capabilities: Required capabilities
            optional_capabilities: Optional capabilities
            min_match: Minimum matches required
            
        Returns:
            List of matching agents with scores
        """
        # Exclude self
        results = self.registry.find_agents_by_capabilities(
            required_capabilities=required_capabilities,
            optional_capabilities=optional_capabilities,
            min_match=min_match
        )
        
        # Filter out self
        results = [r for r in results if r["agent_id"] != agent_id]
        
        return results
    
    async def negotiate_capabilities(
        self,
        requester_id: str,
        provider_id: str,
        required_capabilities: List[str],
        terms: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Negotiate capability usage between agents.
        
        Args:
            requester_id: ID of the requesting agent
            provider_id: ID of the provider agent
            required_capabilities: Required capabilities
            terms: Negotiation terms
            
        Returns:
            Negotiation result
        """
        # Check if provider has capabilities
        provider_caps = self.registry.get_agent_capabilities(provider_id)
        provider_cap_names = [c.name for c in provider_caps]
        
        missing = [c for c in required_capabilities if c not in provider_cap_names]
        if missing:
            return {
                "status": "failed",
                "reason": f"Provider missing capabilities: {missing}",
                "missing": missing,
            }
        
        # Create negotiation record
        negotiation_id = f"neg_{len(self._pending_matches)}"
        self._pending_matches[negotiation_id] = {
            "requester": requester_id,
            "provider": provider_id,
            "required": required_capabilities,
            "terms": terms or {},
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        
        return {
            "status": "pending",
            "negotiation_id": negotiation_id,
            "message": "Negotiation initiated",
        }
    
    def accept_negotiation(self, negotiation_id: str) -> Dict[str, Any]:
        """Accept a negotiation."""
        if negotiation_id not in self._pending_matches:
            return {"status": "failed", "reason": "Negotiation not found"}
        
        negotiation = self._pending_matches[negotiation_id]
        negotiation["status"] = "accepted"
        
        return {
            "status": "accepted",
            "negotiation_id": negotiation_id,
            "message": "Negotiation accepted",
        }
    
    def reject_negotiation(self, negotiation_id: str, reason: str = None) -> Dict[str, Any]:
        """Reject a negotiation."""
        if negotiation_id not in self._pending_matches:
            return {"status": "failed", "reason": "Negotiation not found"}
        
        negotiation = self._pending_matches[negotiation_id]
        negotiation["status"] = "rejected"
        
        return {
            "status": "rejected",
            "negotiation_id": negotiation_id,
            "reason": reason or "Negotiation rejected",
        }
    
    def get_negotiation(self, negotiation_id: str) -> Optional[Dict[str, Any]]:
        """Get negotiation details."""
        return self._pending_matches.get(negotiation_id)
    
    def cleanup_negotiations(self, max_age_seconds: int = 300) -> None:
        """Clean up old negotiations."""
        now = datetime.now()
        to_remove = []
        
        for neg_id, neg in self._pending_matches.items():
            if neg["status"] in ["accepted", "rejected"]:
                continue
            
            created = datetime.fromisoformat(neg["created_at"])
            if (now - created).total_seconds() > max_age_seconds:
                to_remove.append(neg_id)
        
        for neg_id in to_remove:
            del self._pending_matches[neg_id]