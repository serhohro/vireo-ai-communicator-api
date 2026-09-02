# Vireo Agent Core Package
# Version: 2.0.1

from .base import BaseAgent, AgentInfo
from .registry import AgentRegistry
from .roles import AgentRole, RoleDefinition, ROLES, get_role_definition, get_roles, validate_role_permission

__all__ = [
    # Base
    'BaseAgent',
    'AgentInfo',
    # Registry
    'AgentRegistry',
    # Roles
    'AgentRole',
    'RoleDefinition',
    'ROLES',
    'get_role_definition',
    'get_roles',
    'validate_role_permission',
]

__version__ = "2.0.1"