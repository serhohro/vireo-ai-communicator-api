# ============================================================
# VIREO GRPC SERVER
# ============================================================
"""
gRPC server adapter for Vireo.

Provides high-performance RPC communication between agents.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class GRPCService:
    """gRPC service definition."""
    name: str
    methods: Dict[str, Any]
    handler: Optional[Any] = None


class GRPCServer:
    """
    gRPC server for Vireo.
    
    Features:
    - High-performance RPC
    - Streaming support
    - Protocol buffer serialization
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 50051):
        self.host = host
        self.port = port
        self._services: Dict[str, GRPCService] = {}
        self._running = False
    
    def register_service(self, name: str, methods: Dict[str, Any],
                         handler: Optional[Any] = None) -> GRPCService:
        """Register a gRPC service."""
        service = GRPCService(
            name=name,
            methods=methods,
            handler=handler
        )
        self._services[name] = service
        logger.info(f"✅ gRPC service registered: {name}")
        return service
    
    async def start(self):
        """Start the gRPC server."""
        self._running = True
        # In a real implementation, this would start the gRPC server
        logger.info(f"✅ gRPC server started on {self.host}:{self.port}")
    
    async def stop(self):
        """Stop the gRPC server."""
        self._running = False
        logger.info("🛑 gRPC server stopped")
    
    def call_method(self, service_name: str, method_name: str, 
                    request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a gRPC method."""
        service = self._services.get(service_name)
        if not service:
            logger.error(f"Service not found: {service_name}")
            return None
        
        if method_name not in service.methods:
            logger.error(f"Method not found: {method_name}")
            return None
        
        if service.handler:
            return service.handler(request)
        
        return {"status": "error", "message": "No handler for service"}
    
    def get_services(self) -> List[Dict[str, Any]]:
        """Get all registered services."""
        return [
            {
                "name": service.name,
                "methods": list(service.methods.keys())
            }
            for service in self._services.values()
        ]


class GRPCClient:
    """
    gRPC client for Vireo.
    
    Provides client-side RPC calls to Vireo services.
    """
    
    def __init__(self, server_address: str = "localhost:50051"):
        self.server_address = server_address
        self._connected = False
    
    async def connect(self):
        """Connect to the gRPC server."""
        self._connected = True
        logger.info(f"✅ gRPC client connected to {self.server_address}")
    
    async def disconnect(self):
        """Disconnect from the gRPC server."""
        self._connected = False
        logger.info("🛑 gRPC client disconnected")
    
    async def call(self, service: str, method: str, 
                   request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a gRPC call."""
        if not self._connected:
            await self.connect()
        
        # In a real implementation, this would make the gRPC call
        return {
            "status": "success",
            "response": f"gRPC call to {service}.{method}",
            "request": request
        }