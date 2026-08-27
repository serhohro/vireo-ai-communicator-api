# [file name]: protocol/agents/researcher_agent.py
# ============================================================
# RESEARCHER AGENT - Дослідник
# ============================================================

from .base_agent import create_role_agent


def create_researcher_agent(agent_id: str = "agent-researcher", **kwargs):
    """Створює агента-дослідника."""
    return create_role_agent("researcher", agent_id, **kwargs)