# Vireo v3.0.0 — Agent SDK

from typing import Optional, Dict, Any, List

from protocol.agent import Agent


class AgentSDK:
    """Agent SDK for Vireo."""
    
    def __init__(
        self,
        agent_id: str,
        private_key: bytes,
        public_key: bytes,
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ):
        self.agent = Agent(agent_id, private_key, public_key, name, capabilities)
    
    def propose(self, recipient: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        msg = self.agent.propose(recipient, contract)
        return {
            "type": "propose",
            "message": msg.serialize().hex(),
        }
    
    def commit(self, recipient: str, proposal_id: str) -> Dict[str, Any]:
        msg = self.agent.commit(recipient, proposal_id)
        return {
            "type": "commit",
            "message": msg.serialize().hex(),
        }
    
    def execute(self, recipient: str, proposal_id: str) -> Dict[str, Any]:
        msg = self.agent.execute(recipient, proposal_id)
        return {
            "type": "execute",
            "message": msg.serialize().hex(),
        }
    
    def verify(self, recipient: str, proposal_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        msg = self.agent.verify(recipient, proposal_id, result)
        return {
            "type": "verify",
            "message": msg.serialize().hex(),
        }
    
    def done(self, recipient: str, proposal_id: str) -> Dict[str, Any]:
        msg = self.agent.done(recipient, proposal_id)
        return {
            "type": "done",
            "message": msg.serialize().hex(),
        }
    
    def receive(self, message_data: bytes) -> Optional[Dict[str, Any]]:
        from core.protocol.message import Message
        msg = Message.deserialize(message_data)
        response = self.agent.receive(msg)
        if response:
            return {
                "type": "response",
                "message": response.serialize().hex(),
            }
        return None
    
    def get_state(self) -> str:
        return self.agent.get_state()