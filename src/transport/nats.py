# [file name]: src/transport/nats.py
# ============================================================
# NATS TRANSPORT FOR VIREO
# ============================================================
"""
NATS transport implementation for Vireo.

Provides:
- High-performance messaging
- Distributed communication
- Cloud-native integration
"""

import json
import logging
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger("vireo.transport.nats")


class NATSEventBus:
    """NATS транспорт для розподіленої комунікації."""
    
    def __init__(
        self,
        servers: str = "nats://localhost:4222",
        name: str = "vireo-agent"
    ):
        self.servers = servers
        self.name = name
        self.nc = None
        self.js = None
        self._handlers: Dict[str, Callable] = {}
        self._running = False
    
    async def connect(self):
        """Підключається до NATS."""
        try:
            import nats
            from nats.js import JetStreamContext
            
            self.nc = await nats.connect(
                servers=[self.servers],
                name=self.name
            )
            self.js = self.nc.jetstream()
            logger.info(f"✅ Connected to NATS: {self.servers}")
        except ImportError:
            logger.warning("⚠️ NATS not installed. Install: pip install nats-py")
        except Exception as e:
            logger.error(f"❌ NATS connection failed: {e}")
    
    async def publish(self, subject: str, message: Any) -> None:
        """
        Публікує повідомлення в тему.
        
        Args:
            subject: Назва теми
            message: Повідомлення
        """
        if not self.nc:
            await self.connect()
            if not self.nc:
                return
        
        try:
            data = message.to_json() if hasattr(message, 'to_json') else json.dumps(message)
            await self.nc.publish(subject, data.encode())
            logger.info(f"📤 Published to {subject}")
        except Exception as e:
            logger.error(f"❌ Publish failed: {e}")
    
    async def subscribe(self, subject: str, handler: Callable) -> None:
        """
        Підписується на тему.
        
        Args:
            subject: Назва теми
            handler: Функція-обробник
        """
        if not self.nc:
            await self.connect()
            if not self.nc:
                return
        
        self._handlers[subject] = handler
        
        async def msg_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                handler(data)
            except Exception as e:
                logger.error(f"❌ Message processing error: {e}")
        
        await self.nc.subscribe(subject, cb=msg_handler)
        logger.info(f"📥 Subscribed to {subject}")
    
    async def start(self):
        """Запускає обробку повідомлень."""
        self._running = True
        logger.info("🚀 NATS event bus started")
    
    async def stop(self):
        """Зупиняє обробку повідомлень."""
        self._running = False
        if self.nc:
            await self.nc.close()
            logger.info("🛑 NATS event bus stopped")
    
    async def close(self):
        """Закриває з'єднання."""
        await self.stop()