"""
Vireo Transport Package

Transport layer adapters for agent communication.

Provides:
- Redis transport (pub/sub, queue)
- WebSocket transport (real-time, bidirectional)
- gRPC transport (high-performance RPC)
- HTTP transport (REST API)
"""

from .redis import RedisTransport, RedisConfig
from .websocket import WebSocketTransport, WebSocketConfig
from .grpc import GRPCTransport, GRPCConfig
from .http import HTTPTransport, HTTPConfig

__all__ = [
    'RedisTransport',
    'RedisConfig',
    'WebSocketTransport',
    'WebSocketConfig',
    'GRPCTransport',
    'GRPCConfig',
    'HTTPTransport',
    'HTTPConfig',
]