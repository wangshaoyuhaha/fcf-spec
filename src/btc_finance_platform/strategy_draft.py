from typing import Any


def create_strategy_draft(analysis: dict[str, Any], risk: dict[str, Any]) -> dict[str, Any]:
    if analysis.get("paper_only") is not True:
        raise AssertionError("strategy draft requires paper-only analysis")

    if risk.get("paper_only") is not True:
        raise AssertionError("strategy draft requires paper-only risk")

    scenario = analysis["scenario"]
    risk_level = risk["risk_level"]

    if risk_level == "HIGH":
        stance = "REVIEW_ONLY"
    elif scenario == "PAPER_UPSIDE_MOVE":
        stance = "PAPER_OBSERVE_UPSIDE"
    elif scenario == "PAPER_DOWNSIDE_MOVE":
        stance = "PAPER_OBSERVE_DOWNSIDE"
    else:
        stance = "PAPER_OBSERVE_RANGE"

    return {
        "ok": True,
        "type": "paper_strategy_draft",
        "symbol": analysis["symbol"],
        "stance": stance,
        "scenario": scenario,
        "risk_level": risk_level,
        "action": "NO_LIVE_ACTION",
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }
