# ============================================================
# VIREO WEBSOCKET ADAPTER
# ============================================================
"""
WebSocket adapter for Vireo.

Provides:
- Real-time agent communication
- Bidirectional messaging
- Connection management
"""

from .server import WebSocketServer, WebSocketConnection, WebSocketMessage

__all__ = [
    'WebSocketServer',
    'WebSocketConnection',
    'WebSocketMessage',
]