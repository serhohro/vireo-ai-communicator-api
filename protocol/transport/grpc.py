"""
Vireo gRPC Transport

gRPC-based transport for high-performance agent communication.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime

try:
    import grpc
    from grpc.aio import insecure_channel, secure_channel, server
    HAS_GRPC = True
except ImportError:
    HAS_GRPC = False

from core.protocol import Message

logger = logging.getLogger(__name__)


@dataclass
class GRPCConfig:
    """gRPC transport configuration."""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 50051
    
    # SSL
    ssl: bool = False
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    ssl_ca: Optional[str] = None
    
    # Connection
    max_message_length: int = 100 * 1024 * 1024  # 100MB
    timeout: float = 30.0
    keepalive_time: int = 30000  # milliseconds
    keepalive_timeout: int = 10000  # milliseconds
    
    # Client
    target: Optional[str] = None
    insecure: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "ssl": self.ssl,
            "max_message_length": self.max_message_length,
            "timeout": self.timeout,
        }


class GRPCTransport:
    """
    gRPC transport for agent communication.
    
    Supports:
    - High-performance RPC
    - Streaming
    - Bidirectional communication
    - SSL/TLS
    """
    
    def __init__(self, config: Optional[GRPCConfig] = None):
        if not HAS_GRPC:
            raise ImportError("grpcio required for GRPCTransport. Install with: pip install grpcio grpcio-tools")
        
        self.config = config or GRPCConfig()
        
        # gRPC state
        self._server: Optional[grpc.aio.Server] = None
        self._channel: Optional[grpc.aio.Channel] = None
        
        self._running: bool = False
        self._connected: bool = False
        self._tasks: List[asyncio.Task] = []
        
        # Handlers
        self._request_handlers: Dict[str, Callable] = {}
        self._stream_handlers: Dict[str, Callable] = {}
        
        # Message queue
        self._send_queue: asyncio.Queue = asyncio.Queue()
        
        logger.info(f"GRPCTransport initialized (port={config.port})")
    
    # ============================================================
    # Server Mode
    # ============================================================
    
    async def start_server(self) -> bool:
        """Start the gRPC server."""
        if self._running:
            return True
        
        try:
            # Create server
            self._server = server()
            
            # Add SSL if configured
            if self.config.ssl:
                credentials = self._create_server_credentials()
                self._server = server(credentials=credentials)
            
            # Add port
            address = f"{self.config.host}:{self.config.port}"
            self._server.add_insecure_port(address)
            
            # Start server
            await self._server.start()
            
            self._running = True
            self._connected = True
            
            logger.info(f"gRPC server started on {address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start gRPC server: {e}")
            return False
    
    async def stop_server(self) -> None:
        """Stop the gRPC server."""
        self._running = False
        self._connected = False
        
        if self._server:
            await self._server.stop(5)
            self._server = None
        
        logger.info("gRPC server stopped")
    
    def _create_server_credentials(self) -> grpc.aio.ServerCredentials:
        """Create server SSL credentials."""
        import grpc
        
        with open(self.config.ssl_cert, 'rb') as f:
            cert = f.read()
        with open(self.config.ssl_key, 'rb') as f:
            key = f.read()
        
        return grpc.ssl_server_credentials([(key, cert)])
    
    # ============================================================
    # Client Mode
    # ============================================================
    
    async def connect_client(self) -> bool:
        """Connect to a gRPC server as client."""
        if self._connected:
            return True
        
        if not self.config.target:
            logger.error("gRPC target not configured")
            return False
        
        try:
            if self.config.ssl and not self.config.insecure:
                credentials = self._create_client_credentials()
                self._channel = secure_channel(
                    self.config.target,
                    credentials,
                    options=self._get_channel_options()
                )
            else:
                self._channel = insecure_channel(
                    self.config.target,
                    options=self._get_channel_options()
                )
            
            self._connected = True
            logger.info(f"Connected to gRPC server: {self.config.target}")
            
            # Start receiver
            self._tasks.append(
                asyncio.create_task(self._client_receiver_loop())
            )
            self._tasks.append(
                asyncio.create_task(self._sender_loop())
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to gRPC server: {e}")
            return False
    
    async def disconnect_client(self) -> None:
        """Disconnect from gRPC server."""
        self._connected = False
        
        if self._channel:
            await self._channel.close()
            self._channel = None
        
        # Cancel tasks
        for task in self._tasks:
            task.cancel()
        
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()
        
        logger.info("Disconnected from gRPC server")
    
    def _create_client_credentials(self) -> grpc.aio.ChannelCredentials:
        """Create client SSL credentials."""
        import grpc
        
        if self.config.ssl_ca:
            with open(self.config.ssl_ca, 'rb') as f:
                ca = f.read()
            return grpc.ssl_channel_credentials(root_certificates=ca)
        
        return grpc.ssl_channel_credentials()
    
    def _get_channel_options(self) -> List[tuple]:
        """Get channel options."""
        return [
            ('grpc.max_receive_message_length', self.config.max_message_length),
            ('grpc.max_send_message_length', self.config.max_message_length),
            ('grpc.keepalive_time_ms', self.config.keepalive_time),
            ('grpc.keepalive_timeout_ms', self.config.keepalive_timeout),
        ]
    
    # ============================================================
    # Message Handling
    # ============================================================
    
    async def _client_receiver_loop(self) -> None:
        """Loop for receiving messages in client mode."""
        while self._connected and self._channel:
            try:
                # Placeholder - actual implementation depends on protobuf definitions
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Client receiver error: {e}")
                await asyncio.sleep(1)
    
    async def _sender_loop(self) -> None:
        """Loop for sending queued messages."""
        while self._running or self._connected:
            try:
                # Get message from queue
                try:
                    message = await asyncio.wait_for(
                        self._send_queue.get(),
                        timeout=0.1
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Send message
                await self._send_message(message)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sender loop error: {e}")
                await asyncio.sleep(0.1)
    
    async def _send_message(self, message: Any) -> bool:
        """Send a message."""
        if not self._connected:
            return False
        
        # Format message
        if isinstance(message, Message):
            data = message.to_dict()
        elif isinstance(message, dict):
            data = message
        else:
            data = {"data": str(message)}
        
        # Add metadata
        data["_meta"] = {
            "timestamp": datetime.now().isoformat(),
            "transport": "grpc",
        }
        
        # Placeholder - actual implementation depends on protobuf definitions
        return True
    
    # ============================================================
    # Public Methods
    # ============================================================
    
    async def send(self, message: Any) -> bool:
        """
        Send a message.
        
        Args:
            message: Message to send
            
        Returns:
            True if queued successfully
        """
        if not self._connected:
            logger.warning("Not connected to gRPC")
            return False
        
        await self._send_queue.put(message)
        return True
    
    def on_request(self, method: str, handler: Callable) -> None:
        """Register a request handler."""
        self._request_handlers[method] = handler
    
    def on_stream(self, method: str, handler: Callable) -> None:
        """Register a stream handler."""
        self._stream_handlers[method] = handler
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
    
    def is_server(self) -> bool:
        """Check if running in server mode."""
        return self._server is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get transport statistics."""
        return {
            "connected": self._connected,
            "server_mode": self._server is not None,
            "host": self.config.host,
            "port": self.config.port,
            "queue_size": self._send_queue.qsize(),
            "request_handlers": len(self._request_handlers),
            "stream_handlers": len(self._stream_handlers),
        }