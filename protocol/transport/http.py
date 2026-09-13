"""
Vireo HTTP Transport

HTTP-based transport for agent communication.
"""

import aiohttp
import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime
from aiohttp import web

from core.protocol import Message

logger = logging.getLogger(__name__)


@dataclass
class HTTPConfig:
    """HTTP transport configuration."""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    
    # SSL
    ssl: bool = False
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    
    # Client
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    
    # Headers
    auth_token: Optional[str] = None
    
    # CORS
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "ssl": self.ssl,
            "timeout": self.timeout,
            "cors_origins": self.cors_origins,
        }


class HTTPTransport:
    """
    HTTP transport for agent communication.
    
    Supports:
    - REST API endpoints
    - Webhooks
    - Client requests
    - Server responses
    """
    
    def __init__(self, config: Optional[HTTPConfig] = None):
        self.config = config or HTTPConfig()
        
        # Server state
        self._app: Optional[web.Application] = None
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        
        self._running: bool = False
        self._connected: bool = False
        
        # Client state
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Handlers
        self._route_handlers: Dict[str, Callable] = {}
        self._webhook_handlers: List[Callable] = []
        
        logger.info(f"HTTPTransport initialized (port={config.port})")
    
    # ============================================================
    # Server Mode
    # ============================================================
    
    async def start_server(self) -> bool:
        """Start the HTTP server."""
        if self._running:
            return True
        
        try:
            # Create app
            self._app = web.Application()
            
            # Setup routes
            self._setup_routes()
            
            # Add middleware
            self._setup_middleware()
            
            # Setup runner
            self._runner = web.AppRunner(self._app)
            await self._runner.setup()
            
            # Setup site
            self._site = web.TCPSite(
                self._runner,
                host=self.config.host,
                port=self.config.port
            )
            
            await self._site.start()
            
            self._running = True
            self._connected = True
            
            logger.info(f"HTTP server started on {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start HTTP server: {e}")
            return False
    
    async def stop_server(self) -> None:
        """Stop the HTTP server."""
        self._running = False
        self._connected = False
        
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
        
        if self._app:
            self._app = None
        
        self._site = None
        
        logger.info("HTTP server stopped")
    
    def _setup_routes(self) -> None:
        """Setup HTTP routes."""
        # Health check
        self._app.router.add_get("/health", self._health_handler)
        self._app.router.add_get("/ready", self._ready_handler)
        
        # Message endpoint
        self._app.router.add_post("/messages", self._message_handler)
        self._app.router.add_get("/messages/{message_id}", self._get_message_handler)
        
        # Webhook endpoint
        self._app.router.add_post("/webhook", self._webhook_handler)
        
        # Agent endpoints
        self._app.router.add_get("/agents", self._list_agents_handler)
        self._app.router.add_post("/agents", self._create_agent_handler)
        
        # Contract endpoints
        self._app.router.add_get("/contracts", self._list_contracts_handler)
        self._app.router.add_post("/contracts", self._create_contract_handler)
    
    def _setup_middleware(self) -> None:
        """Setup middleware."""
        # CORS
        @web.middleware
        async def cors_middleware(request: web.Request, handler):
            response = await handler(request)
            response.headers["Access-Control-Allow-Origin"] = ", ".join(self.config.cors_origins)
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        
        self._app.middlewares.append(cors_middleware)
        
        # Authentication
        @web.middleware
        async def auth_middleware(request: web.Request, handler):
            if self.config.auth_token:
                auth = request.headers.get("Authorization", "")
                if not auth.startswith("Bearer "):
                    return web.Response(status=401, text="Unauthorized")
                
                token = auth[7:]
                if token != self.config.auth_token:
                    return web.Response(status=403, text="Forbidden")
            
            return await handler(request)
        
        self._app.middlewares.append(auth_middleware)
        
        # Logging
        @web.middleware
        async def logging_middleware(request: web.Request, handler):
            start = datetime.now()
            response = await handler(request)
            duration = (datetime.now() - start).total_seconds()
            logger.info(f"{request.method} {request.path} - {response.status} - {duration:.3f}s")
            return response
        
        self._app.middlewares.append(logging_middleware)
    
    # ============================================================
    # HTTP Handlers
    # ============================================================
    
    async def _health_handler(self, request: web.Request) -> web.Response:
        """Health check handler."""
        return web.json_response({
            "status": "healthy",
            "version": "3.0.0",
            "timestamp": datetime.now().isoformat(),
        })
    
    async def _ready_handler(self, request: web.Request) -> web.Response:
        """Ready check handler."""
        return web.json_response({
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
        })
    
    async def _message_handler(self, request: web.Request) -> web.Response:
        """Message handler."""
        try:
            data = await request.json()
            
            # Process message
            message_type = data.get("type")
            payload = data.get("payload", {})
            recipient = data.get("recipient")
            sender = data.get("sender")
            
            # Call registered handlers
            if message_type in self._route_handlers:
                result = await self._route_handlers[message_type](data)
                return web.json_response(result)
            
            # Default response
            return web.json_response({
                "status": "received",
                "timestamp": datetime.now().isoformat(),
            })
            
        except json.JSONDecodeError:
            return web.Response(status=400, text="Invalid JSON")
        except Exception as e:
            logger.error(f"Message handler error: {e}")
            return web.Response(status=500, text=str(e))
    
    async def _get_message_handler(self, request: web.Request) -> web.Response:
        """Get message handler."""
        message_id = request.match_info.get("message_id")
        return web.json_response({
            "message_id": message_id,
            "status": "found",
            "timestamp": datetime.now().isoformat(),
        })
    
    async def _webhook_handler(self, request: web.Request) -> web.Response:
        """Webhook handler."""
        try:
            data = await request.json()
            
            # Call webhook handlers
            for handler in self._webhook_handlers:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Webhook handler error: {e}")
            
            return web.json_response({
                "status": "processed",
                "timestamp": datetime.now().isoformat(),
            })
            
        except json.JSONDecodeError:
            return web.Response(status=400, text="Invalid JSON")
    
    async def _list_agents_handler(self, request: web.Request) -> web.Response:
        """List agents handler."""
        return web.json_response({
            "agents": [],
            "count": 0,
            "timestamp": datetime.now().isoformat(),
        })
    
    async def _create_agent_handler(self, request: web.Request) -> web.Response:
        """Create agent handler."""
        try:
            data = await request.json()
            return web.json_response({
                "agent_id": f"agent_{datetime.now().timestamp()}",
                "created": True,
                "timestamp": datetime.now().isoformat(),
            })
        except json.JSONDecodeError:
            return web.Response(status=400, text="Invalid JSON")
    
    async def _list_contracts_handler(self, request: web.Request) -> web.Response:
        """List contracts handler."""
        return web.json_response({
            "contracts": [],
            "count": 0,
            "timestamp": datetime.now().isoformat(),
        })
    
    async def _create_contract_handler(self, request: web.Request) -> web.Response:
        """Create contract handler."""
        try:
            data = await request.json()
            return web.json_response({
                "contract_id": f"ctr_{datetime.now().timestamp()}",
                "created": True,
                "timestamp": datetime.now().isoformat(),
            })
        except json.JSONDecodeError:
            return web.Response(status=400, text="Invalid JSON")
    
    # ============================================================
    # Client Mode
    # ============================================================
    
    async def connect_client(self) -> bool:
        """Connect to HTTP server as client."""
        if self._connected:
            return True
        
        if not self.config.base_url:
            logger.error("HTTP base URL not configured")
            return False
        
        try:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                headers=self._get_client_headers()
            )
            
            self._connected = True
            logger.info(f"Connected to HTTP server: {self.config.base_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to HTTP server: {e}")
            return False
    
    async def disconnect_client(self) -> None:
        """Disconnect from HTTP server."""
        self._connected = False
        
        if self._session:
            await self._session.close()
            self._session = None
        
        logger.info("Disconnected from HTTP server")
    
    def _get_client_headers(self) -> Dict[str, str]:
        """Get client headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        
        return headers
    
    # ============================================================
    # Public Methods
    # ============================================================
    
    async def send(self, message: Any) -> Optional[Dict[str, Any]]:
        """
        Send a message via HTTP.
        
        Args:
            message: Message to send
            
        Returns:
            Response data or None
        """
        if not self._connected or not self._session:
            logger.warning("Not connected to HTTP")
            return None
        
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
            "transport": "http",
        }
        
        # Send request
        url = f"{self.config.base_url}/messages"
        
        for attempt in range(self.config.max_retries):
            try:
                async with self._session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"HTTP error: {response.status}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Request error: {e}")
            
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    async def get(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Make a GET request.
        
        Args:
            path: API path
            
        Returns:
            Response data or None
        """
        if not self._connected or not self._session:
            return None
        
        url = f"{self.config.base_url}{path}"
        
        try:
            async with self._session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"GET error: {e}")
            return None
    
    async def post(self, path: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make a POST request.
        
        Args:
            path: API path
            data: Request data
            
        Returns:
            Response data or None
        """
        if not self._connected or not self._session:
            return None
        
        url = f"{self.config.base_url}{path}"
        
        try:
            async with self._session.post(url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"POST error: {e}")
            return None
    
    def on_route(self, path: str, method: str = "POST", handler: Callable = None):
        """Decorator to register a route handler."""
        def decorator(func):
            self._route_handlers[path] = func
            return func
        return decorator
    
    def on_webhook(self, handler: Callable) -> None:
        """Register a webhook handler."""
        self._webhook_handlers.append(handler)
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
    
    def is_server(self) -> bool:
        """Check if running in server mode."""
        return self._runner is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get transport statistics."""
        return {
            "connected": self._connected,
            "server_mode": self._runner is not None,
            "host": self.config.host,
            "port": self.config.port,
            "base_url": self.config.base_url,
            "routes": len(self._route_handlers),
            "webhooks": len(self._webhook_handlers),
        }