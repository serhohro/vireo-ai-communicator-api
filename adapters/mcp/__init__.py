# ============================================================
# VIREO MCP ADAPTER
# ============================================================
"""
MCP (Model Context Protocol) adapter for Vireo.

Provides:
- MCP server compatibility
- Tool registration
- Resource management
- Context sharing
"""

from .server import MCPServer, MCPTool, MCPResource

__all__ = [
    'MCPServer',
    'MCPTool',
    'MCPResource',
]