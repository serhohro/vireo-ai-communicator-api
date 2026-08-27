# [file name]: protocol/agents/nlp_agent.py
from .base_agent import create_role_agent

def create_nlp_agent(agent_id: str = "agent-nlp", **kwargs):
    return create_role_agent("nlp", agent_id, **kwargs)