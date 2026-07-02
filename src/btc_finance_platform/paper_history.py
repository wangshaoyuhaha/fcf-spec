import json
from pathlib import Path
from typing import Any


def save_paper_run_record(record: dict[str, Any], output_dir: str = "data/paper/runs") -> dict[str, Any]:
    if record.get("paper_only") is not True:
        raise AssertionError("paper history requires paper-only record")

    if record.get("real_order") is not False:
        raise AssertionError("paper history must not save real order")

    run_id = record.get("run_id")
    if not run_id:
        raise ValueError("run_id is required")

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / f"{run_id}.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "paper_history_saved",
        "path": str(path),
        "run_id": run_id,
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }


def summarize_paper_history(output_dir: str = "data/paper/runs") -> dict[str, Any]:
    directory = Path(output_dir)
    files = sorted(directory.glob("*.json")) if directory.exists() else []

    return {
        "ok": True,
        "type": "paper_history_summary",
        "run_count": len(files),
        "files": [str(path) for path in files],
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }
