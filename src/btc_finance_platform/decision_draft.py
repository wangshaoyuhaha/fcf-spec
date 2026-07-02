from typing import Any


def create_paper_decision_draft(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a dict")

    if snapshot.get("paper_only") is not True:
        raise AssertionError("decision draft requires paper-only snapshot")

    if snapshot.get("real_exchange_api") is not False:
        raise AssertionError("decision draft must not use real exchange API")

    symbol = snapshot.get("symbol")
    price = snapshot.get("price")

    if not symbol:
        raise ValueError("snapshot symbol is required")

    if price is None or float(price) <= 0:
        raise ValueError("snapshot price must be positive")

    return {
        "ok": True,
        "type": "paper_decision_draft",
        "symbol": str(symbol).upper(),
        "reference_price": float(price),
        "status": "REVIEW_REQUIRED",
        "action": "NO_LIVE_ACTION",
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
        "bypass_policy_risk_safe_boundary": False,
        "rationale": [
            "paper-only decision draft created",
            "operator review is required",
            "no real order is allowed",
            "no real execution is claimed",
        ],
    }


def assert_paper_decision_draft(draft: dict[str, Any]) -> bool:
    required = {
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
        "bypass_policy_risk_safe_boundary": False,
    }

    for key, expected in required.items():
        if draft.get(key) is not expected:
            raise AssertionError(f"invalid decision draft flag: {key}")

    if draft.get("action") != "NO_LIVE_ACTION":
        raise AssertionError("paper decision draft must not create live action")

    if draft.get("status") != "REVIEW_REQUIRED":
        raise AssertionError("paper decision draft must require review")

    return True
