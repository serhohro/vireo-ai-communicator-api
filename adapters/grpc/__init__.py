# ============================================================
# VIREO GRPC ADAPTER
# ============================================================
"""
gRPC adapter for Vireo.

Provides:
- High-performance RPC communication
- Streaming support
- Protocol buffer serialization
"""

from .server import GRPCServer, GRPCService, GRPCClient

__all__ = [
    'GRPCServer',
    'GRPCService',
    'GRPCClient',
]