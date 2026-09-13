# ============================================================
# LAYER 3 — AI PROTOCOL: MESSAGE WITH DUAL-REPRESENTATION
# ============================================================

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Dict

from .intent import Intent

PROTOCOL_NAME = "VIREO-A2A"
PROTOCOL_VERSION = "1.0"


@dataclass
class AgentRef:
    id: str
    model: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Message:
    sender: AgentRef
    recipient: AgentRef
    intent: Intent
    payload: dict = field(default_factory=dict)
    constraints: dict = field(default_factory=dict)
    
    conversation_id: str = field(default_factory=lambda: f"conv-{uuid.uuid4().hex[:8]}")
    proposal_id: Optional[str] = None
    context_version: Optional[int] = None
    
    message_id: str = field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None
    protocol: str = PROTOCOL_NAME
    version: str = PROTOCOL_VERSION
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d["sender"] = self.sender.to_dict()
        d["recipient"] = self.recipient.to_dict()
        d["intent"] = self.intent.value
        return d
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, d: dict) -> "Message":
        d = dict(d)
        d["sender"] = AgentRef(**d["sender"])
        d["recipient"] = AgentRef(**d["recipient"])
        d["intent"] = Intent(d["intent"])
        known = {f for f in cls.__dataclass_fields__.keys() if not f.startswith("_")}
        d = {k: v for k, v in d.items() if k in known}
        return cls(**d)
    
    @classmethod
    def from_json(cls, s: str) -> "Message":
        return cls.from_dict(json.loads(s))
    
    def unsigned_payload_for_signature(self) -> str:
        d = self.to_dict()
        d.pop("signature", None)
        return json.dumps(d, sort_keys=True, ensure_ascii=False)


def make_message(
    sender_id: str,
    recipient_id: str,
    intent: Intent,
    payload: dict,
    *,
    sender_model: Optional[str] = None,
    constraints: Optional[dict] = None,
    conversation_id: Optional[str] = None,
    proposal_id: Optional[str] = None,
    context_version: Optional[int] = None,
) -> Message:
    kwargs = dict(
        sender=AgentRef(id=sender_id, model=sender_model),
        recipient=AgentRef(id=recipient_id),
        intent=intent,
        payload=payload or {},
        constraints=constraints or {},
        proposal_id=proposal_id,
        context_version=context_version,
    )
    if conversation_id is not None:
        kwargs["conversation_id"] = conversation_id
    return Message(**kwargs)