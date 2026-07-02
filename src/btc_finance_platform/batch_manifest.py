from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def build_batch_manifest(
    batch_result: dict[str, Any],
    summary: dict[str, Any],
    quality: dict[str, Any],
) -> dict[str, Any]:
    if batch_result.get("paper_only") is not True:
        raise AssertionError("manifest requires paper-only batch result")

    if summary.get("paper_only") is not True:
        raise AssertionError("manifest requires paper-only summary")

    if quality.get("paper_only") is not True:
        raise AssertionError("manifest requires paper-only quality gate")

    return {
        "ok": True,
        "type": "paper_batch_manifest",
        "manifest_id": str(uuid4()),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": summary["count"],
        "symbols": summary["symbols"],
        "risk_counts": summary["risk_counts"],
        "quality_status": quality["quality_status"],
        "quality_note": quality["quality_note"],
        "action": "NO_LIVE_ACTION",
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }
