# [file name]: protocol/agents/analyst_agent.py
# ============================================================
# ANALYST AGENT - Аналіз даних
# ============================================================

from .base_agent import create_role_agent


def create_analyst_agent(agent_id: str = "agent-analyst", **kwargs):
    """Створює агента для аналізу даних."""
    return create_role_agent("analyst", agent_id, **kwargs)