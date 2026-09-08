"""
Vireo Redis Transport

Redis-based transport for agent communication using pub/sub and queues.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime

try:
    import redis.asyncio as redis
    from redis.asyncio import Redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    Redis = None

from core.protocol import Message

logger = logging.getLogger(__name__)


@dataclass
class RedisConfig:
    """Redis transport configuration."""
    
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    
    # Pub/sub
    channel_prefix: str = "vireo:"
    subscribe_patterns: List[str] = field(default_factory=lambda: ["vireo:*"])
    
    # Queue
    queue_prefix: str = "vireo:queue:"
    queue_timeout: int = 30  # seconds
    
    # Connection pool
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    
    # Retry
    retry_on_timeout: bool = True
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "password": self.password,
            "ssl": self.ssl,
            "channel_prefix": self.channel_prefix,
            "queue_prefix": self.queue_prefix,
            "max_connections": self.max_connections,
            "socket_timeout": self.socket_timeout,
            "retry_on_timeout": self.retry_on_timeout,
        }


class RedisTransport:
    """
    Redis transport for agent communication.
    
    Supports:
    - Pub/Sub for broadcast messages
    - Queues for point-to-point messages
    - Message persistence
    - Pattern-based subscriptions
    """
    
    def __init__(self, config: Optional[RedisConfig] = None):
        if not HAS_REDIS:
            raise ImportError("redis-py required for RedisTransport. Install with: pip install redis")
        
        self.config = config or RedisConfig()
        self._redis: Optional[Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._running: bool = False
        self._tasks: List[asyncio.Task] = []
        
        # Handlers
        self._message_handlers: Dict[str, List[Callable]] = {}
        self._default_handler: Optional[Callable] = None
        
        # Connection state
        self._connected: bool = False
        self._reconnect_task: Optional[asyncio.Task] = None
        
        logger.info(f"RedisTransport initialized (host={config.host}:{config.port})")
    
    # ============================================================
    # Connection Management
    # ============================================================
    
    async def connect(self) -> bool:
        """Connect to Redis."""
        if self._connected:
            return True
        
        try:
            self._redis = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                ssl=self.config.ssl,
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                decode_responses=True,
            )
            
            # Test connection
            await self._redis.ping()
            
            # Initialize pubsub
            self._pubsub = self._redis.pubsub()
            await self._pubsub.connect()
            
            self._connected = True
            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
            
            # Start subscriber
            await self._start_subscriber()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            
            if self.config.retry_on_timeout:
                await self._schedule_reconnect()
            
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        self._running = False
        self._connected = False
        
        # Cancel tasks
        for task in self._tasks:
            task.cancel()
        
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()
        
        # Close pubsub
        if self._pubsub:
            await self._pubsub.close()
            self._pubsub = None
        
        # Close connection
        if self._redis:
            await self._redis.close()
            self._redis = None
        
        logger.info("Disconnected from Redis")
    
    async def _schedule_reconnect(self) -> None:
        """Schedule reconnection attempt."""
        if self._reconnect_task and not self._reconnect_task.done():
            return
        
        async def reconnect():
            await asyncio.sleep(self.config.retry_delay)
            if not self._connected:
                await self.connect()
        
        self._reconnect_task = asyncio.create_task(reconnect())
    
    # ============================================================
    # Message Publishing
    # ============================================================
    
    async def publish(self, channel: str, message: Any) -> bool:
        """
        Publish a message to a channel.
        
        Args:
            channel: Channel name
            message: Message to publish (dict or Message object)
            
        Returns:
            True if published successfully
        """
        if not self._connected:
            logger.warning("Not connected to Redis")
            return False
        
        try:
            # Format channel
            full_channel = f"{self.config.channel_prefix}{channel}"
            
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
                "channel": full_channel,
                "transport": "redis",
            }
            
            # Publish
            result = await self._redis.publish(
                full_channel,
                json.dumps(data)
            )
            
            logger.debug(f"Published to {full_channel}: {result} subscribers")
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            return False
    
    async def publish_queue(self, queue: str, message: Any) -> bool:
        """
        Publish a message to a queue.
        
        Args:
            queue: Queue name
            message: Message to publish
            
        Returns:
            True if published successfully
        """
        if not self._connected:
            logger.warning("Not connected to Redis")
            return False
        
        try:
            full_queue = f"{self.config.queue_prefix}{queue}"
            
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
                "queue": full_queue,
                "transport": "redis",
            }
            
            # Push to queue (LPUSH, RPOP for FIFO)
            await self._redis.lpush(
                full_queue,
                json.dumps(data)
            )
            
            logger.debug(f"Published to queue {full_queue}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish to queue {queue}: {e}")
            return False
    
    # ============================================================
    # Message Subscription
    # ============================================================
    
    async def subscribe(
        self,
        channel: str,
        handler: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """
        Subscribe to a channel.
        
        Args:
            channel: Channel name (can include wildcard)
            handler: Async function to handle messages
        """
        full_channel = f"{self.config.channel_prefix}{channel}"
        
        if full_channel not in self._message_handlers:
            self._message_handlers[full_channel] = []
        self._message_handlers[full_channel].append(handler)
        
        # Subscribe to pattern if wildcard
        if "*" in full_channel:
            await self._subscribe_pattern(full_channel)
        else:
            await self._subscribe_channel(full_channel)
        
        logger.info(f"Subscribed to {full_channel}")
    
    async def _subscribe_channel(self, channel: str) -> None:
        """Subscribe to a specific channel."""
        if not self._pubsub:
            return
        
        try:
            await self._pubsub.subscribe(channel)
        except Exception as e:
            logger.error(f"Failed to subscribe to {channel}: {e}")
    
    async def _subscribe_pattern(self, pattern: str) -> None:
        """Subscribe to a pattern."""
        if not self._pubsub:
            return
        
        try:
            await self._pubsub.psubscribe(pattern)
        except Exception as e:
            logger.error(f"Failed to subscribe to pattern {pattern}: {e}")
    
    async def unsubscribe(self, channel: str) -> None:
        """Unsubscribe from a channel."""
        full_channel = f"{self.config.channel_prefix}{channel}"
        
        if full_channel in self._message_handlers:
            del self._message_handlers[full_channel]
        
        try:
            if self._pubsub:
                if "*" in full_channel:
                    await self._pubsub.punsubscribe(full_channel)
                else:
                    await self._pubsub.unsubscribe(full_channel)
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {full_channel}: {e}")
    
    async def _start_subscriber(self) -> None:
        """Start the subscriber loop."""
        if self._running:
            return
        
        self._running = True
        self._tasks.append(
            asyncio.create_task(self._subscriber_loop())
        )
        
        # Also start queue consumer
        self._tasks.append(
            asyncio.create_task(self._queue_consumer_loop())
        )
    
    async def _subscriber_loop(self) -> None:
        """Main subscriber loop for pub/sub messages."""
        while self._running and self._connected:
            try:
                message = await self._pubsub.get_message(
                    timeout=1.0,
                    ignore_subscribe_messages=True
                )
                
                if message:
                    await self._handle_pubsub_message(message)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Subscriber loop error: {e}")
                await asyncio.sleep(1)
    
    async def _handle_pubsub_message(self, message: Dict[str, Any]) -> None:
        """Handle a pub/sub message."""
        try:
            channel = message.get("channel")
            data_str = message.get("data")
            
            if not channel or not data_str:
                return
            
            # Parse data
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                data = {"data": data_str}
            
            # Find handlers
            handlers = []
            for pattern, hlist in self._message_handlers.items():
                if self._match_pattern(channel, pattern):
                    handlers.extend(hlist)
            
            # Call handlers
            for handler in handlers:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Handler error for {channel}: {e}")
            
            # Default handler
            if self._default_handler and not handlers:
                try:
                    await self._default_handler(channel, data)
                except Exception as e:
                    logger.error(f"Default handler error: {e}")
            
        except Exception as e:
            logger.error(f"Error handling pubsub message: {e}")
    
    def _match_pattern(self, channel: str, pattern: str) -> bool:
        """Match channel against pattern (supports wildcard)."""
        if pattern == channel:
            return True
        
        if "*" in pattern:
            # Simple wildcard matching
            parts = pattern.split("*")
            if len(parts) == 2:
                return channel.startswith(parts[0]) and channel.endswith(parts[1])
        
        return False
    
    # ============================================================
    # Queue Consumer
    # ============================================================
    
    async def _queue_consumer_loop(self) -> None:
        """Loop for consuming queue messages."""
        # Collect all queue patterns
        queue_patterns = set()
        for pattern in self._message_handlers:
            if pattern.startswith(self.config.queue_prefix):
                queue_patterns.add(pattern)
        
        if not queue_patterns:
            return
        
        while self._running and self._connected:
            try:
                # Check each queue
                for queue_pattern in queue_patterns:
                    await self._consume_queue(queue_pattern)
                
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue consumer error: {e}")
                await asyncio.sleep(1)
    
    async def _consume_queue(self, queue_pattern: str) -> None:
        """Consume messages from a queue."""
        if not self._redis:
            return
        
        try:
            # Pop message (RPOP)
            data_str = await self._redis.rpop(queue_pattern)
            if not data_str:
                return
            
            # Parse data
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                data = {"data": data_str}
            
            # Find handlers for this queue
            handlers = self._message_handlers.get(queue_pattern, [])
            for handler in handlers:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Queue handler error for {queue_pattern}: {e}")
            
        except Exception as e:
            logger.error(f"Error consuming queue {queue_pattern}: {e}")
    
    # ============================================================
    # Message Acknowledgment
    # ============================================================
    
    async def ack(self, queue: str, message_id: str) -> bool:
        """
        Acknowledge a message from a queue.
        
        Args:
            queue: Queue name
            message_id: Message ID to acknowledge
            
        Returns:
            True if acknowledged
        """
        if not self._connected:
            return False
        
        try:
            full_queue = f"{self.config.queue_prefix}{queue}"
            # Store acknowledgment in a separate set
            ack_key = f"{full_queue}:ack"
            await self._redis.sadd(ack_key, message_id)
            
            # Remove from queue
            await self._redis.lrem(full_queue, 1, message_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge message: {e}")
            return False
    
    # ============================================================
    # Utility Methods
    # ============================================================
    
    def set_default_handler(self, handler: Callable) -> None:
        """Set default handler for unhandled messages."""
        self._default_handler = handler
    
    async def get_queue_length(self, queue: str) -> int:
        """Get the length of a queue."""
        if not self._connected:
            return 0
        
        try:
            full_queue = f"{self.config.queue_prefix}{queue}"
            return await self._redis.llen(full_queue)
        except Exception:
            return 0
    
    async def clear_queue(self, queue: str) -> int:
        """Clear a queue."""
        if not self._connected:
            return 0
        
        try:
            full_queue = f"{self.config.queue_prefix}{queue}"
            return await self._redis.delete(full_queue)
        except Exception:
            return 0
    
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected
    
    def get_stats(self) -> Dict[str, Any]:
        """Get transport statistics."""
        return {
            "connected": self._connected,
            "host": self.config.host,
            "port": self.config.port,
            "db": self.config.db,
            "subscriptions": len(self._message_handlers),
            "queue_prefix": self.config.queue_prefix,
        }