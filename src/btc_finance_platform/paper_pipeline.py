from typing import Any

from btc_finance_platform.decision_draft import (
    assert_paper_decision_draft,
    create_paper_decision_draft,
)
from btc_finance_platform.market_snapshot import create_paper_market_snapshot
from btc_finance_platform.operator_review import (
    assert_operator_review_gate,
    require_operator_review,
)
from btc_finance_platform.safe_boundary import assert_safe_boundary


def run_paper_pipeline(symbol: str, price: float) -> dict[str, Any]:
    assert_safe_boundary()

    snapshot = create_paper_market_snapshot(symbol, price)
    draft = create_paper_decision_draft(snapshot)
    assert_paper_decision_draft(draft)

    review_gate = require_operator_review(draft)
    assert_operator_review_gate(review_gate)

    return {
        "ok": True,
        "type": "paper_pipeline_result",
        "symbol": snapshot["symbol"],
        "mode": "paper",
        "status": "WAITING_FOR_OPERATOR_REVIEW",
        "action": "NO_LIVE_ACTION",
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
        "bypass_policy_risk_safe_boundary": False,
        "snapshot": snapshot,
        "decision_draft": draft,
        "operator_review_gate": review_gate,
    }


def assert_paper_pipeline_result(result: dict[str, Any]) -> bool:
    required = {
        "ok": True,
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
        "bypass_policy_risk_safe_boundary": False,
    }

    for key, expected in required.items():
        if result.get(key) is not expected:
            raise AssertionError(f"invalid paper pipeline result flag: {key}")

    if result.get("mode") != "paper":
        raise AssertionError("pipeline must remain paper mode")

    if result.get("action") != "NO_LIVE_ACTION":
        raise AssertionError("pipeline must not create live action")

    if result.get("status") != "WAITING_FOR_OPERATOR_REVIEW":
        raise AssertionError("pipeline must wait for operator review")

    return True
