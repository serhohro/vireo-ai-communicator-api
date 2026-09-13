"""
Vireo Agent v3.1 — uses VireoStateMachine + real signing.
"""

import time
import uuid
from typing import Any, Optional

from core.crypto.ed25519 import sign_vireo_message
from core.crypto.canonical import canonical_wire_bytes
from core.crypto.hashing import did_hash
from core.protocol.state import ProtocolState, VireoStateMachine
from core.protocol.nonce_manager import get_nonce_manager
from core.protocol.verification import verify_vireo_signature
from core.identity.did import make_did, register_did


class Agent:
    """
    Base Vireo agent.

    Every agent:
    - has a DID
    - holds an Ed25519 keypair
    - enforces the protocol state machine
    - signs every outgoing message
    - verifies every incoming message
    """

    def __init__(
        self,
        agent_id: str,
        private_key_hex: str,
        public_key_hex: str,
        name: Optional[str] = None,
    ):
        self.id = agent_id
        self.name = name or agent_id
        self.private_key_hex = private_key_hex
        self.public_key_hex = public_key_hex
        self.did = make_did(self.name)
        self.sm = VireoStateMachine()
        self.capabilities: list[str] = []
        self._pending_proposals: dict[str, dict] = {}

        register_did(self.did, public_key_hex, name=self.name)

    # ───────────── Capabilities ─────────────

    def add_capability(self, cap: str) -> None:
        if cap not in self.capabilities:
            self.capabilities.append(cap)

    # ───────────── Outgoing ─────────────

    def build_envelope(
        self,
        intent: str,
        payload: dict[str, Any],
        recipient_did: str,
    ) -> dict:
        return {
            "intent": intent,
            "timestamp_ms": int(time.time() * 1000),
            "nonce": uuid.uuid4().bytes,
            "sender_did_hash": did_hash(self.did),
            "recipient_did_hash": did_hash(recipient_did),
            "payload": payload,
        }

    def sign_envelope(self, envelope: dict) -> str:
        canonical = canonical_wire_bytes(envelope)
        return sign_vireo_message(self.private_key_hex, canonical)

    def send(self, intent: str, payload: dict, recipient_did: str) -> dict:
        envelope = self.build_envelope(intent, payload, recipient_did)
        signature = self.sign_envelope(envelope)
        return {
            "envelope": {
                **envelope,
                "nonce": envelope["nonce"].hex(),
                "sender_did_hash": envelope["sender_did_hash"].hex(),
                "recipient_did_hash": envelope["recipient_did_hash"].hex(),
            },
            "signature": signature,
            "sender_did": self.did,
        }

    # ───────────── Incoming ─────────────

    def receive(self, message: dict) -> dict:
        # Verify signature
        result = verify_vireo_signature(message)
        if not result["valid"]:
            return {"accepted": False, "error": result["error"]}

        env = message["envelope"]
        nonce = bytes.fromhex(env["nonce"]) if isinstance(env["nonce"], str) else env["nonce"]
        sender_hash = bytes.fromhex(env["sender_did_hash"]) if isinstance(env["sender_did_hash"], str) else env["sender_did_hash"]

        # Nonce replay check
        nm = get_nonce_manager()
        ok, err = nm.check_and_store(nonce, sender_hash, env["timestamp_ms"])
        if not ok:
            return {"accepted": False, "error": err}

        # Apply state transition
        try:
            target_state = ProtocolState(env["intent"])
            self.sm.transition(target_state)
        except Exception as e:
            return {"accepted": False, "error": f"state transition failed: {e}"}

        return {
            "accepted": True,
            "intent": env["intent"],
            "state": self.sm.state.value,
            "payload": env["payload"],
        }

    # ───────────── Negotiation ─────────────

    def propose(self, recipient_did: str, terms: dict, task: str) -> dict:
        proposal_id = str(uuid.uuid4())
        self._pending_proposals[proposal_id] = {
            "terms": terms,
            "task": task,
            "recipient_did": recipient_did,
            "created_at": time.time(),
        }
        payload = {"proposal_id": proposal_id, "terms": terms, "task": task}
        return self.send("PROPOSE", payload, recipient_did)

    def evaluate_proposal(self, terms: dict) -> tuple[str, str]:
        """
        Deterministic policy check.
        Returns (decision, reason) where decision ∈ {"accept", "reject"}.
        """
        max_cost = 10.0
        if terms.get("cost_usd", 0) > max_cost:
            return "reject", f"cost exceeds max {max_cost}"
        if terms.get("max_tokens", 0) > 100_000:
            return "reject", "max_tokens exceeds limit"
        return "accept", "policy passed"

    def cleanup_pending(self, max_age_sec: int = 3600) -> int:
        now = time.time()
        expired = [
            pid for pid, p in self._pending_proposals.items()
            if now - p["created_at"] > max_age_sec
        ]
        for pid in expired:
            del self._pending_proposals[pid]
        return len(expired)

    def state_info(self) -> dict:
        return self.sm.to_dict()