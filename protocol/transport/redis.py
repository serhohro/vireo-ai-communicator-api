"""Redis Transport for Vireo v2.0.1"""

from typing import Optional, Dict, Any
import json
import logging
import redis
from ..message import Message, MessageType

logger = logging.getLogger(__name__)


class RedisTransport:
    """Redis transport for Vireo messages"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        agent_id: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.agent_id = agent_id
        
        self._client = None
        self._connected = False
        self._logger = logging.getLogger(f"{__name__}.RedisTransport")
    
    def connect(self) -> None:
        """Connect to Redis"""
        try:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
            self._client.ping()
            self._connected = True
            self._logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            self._logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self._client:
            self._client.close()
            self._connected = False
            self._logger.info("Disconnected from Redis")
    
    def send(self, message: Message, recipient: str) -> bool:
        """Send a message to a recipient"""
        if not self._connected:
            self.connect()
        
        try:
            # Convert message to dict
            message_dict = message.to_dict()
            
            # Store in Redis
            channel = f"vireo:agent:{recipient}:inbox"
            self._client.lpush(channel, json.dumps(message_dict))
            self._logger.debug(f"Sent message {message.message_id} to {recipient}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to send message: {e}")
            return False
    
    def receive(self, timeout: int = 5) -> Optional[Message]:
        """Receive a message from the inbox"""
        if not self._connected:
            self.connect()
        
        if not self.agent_id:
            self._logger.error("Agent ID not set")
            return None
        
        try:
            channel = f"vireo:agent:{self.agent_id}:inbox"
            result = self._client.brpop(channel, timeout=timeout)
            
            if result:
                # result is (channel, data)
                data = json.loads(result[1])
                
                # Convert to Message using from_dict
                message = Message.from_dict(data)
                self._logger.debug(f"Received message {message.message_id} from {message.sender_id}")
                return message
            
            return None
        except Exception as e:
            self._logger.error(f"Failed to receive message: {e}")
            return None
    
    def broadcast(self, message: Message) -> bool:
        """Broadcast a message to all agents"""
        if not self._connected:
            self.connect()
        
        try:
            message_dict = message.to_dict()
            channel = "vireo:broadcast"
            self._client.publish(channel, json.dumps(message_dict))
            self._logger.debug(f"Broadcast message {message.message_id}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to broadcast: {e}")
            return False
    
    def subscribe(self, callback) -> None:
        """Subscribe to broadcast messages"""
        if not self._connected:
            self.connect()
        
        try:
            pubsub = self._client.pubsub()
            pubsub.subscribe("vireo:broadcast")
            
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    msg = Message.from_dict(data)
                    callback(msg)
        except Exception as e:
            self._logger.error(f"Subscription error: {e}")
    
    def set_agent_id(self, agent_id: str) -> None:
        """Set agent ID for receiving messages"""
        self.agent_id = agent_id
    
    def is_connected(self) -> bool:
        """Check if connected to Redis"""
        return self._connected
    
    def clear_inbox(self) -> None:
        """Clear the agent's inbox"""
        if not self._connected:
            self.connect()
        
        if not self.agent_id:
            return
        
        try:
            channel = f"vireo:agent:{self.agent_id}:inbox"
            self._client.delete(channel)
            self._logger.debug(f"Cleared inbox for {self.agent_id}")
        except Exception as e:
            self._logger.error(f"Failed to clear inbox: {e}")
    
    def get_inbox_size(self) -> int:
        """Get the number of messages in the inbox"""
        if not self._connected:
            self.connect()
        
        if not self.agent_id:
            return 0
        
        try:
            channel = f"vireo:agent:{self.agent_id}:inbox"
            return self._client.llen(channel)
        except Exception as e:
            self._logger.error(f"Failed to get inbox size: {e}")
            return 0