# [file name]: src/transport/redis.py
# ============================================================
# REDIS TRANSPORT FOR VIREO
# ============================================================
"""
Redis transport implementation for Vireo.

Provides:
- Pub/Sub communication
- Distributed messaging
- Event bus functionality
"""

import redis
import json
from typing import Callable, Optional, Dict, Any
import logging
from protocol.message import Message  # ← ДОДАНО

logger = logging.getLogger("vireo.transport.redis")


class RedisEventBus:
    """Redis транспорт для розподіленої комунікації."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.pubsub = None
        self._handlers: Dict[str, Callable] = {}
        self._running = False
    
    def connect(self):
        """Підключається до Redis."""
        try:
            self.redis = redis.from_url(self.redis_url)
            self.pubsub = self.redis.pubsub()
            logger.info(f"✅ Connected to Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    def publish(self, channel: str, message: Any) -> None:
        """
        Публікує повідомлення в канал.
        
        Args:
            channel: Назва каналу
            message: Повідомлення (буде серіалізовано в JSON)
        """
        if not self.redis:
            self.connect()
        
        try:
            data = message.to_json() if hasattr(message, 'to_json') else json.dumps(message)
            self.redis.publish(channel, data)
            logger.info(f"📤 Published to {channel}")
        except Exception as e:
            logger.error(f"❌ Publish failed: {e}")
    
    def subscribe(self, channel: str, handler: Callable) -> None:
        """
        Підписується на канал.
        
        Args:
            channel: Назва каналу
            handler: Функція-обробник
        """
        if not self.redis:
            self.connect()
        
        self._handlers[channel] = handler
        self.pubsub.subscribe(**{channel: self._on_message})
        logger.info(f"📥 Subscribed to {channel}")
    
    def _on_message(self, message):
        """Обробляє вхідне повідомлення."""
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                handler = self._handlers.get(message['channel'])
                if handler:
                    # Створюємо Message з dict і передаємо його
                    msg = Message.from_dict(data)
                    handler(msg)
            except Exception as e:
                logger.error(f"❌ Message processing error: {e}")
    
    def start(self):
        """Запускає обробку повідомлень."""
        if not self._running:
            self._running = True
            self.pubsub.run_in_thread(sleep_time=0.001)
            logger.info("🚀 Redis event bus started")
    
    def stop(self):
        """Зупиняє обробку повідомлень."""
        if self._running:
            self._running = False
            self.pubsub.close()
            logger.info("🛑 Redis event bus stopped")
    
    def close(self):
        """Закриває з'єднання."""
        self.stop()
        if self.redis:
            self.redis.close()
            logger.info("🔌 Redis connection closed")