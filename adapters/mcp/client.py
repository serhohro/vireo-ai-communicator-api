# Vireo v3.0.0 — MCP Client
# Model Context Protocol Client Adapter

import json
import time
import asyncio
from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from core.protocol.message import Message, Intent
from core.identity.did import DID
from core.errors import ProtocolError, ValidationError


class MCPMethod(Enum):
    """MCP (Model Context Protocol) methods."""
    # Context Management
    SET_CONTEXT = "set_context"
    GET_CONTEXT = "get_context"
    UPDATE_CONTEXT = "update_context"
    DELETE_CONTEXT = "delete_context"
    LIST_CONTEXTS = "list_contexts"
    
    # Message Handling
    SEND_MESSAGE = "send_message"
    RECEIVE_MESSAGE = "receive_message"
    STREAM_MESSAGE = "stream_message"
    
    # Agent Management
    REGISTER_AGENT = "register_agent"
    UNREGISTER_AGENT = "unregister_agent"
    GET_AGENT = "get_agent"
    LIST_AGENTS = "list_agents"
    
    # Capability Discovery
    QUERY_CAPABILITIES = "query_capabilities"
    INFORM_CAPABILITIES = "inform_capabilities"
    
    # Contract Management
    PROPOSE_CONTRACT = "propose_contract"
    COMMIT_CONTRACT = "commit_contract"
    VERIFY_CONTRACT = "verify_contract"
    
    # System
    PING = "ping"
    STATUS = "status"
    SHUTDOWN = "shutdown"


@dataclass
class MCPContext:
    """MCP context data."""
    context_id: str
    agent_id: str
    data: Dict[str, Any]
    created_at: int
    updated_at: int
    ttl: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if context is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.updated_at > self.ttl
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "context_id": self.context_id,
            "agent_id": self.agent_id,
            "data": self.data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "ttl": self.ttl,
            "metadata": self.metadata,
            "expired": self.is_expired()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPContext':
        """Create from dictionary."""
        return cls(
            context_id=data["context_id"],
            agent_id=data["agent_id"],
            data=data.get("data", {}),
            created_at=data.get("created_at", int(time.time())),
            updated_at=data.get("updated_at", int(time.time())),
            ttl=data.get("ttl"),
            metadata=data.get("metadata", {})
        )


@dataclass
class MCPMessage:
    """MCP message format."""
    message_id: str
    method: str
    params: Dict[str, Any]
    timestamp: int
    from_agent: str
    to_agent: str
    response_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "method": self.method,
            "params": self.params,
            "timestamp": self.timestamp,
            "from": self.from_agent,
            "to": self.to_agent,
            "response_to": self.response_to
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create from dictionary."""
        return cls(
            message_id=data["message_id"],
            method=data["method"],
            params=data.get("params", {}),
            timestamp=data.get("timestamp", int(time.time())),
            from_agent=data["from"],
            to_agent=data["to"],
            response_to=data.get("response_to")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """Create from JSON."""
        return cls.from_dict(json.loads(json_str))


class MCPClient:
    """
    MCP (Model Context Protocol) Client Adapter.
    
    This client provides an interface to MCP-compatible servers
    for agent communication, context management, and contract handling.
    """
    
    def __init__(
        self,
        agent_id: str,
        server_url: Optional[str] = None,
        server: Optional['MCPServer'] = None,
        timeout_seconds: int = 30,
        enable_retry: bool = True,
        max_retries: int = 3
    ):
        """
        Initialize MCP client.
        
        Args:
            agent_id: Agent identifier
            server_url: MCP server URL (optional)
            server: MCPServer instance (optional)
            timeout_seconds: Request timeout
            enable_retry: Enable retry on failure
            max_retries: Maximum retry attempts
        """
        self.agent_id = agent_id
        self.did = f"did:vireo:agent:{agent_id}"
        self.server_url = server_url
        self.server = server
        self.timeout_seconds = timeout_seconds
        self.enable_retry = enable_retry
        self.max_retries = max_retries
        
        self._contexts: Dict[str, MCPContext] = {}
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._handlers: Dict[str, Callable] = {}
        self._connected = False
        self._message_counter = 0
    
    # ============================================================
    # CONNECTION MANAGEMENT
    # ============================================================
    
    async def connect(self) -> bool:
        """
        Connect to MCP server.
        
        Returns:
            True if connected successfully
        """
        if self.server:
            self._connected = True
            return True
        
        if self.server_url:
            try:
                # In production, this would establish actual connection
                # For now, simulate connection
                self._connected = True
                return True
            except Exception as e:
                raise ProtocolError(f"Failed to connect to MCP server: {e}")
        
        return False
    
    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        self._connected = False
        # Cancel pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()
    
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected
    
    # ============================================================
    # CONTEXT MANAGEMENT
    # ============================================================
    
    async def set_context(
        self,
        context_id: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> MCPContext:
        """
        Set a context.
        
        Args:
            context_id: Context identifier
            data: Context data
            ttl: Time to live in seconds
            metadata: Additional metadata
            agent_id: Target agent ID (for remote contexts)
        
        Returns:
            Created context
        """
        target_agent = agent_id or self.agent_id
        
        if target_agent == self.agent_id or not self.server:
            # Local context
            context = MCPContext(
                context_id=context_id,
                agent_id=target_agent,
                data=data,
                created_at=int(time.time()),
                updated_at=int(time.time()),
                ttl=ttl,
                metadata=metadata or {}
            )
            self._contexts[context_id] = context
            return context
        
        # Remote context
        result = await self._call_method(
            MCPMethod.SET_CONTEXT.value,
            {
                "context_id": context_id,
                "data": data,
                "ttl": ttl,
                "metadata": metadata,
                "agent_id": target_agent
            }
        )
        
        return MCPContext.from_dict(result["context"])
    
    async def get_context(
        self,
        context_id: str,
        agent_id: Optional[str] = None
    ) -> Optional[MCPContext]:
        """
        Get a context.
        
        Args:
            context_id: Context identifier
            agent_id: Target agent ID
        
        Returns:
            Context or None if not found
        """
        target_agent = agent_id or self.agent_id
        
        if target_agent == self.agent_id:
            # Local context
            context = self._contexts.get(context_id)
            if context and context.is_expired():
                del self._contexts[context_id]
                return None
            return context
        
        # Remote context
        result = await self._call_method(
            MCPMethod.GET_CONTEXT.value,
            {
                "context_id": context_id,
                "agent_id": target_agent
            }
        )
        
        if result.get("context"):
            return MCPContext.from_dict(result["context"])
        return None
    
    async def update_context(
        self,
        context_id: str,
        data: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> Optional[MCPContext]:
        """
        Update a context.
        
        Args:
            context_id: Context identifier
            data: New context data
            agent_id: Target agent ID
        
        Returns:
            Updated context or None
        """
        target_agent = agent_id or self.agent_id
        
        if target_agent == self.agent_id:
            # Local context
            context = self._contexts.get(context_id)
            if not context:
                return None
            context.data.update(data)
            context.updated_at = int(time.time())
            return context
        
        # Remote context
        result = await self._call_method(
            MCPMethod.UPDATE_CONTEXT.value,
            {
                "context_id": context_id,
                "data": data,
                "agent_id": target_agent
            }
        )
        
        if result.get("context"):
            return MCPContext.from_dict(result["context"])
        return None
    
    async def delete_context(
        self,
        context_id: str,
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Delete a context.
        
        Args:
            context_id: Context identifier
            agent_id: Target agent ID
        
        Returns:
            True if deleted successfully
        """
        target_agent = agent_id or self.agent_id
        
        if target_agent == self.agent_id:
            # Local context
            if context_id in self._contexts:
                del self._contexts[context_id]
                return True
            return False
        
        # Remote context
        result = await self._call_method(
            MCPMethod.DELETE_CONTEXT.value,
            {
                "context_id": context_id,
                "agent_id": target_agent
            }
        )
        
        return result.get("success", False)
    
    async def list_contexts(
        self,
        agent_id: Optional[str] = None
    ) -> List[MCPContext]:
        """
        List all contexts.
        
        Args:
            agent_id: Target agent ID
        
        Returns:
            List of contexts
        """
        target_agent = agent_id or self.agent_id
        
        if target_agent == self.agent_id:
            # Local contexts
            return [
                context for context in self._contexts.values()
                if not context.is_expired()
            ]
        
        # Remote contexts
        result = await self._call_method(
            MCPMethod.LIST_CONTEXTS.value,
            {"agent_id": target_agent}
        )
        
        return [
            MCPContext.from_dict(ctx)
            for ctx in result.get("contexts", [])
        ]
    
    # ============================================================
    # MESSAGE HANDLING
    # ============================================================
    
    async def send_message(
        self,
        to_agent: str,
        method: Union[str, MCPMethod],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send an MCP message.
        
        Args:
            to_agent: Recipient agent ID
            method: MCP method
            params: Method parameters
        
        Returns:
            Response data
        """
        if isinstance(method, MCPMethod):
            method = method.value
        
        message = MCPMessage(
            message_id=self._generate_message_id(),
            method=method,
            params=params or {},
            timestamp=int(time.time()),
            from_agent=self.agent_id,
            to_agent=to_agent
        )
        
        return await self._call_method(
            MCPMethod.SEND_MESSAGE.value,
            {
                "message": message.to_dict(),
                "timeout": self.timeout_seconds
            }
        )
    
    async def receive_message(
        self,
        message: Union[MCPMessage, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Receive and process an MCP message.
        
        Args:
            message: MCP message
        
        Returns:
            Response data
        """
        if isinstance(message, dict):
            message = MCPMessage.from_dict(message)
        
        # Check if there's a handler for this method
        if message.method in self._handlers:
            try:
                result = await self._handlers[message.method](message.params)
                return {
                    "success": True,
                    "result": result,
                    "message_id": message.message_id
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message_id": message.message_id
                }
        
        return {
            "success": False,
            "error": f"No handler for method: {message.method}",
            "message_id": message.message_id
        }
    
    async def stream_message(
        self,
        to_agent: str,
        method: Union[str, MCPMethod],
        params: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None
    ) -> None:
        """
        Stream a message (for streaming responses).
        
        Args:
            to_agent: Recipient agent ID
            method: MCP method
            params: Method parameters
            callback: Callback for streaming chunks
        """
        if isinstance(method, MCPMethod):
            method = method.value
        
        result = await self._call_method(
            MCPMethod.STREAM_MESSAGE.value,
            {
                "to": to_agent,
                "method": method,
                "params": params or {},
                "callback": bool(callback)
            }
        )
        
        if callback and result.get("stream_id"):
            # In production, this would handle streaming
            pass
    
    # ============================================================
    # AGENT MANAGEMENT
    # ============================================================
    
    async def register_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register an agent with the MCP server.
        
        Args:
            agent_id: Agent identifier
            capabilities: Agent capabilities
            name: Human-readable name
            metadata: Additional metadata
        
        Returns:
            Registration response
        """
        return await self._call_method(
            MCPMethod.REGISTER_AGENT.value,
            {
                "agent_id": agent_id,
                "capabilities": capabilities,
                "name": name or agent_id,
                "metadata": metadata or {}
            }
        )
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            True if unregistered successfully
        """
        result = await self._call_method(
            MCPMethod.UNREGISTER_AGENT.value,
            {"agent_id": agent_id}
        )
        return result.get("success", False)
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent information.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent information or None
        """
        result = await self._call_method(
            MCPMethod.GET_AGENT.value,
            {"agent_id": agent_id}
        )
        return result.get("agent")
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent information
        """
        result = await self._call_method(
            MCPMethod.LIST_AGENTS.value,
            {}
        )
        return result.get("agents", [])
    
    # ============================================================
    # CAPABILITY DISCOVERY
    # ============================================================
    
    async def query_capabilities(
        self,
        agent_id: Optional[str] = None
    ) -> List[str]:
        """
        Query agent capabilities.
        
        Args:
            agent_id: Agent ID (uses self if None)
        
        Returns:
            List of capabilities
        """
        target = agent_id or self.agent_id
        
        result = await self._call_method(
            MCPMethod.QUERY_CAPABILITIES.value,
            {"agent_id": target}
        )
        return result.get("capabilities", [])
    
    async def inform_capabilities(
        self,
        capabilities: List[str],
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Inform MCP server about capabilities.
        
        Args:
            capabilities: List of capabilities
            agent_id: Agent ID (uses self if None)
        
        Returns:
            True if successful
        """
        target = agent_id or self.agent_id
        
        result = await self._call_method(
            MCPMethod.INFORM_CAPABILITIES.value,
            {
                "agent_id": target,
                "capabilities": capabilities
            }
        )
        return result.get("success", False)
    
    # ============================================================
    # CONTRACT MANAGEMENT
    # ============================================================
    
    async def propose_contract(
        self,
        to_agent: str,
        contract: Dict[str, Any],
        proposal_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Propose a contract.
        
        Args:
            to_agent: Recipient agent ID
            contract: Contract data
            proposal_id: Optional proposal ID
        
        Returns:
            Proposal response
        """
        return await self._call_method(
            MCPMethod.PROPOSE_CONTRACT.value,
            {
                "to": to_agent,
                "contract": contract,
                "proposal_id": proposal_id or self._generate_proposal_id()
            }
        )
    
    async def commit_contract(
        self,
        proposal_id: str,
        to_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Commit to a contract.
        
        Args:
            proposal_id: Proposal ID
            to_agent: Recipient agent ID
        
        Returns:
            Commit response
        """
        return await self._call_method(
            MCPMethod.COMMIT_CONTRACT.value,
            {
                "proposal_id": proposal_id,
                "to": to_agent or self.agent_id
            }
        )
    
    async def verify_contract(
        self,
        proposal_id: str,
        result: Dict[str, Any],
        to_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify contract execution.
        
        Args:
            proposal_id: Proposal ID
            result: Execution result
            to_agent: Recipient agent ID
        
        Returns:
            Verification response
        """
        return await self._call_method(
            MCPMethod.VERIFY_CONTRACT.value,
            {
                "proposal_id": proposal_id,
                "result": result,
                "to": to_agent or self.agent_id
            }
        )
    
    # ============================================================
    # SYSTEM METHODS
    # ============================================================
    
    async def ping(self) -> bool:
        """
        Ping the MCP server.
        
        Returns:
            True if server responds
        """
        try:
            result = await self._call_method(
                MCPMethod.PING.value,
                {}
            )
            return result.get("status") == "ok"
        except Exception:
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get server status.
        
        Returns:
            Server status information
        """
        return await self._call_method(
            MCPMethod.STATUS.value,
            {}
        )
    
    async def shutdown(self) -> bool:
        """
        Shutdown the MCP server.
        
        Returns:
            True if shutdown initiated
        """
        result = await self._call_method(
            MCPMethod.SHUTDOWN.value,
            {}
        )
        return result.get("success", False)
    
    # ============================================================
    # HANDLER MANAGEMENT
    # ============================================================
    
    def register_handler(
        self,
        method: Union[str, MCPMethod],
        handler: Callable
    ) -> None:
        """
        Register a handler for an MCP method.
        
        Args:
            method: MCP method name
            handler: Async function to handle requests
        """
        if isinstance(method, MCPMethod):
            method = method.value
        self._handlers[method] = handler
    
    def unregister_handler(self, method: Union[str, MCPMethod]) -> None:
        """
        Unregister a handler.
        
        Args:
            method: MCP method name
        """
        if isinstance(method, MCPMethod):
            method = method.value
        self._handlers.pop(method, None)
    
    # ============================================================
    # PRIVATE METHODS
    # ============================================================
    
    def _generate_message_id(self) -> str:
        """Generate a unique message ID."""
        self._message_counter += 1
        return f"mcp_{int(time.time()*1000)}_{self._message_counter:06d}_{self.agent_id[:8]}"
    
    def _generate_proposal_id(self) -> str:
        """Generate a proposal ID."""
        return f"prop_{int(time.time()*1000)}_{self.agent_id[:8]}_{self._message_counter:04d}"
    
    async def _call_method(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an MCP method.
        
        Args:
            method: Method name
            params: Method parameters
        
        Returns:
            Method response
        """
        # Check connection
        if not self._connected:
            await self.connect()
        
        # If we have a local server, use it
        if self.server:
            return self.server.handle({"method": method, "params": params})
        
        # If we have a server URL, send request (simplified)
        if self.server_url:
            # In production, this would make an HTTP/gRPC request
            # For now, simulate response
            return await self._simulate_request(method, params)
        
        raise ProtocolError("No MCP server configured")
    
    async def _simulate_request(
        self,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate an MCP request (for testing).
        
        Args:
            method: Method name
            params: Method parameters
        
        Returns:
            Simulated response
        """
        # Simple simulation
        if method == MCPMethod.PING.value:
            return {"status": "ok", "timestamp": int(time.time())}
        
        elif method == MCPMethod.STATUS.value:
            return {
                "status": "running",
                "version": "3.0.0",
                "uptime": 3600,
                "agents": len(self._contexts) + 1
            }
        
        elif method == MCPMethod.SET_CONTEXT.value:
            context_id = params.get("context_id", "ctx_001")
            return {
                "context": {
                    "context_id": context_id,
                    "agent_id": params.get("agent_id", self.agent_id),
                    "data": params.get("data", {}),
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                    "ttl": params.get("ttl"),
                    "metadata": params.get("metadata", {})
                }
            }
        
        elif method == MCPMethod.GET_CONTEXT.value:
            context_id = params.get("context_id", "ctx_001")
            if context_id in self._contexts:
                return {"context": self._contexts[context_id].to_dict()}
            return {"context": None}
        
        elif method == MCPMethod.LIST_CONTEXTS.value:
            return {
                "contexts": [ctx.to_dict() for ctx in self._contexts.values()]
            }
        
        elif method == MCPMethod.REGISTER_AGENT.value:
            return {
                "success": True,
                "agent_id": params.get("agent_id"),
                "registered_at": int(time.time())
            }
        
        elif method == MCPMethod.QUERY_CAPABILITIES.value:
            return {
                "capabilities": ["chat", "execute", "verify", "negotiate"]
            }
        
        elif method == MCPMethod.PROPOSE_CONTRACT.value:
            return {
                "proposal_id": params.get("proposal_id", "prop_001"),
                "status": "proposed",
                "timestamp": int(time.time())
            }
        
        elif method == MCPMethod.COMMIT_CONTRACT.value:
            return {
                "proposal_id": params.get("proposal_id"),
                "status": "committed",
                "timestamp": int(time.time())
            }
        
        else:
            return {
                "success": True,
                "result": f"Method {method} called with params {params}"
            }
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Export client state to dictionary."""
        return {
            "agent_id": self.agent_id,
            "did": self.did,
            "server_url": self.server_url,
            "timeout_seconds": self.timeout_seconds,
            "enable_retry": self.enable_retry,
            "max_retries": self.max_retries,
            "connected": self._connected,
            "contexts": {
                ctx_id: ctx.to_dict()
                for ctx_id, ctx in self._contexts.items()
            },
            "handlers": list(self._handlers.keys())
        }
    
    def to_json(self) -> str:
        """Export client state to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        server: Optional['MCPServer'] = None
    ) -> 'MCPClient':
        """Create client from dictionary."""
        client = cls(
            agent_id=data["agent_id"],
            server_url=data.get("server_url"),
            server=server,
            timeout_seconds=data.get("timeout_seconds", 30),
            enable_retry=data.get("enable_retry", True),
            max_retries=data.get("max_retries", 3)
        )
        
        # Restore contexts
        for ctx_id, ctx_data in data.get("contexts", {}).items():
            client._contexts[ctx_id] = MCPContext.from_dict(ctx_data)
        
        return client
    
    @classmethod
    def from_json(
        cls,
        json_str: str,
        server: Optional['MCPServer'] = None
    ) -> 'MCPClient':
        """Create client from JSON."""
        return cls.from_dict(json.loads(json_str), server)


# ============================================================
# MCP MESSAGE CONVERTER
# ============================================================

class MCPMessageConverter:
    """
    Converter between Vireo and MCP message formats.
    """
    
    @staticmethod
    def vireo_to_mcp(message: Message) -> MCPMessage:
        """
        Convert Vireo message to MCP message.
        
        Args:
            message: Vireo message
        
        Returns:
            MCP message
        """
        # Map Vireo intent to MCP method
        intent_to_method = {
            Intent.PROPOSE: MCPMethod.PROPOSE_CONTRACT.value,
            Intent.COMMIT: MCPMethod.COMMIT_CONTRACT.value,
            Intent.VERIFY: MCPMethod.VERIFY_CONTRACT.value,
        }
        
        method = intent_to_method.get(message.intent, "unknown")
        
        return MCPMessage(
            message_id=message.proposal_id,
            method=method,
            params=message.payload or {},
            timestamp=message.timestamp_ms // 1000,
            from_agent=message.sender.split(":")[-1],
            to_agent=message.recipient.split(":")[-1]
        )
    
    @staticmethod
    def mcp_to_vireo(
        mcp_message: MCPMessage,
        sender_did: str,
        recipient_did: str
    ) -> Message:
        """
        Convert MCP message to Vireo message.
        
        Args:
            mcp_message: MCP message
            sender_did: Sender DID
            recipient_did: Recipient DID
        
        Returns:
            Vireo message
        """
        # Map MCP method to Vireo intent
        method_to_intent = {
            MCPMethod.PROPOSE_CONTRACT.value: Intent.PROPOSE,
            MCPMethod.COMMIT_CONTRACT.value: Intent.COMMIT,
            MCPMethod.VERIFY_CONTRACT.value: Intent.VERIFY,
        }
        
        intent = method_to_intent.get(mcp_message.method, Intent.PROPOSE)
        
        return Message.create(
            sender=sender_did,
            recipient=recipient_did,
            intent=intent,
            proposal_id=mcp_message.message_id,
            payload=mcp_message.params
        )