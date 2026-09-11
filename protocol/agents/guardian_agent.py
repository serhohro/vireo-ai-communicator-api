"""Guardian Agent v3.1 — monitors policy compliance."""

from protocol.agent import Agent


class GuardianAgent(Agent):
    def check_compliance(self, contract: dict, message: dict) -> dict:
        violations = []
        terms = contract.get("terms", {})

        payload = message.get("envelope", {}).get("payload", {})
        if "max_cost_usd" in terms:
            if payload.get("cost_usd", 0) > terms["max_cost_usd"]:
                violations.append("cost_usd exceeds contract limit")

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
        }