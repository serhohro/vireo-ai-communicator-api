"""
Vireo Agent Base Classes

Core agent implementation for the A2A protocol.
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Awaitable, Union, Set

from core.identity import DID, KeyManager
from core.crypto import ed25519, blake2b
from core.protocol import Message, Protocol, State, MessageType
from core.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Agent configuration."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    did: Optional[str] = None
    private_key: Optional[bytes] = None
    public_key: Optional[bytes] = None
    
    # Protocol settings
    protocol_version: str = "3.0.0"
    max_message_size: int = 1024 * 1024  # 1MB
    message_timeout: int = 30  # seconds
    max_retries: int = 3
    
    # Security settings
    require_signatures: bool = True
    require_encryption: bool = False
    replay_protection: bool = True
    
    # Runtime settings
    enable_jit: bool = True
    enable_gpu: bool = False
    enable_wasm: bool = False
    
    # Storage
    storage_path: str = "~/.vireo/data"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "did": self.did,
            "protocol_version": self.protocol_version,
            "max_message_size": self.max_message_size,
            "message_timeout": self.message_timeout,
            "require_signatures": self.require_signatures,
            "require_encryption": self.require_encryption,
            "replay_protection": self.replay_protection,
            "enable_jit": self.enable_jit,
            "enable_gpu": self.enable_gpu,
            "enable_wasm": self.enable_wasm,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        """Create from dictionary."""
        return cls(**data)


class Agent(ABC):
    """
    Base Agent class for Vireo A2A protocol.
    
    This class provides the core functionality for AI agents to communicate,
    negotiate, and coordinate with other agents.
    """
    
    def __init__(self, config: Union[AgentConfig, Dict[str, Any]]):
        """
        Initialize the agent.
        
        Args:
            config: Agent configuration or dict
        """
        if isinstance(config, dict):
            config = AgentConfig(**config)
        
        self.config = config
        self.id = config.did or f"did:vireo:{config.name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        self.name = config.name
        self.version = config.version
        self.capabilities = set(config.capabilities)
        
        # Initialize protocol
        self.protocol = Protocol(version=config.protocol_version)
        
        # Initialize key manager
        self.key_manager = KeyManager()
        if config.private_key and config.public_key:
            self.key_manager.import_keypair(config.private_key, config.public_key)
        
        # State
        self.status = "idle"
        self.peers: Dict[str, Any] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
        # Stats
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_processed": 0,
            "errors": 0,
            "started_at": None,
            "last_activity": None,
        }
        
        # Registry
        self.registry: Optional[Any] = None
        
        logger.info(f"Agent initialized: {self.id} ({self.name})")
    
    # ============================================================
    # Agent Lifecycle
    # ============================================================
    
    async def start(self) -> None:
        """Start the agent."""
        if self._running:
            return
        
        self._running = True
        self.status = "active"
        self.stats["started_at"] = datetime.now()
        
        # Start message processor
        self._tasks.append(
            asyncio.create_task(self._process_messages())
        )
        
        # Start heartbeat
        self._tasks.append(
            asyncio.create_task(self._heartbeat_loop())
        )
        
        # Initialize
        await self._on_start()
        
        logger.info(f"Agent started: {self.id}")
        self.emit("started", {"agent_id": self.id})
    
    async def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        self.status = "stopped"
        
        # Cancel tasks
        for task in self._tasks:
            task.cancel()
        
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        await self._on_stop()
        
        logger.info(f"Agent stopped: {self.id}")
        self.emit("stopped", {"agent_id": self.id})
    
    async def _on_start(self) -> None:
        """Called when agent starts."""
        pass
    
    async def _on_stop(self) -> None:
        """Called when agent stops."""
        pass
    
    # ============================================================
    # Message Handling
    # ============================================================
    
    def on_message(self, msg_type: Union[str, MessageType], handler: Callable) -> None:
        """
        Register a message handler.
        
        Args:
            msg_type: Message type to handle
            handler: Async function to handle the message
        """
        key = str(msg_type)
        if key not in self.message_handlers:
            self.message_handlers[key] = []
        self.message_handlers[key].append(handler)
    
    def on_event(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler.
        
        Args:
            event_type: Event type to handle
            handler: Function to handle the event
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit(self, event_type: str, data: Any) -> None:
        """
        Emit an event.
        
        Args:
            event_type: Event type
            data: Event data
        """
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
    
    async def handle_message(self, message: Union[Message, Dict[str, Any]]) -> Optional[Message]:
        """
        Handle an incoming message.
        
        Args:
            message: Message to handle
            
        Returns:
            Response message or None
        """
        if isinstance(message, dict):
            message = Message.from_dict(message)
        
        self.stats["messages_received"] += 1
        self.stats["last_activity"] = datetime.now()
        
        # Validate message
        if not self._validate_message(message):
            return self._create_error_message(
                "invalid_message",
                "Message validation failed",
                message.id
            )
        
        # Process through protocol
        try:
            result = self.protocol.process(message)
            if result and isinstance(result, Message):
                await self.send_message(result)
        except Exception as e:
            logger.error(f"Protocol error: {e}")
            return self._create_error_message(
                "protocol_error",
                str(e),
                message.id
            )
        
        # Find and execute handlers
        handlers = self.message_handlers.get(message.type, [])
        handlers.extend(self.message_handlers.get("*", []))
        
        response = None
        for handler in handlers:
            try:
                result = await handler(message)
                if result:
                    response = result
                    break
            except Exception as e:
                logger.error(f"Handler error for {message.type}: {e}")
        
        self.stats["messages_processed"] += 1
        
        if response:
            self.stats["messages_sent"] += 1
        
        return response
    
    async def send_message(self, message: Union[Message, Dict[str, Any]]) -> Optional[Message]:
        """
        Send a message to a peer.
        
        Args:
            message: Message to send
            
        Returns:
            Response message or None
        """
        if isinstance(message, dict):
            message = Message.from_dict(message)
        
        # Sign message
        if self.config.require_signatures and self.key_manager:
            signature = await self.key_manager.sign(
                did=self.id,
                data=message.to_bytes()
            )
            message.signature = signature
        
        self.stats["messages_sent"] += 1
        self.stats["last_activity"] = datetime.now()
        
        # Queue for sending
        await self._message_queue.put(("send", message))
        
        # Wait for response if expecting one
        if message.requires_response():
            return await self._wait_for_response(message.id)
        
        return None
    
    async def _process_messages(self) -> None:
        """Process messages from queue."""
        while self._running:
            try:
                item = await asyncio.wait_for(
                    self._message_queue.get(),
                    timeout=1.0
                )
                
                if item[0] == "send":
                    await self._deliver_message(item[1])
                elif item[0] == "response":
                    self._handle_response(item[1])
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Message processing error: {e}")
                self.stats["errors"] += 1
    
    async def _deliver_message(self, message: Message) -> None:
        """Deliver a message to the transport layer."""
        # This should be implemented by subclasses
        pass
    
    async def _wait_for_response(self, message_id: str, timeout: Optional[int] = None) -> Optional[Message]:
        """Wait for a response to a message."""
        timeout = timeout or self.config.message_timeout
        # This should be implemented by subclasses
        return None
    
    def _handle_response(self, response: Message) -> None:
        """Handle a response message."""
        # This should be implemented by subclasses
        pass
    
    # ============================================================
    # Message Validation
    # ============================================================
    
    def _validate_message(self, message: Message) -> bool:
        """Validate an incoming message."""
        # Check size
        if len(message.to_bytes()) > self.config.max_message_size:
            logger.warning(f"Message too large: {len(message.to_bytes())} bytes")
            return False
        
        # Check version
        if message.version != self.config.protocol_version:
            logger.warning(f"Protocol version mismatch: {message.version}")
            return False
        
        # Verify signature
        if self.config.require_signatures and message.signature:
            if not self._verify_signature(message):
                logger.warning(f"Invalid signature for message: {message.id}")
                return False
        
        # Check replay
        if self.config.replay_protection:
            if not self.protocol.check_nonce(message.nonce):
                logger.warning(f"Replay attack detected: {message.nonce}")
                return False
        
        return True
    
    def _verify_signature(self, message: Message) -> bool:
        """Verify a message signature."""
        if not self.key_manager:
            return False
        
        # Get sender's public key
        public_key = self.key_manager.get_public_key(message.sender)
        if not public_key:
            return False
        
        # Verify
        try:
            data = message.to_bytes_without_signature()
            return ed25519.Ed25519.verify(data, message.signature, public_key)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def _create_error_message(self, code: str, message: str, in_response_to: Optional[str] = None) -> Message:
        """Create an error message."""
        return Message(
            type="error",
            sender=self.id,
            payload={
                "error": {
                    "code": code,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                }
            },
            in_response_to=in_response_to,
        )
    
    # ============================================================
    # Heartbeat
    # ============================================================
    
    async def _heartbeat_loop(self) -> None:
        """Send heartbeats to peers."""
        while self._running:
            try:
                await asyncio.sleep(30)
                
                # Send heartbeat to all peers
                for peer_id in list(self.peers.keys()):
                    try:
                        await self.send_message(
                            Message(
                                type="heartbeat",
                                sender=self.id,
                                recipient=peer_id,
                                payload={
                                    "timestamp": datetime.now().isoformat(),
                                    "status": self.status,
                                }
                            )
                        )
                    except Exception as e:
                        logger.debug(f"Heartbeat to {peer_id} failed: {e}")
                        await self._remove_peer(peer_id)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def _remove_peer(self, peer_id: str) -> None:
        """Remove a peer from the peer list."""
        if peer_id in self.peers:
            del self.peers[peer_id]
            self.emit("peer_removed", {"peer_id": peer_id})
    
    # ============================================================
    # Capabilities
    # ============================================================
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities
    
    def add_capability(self, capability: str) -> None:
        """Add a capability to the agent."""
        self.capabilities.add(capability)
    
    def remove_capability(self, capability: str) -> None:
        """Remove a capability from the agent."""
        self.capabilities.discard(capability)
    
    def get_capabilities(self) -> List[str]:
        """Get all capabilities."""
        return list(self.capabilities)
    
    # ============================================================
    # Status & Info
    # ============================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "capabilities": list(self.capabilities),
            "peers": len(self.peers),
            "stats": self.stats,
            "uptime": (datetime.now() - self.stats["started_at"]).total_seconds() if self.stats["started_at"] else 0,
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information for discovery."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.config.description,
            "capabilities": list(self.capabilities),
            "protocol_version": self.config.protocol_version,
            "did": self.id,
        }
    
    # ============================================================
    # Abstract Methods
    # ============================================================
    
    @abstractmethod
    async def connect(self, peer_id: str, **kwargs) -> bool:
        """Connect to a peer agent."""
        pass
    
    @abstractmethod
    async def disconnect(self, peer_id: str) -> bool:
        """Disconnect from a peer agent."""
        pass
    
    @abstractmethod
    async def discover(self, **kwargs) -> List[Dict[str, Any]]:
        """Discover other agents."""
        pass


class BaseAgent(Agent):
    """
    Simple base agent implementation.
    """
    
    def __init__(self, config: Union[AgentConfig, Dict[str, Any]]):
        super().__init__(config)
        self._connections: Dict[str, Any] = {}
        self._transport = None
    
    async def connect(self, peer_id: str, **kwargs) -> bool:
        """Connect to a peer."""
        try:
            # Store peer
            self.peers[peer_id] = {
                "connected_at": datetime.now(),
                "status": "connected",
                "metadata": kwargs.get("metadata", {}),
            }
            self.emit("peer_connected", {"peer_id": peer_id})
            return True
        except Exception as e:
            logger.error(f"Connection to {peer_id} failed: {e}")
            return False
    
    async def disconnect(self, peer_id: str) -> bool:
        """Disconnect from a peer."""
        if peer_id in self.peers:
            del self.peers[peer_id]
            self.emit("peer_disconnected", {"peer_id": peer_id})
            return True
        return False
    
    async def discover(self, **kwargs) -> List[Dict[str, Any]]:
        """Discover other agents."""
        # Base implementation returns empty list
        return []
    
    async def _deliver_message(self, message: Message) -> None:
        """Deliver a message via transport."""
        if self._transport:
            await self._transport.send(message)