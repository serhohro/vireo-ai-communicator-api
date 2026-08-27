# [file name]: protocol/agents/executor_agent.py
# ============================================================
# EXECUTOR AGENT - Виконавець
# ============================================================

from .base_agent import create_role_agent


def create_executor_agent(agent_id: str = "agent-executor", **kwargs):
    """Створює агента-виконавця."""
    return create_role_agent("executor", agent_id, **kwargs)