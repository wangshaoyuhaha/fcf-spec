import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def create_batch_run_record(batch_result: dict[str, Any], summary: dict[str, Any], report: str) -> dict[str, Any]:
    if batch_result.get("paper_only") is not True:
        raise AssertionError("batch record requires paper-only batch result")

    if summary.get("paper_only") is not True:
        raise AssertionError("batch record requires paper-only summary")

    if "NO_LIVE_ACTION" not in report:
        raise AssertionError("batch report must include NO_LIVE_ACTION")

    return {
        "ok": True,
        "type": "paper_batch_run_record",
        "batch_run_id": str(uuid4()),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": summary["count"],
        "symbols": summary["symbols"],
        "risk_counts": summary["risk_counts"],
        "report": report,
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }


def save_batch_run_record(record: dict[str, Any], output_dir: str = "data/paper/batch_runs") -> dict[str, Any]:
    if record.get("paper_only") is not True:
        raise AssertionError("batch history requires paper-only record")

    if record.get("real_order") is not False:
        raise AssertionError("batch history must not save real order")

    batch_run_id = record.get("batch_run_id")
    if not batch_run_id:
        raise ValueError("batch_run_id is required")

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / f"{batch_run_id}.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "paper_batch_history_saved",
        "path": str(path),
        "batch_run_id": batch_run_id,
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }


def summarize_batch_history(output_dir: str = "data/paper/batch_runs") -> dict[str, Any]:
    directory = Path(output_dir)
    files = sorted(directory.glob("*.json")) if directory.exists() else []

    return {
        "ok": True,
        "type": "paper_batch_history_summary",
        "batch_run_count": len(files),
        "files": [str(path) for path in files],
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }
