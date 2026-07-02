from typing import Any


def require_operator_review(draft: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(draft, dict):
        raise ValueError("draft must be a dict")

    if draft.get("paper_only") is not True:
        raise AssertionError("operator review requires paper-only draft")

    if draft.get("operator_review_required") is not True:
        raise AssertionError("operator review must be required")

    if draft.get("bypass_operator_review") is not False:
        raise AssertionError("operator review bypass is not allowed")

    if draft.get("real_order") is not False:
        raise AssertionError("real order is not allowed")

    if draft.get("real_execution") is not False:
        raise AssertionError("real execution is not allowed")

    if draft.get("real_money_impact") is not False:
        raise AssertionError("real money impact is not allowed")

    return {
        "ok": True,
        "type": "operator_review_gate",
        "status": "WAITING_FOR_OPERATOR_REVIEW",
        "action": "NO_LIVE_ACTION",
        "paper_only": True,
        "operator_review_required": True,
        "operator_approved": False,
        "bypass_operator_review": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "source_draft": draft,
    }


def assert_operator_review_gate(gate: dict[str, Any]) -> bool:
    required = {
        "paper_only": True,
        "operator_review_required": True,
        "operator_approved": False,
        "bypass_operator_review": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }

    for key, expected in required.items():
        if gate.get(key) is not expected:
            raise AssertionError(f"invalid operator review gate flag: {key}")

    if gate.get("action") != "NO_LIVE_ACTION":
        raise AssertionError("operator review gate must not create live action")

    if gate.get("status") != "WAITING_FOR_OPERATOR_REVIEW":
        raise AssertionError("operator review gate must wait for review")

    return True
