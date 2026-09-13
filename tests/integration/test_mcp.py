#!/usr/bin/env python3
"""
Integration Tests: MCP (Model Context Protocol)

Tests for MCP (Model Context Protocol) integration.
"""

import pytest
import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from protocol.transport import HTTPTransport, HTTPConfig
    HAS_TRANSPORT = True
except ImportError:
    HAS_TRANSPORT = False

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


@pytest.mark.skipif(not HAS_TRANSPORT, reason="HTTPTransport not available")
@pytest.mark.skipif(not HAS_AIOHTTP, reason="aiohttp not installed")
class TestMCPIntegration:
    """MCP (Model Context Protocol) integration tests."""
    
    @pytest.fixture
    async def mcp_server(self):
        """Create an MCP server."""
        config = HTTPConfig(
            host="127.0.0.1",
            port=8081
        )
        transport = HTTPTransport(config)
        await transport.start_server()
        yield transport
        await transport.stop_server()
        
    @pytest.fixture
    async def http_client(self):
        """Create an HTTP client."""
        session = aiohttp.ClientSession()
        yield session
        await session.close()
        
    @pytest.mark.asyncio
    async def test_health_check(self, mcp_server, http_client):
        """Test health check endpoint."""
        async with http_client.get("http://127.0.0.1:8081/health") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "healthy"
            assert data["version"] == "3.0.0"
            
    @pytest.mark.asyncio
    async def test_ready_check(self, mcp_server, http_client):
        """Test ready check endpoint."""
        async with http_client.get("http://127.0.0.1:8081/ready") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "ready"
            
    @pytest.mark.asyncio
    async def test_message_endpoint(self, mcp_server, http_client):
        """Test message endpoint."""
        message = {
            "type": "test",
            "payload": {"data": "hello"},
            "sender": "test_agent",
            "recipient": "mcp_server"
        }
        
        async with http_client.post(
            "http://127.0.0.1:8081/messages",
            json=message
        ) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "received"
            
    @pytest.mark.asyncio
    async def test_webhook(self, mcp_server, http_client):
        """Test webhook endpoint."""
        webhook_data = {
            "event": "test",
            "data": {"value": 42}
        }
        
        # Register webhook handler
        received = []
        
        def handler(data):
            received.append(data)
            
        mcp_server.on_webhook(handler)
        
        # Send webhook
        async with http_client.post(
            "http://127.0.0.1:8081/webhook",
            json=webhook_data
        ) as resp:
            assert resp.status == 200
            
        await asyncio.sleep(0.5)
        
        # Should have received webhook
        assert len(received) > 0
        assert received[0]["event"] == "test"
        
    @pytest.mark.asyncio
    async def test_agents_endpoint(self, mcp_server, http_client):
        """Test agents endpoint."""
        async with http_client.get("http://127.0.0.1:8081/agents") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert "agents" in data
            assert "count" in data
            
    @pytest.mark.asyncio
    async def test_contracts_endpoint(self, mcp_server, http_client):
        """Test contracts endpoint."""
        async with http_client.get("http://127.0.0.1:8081/contracts") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert "contracts" in data
            assert "count" in data
            
    @pytest.mark.asyncio
    async def test_cors_headers(self, mcp_server, http_client):
        """Test CORS headers."""
        async with http_client.options("http://127.0.0.1:8081/messages") as resp:
            assert resp.status == 200
            assert "Access-Control-Allow-Origin" in resp.headers
            assert "Access-Control-Allow-Methods" in resp.headers
            
    @pytest.mark.asyncio
    async def test_invalid_json(self, mcp_server, http_client):
        """Test invalid JSON handling."""
        async with http_client.post(
            "http://127.0.0.1:8081/messages",
            data="invalid json"
        ) as resp:
            assert resp.status == 400
            
    @pytest.mark.asyncio
    async def test_not_found(self, mcp_server, http_client):
        """Test not found handling."""
        async with http_client.get("http://127.0.0.1:8081/notfound") as resp:
            assert resp.status == 404