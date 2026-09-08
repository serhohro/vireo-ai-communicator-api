"""
Vireo WebSocket Transport

WebSocket-based transport for real-time agent communication.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set
from datetime import datetime
from urllib.parse import urlparse

try:
    import websockets
    from websockets.client import WebSocketClientProtocol, connect
    from websockets.server import WebSocketServerProtocol, serve
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    WebSocketClientProtocol = None
    WebSocketServerProtocol = None

from core.protocol import Message

logger = logging.getLogger(__name__)


@dataclass
class WebSocketConfig:
    """WebSocket transport configuration."""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8765
    path: str = "/ws"
    
    # Client
    url: Optional[str] = None
    
    # SSL
    ssl: bool = False
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    
    # Connection
    ping_interval: int = 20
    ping_timeout: int = 20
    close_timeout: int = 10
    max_size: int = 2 ** 23  # 8MB
    
    # Authentication
    auth_token: Optional[str] = None
    
    # Reconnection
    reconnect: bool = True
    max_reconnect_attempts: int = 10
    reconnect_delay: float = 1.0
    max_reconnect_delay: float = 30.0
    
    # Other
    origins: List[str] = field(default_factory=lambda: ["*"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "path": self.path,
            "ssl": self.ssl,
            "ping_interval": self.ping_interval,
            "ping_timeout": self.ping_timeout,
            "max_size": self.max_size,
        }


class WebSocketTransport:
    """
    WebSocket transport for agent communication.
    
    Supports:
    - Bidirectional real-time messaging
    - Server and client modes
    - Authentication
    - Automatic reconnection
    """
    
    def __init__(self, config: Optional[WebSocketConfig] = None):
        if not HAS_WEBSOCKETS:
            raise ImportError("websockets required for WebSocketTransport. Install with: pip install websockets")
        
        self.config = config or WebSocketConfig()
        
        # Connection state
        self._websocket: Optional[WebSocketServerProtocol] = None
        self._client_websocket: Optional[WebSocketClientProtocol] = None
        self._server: Optional[asyncio.Server] = None
        
        self._running: bool = False
        self._connected: bool = False
        self._tasks: List[asyncio.Task] = []
        
        # Handlers
        self._message_handlers: List[Callable] = []
        self._connection_handlers: List[Callable] = []
        self._disconnection_handlers: List[Callable] = []
        
        # Connected clients (server mode)
        self._clients: Set[WebSocketServerProtocol] = set()
        
        # Reconnection
        self._reconnect_attempts: int = 0
        self._reconnect_task: Optional[asyncio.Task] = None
        
        # Message queue
        self._send_queue: asyncio.Queue = asyncio.Queue()
        
        logger.info(f"WebSocketTransport initialized (port={config.port}, path={config.path})")
    
    # ============================================================
    # Server Mode
    # ============================================================
    
    async def start_server(self) -> bool:
        """Start the WebSocket server."""
        if self._running:
            return True
        
        try:
            # Create SSL context if needed
            ssl_context = None
            if self.config.ssl:
                import ssl
                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                if self.config.ssl_cert and self.config.ssl_key:
                    ssl_context.load_cert_chain(
                        self.config.ssl_cert,
                        self.config.ssl_key
                    )
            
            # Start server
            self._server = await serve(
                self._handle_client_connection,
                host=self.config.host,
                port=self.config.port,
                ssl=ssl_context,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.ping_timeout,
                close_timeout=self.config.close_timeout,
                max_size=self.config.max_size,
                origins=self.config.origins,
            )
            
            self._running = True
            self._connected = True
            
            # Start message sender
            self._tasks.append(
                asyncio.create_task(self._sender_loop())
            )
            
            logger.info(f"WebSocket server started on {self.config.host}:{self.config.port}{self.config.path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            return False
    
    async def stop_server(self) -> None:
        """Stop the WebSocket server."""
        self._running = False
        self._connected = False
        
        # Close all client connections
        for client in list(self._clients):
            try:
                await client.close()
            except:
                pass
        
        # Cancel tasks
        for task in self._tasks:
            task.cancel()
        
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()
        
        # Close server
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        
        logger.info("WebSocket server stopped")
    
    async def _handle_client_connection(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """Handle a client connection."""
        if path != self.config.path:
            await websocket.close(1008, "Invalid path")
            return
        
        # Authentication
        if self.config.auth_token:
            # Check authentication header
            auth_header = websocket.request_headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                await websocket.close(1008, "Authentication required")
                return
            
            token = auth_header[7:]
            if token != self.config.auth_token:
                await websocket.close(1008, "Invalid authentication")
                return
        
        # Add client
        self._clients.add(websocket)
        
        # Notify connection handlers
        for handler in self._connection_handlers:
            try:
                await handler(websocket)
            except Exception as e:
                logger.error(f"Connection handler error: {e}")
        
        try:
            # Handle messages
            async for message in websocket:
                await self._handle_incoming_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            # Remove client
            self._clients.discard(websocket)
            
            # Notify disconnection handlers
            for handler in self._disconnection_handlers:
                try:
                    await handler(websocket)
                except Exception as e:
                    logger.error(f"Disconnection handler error: {e}")
    
    # ============================================================
    # Client Mode
    # ============================================================
    
    async def connect_client(self) -> bool:
        """Connect to a WebSocket server as client."""
        if self._connected:
            return True
        
        if not self.config.url:
            logger.error("WebSocket URL not configured")
            return False
        
        try:
            # Parse URL
            parsed = urlparse(self.config.url)
            is_secure = parsed.scheme == "wss"
            
            # Create headers
            headers = {}
            if self.config.auth_token:
                headers["Authorization"] = f"Bearer {self.config.auth_token}"
            
            # Connect
            self._client_websocket = await connect(
                self.config.url,
                extra_headers=headers,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.ping_timeout,
                close_timeout=self.config.close_timeout,
                max_size=self.config.max_size,
                ssl=is_secure,
            )
            
            self._connected = True
            self._reconnect_attempts = 0
            
            # Start receiver
            self._tasks.append(
                asyncio.create_task(self._client_receiver_loop())
            )
            self._tasks.append(
                asyncio.create_task(self._sender_loop())
            )
            
            logger.info(f"Connected to WebSocket server: {self.config.url}")
            
            # Notify connection handlers
            for handler in self._connection_handlers:
                try:
                    await handler(self._client_websocket)
                except Exception as e:
                    logger.error(f"Connection handler error: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            
            if self.config.reconnect:
                await self._schedule_reconnect()
            
            return False
    
    async def disconnect_client(self) -> None:
        """Disconnect from WebSocket server."""
        if self._client_websocket:
            try:
                await self._client_websocket.close()
            except:
                pass
            self._client_websocket = None
        
        self._connected = False
        
        # Cancel tasks
        for task in self._tasks:
            task.cancel()
        
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()
        
        logger.info("Disconnected from WebSocket server")
    
    async def _schedule_reconnect(self) -> None:
        """Schedule reconnection attempt."""
        if self._reconnect_task and not self._reconnect_task.done():
            return
        
        if self._reconnect_attempts >= self.config.max_reconnect_attempts:
            logger.warning("Max reconnect attempts reached")
            return
        
        self._reconnect_attempts += 1
        delay = min(
            self.config.reconnect_delay * (2 ** (self._reconnect_attempts - 1)),
            self.config.max_reconnect_delay
        )
        
        async def reconnect():
            await asyncio.sleep(delay)
            if not self._connected:
                await self.connect_client()
        
        self._reconnect_task = asyncio.create_task(reconnect())
        logger.info(f"Scheduled reconnect in {delay}s (attempt {self._reconnect_attempts})")
    
    # ============================================================
    # Message Handling
    # ============================================================
    
    async def _handle_incoming_message(self, websocket: WebSocketServerProtocol, message: Any) -> None:
        """Handle an incoming message."""
        try:
            # Parse message
            if isinstance(message, str):
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    data = {"data": message}
            else:
                data = message
            
            # Call handlers
            for handler in self._message_handlers:
                try:
                    await handler(data, websocket)
                except Exception as e:
                    logger.error(f"Message handler error: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")
    
    async def _client_receiver_loop(self) -> None:
        """Loop for receiving messages in client mode."""
        while self._connected and self._client_websocket:
            try:
                message = await self._client_websocket.recv()
                await self._handle_incoming_message(self._client_websocket, message)
                
            except websockets.exceptions.ConnectionClosed:
                break
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
            "transport": "websocket",
        }
        
        # Convert to string
        if not isinstance(data, str):
            data = json.dumps(data)
        
        # Send to all clients (server mode)
        if self._server and self._clients:
            failed = []
            for client in self._clients:
                try:
                    await client.send(data)
                except Exception:
                    failed.append(client)
            
            # Remove failed clients
            for client in failed:
                self._clients.discard(client)
            
            return len(failed) < len(self._clients)
        
        # Send to server (client mode)
        elif self._client_websocket:
            try:
                await self._client_websocket.send(data)
                return True
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                return False
        
        return False
    
    # ============================================================
    # Public Methods
    # ============================================================
    
    async def send(self, message: Any) -> bool:
        """
        Send a message.
        
        Args:
            message: Message to send (dict or Message object)
            
        Returns:
            True if queued successfully
        """
        if not self._connected:
            logger.warning("Not connected to WebSocket")
            return False
        
        await self._send_queue.put(message)
        return True
    
    async def send_to_client(self, client: WebSocketServerProtocol, message: Any) -> bool:
        """
        Send a message to a specific client (server mode).
        
        Args:
            client: Client websocket
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        if not self._server:
            logger.warning("Not in server mode")
            return False
        
        try:
            if isinstance(message, Message):
                data = message.to_dict()
            elif isinstance(message, dict):
                data = message
            else:
                data = {"data": str(message)}
            
            if not isinstance(data, str):
                data = json.dumps(data)
            
            await client.send(data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")
            return False
    
    def on_message(self, handler: Callable) -> None:
        """Register a message handler."""
        self._message_handlers.append(handler)
    
    def on_connect(self, handler: Callable) -> None:
        """Register a connection handler."""
        self._connection_handlers.append(handler)
    
    def on_disconnect(self, handler: Callable) -> None:
        """Register a disconnection handler."""
        self._disconnection_handlers.append(handler)
    
    def get_connected_clients(self) -> int:
        """Get number of connected clients (server mode)."""
        return len(self._clients)
    
    def get_client_count(self) -> int:
        """Get total connected clients."""
        if self._server:
            return len(self._clients)
        return 1 if self._connected else 0
    
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
            "clients": self.get_client_count(),
            "host": self.config.host,
            "port": self.config.port,
            "path": self.config.path,
            "queue_size": self._send_queue.qsize(),
            "handlers": len(self._message_handlers),
        }