"""Agent Roles for Vireo v2.0.1

This module defines all available agent roles, their permissions,
capabilities, and constraints.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field


class AgentRole(Enum):
    """Agent roles in the Vireo ecosystem"""
    
    MASTER = "master"
    """Master agent that coordinates other agents"""
    
    WORKER = "worker"
    """Standard worker agent"""
    
    EXECUTOR = "executor"
    """Agent specialized in executing tasks"""
    
    GUARDIAN = "guardian"
    """Agent specialized in verification and security"""
    
    RESEARCHER = "researcher"
    """Agent specialized in research and analysis"""
    
    ANALYST = "analyst"
    """Agent specialized in data analysis"""
    
    TEACHER = "teacher"
    """Agent specialized in training and education"""
    
    CUSTOM = "custom"
    """Custom agent role"""


@dataclass
class RoleDefinition:
    """Definition of an agent role"""
    
    name: str
    """Role name"""
    
    description: str
    """Role description"""
    
    default_capabilities: List[str] = field(default_factory=list)
    """Default capabilities for this role"""
    
    permissions: List[str] = field(default_factory=list)
    """Permissions granted to this role"""
    
    max_contracts: int = 10
    """Maximum number of active contracts"""
    
    max_tokens_per_day: int = 100000
    """Maximum tokens per day"""
    
    max_cost_per_day: float = 100.0
    """Maximum cost per day in USD"""
    
    requires_verification: bool = True
    """Whether this role requires verification"""
    
    can_create_contracts: bool = True
    """Whether this role can create contracts"""
    
    can_execute_contracts: bool = True
    """Whether this role can execute contracts"""
    
    can_escalate: bool = True
    """Whether this role can escalate issues"""
    
    can_verify: bool = False
    """Whether this role can verify contracts"""
    
    requires_human_oversight: bool = False
    """Whether this role requires human oversight"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata"""


# Predefined roles with full definitions
ROLES: Dict[AgentRole, RoleDefinition] = {
    AgentRole.MASTER: RoleDefinition(
        name="master",
        description="Master agent that coordinates other agents and manages the system",
        default_capabilities=[
            "coordinate",
            "assign",
            "monitor",
            "verify",
            "manage_contracts",
            "discover_agents",
            "negotiate"
        ],
        permissions=[
            "create_contract",
            "modify_contract",
            "terminate_contract",
            "assign_task",
            "manage_agents",
            "view_all_contracts",
            "escalate_any"
        ],
        max_contracts=50,
        max_tokens_per_day=1000000,
        max_cost_per_day=500.0,
        requires_verification=True,
        can_create_contracts=True,
        can_execute_contracts=True,
        can_escalate=True,
        can_verify=True,
        requires_human_oversight=False,
        metadata={
            "priority": 1,
            "system_role": True,
            "can_delegate": True
        }
    ),
    
    AgentRole.WORKER: RoleDefinition(
        name="worker",
        description="Standard worker agent that executes assigned tasks",
        default_capabilities=[
            "execute",
            "report",
            "negotiate",
            "process_data"
        ],
        permissions=[
            "execute_contract",
            "propose_contract",
            "report_status"
        ],
        max_contracts=20,
        max_tokens_per_day=200000,
        max_cost_per_day=100.0,
        requires_verification=True,
        can_create_contracts=True,
        can_execute_contracts=True,
        can_escalate=True,
        can_verify=False,
        requires_human_oversight=False,
        metadata={
            "priority": 3,
            "system_role": False,
            "can_delegate": False
        }
    ),
    
    AgentRole.EXECUTOR: RoleDefinition(
        name="executor",
        description="Agent specialized in executing compute-intensive tasks",
        default_capabilities=[
            "execute",
            "compute",
            "process",
            "batch_process",
            "parallel_execute"
        ],
        permissions=[
            "execute_contract",
            "use_compute_resources",
            "batch_execute"
        ],
        max_contracts=30,
        max_tokens_per_day=300000,
        max_cost_per_day=200.0,
        requires_verification=True,
        can_create_contracts=False,
        can_execute_contracts=True,
        can_escalate=True,
        can_verify=False,
        requires_human_oversight=False,
        metadata={
            "priority": 2,
            "system_role": False,
            "compute_heavy": True
        }
    ),
    
    AgentRole.GUARDIAN: RoleDefinition(
        name="guardian",
        description="Agent specialized in verification, security, and compliance",
        default_capabilities=[
            "verify",
            "validate",
            "audit",
            "monitor",
            "compliance_check",
            "security_scan",
            "risk_assessment"
        ],
        permissions=[
            "verify_contract",
            "escalate_issue",
            "audit_agent",
            "revoke_trust",
            "validate_execution",
            "security_check"
        ],
        max_contracts=10,
        max_tokens_per_day=100000,
        max_cost_per_day=50.0,
        requires_verification=True,
        can_create_contracts=False,
        can_execute_contracts=False,
        can_escalate=True,
        can_verify=True,
        requires_human_oversight=True,
        metadata={
            "priority": 1,
            "system_role": True,
            "security_focused": True
        }
    ),
    
    AgentRole.RESEARCHER: RoleDefinition(
        name="researcher",
        description="Agent specialized in research, exploration, and discovery",
        default_capabilities=[
            "research",
            "analyze",
            "summarize",
            "explore",
            "discover",
            "literature_review",
            "hypothesis_generation"
        ],
        permissions=[
            "analyze_data",
            "generate_report",
            "discover_capabilities",
            "explore_domains"
        ],
        max_contracts=15,
        max_tokens_per_day=200000,
        max_cost_per_day=150.0,
        requires_verification=False,
        can_create_contracts=True,
        can_execute_contracts=False,
        can_escalate=True,
        can_verify=False,
        requires_human_oversight=False,
        metadata={
            "priority": 3,
            "system_role": False,
            "research_focused": True
        }
    ),
    
    AgentRole.ANALYST: RoleDefinition(
        name="analyst",
        description="Agent specialized in data analysis and reporting",
        default_capabilities=[
            "analyze",
            "report",
            "visualize",
            "statistics",
            "pattern_recognition",
            "predict",
            "forecast"
        ],
        permissions=[
            "analyze_data",
            "generate_report",
            "create_visualization",
            "statistical_analysis"
        ],
        max_contracts=20,
        max_tokens_per_day=150000,
        max_cost_per_day=75.0,
        requires_verification=False,
        can_create_contracts=True,
        can_execute_contracts=True,
        can_escalate=True,
        can_verify=False,
        requires_human_oversight=False,
        metadata={
            "priority": 3,
            "system_role": False,
            "analysis_focused": True
        }
    ),
    
    AgentRole.TEACHER: RoleDefinition(
        name="teacher",
        description="Agent specialized in training, education, and knowledge transfer",
        default_capabilities=[
            "teach",
            "explain",
            "evaluate",
            "train",
            "mentor",
            "knowledge_transfer",
            "curriculum_design"
        ],
        permissions=[
            "create_lesson",
            "evaluate_student",
            "provide_feedback",
            "design_curriculum"
        ],
        max_contracts=10,
        max_tokens_per_day=100000,
        max_cost_per_day=50.0,
        requires_verification=False,
        can_create_contracts=True,
        can_execute_contracts=False,
        can_escalate=False,
        can_verify=False,
        requires_human_oversight=False,
        metadata={
            "priority": 3,
            "system_role": False,
            "educational": True
        }
    ),
    
    AgentRole.CUSTOM: RoleDefinition(
        name="custom",
        description="Custom agent role with user-defined capabilities",
        default_capabilities=[],
        permissions=[],
        max_contracts=10,
        max_tokens_per_day=100000,
        max_cost_per_day=50.0,
        requires_verification=True,
        can_create_contracts=True,
        can_execute_contracts=True,
        can_escalate=True,
        can_verify=False,
        requires_human_oversight=False,
        metadata={
            "priority": 4,
            "system_role": False,
            "custom": True
        }
    )
}


def get_role_definition(role: AgentRole) -> Optional[RoleDefinition]:
    """Get role definition for a role"""
    return ROLES.get(role)


def get_roles() -> List[str]:
    """Get all available role names"""
    return [role.value for role in AgentRole]


def get_roles_by_capability(capability: str) -> List[AgentRole]:
    """Get all roles that have a specific capability"""
    roles = []
    for role, definition in ROLES.items():
        if capability in definition.default_capabilities:
            roles.append(role)
    return roles


def validate_role_permission(role: AgentRole, permission: str) -> bool:
    """Check if a role has a specific permission"""
    definition = get_role_definition(role)
    if definition:
        return permission in definition.permissions
    return False


def validate_role_capability(role: AgentRole, capability: str) -> bool:
    """Check if a role has a specific capability"""
    definition = get_role_definition(role)
    if definition:
        return capability in definition.default_capabilities
    return False


def get_role_permissions(role: AgentRole) -> List[str]:
    """Get all permissions for a role"""
    definition = get_role_definition(role)
    if definition:
        return definition.permissions
    return []


def get_role_capabilities(role: AgentRole) -> List[str]:
    """Get all default capabilities for a role"""
    definition = get_role_definition(role)
    if definition:
        return definition.default_capabilities
    return []


def is_system_role(role: AgentRole) -> bool:
    """Check if a role is a system role"""
    definition = get_role_definition(role)
    if definition:
        return definition.metadata.get("system_role", False)
    return False


def get_role_priority(role: AgentRole) -> int:
    """Get the priority of a role (lower = higher priority)"""
    definition = get_role_definition(role)
    if definition:
        return definition.metadata.get("priority", 3)
    return 3


def get_role_by_name(name: str) -> Optional[AgentRole]:
    """Get role by name"""
    for role in AgentRole:
        if role.value == name:
            return role
    return None


def create_custom_role_definition(
    name: str,
    description: str,
    capabilities: List[str],
    permissions: List[str],
    **kwargs
) -> RoleDefinition:
    """Create a custom role definition"""
    return RoleDefinition(
        name=name,
        description=description,
        default_capabilities=capabilities,
        permissions=permissions,
        max_contracts=kwargs.get("max_contracts", 10),
        max_tokens_per_day=kwargs.get("max_tokens_per_day", 100000),
        max_cost_per_day=kwargs.get("max_cost_per_day", 50.0),
        requires_verification=kwargs.get("requires_verification", True),
        can_create_contracts=kwargs.get("can_create_contracts", True),
        can_execute_contracts=kwargs.get("can_execute_contracts", True),
        can_escalate=kwargs.get("can_escalate", True),
        can_verify=kwargs.get("can_verify", False),
        requires_human_oversight=kwargs.get("requires_human_oversight", False),
        metadata=kwargs.get("metadata", {})
    )