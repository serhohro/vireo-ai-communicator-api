#!/usr/bin/env python3
"""
Integration Tests: gRPC

Tests for gRPC transport integration.
"""

import pytest
import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import grpc
    HAS_GRPC = True
except ImportError:
    HAS_GRPC = False

try:
    from protocol.transport.grpc import GRPCTransport, GRPCConfig
    HAS_TRANSPORT = True
except ImportError:
    HAS_TRANSPORT = False


@pytest.mark.skipif(not HAS_GRPC, reason="grpcio not installed")
@pytest.mark.skipif(not HAS_TRANSPORT, reason="GRPCTransport not available")
class TestGRPCIntegration:
    """gRPC transport integration tests."""
    
    @pytest.fixture
    async def grpc_server(self):
        """Create a gRPC server transport."""
        config = GRPCConfig(
            host="127.0.0.1",
            port=50052
        )
        transport = GRPCTransport(config)
        await transport.start_server()
        yield transport
        await transport.stop_server()
        
    @pytest.fixture
    async def grpc_client(self):
        """Create a gRPC client transport."""
        config = GRPCConfig(
            target="127.0.0.1:50052"
        )
        transport = GRPCTransport(config)
        await transport.connect_client()
        yield transport
        await transport.disconnect_client()
        
    @pytest.mark.asyncio
    async def test_server_start_stop(self, grpc_server):
        """Test server start and stop."""
        assert grpc_server.is_connected() is True
        assert grpc_server.is_server() is True
        
    @pytest.mark.asyncio
    async def test_client_connect(self, grpc_client):
        """Test client connection."""
        assert grpc_client.is_connected() is True
        
    @pytest.mark.asyncio
    async def test_message_send(self, grpc_server, grpc_client):
        """Test sending message."""
        # Register handler
        received = []
        
        def handler(request):
            received.append(request)
            return {"status": "ok"}
            
        grpc_server.on_request("test", handler)
        
        # Send message
        await grpc_client.send({"type": "test", "payload": {"data": "hello"}})
        
        await asyncio.sleep(0.5)
        
        # Should have received message
        assert len(received) > 0
        
    @pytest.mark.asyncio
    async def test_request_handlers(self, grpc_server):
        """Test request handlers."""
        # Register multiple handlers
        handlers = {}
        
        def handler1(request):
            return {"response": "handler1"}
            
        def handler2(request):
            return {"response": "handler2"}
            
        grpc_server.on_request("method1", handler1)
        grpc_server.on_request("method2", handler2)
        
        stats = grpc_server.get_stats()
        assert stats["request_handlers"] == 2