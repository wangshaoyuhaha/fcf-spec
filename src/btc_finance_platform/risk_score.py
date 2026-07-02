from typing import Any


def score_paper_risk(analysis: dict[str, Any]) -> dict[str, Any]:
    if analysis.get("paper_only") is not True:
        raise AssertionError("risk score requires paper-only analysis")

    if analysis.get("real_order") is not False:
        raise AssertionError("risk score must not allow real order")

    change_abs = abs(float(analysis["change_pct"]))

    if change_abs >= 5.0:
        risk_level = "HIGH"
    elif change_abs >= 2.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "ok": True,
        "type": "paper_risk_score",
        "symbol": analysis["symbol"],
        "risk_level": risk_level,
        "change_abs_pct": round(change_abs, 6),
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }
