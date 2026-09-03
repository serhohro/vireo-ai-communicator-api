# ============================================================
# VIREO WEBSOCKET SERVER
# ============================================================
"""
WebSocket server adapter for Vireo.

Provides real-time communication between agents.
"""

import json
import uuid
import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from websockets import serve, WebSocketServerProtocol

logger = logging.getLogger(__name__)


@dataclass
class WebSocketConnection:
    """WebSocket connection."""
    id: str
    agent_id: Optional[str] = None
    websocket: Optional[WebSocketServerProtocol] = None
    connected: bool = False


@dataclass
class WebSocketMessage:
    """WebSocket message format."""
    type: str  # 'message', 'register', 'unregister'
    sender: str
    recipient: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: f"ws-{uuid.uuid4().hex[:8]}")


class WebSocketServer:
    """
    WebSocket server for real-time agent communication.
    
    Features:
    - Agent registration via WebSocket
    - Bidirectional messaging
    - Connection management
    - Automatic reconnection support
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self._connections: Dict[str, WebSocketConnection] = {}
        self._agent_connections: Dict[str, str] = {}  # agent_id → connection_id
        self._server = None
        self._running = False
    
    async def start(self):
        """Start the WebSocket server."""
        self._running = True
        self._server = await serve(self._handler, self.host, self.port)
        logger.info(f"✅ WebSocket server started on ws://{self.host}:{self.port}")
    
    async def stop(self):
        """Stop the WebSocket server."""
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logger.info("🛑 WebSocket server stopped")
    
    async def _handler(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket connection."""
        conn_id = f"conn-{uuid.uuid4().hex[:8]}"
        connection = WebSocketConnection(
            id=conn_id,
            websocket=websocket,
            connected=True
        )
        self._connections[conn_id] = connection
        
        logger.info(f"🔌 WebSocket connection: {conn_id}")
        
        try:
            async for message in websocket:
                await self._process_message(connection, message)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self._disconnect(conn_id)
    
    async def _process_message(self, connection: WebSocketConnection, message: str):
        """Process incoming WebSocket message."""
        try:
            data = json.loads(message)
            msg_type = data.get("type", "message")
            
            if msg_type == "register":
                agent_id = data.get("agent_id")
                if agent_id:
                    connection.agent_id = agent_id
                    self._agent_connections[agent_id] = connection.id
                    logger.info(f"✅ Agent registered via WebSocket: {agent_id}")
                    await self._send(connection, {
                        "type": "registered",
                        "agent_id": agent_id,
                        "status": "success"
                    })
            
            elif msg_type == "message":
                sender = data.get("sender")
                recipient = data.get("recipient")
                payload = data.get("payload", {})
                
                if recipient and recipient in self._agent_connections:
                    conn_id = self._agent_connections[recipient]
                    await self._send_to_conn(conn_id, {
                        "type": "message",
                        "sender": sender,
                        "payload": payload,
                        "message_id": data.get("message_id", f"msg-{uuid.uuid4().hex[:8]}")
                    })
                else:
                    await self._send(connection, {
                        "type": "error",
                        "message": f"Recipient not found: {recipient}"
                    })
            
            elif msg_type == "unregister":
                if connection.agent_id:
                    agent_id = connection.agent_id
                    self._agent_connections.pop(agent_id, None)
                    logger.info(f"🚫 Agent unregistered: {agent_id}")
                    await self._send(connection, {
                        "type": "unregistered",
                        "agent_id": agent_id,
                        "status": "success"
                    })
        
        except json.JSONDecodeError:
            await self._send(connection, {
                "type": "error",
                "message": "Invalid JSON"
            })
    
    async def _send(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Send data to a connection."""
        if connection.websocket and connection.connected:
            try:
                await connection.websocket.send(json.dumps(data))
            except Exception as e:
                logger.error(f"Send error: {e}")
    
    async def _send_to_conn(self, conn_id: str, data: Dict[str, Any]):
        """Send data to a specific connection."""
        connection = self._connections.get(conn_id)
        if connection:
            await self._send(connection, data)
    
    def _disconnect(self, conn_id: str):
        """Disconnect a connection."""
        connection = self._connections.pop(conn_id, None)
        if connection and connection.agent_id:
            self._agent_connections.pop(connection.agent_id, None)
            logger.info(f"🔌 WebSocket disconnected: {conn_id}")
    
    def get_connections(self) -> List[Dict[str, Any]]:
        """Get all active connections."""
        return [
            {
                "id": conn_id,
                "agent_id": conn.agent_id,
                "connected": conn.connected
            }
            for conn_id, conn in self._connections.items()
        ]
    
    def get_connected_agents(self) -> List[str]:
        """Get all connected agents."""
        return list(self._agent_connections.keys())