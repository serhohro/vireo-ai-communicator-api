# [file name]: src/transport/kafka.py
# ============================================================
# KAFKA TRANSPORT FOR VIREO
# ============================================================
"""
Kafka transport implementation for Vireo.

Provides:
- Event streaming
- Distributed communication
- High-throughput messaging
"""

from kafka import KafkaProducer, KafkaConsumer
import json
from typing import Callable, Optional, Dict, Any
import logging
import threading

logger = logging.getLogger("vireo.transport.kafka")


class KafkaEventBus:
    """Kafka транспорт для розподіленої комунікації."""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "vireo-group"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.producer = None
        self.consumer = None
        self._handlers: Dict[str, Callable] = {}
        self._running = False
        self._thread = None
    
    def connect(self):
        """Підключається до Kafka."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info(f"✅ Connected to Kafka: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"❌ Kafka connection failed: {e}")
            raise
    
    def publish(self, topic: str, message: Any) -> None:
        """
        Публікує повідомлення в топик.
        
        Args:
            topic: Назва топика
            message: Повідомлення
        """
        if not self.producer:
            self.connect()
        
        try:
            data = message.to_dict() if hasattr(message, 'to_dict') else message
            self.producer.send(topic, value=data)
            self.producer.flush()
            logger.info(f"📤 Published to {topic}")
        except Exception as e:
            logger.error(f"❌ Publish failed: {e}")
    
    def subscribe(self, topic: str, handler: Callable) -> None:
        """
        Підписується на топик.
        
        Args:
            topic: Назва топика
            handler: Функція-обробник
        """
        if not self.producer:
            self.connect()
        
        self._handlers[topic] = handler
        
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        logger.info(f"📥 Subscribed to {topic}")
    
    def _consume_messages(self):
        """Функція для споживання повідомлень у окремому потоці."""
        for msg in self.consumer:
            if not self._running:
                break
            try:
                handler = self._handlers.get(msg.topic)
                if handler:
                    handler(msg.value)
            except Exception as e:
                logger.error(f"❌ Message processing error: {e}")
    
    def start(self):
        """Запускає обробку повідомлень."""
        if not self._running and self.consumer:
            self._running = True
            self._thread = threading.Thread(target=self._consume_messages)
            self._thread.daemon = True
            self._thread.start()
            logger.info("🚀 Kafka event bus started")
    
    def stop(self):
        """Зупиняє обробку повідомлень."""
        self._running = False
        if self.consumer:
            self.consumer.close()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("🛑 Kafka event bus stopped")
    
    def close(self):
        """Закриває з'єднання."""
        self.stop()
        if self.producer:
            self.producer.close()
            logger.info("🔌 Kafka connection closed")