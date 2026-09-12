#!/usr/bin/env python3
"""
Integration Tests: WebSocket

Tests for WebSocket transport integration.
"""

import pytest
import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

try:
    from protocol.transport.websocket import WebSocketTransport, WebSocketConfig
    HAS_TRANSPORT = True
except ImportError:
    HAS_TRANSPORT = False


@pytest.mark.skipif(not HAS_WEBSOCKETS, reason="websockets not installed")
@pytest.mark.skipif(not HAS_TRANSPORT, reason="WebSocketTransport not available")
class TestWebSocketIntegration:
    """WebSocket transport integration tests."""
    
    @pytest.fixture
    async def ws_server(self):
        """Create a WebSocket server transport."""
        config = WebSocketConfig(
            host="127.0.0.1",
            port=8766,
            path="/test"
        )
        transport = WebSocketTransport(config)
        await transport.start_server()
        yield transport
        await transport.stop_server()
        
    @pytest.fixture
    async def ws_client(self):
        """Create a WebSocket client transport."""
        config = WebSocketConfig(
            url="ws://127.0.0.1:8766/test"
        )
        transport = WebSocketTransport(config)
        await transport.connect_client()
        yield transport
        await transport.disconnect_client()
        
    @pytest.mark.asyncio
    async def test_server_start_stop(self, ws_server):
        """Test server start and stop."""
        assert ws_server.is_connected() is True
        assert ws_server.is_server() is True
        
    @pytest.mark.asyncio
    async def test_client_connect(self, ws_client):
        """Test client connection."""
        assert ws_client.is_connected() is True
        
    @pytest.mark.asyncio
    async def test_message_exchange(self, ws_server, ws_client):
        """Test message exchange."""
        received = []
        
        def handler(message, client):
            received.append(message)
            
        ws_server.on_message(handler)
        
        # Send message from client
        await ws_client.send({"type": "ping", "payload": {"data": "hello"}})
        
        # Wait for message
        await asyncio.sleep(0.5)
        
        # Server should have received it
        assert len(received) > 0
        assert received[0]["type"] == "ping"
        
    @pytest.mark.asyncio
    async def test_multiple_clients(self, ws_server):
        """Test multiple clients."""
        received = []
        
        def handler(message, client):
            received.append(message)
            
        ws_server.on_message(handler)
        
        # Create multiple clients
        clients = []
        for i in range(3):
            config = WebSocketConfig(url="ws://127.0.0.1:8766/test")
            client = WebSocketTransport(config)
            await client.connect_client()
            clients.append(client)
            
        # Send messages
        for i, client in enumerate(clients):
            await client.send({"type": "test", "payload": {"id": i}})
            
        await asyncio.sleep(0.5)
        
        # All messages should be received
        assert len(received) == 3
        
        # Cleanup
        for client in clients:
            await client.disconnect_client()
            
    @pytest.mark.asyncio
    async def test_connection_handlers(self, ws_server):
        """Test connection and disconnection handlers."""
        connect_called = False
        disconnect_called = False
        
        def on_connect(client):
            nonlocal connect_called
            connect_called = True
            
        def on_disconnect(client):
            nonlocal disconnect_called
            disconnect_called = True
            
        ws_server.on_connect(on_connect)
        ws_server.on_disconnect(on_disconnect)
        
        # Connect client
        config = WebSocketConfig(url="ws://127.0.0.1:8766/test")
        client = WebSocketTransport(config)
        await client.connect_client()
        
        await asyncio.sleep(0.5)
        
        assert connect_called is True
        
        # Disconnect client
        await client.disconnect_client()
        
        await asyncio.sleep(0.5)
        
        assert disconnect_called is True
        
    @pytest.mark.asyncio
    async def test_client_count(self, ws_server):
        """Test client count."""
        # No clients initially
        assert ws_server.get_client_count() == 0
        
        # Connect clients
        clients = []
        for i in range(2):
            config = WebSocketConfig(url="ws://127.0.0.1:8766/test")
            client = WebSocketTransport(config)
            await client.connect_client()
            clients.append(client)
            
        await asyncio.sleep(0.5)
        
        # Should have 2 clients
        assert ws_server.get_client_count() == 2
        
        # Cleanup
        for client in clients:
            await client.disconnect_client()