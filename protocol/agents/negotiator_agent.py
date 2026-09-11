"""
Negotiator Agent v3.1 — real PROPOSE → NEGOTIATE → COMMIT flow.
"""

import uuid
import time
from typing import Optional

from protocol.agent import Agent


class NegotiatorAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_max_cost = 10.0
        self.policy_max_tokens = 100_000

    def evaluate(self, terms: dict) -> tuple[str, str]:
        """Deterministic policy evaluation."""
        if terms.get("cost_usd", 0) > self.policy_max_cost:
            return "reject", f"cost exceeds {self.policy_max_cost}"
        if terms.get("max_tokens", 0) > self.policy_max_tokens:
            return "reject", f"max_tokens exceeds {self.policy_max_tokens}"
        return "accept", "policy passed"

    def handle_proposal(self, message: dict) -> dict:
        """Handle incoming PROPOSE and respond with NEGOTIATE/REJECT."""
        env = message["envelope"]
        payload = env["payload"]
        proposal_id = payload.get("proposal_id")
        terms = payload.get("terms", {})

        decision, reason = self.evaluate(terms)

        if decision == "reject":
            return self.send(
                "REJECT",
                {"proposal_id": proposal_id, "reason": reason},
                message["sender_did"],
            )

        # Accept → negotiate terms → commit
        counter_terms = {**terms, "accepted": True}
        return self.send(
            "NEGOTIATE",
            {"proposal_id": proposal_id, "terms": counter_terms},
            message["sender_did"],
        )

    def handle_negotiate(self, message: dict) -> dict:
        """Handle incoming NEGOTIATE and respond with COMMIT."""
        payload = message["envelope"]["payload"]
        proposal_id = payload.get("proposal_id")
        terms = payload.get("terms", {})
        terms_hash = self._terms_hash(terms)

        return self.send(
            "COMMIT",
            {"proposal_id": proposal_id, "terms_hash": terms_hash, "terms": terms},
            message["sender_did"],
        )

    @staticmethod
    def _terms_hash(terms: dict) -> str:
        from core.crypto.hashing import blake2b_256
        import json
        canonical = json.dumps(terms, sort_keys=True, separators=(",", ":")).encode()
        return blake2b_256(canonical).hex()

    def verify_commit(self, message: dict, expected_proposal: dict) -> bool:
        """Verify COMMIT matches original proposal."""
        payload = message["envelope"]["payload"]
        if payload.get("proposal_id") != expected_proposal.get("proposal_id"):
            return False
        expected_hash = self._terms_hash(expected_proposal.get("terms", {}))
        return payload.get("terms_hash") == expected_hash