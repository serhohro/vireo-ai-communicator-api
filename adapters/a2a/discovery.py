# Vireo v3.0.0 — A2A Discovery
# Google Agent-to-Agent Protocol Discovery Adapter

import time
import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from core.identity.did import DID
from core.protocol.message import Message, Intent


class DiscoveryStatus(Enum):
    """Discovery status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


@dataclass
class AgentInfo:
    """Agent information for discovery."""
    agent_id: str
    did: str
    name: str
    capabilities: List[str]
    status: DiscoveryStatus
    last_seen: int
    endpoints: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "did": self.did,
            "name": self.name,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "last_seen": self.last_seen,
            "endpoints": self.endpoints,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentInfo':
        """Create from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            did=data["did"],
            name=data["name"],
            capabilities=data["capabilities"],
            status=DiscoveryStatus(data.get("status", "active")),
            last_seen=data.get("last_seen", int(time.time())),
            endpoints=data.get("endpoints", []),
            metadata=data.get("metadata", {})
        )


class Discovery:
    """
    Agent discovery for A2A (Agent-to-Agent) protocol.
    
    This class handles:
    - Agent registration and unregistration
    - Capability-based discovery
    - Agent status tracking
    - Endpoint management
    """
    
    def __init__(self, registry_url: str = "", ttl_seconds: int = 300):
        """
        Initialize discovery.
        
        Args:
            registry_url: URL of the registry service (optional)
            ttl_seconds: Time to live for agent entries (seconds)
        """
        self.registry_url = registry_url
        self.ttl_seconds = ttl_seconds
        self._agents: Dict[str, AgentInfo] = {}
        self._capability_index: Dict[str, Set[str]] = {}  # capability -> set of agent_ids
        self._discovery_handlers: List[callable] = []
    
    def register(
        self,
        agent_id: str,
        did: str,
        name: str,
        capabilities: List[str],
        endpoints: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Register an agent for discovery.
        
        Args:
            agent_id: Unique agent identifier
            did: Decentralized Identifier
            name: Human-readable agent name
            capabilities: List of agent capabilities
            endpoints: List of endpoint URLs
            metadata: Additional metadata
            ttl: Time to live (overrides default)
        
        Returns:
            True if registration successful
        """
        if not agent_id or not did or not name:
            return False
        
        # Validate DID format
        try:
            did_obj = DID.from_string(did)
            if did_obj.scheme != "did" or did_obj.method != "vireo":
                return False
        except ValueError:
            return False
        
        # Create agent info
        agent_info = AgentInfo(
            agent_id=agent_id,
            did=did,
            name=name,
            capabilities=capabilities or [],
            status=DiscoveryStatus.ACTIVE,
            last_seen=int(time.time()),
            endpoints=endpoints or [],
            metadata=metadata or {}
        )
        
        # Store agent
        self._agents[agent_id] = agent_info
        
        # Update capability index
        for capability in capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = set()
            self._capability_index[capability].add(agent_id)
        
        # Notify handlers
        for handler in self._discovery_handlers:
            try:
                handler("register", agent_info)
            except Exception:
                pass
        
        return True
    
    def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: Agent identifier to unregister
        
        Returns:
            True if unregistration successful
        """
        if agent_id not in self._agents:
            return False
        
        agent_info = self._agents[agent_id]
        
        # Remove from capability index
        for capability in agent_info.capabilities:
            if capability in self._capability_index:
                self._capability_index[capability].discard(agent_id)
                if not self._capability_index[capability]:
                    del self._capability_index[capability]
        
        # Remove agent
        del self._agents[agent_id]
        
        # Notify handlers
        for handler in self._discovery_handlers:
            try:
                handler("unregister", agent_id)
            except Exception:
                pass
        
        return True
    
    def update_status(self, agent_id: str, status: DiscoveryStatus) -> bool:
        """
        Update agent status.
        
        Args:
            agent_id: Agent identifier
            status: New status
        
        Returns:
            True if update successful
        """
        if agent_id not in self._agents:
            return False
        
        self._agents[agent_id].status = status
        self._agents[agent_id].last_seen = int(time.time())
        return True
    
    def update_endpoints(self, agent_id: str, endpoints: List[str]) -> bool:
        """
        Update agent endpoints.
        
        Args:
            agent_id: Agent identifier
            endpoints: New endpoint list
        
        Returns:
            True if update successful
        """
        if agent_id not in self._agents:
            return False
        
        self._agents[agent_id].endpoints = endpoints
        self._agents[agent_id].last_seen = int(time.time())
        return True
    
    def update_metadata(self, agent_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update agent metadata.
        
        Args:
            agent_id: Agent identifier
            metadata: New metadata
        
        Returns:
            True if update successful
        """
        if agent_id not in self._agents:
            return False
        
        self._agents[agent_id].metadata.update(metadata)
        self._agents[agent_id].last_seen = int(time.time())
        return True
    
    def discover(
        self,
        capability: Optional[str] = None,
        status: Optional[DiscoveryStatus] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover agents by capability and status.
        
        Args:
            capability: Filter by capability
            status: Filter by status
            limit: Maximum number of results
            offset: Offset for pagination
        
        Returns:
            List of agent dictionaries
        """
        # Clean expired agents
        self._clean_expired()
        
        # Get agent IDs
        if capability:
            agent_ids = self._capability_index.get(capability, set())
        else:
            agent_ids = set(self._agents.keys())
        
        # Filter by status
        if status:
            agent_ids = {
                aid for aid in agent_ids
                if aid in self._agents and self._agents[aid].status == status
            }
        
        # Convert to list
        results = [
            self._agents[aid].to_dict()
            for aid in agent_ids
            if aid in self._agents
        ]
        
        # Apply pagination
        if offset is not None:
            results = results[offset:]
        if limit is not None:
            results = results[:limit]
        
        return results
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent dictionary or None if not found
        """
        self._clean_expired()
        
        if agent_id in self._agents:
            return self._agents[agent_id].to_dict()
        return None
    
    def get_agent_by_did(self, did: str) -> Optional[Dict[str, Any]]:
        """
        Get agent by DID.
        
        Args:
            did: Decentralized Identifier
        
        Returns:
            Agent dictionary or None if not found
        """
        self._clean_expired()
        
        for agent in self._agents.values():
            if agent.did == did:
                return agent.to_dict()
        return None
    
    def list_capabilities(self) -> List[str]:
        """
        List all registered capabilities.
        
        Returns:
            List of capability names
        """
        self._clean_expired()
        return list(self._capability_index.keys())
    
    def get_agents_with_capability(self, capability: str) -> List[Dict[str, Any]]:
        """
        Get all agents with a specific capability.
        
        Args:
            capability: Capability name
        
        Returns:
            List of agent dictionaries
        """
        return self.discover(capability=capability)
    
    def get_active_agents(self) -> List[Dict[str, Any]]:
        """
        Get all active agents.
        
        Returns:
            List of active agent dictionaries
        """
        return self.discover(status=DiscoveryStatus.ACTIVE)
    
    def count_agents(self, capability: Optional[str] = None) -> int:
        """
        Count registered agents.
        
        Args:
            capability: Filter by capability
        
        Returns:
            Number of agents
        """
        self._clean_expired()
        
        if capability:
            return len(self._capability_index.get(capability, set()))
        return len(self._agents)
    
    def register_discovery_handler(self, handler: callable) -> None:
        """
        Register a handler for discovery events.
        
        Args:
            handler: Function(event_type, data) -> None
        """
        self._discovery_handlers.append(handler)
    
    def _clean_expired(self) -> None:
        """Remove expired agents."""
        now = int(time.time())
        expired = [
            agent_id for agent_id, info in self._agents.items()
            if now - info.last_seen > self.ttl_seconds
        ]
        
        for agent_id in expired:
            self.unregister(agent_id)
    
    def create_discovery_message(
        self,
        query: Optional[str] = None,
        capability: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a discovery request message.
        
        Args:
            query: Search query
            capability: Filter by capability
            agent_id: Specific agent ID
        
        Returns:
            Discovery message dictionary
        """
        message = {
            "type": "DISCOVERY_REQUEST",
            "timestamp": int(time.time()),
            "payload": {}
        }
        
        if query:
            message["payload"]["query"] = query
        if capability:
            message["payload"]["capability"] = capability
        if agent_id:
            message["payload"]["agent_id"] = agent_id
        
        return message
    
    def handle_discovery_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a discovery request message.
        
        Args:
            message: Discovery message dictionary
        
        Returns:
            Discovery response
        """
        payload = message.get("payload", {})
        query = payload.get("query")
        capability = payload.get("capability")
        agent_id = payload.get("agent_id")
        
        # Find matching agents
        if agent_id:
            agents = self.get_agent(agent_id)
            if agents:
                agents = [agents]
            else:
                agents = []
        elif capability:
            agents = self.get_agents_with_capability(capability)
        else:
            agents = self.discover()
        
        return {
            "type": "DISCOVERY_RESPONSE",
            "timestamp": int(time.time()),
            "payload": {
                "agents": agents,
                "count": len(agents),
                "query": query,
                "capability": capability
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export discovery registry to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "registry_url": self.registry_url,
            "ttl_seconds": self.ttl_seconds,
            "agents": {
                agent_id: info.to_dict()
                for agent_id, info in self._agents.items()
            },
            "capabilities": {
                cap: list(agent_ids)
                for cap, agent_ids in self._capability_index.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Discovery':
        """
        Create discovery from dictionary.
        
        Args:
            data: Dictionary representation
        
        Returns:
            Discovery instance
        """
        discovery = cls(
            registry_url=data.get("registry_url", ""),
            ttl_seconds=data.get("ttl_seconds", 300)
        )
        
        for agent_id, agent_data in data.get("agents", {}).items():
            discovery.register(
                agent_id=agent_id,
                did=agent_data.get("did", ""),
                name=agent_data.get("name", agent_id),
                capabilities=agent_data.get("capabilities", []),
                endpoints=agent_data.get("endpoints", []),
                metadata=agent_data.get("metadata", {})
            )
        
        return discovery
    
    def to_json(self) -> str:
        """
        Export discovery registry to JSON.
        
        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Discovery':
        """
        Create discovery from JSON.
        
        Args:
            json_str: JSON string
        
        Returns:
            Discovery instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


# ============================================================
# A2A DISCOVERY PROTOCOL HELPERS
# ============================================================

def create_capability_query(capability: str) -> Message:
    """
    Create a capability query message.
    
    Args:
        capability: Capability to query
    
    Returns:
        Vireo message
    """
    return Message.create(
        sender="did:vireo:agent:discovery",
        recipient="did:vireo:agent:discovery",
        intent=Intent.PROPOSE,
        proposal_id=f"discover_{capability}_{int(time.time())}",
        payload={
            "type": "CAPABILITY_QUERY",
            "capability": capability
        }
    )


def create_capability_response(capabilities: List[str]) -> Dict[str, Any]:
    """
    Create a capability response.
    
    Args:
        capabilities: List of capabilities
    
    Returns:
        Response dictionary
    """
    return {
        "type": "CAPABILITY_RESPONSE",
        "timestamp": int(time.time()),
        "capabilities": capabilities
    }


def parse_discovery_message(message: Message) -> Dict[str, Any]:
    """
    Parse a discovery message.
    
    Args:
        message: Vireo message
    
    Returns:
        Parsed payload
    """
    if not message.payload:
        return {}
    
    payload = message.payload
    msg_type = payload.get("type", "UNKNOWN")
    
    if msg_type == "CAPABILITY_QUERY":
        return {
            "type": "query",
            "capability": payload.get("capability")
        }
    elif msg_type == "CAPABILITY_RESPONSE":
        return {
            "type": "response",
            "capabilities": payload.get("capabilities", [])
        }
    elif msg_type == "DISCOVERY_REQUEST":
        return {
            "type": "discovery",
            "query": payload.get("query"),
            "capability": payload.get("capability"),
            "agent_id": payload.get("agent_id")
        }
    else:
        return {
            "type": "unknown",
            "payload": payload
        }