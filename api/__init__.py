"""
Vireo API Package

REST API and WebSocket interface for Vireo AI agents.
"""

from .server import app
from .routes import router
from .middleware import setup_middleware
from .auth import AuthManager, require_auth, require_api_key
from .websocket import WebSocketManager, ConnectionManager

__all__ = [
    'app',
    'create_app',
    'router',
    'setup_middleware',
    'AuthManager',
    'require_auth',
    'require_api_key',
    'WebSocketManager',
    'ConnectionManager',
]

__version__ = '3.0.0'