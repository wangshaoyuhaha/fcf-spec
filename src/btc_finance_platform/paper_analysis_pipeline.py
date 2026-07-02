import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.local_data_handoff import build_local_analysis_handoff_package
from btc_finance_platform.paper_analysis_logic import analyze_paper_batch


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_api_key_required": False,
    "wallet_private_key_required": False,
    "real_order": False,
    "real_execution": False,
    "real_balance": False,
    "real_position": False,
    "real_money_impact": False,
    "operator_review_required": True,
}


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def extract_analysis_items_from_handoff(
    handoff_package: dict[str, Any],
) -> list[dict[str, Any]]:
    if not isinstance(handoff_package, dict):
        raise ValueError("handoff_package must be a dict")

    if handoff_package.get("ok") is not True:
        raise ValueError("handoff_package must be ok")

    if handoff_package.get("gate") != "pass":
        raise ValueError("handoff_package gate must pass")

    analysis_inputs = handoff_package.get("analysis_inputs")
    if not isinstance(analysis_inputs, dict):
        raise ValueError("handoff_package missing analysis_inputs")

    items = analysis_inputs.get("items")
    if not isinstance(items, list):
        raise ValueError("analysis_inputs.items must be a list")

    if not items:
        raise ValueError("analysis_inputs.items must not be empty")

    return items


def run_paper_analysis_from_handoff_package(
    handoff_package: dict[str, Any],
) -> dict[str, Any]:
    items = extract_analysis_items_from_handoff(handoff_package)
    batch_analysis = analyze_paper_batch(items)

    return {
        "ok": batch_analysis["ok"] is True,
        "type": "paper_analysis_from_handoff_package",
        "handoff_type": handoff_package["type"],
        "handoff_gate": handoff_package["gate"],
        "count": batch_analysis["count"],
        "symbols": batch_analysis["symbols"],
        "analysis": batch_analysis,
        "source_manifest": handoff_package["analysis_inputs"]["source_manifest"],
        "decision": "paper_analysis_only_no_real_trade",
        **paper_flags(),
    }


def run_paper_analysis_from_local_files(file_paths: list[Any]) -> dict[str, Any]:
    handoff_package = build_local_analysis_handoff_package(file_paths)
    pipeline_result = run_paper_analysis_from_handoff_package(handoff_package)

    return {
        "ok": pipeline_result["ok"] is True,
        "type": "paper_analysis_from_local_files",
        "handoff_package": handoff_package,
        "pipeline_result": pipeline_result,
        "count": pipeline_result["count"],
        "symbols": pipeline_result["symbols"],
        "decision": "local_file_to_paper_analysis_only",
        **paper_flags(),
    }


def build_paper_analysis_pipeline_report(file_paths: list[Any]) -> dict[str, Any]:
    pipeline = run_paper_analysis_from_local_files(file_paths)
    analysis = pipeline["pipeline_result"]["analysis"]
    items = analysis["items"]

    risk_levels: dict[str, int] = {}
    signals: dict[str, int] = {}

    for item in items:
        risk_level = item["risk"]["level"]
        signal = item["signal"]
        risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        signals[signal] = signals.get(signal, 0) + 1

    return {
        "ok": pipeline["ok"] is True,
        "type": "paper_analysis_pipeline_report",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": pipeline["count"],
        "symbols": pipeline["symbols"],
        "risk_levels": risk_levels,
        "signals": signals,
        "high_risk_count": analysis["high_risk_count"],
        "pipeline": pipeline,
        "decision": "report_only_no_real_trade",
        **paper_flags(),
    }


def write_paper_analysis_pipeline_report(
    file_paths: list[Any],
    output_path: Any,
) -> dict[str, Any]:
    report = build_paper_analysis_pipeline_report(file_paths)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "paper_analysis_pipeline_report_written",
        "output_file": str(path),
        "report": report,
        **paper_flags(),
    }
