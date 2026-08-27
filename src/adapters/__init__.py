# [file name]: src/adapters/__init__.py
# ============================================================
# VIREO ADAPTERS PACKAGE
# ============================================================
"""
Adapters for integrating Vireo with other frameworks.

Provides:
- MCP (Model Context Protocol) server
- LangChain integration
- CrewAI integration
"""

from .mcp_server import create_mcp_server, VireoMCPServer
from .langchain import VireoAgentTool, VireoTaskInput
from .crewai import VireoCrewAIAgent

__all__ = [
    "create_mcp_server",
    "VireoMCPServer",
    "VireoAgentTool",
    "VireoTaskInput",
    "VireoCrewAIAgent",
]