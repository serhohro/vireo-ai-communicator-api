# api/websocket.py
"""Vireo WebSocket manager."""

import json
import logging
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass
from flask_socketio import emit, join_room, leave_room

logger = logging.getLogger(__name__)

@dataclass
class Connection:
    """WebSocket connection."""
    sid: str
    agent_id: str
    room: str = "default"


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self._connections: Dict[str, Connection] = {}
        self._rooms: Dict[str, Set[str]] = {}
    
    def connect(self, sid: str, agent_id: str, room: str = "default") -> None:
        """Add a new connection."""
        self._connections[sid] = Connection(sid=sid, agent_id=agent_id, room=room)
        
        if room not in self._rooms:
            self._rooms[room] = set()
        self._rooms[room].add(sid)
    
    def disconnect(self, sid: str) -> None:
        """Remove a connection."""
        if sid in self._connections:
            room = self._connections[sid].room
            if room in self._rooms:
                self._rooms[room].discard(sid)
            del self._connections[sid]
    
    def get_agent(self, sid: str) -> Optional[str]:
        """Get agent ID by SID."""
        if sid in self._connections:
            return self._connections[sid].agent_id
        return None
    
    def get_connections(self, room: str) -> list:
        """Get all connections in a room."""
        if room not in self._rooms:
            return []
        return [self._connections[sid] for sid in self._rooms[room] if sid in self._connections]
    
    def broadcast(self, room: str, event: str, data: Any) -> None:
        """Broadcast to all in a room."""
        emit(event, data, room=room)


class WebSocketManager:
    """WebSocket manager for Vireo."""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self._handlers = {}
    
    def register_handler(self, event: str, handler):
        """Register an event handler."""
        self._handlers[event] = handler
    
    async def handle_message(self, sid: str, data: Dict) -> None:
        """Handle incoming message."""
        event = data.get('type')
        if event in self._handlers:
            await self._handlers[event](sid, data)
    
    def broadcast_message(self, room: str, data: Dict) -> None:
        """Broadcast a message."""
        self.connection_manager.broadcast(room, 'message', data)


# Global instances
_ws_manager: Optional[WebSocketManager] = None
_connection_manager: Optional[ConnectionManager] = None

def get_ws_manager() -> WebSocketManager:
    """Get global WebSocket manager."""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager

def get_connection_manager() -> ConnectionManager:
    """Get global connection manager."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


# ============================================================
# SOCKETIO EVENT HANDLERS
# ============================================================

def setup_socketio_handlers(socketio):
    """Setup SocketIO event handlers."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info(f"Client connected: {request.sid}")
        emit('connected', {
            'version': '3.0.0',
            'protocol': 'Open Wire v3.0.0'
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {request.sid}")
        manager = get_connection_manager()
        manager.disconnect(request.sid)
    
    @socketio.on('message')
    def handle_message(data):
        """Handle incoming message."""
        logger.info(f"Message from {request.sid}: {data}")
        emit('message_ack', {
            'status': 'received',
            'timestamp': '2026-09-06T10:30:00Z'
        })
    
    @socketio.on('negotiate')
    def handle_negotiate(data):
        """Handle negotiation."""
        logger.info(f"Negotiation from {request.sid}: {data}")
        emit('negotiate_ack', {
            'status': 'accepted',
            'counter': data.get('proposal', {})
        })
    
    @socketio.on('execute')
    def handle_execute(data):
        """Handle execution."""
        logger.info(f"Execution from {request.sid}: {data}")
        emit('execute_ack', {
            'status': 'executed',
            'result': {'output': 'Execution complete'}
        })
    
    @socketio.on('verify')
    def handle_verify(data):
        """Handle verification."""
        logger.info(f"Verification from {request.sid}: {data}")
        emit('verify_ack', {
            'status': 'verified',
            'verified': True
        })