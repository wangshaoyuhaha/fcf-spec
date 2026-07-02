from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def create_paper_run_record(
    analysis: dict[str, Any],
    risk: dict[str, Any],
    strategy: dict[str, Any],
    report: str,
) -> dict[str, Any]:
    if analysis.get("paper_only") is not True:
        raise AssertionError("paper run record requires paper-only analysis")

    if risk.get("paper_only") is not True:
        raise AssertionError("paper run record requires paper-only risk")

    if strategy.get("paper_only") is not True:
        raise AssertionError("paper run record requires paper-only strategy")

    return {
        "ok": True,
        "type": "paper_run_record",
        "run_id": str(uuid4()),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": analysis["symbol"],
        "scenario": analysis["scenario"],
        "risk_level": risk["risk_level"],
        "stance": strategy["stance"],
        "report": report,
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }


def assert_paper_run_record(record: dict[str, Any]) -> bool:
    required = {
        "ok": True,
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }

    for key, expected in required.items():
        if record.get(key) is not expected:
            raise AssertionError(f"invalid paper run record flag: {key}")

    if not record.get("run_id"):
        raise AssertionError("paper run record requires run_id")

    return True
