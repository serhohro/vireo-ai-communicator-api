# [file name]: protocol/agents/__init__.py
# ============================================================
# AGENTS PACKAGE - Агенти з ролями
# ============================================================

from .base_agent import RoleAgent, AgentRole, ROLES, create_role_agent
from .master_agent import MasterAgent
from .vision_agent import create_vision_agent
from .nlp_agent import create_nlp_agent
from .analyst_agent import create_analyst_agent
from .researcher_agent import create_researcher_agent
from .executor_agent import create_executor_agent
from .guardian_agent import create_guardian_agent
from .teacher_agent import create_teacher_agent

# Користувацькі ролі
from .custom_roles import (
    QUANTUM_ROLE,
    BIOTECH_ROLE,
    DEVOPS_ROLE,
    FRONTEND_ROLE,
    DESIGNER_ROLE,
    WRITER_ROLE,
    PRODUCT_MANAGER_ROLE,
    MARKETING_ROLE,
    create_quantum_agent,
    create_biotech_agent,
    create_devops_agent,
    create_frontend_agent,
    create_designer_agent,
    create_writer_agent,
    create_product_manager_agent,
    create_marketing_agent,
)

__all__ = [
    # Базові
    "RoleAgent",
    "AgentRole",
    "ROLES",
    "create_role_agent",
    "MasterAgent",
    # Стандартні ролі
    "create_vision_agent",
    "create_nlp_agent",
    "create_analyst_agent",
    "create_researcher_agent",
    "create_executor_agent",
    "create_guardian_agent",
    "create_teacher_agent",
    # Користувацькі ролі
    "QUANTUM_ROLE",
    "BIOTECH_ROLE",
    "DEVOPS_ROLE",
    "FRONTEND_ROLE",
    "DESIGNER_ROLE",
    "WRITER_ROLE",
    "PRODUCT_MANAGER_ROLE",
    "MARKETING_ROLE",
    "create_quantum_agent",
    "create_biotech_agent",
    "create_devops_agent",
    "create_frontend_agent",
    "create_designer_agent",
    "create_writer_agent",
    "create_product_manager_agent",
    "create_marketing_agent",
]