# [file name]: protocol/agents/vision_agent.py
from .base_agent import create_role_agent

def create_vision_agent(agent_id: str = "agent-vision", **kwargs):
    return create_role_agent("vision", agent_id, **kwargs)