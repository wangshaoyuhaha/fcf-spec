from typing import Dict, Any


class PolicyEngine:
    """
    Phase 1 mock policy engine.

    The only hard rule implemented now:
    - If panic_probability >= 0.80, block live execution.
    """

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        panic_probability = context.get("panic_probability", 0.0)
        if panic_probability >= 0.80:
            return {
                "policy_pass": False,
                "execution_mode": "BLOCKED",
                "reason": "Emergency policy triggered: panic probability too high.",
            }

        return {
            "policy_pass": True,
            "execution_mode": "SHADOW",
            "reason": "Phase 1 default: only shadow execution is allowed.",
        }
