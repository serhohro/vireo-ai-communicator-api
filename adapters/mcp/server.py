# ============================================================
# VIREO MCP SERVER
# ============================================================
"""
MCP (Model Context Protocol) server adapter for Vireo.

Provides MCP-compatible tools and resources for Vireo agents.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Optional[Callable] = None


@dataclass
class MCPResource:
    """MCP resource definition."""
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"


class MCPServer:
    """
    MCP server adapter for Vireo.
    
    Provides:
    - Tool registration and execution
    - Resource management
    - Context sharing between agents
    """
    
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._resources: Dict[str, MCPResource] = {}
        self._context: Dict[str, Any] = {}
    
    def register_tool(self, name: str, description: str,
                      parameters: Dict[str, Any],
                      handler: Callable) -> MCPTool:
        """Register an MCP tool."""
        tool = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler
        )
        self._tools[name] = tool
        logger.info(f"✅ MCP tool registered: {name}")
        return tool
    
    def register_resource(self, uri: str, name: str,
                          description: str,
                          mime_type: str = "application/json") -> MCPResource:
        """Register an MCP resource."""
        resource = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mime_type=mime_type
        )
        self._resources[uri] = resource
        logger.info(f"✅ MCP resource registered: {uri}")
        return resource
    
    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute an MCP tool."""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        if tool.handler:
            return tool.handler(**arguments)
        return {"status": "error", "message": f"Tool {name} has no handler"}
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self._tools.values()
        ]
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """Get all registered resources."""
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type
            }
            for resource in self._resources.values()
        ]
    
    def set_context(self, key: str, value: Any) -> None:
        """Set context value."""
        self._context[key] = value
    
    def get_context(self, key: str) -> Optional[Any]:
        """Get context value."""
        return self._context.get(key)
    
    def clear_context(self) -> None:
        """Clear all context."""
        self._context.clear()
    
    def vireo_to_mcp(self, vireo_message: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Vireo message to MCP format."""
        return {
            "jsonrpc": "2.0",
            "method": vireo_message.get("intent", "propose").lower(),
            "params": {
                "sender": vireo_message.get("sender", {}).get("id", ""),
                "recipient": vireo_message.get("recipient", {}).get("id", ""),
                "payload": vireo_message.get("payload", {})
            },
            "id": vireo_message.get("message_id", "msg-001")
        }
    
    def mcp_to_vireo(self, mcp_message: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MCP message to Vireo format."""
        method = mcp_message.get("method", "propose").upper()
        params = mcp_message.get("params", {})
        
        return {
            "protocol": "VIREO-A2A",
            "version": "2.0.2",
            "message_id": mcp_message.get("id", "msg-001"),
            "conversation_id": f"conv-{mcp_message.get('id', '001')[:8]}",
            "sender": {"id": params.get("sender", "")},
            "recipient": {"id": params.get("recipient", "")},
            "intent": method,
            "payload": params.get("payload", {}),
            "timestamp": 0
        }