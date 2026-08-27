# [file name]: protocol/agents/teacher_agent.py
# ============================================================
# TEACHER AGENT - Вчитель
# ============================================================

from .base_agent import create_role_agent


def create_teacher_agent(agent_id: str = "agent-teacher", **kwargs):
    """Створює агента-вчителя."""
    return create_role_agent("teacher", agent_id, **kwargs)