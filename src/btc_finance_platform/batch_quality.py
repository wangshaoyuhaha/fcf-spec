from typing import Any


def evaluate_batch_quality(batch_result: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    if batch_result.get("paper_only") is not True:
        raise AssertionError("batch quality requires paper-only batch result")

    if summary.get("paper_only") is not True:
        raise AssertionError("batch quality requires paper-only summary")

    if batch_result.get("count") != summary.get("count"):
        raise AssertionError("batch count mismatch")

    risk_counts = dict(summary.get("risk_counts", {}))
    high_risk_count = int(risk_counts.get("HIGH", 0))

    quality_status = "REVIEW_REQUIRED"
    if high_risk_count > 0:
        quality_note = "HIGH_RISK_PRESENT"
    else:
        quality_note = "NO_HIGH_RISK_PRESENT"

    return {
        "ok": True,
        "type": "paper_batch_quality_gate",
        "count": summary["count"],
        "symbols": summary["symbols"],
        "risk_counts": risk_counts,
        "high_risk_count": high_risk_count,
        "quality_status": quality_status,
        "quality_note": quality_note,
        "action": "NO_LIVE_ACTION",
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }


def assert_batch_quality_gate(quality: dict[str, Any]) -> bool:
    required = {
        "ok": True,
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }

    for key, expected in required.items():
        if quality.get(key) is not expected:
            raise AssertionError(f"invalid batch quality flag: {key}")

    if quality.get("action") != "NO_LIVE_ACTION":
        raise AssertionError("batch quality gate must not create live action")

    if quality.get("quality_status") != "REVIEW_REQUIRED":
        raise AssertionError("batch quality gate must require review")

    return True
