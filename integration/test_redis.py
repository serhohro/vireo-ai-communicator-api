#!/usr/bin/env python3
"""
Integration Tests: Redis

Tests for Redis transport integration.
"""

import pytest
import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

# Try to import protocol transport
try:
    from protocol.transport.redis import RedisTransport, RedisConfig
    HAS_TRANSPORT = True
except ImportError:
    HAS_TRANSPORT = False


@pytest.mark.skipif(not HAS_REDIS, reason="redis-py not installed")
@pytest.mark.skipif(not HAS_TRANSPORT, reason="RedisTransport not available")
class TestRedisIntegration:
    """Redis transport integration tests."""
    
    @pytest.fixture
    async def redis_transport(self):
        """Create a Redis transport instance."""
        config = RedisConfig(
            host="localhost",
            port=6379,
            db=15,  # Use test DB
        )
        transport = RedisTransport(config)
        await transport.connect()
        yield transport
        await transport.disconnect()
        
    @pytest.fixture
    async def redis_client(self):
        """Create a Redis client."""
        client = redis.Redis(
            host="localhost",
            port=6379,
            db=15,
            decode_responses=True
        )
        await client.ping()
        yield client
        await client.flushdb()
        await client.close()
        
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, redis_transport):
        """Test connecting and disconnecting."""
        assert redis_transport.is_connected() is True
        
    @pytest.mark.asyncio
    async def test_publish_subscribe(self, redis_transport, redis_client):
        """Test publish and subscribe."""
        received = []
        
        async def handler(message):
            received.append(message)
        
        # Subscribe
        await redis_transport.subscribe("test_channel", handler)
        
        # Publish
        await redis_transport.publish("test_channel", {"test": "data"})
        
        # Wait for message
        await asyncio.sleep(0.5)
        
        # Should have received message
        assert len(received) > 0
        assert received[0]["test"] == "data"
        
    @pytest.mark.asyncio
    async def test_queue_publish_consume(self, redis_transport, redis_client):
        """Test queue publish and consume."""
        received = []
        
        async def handler(message):
            received.append(message)
        
        # Subscribe to queue pattern
        await redis_transport.subscribe("test_queue", handler)
        
        # Publish to queue
        await redis_transport.publish_queue("test_queue", {"queue": "data"})
        
        # Wait for message
        await asyncio.sleep(0.5)
        
        # Should have received message
        assert len(received) > 0
        assert received[0]["queue"] == "data"
        
    @pytest.mark.asyncio
    async def test_pattern_subscription(self, redis_transport, redis_client):
        """Test pattern subscription."""
        received = []
        
        async def handler(message):
            received.append(message)
        
        # Subscribe to pattern
        await redis_transport.subscribe("test.*", handler)
        
        # Publish to matching channels
        await redis_transport.publish("test.one", {"id": 1})
        await redis_transport.publish("test.two", {"id": 2})
        
        # Wait for messages
        await asyncio.sleep(0.5)
        
        # Should have received both messages
        assert len(received) == 2
        
    @pytest.mark.asyncio
    async def test_message_metadata(self, redis_transport, redis_client):
        """Test message metadata."""
        received = []
        
        async def handler(message):
            received.append(message)
        
        await redis_transport.subscribe("metadata_test", handler)
        await redis_transport.publish("metadata_test", {"data": "test"})
        
        await asyncio.sleep(0.5)
        
        assert len(received) > 0
        assert "_meta" in received[0]
        assert "timestamp" in received[0]["_meta"]
        assert "channel" in received[0]["_meta"]
        
    @pytest.mark.asyncio
    async def test_queue_length(self, redis_transport):
        """Test getting queue length."""
        # Publish multiple messages
        for i in range(5):
            await redis_transport.publish_queue("length_test", {"index": i})
        
        length = await redis_transport.get_queue_length("length_test")
        assert length == 5
        
    @pytest.mark.asyncio
    async def test_clear_queue(self, redis_transport):
        """Test clearing a queue."""
        # Publish messages
        for i in range(3):
            await redis_transport.publish_queue("clear_test", {"index": i})
        
        length = await redis_transport.get_queue_length("clear_test")
        assert length == 3
        
        # Clear queue
        await redis_transport.clear_queue("clear_test")
        
        length = await redis_transport.get_queue_length("