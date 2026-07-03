import json
from pathlib import Path
from typing import Any


def classify_data_quality_issue(
    missing_ratio: float,
    latency_seconds: float,
    outlier_ratio: float,
    max_missing_ratio: float = 0.05,
    max_latency_seconds: float = 300.0,
    max_outlier_ratio: float = 0.02,
) -> str:
    if missing_ratio < 0 or missing_ratio > 1:
        raise ValueError("missing_ratio must be between 0 and 1")

    if latency_seconds < 0:
        raise ValueError("latency_seconds must be non-negative")

    if outlier_ratio < 0 or outlier_ratio > 1:
        raise ValueError("outlier_ratio must be between 0 and 1")

    if missing_ratio > max_missing_ratio:
        return "missing_data_warning"

    if latency_seconds > max_latency_seconds:
        return "stale_data_warning"

    if outlier_ratio > max_outlier_ratio:
        return "outlier_warning"

    return "clean"


def evaluate_data_source_quality(source: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(source, dict):
        raise ValueError("source must be a dict")

    source_id = source.get("source_id")
    if not source_id:
        raise ValueError("source_id is required")

    source_type = str(source.get("source_type", "unknown"))
    missing_ratio = float(source.get("missing_ratio", 0.0))
    latency_seconds = float(source.get("latency_seconds", 0.0))
    outlier_ratio = float(source.get("outlier_ratio", 0.0))

    issue = classify_data_quality_issue(
        missing_ratio=missing_ratio,
        latency_seconds=latency_seconds,
        outlier_ratio=outlier_ratio,
    )

    if issue == "clean":
        proposed_usage = "allow_for_paper_review"
    else:
        proposed_usage = "quarantine_for_operator_review"

    return {
        "ok": True,
        "type": "p14_data_source_quality_result",
        "source_id": str(source_id),
        "source_type": source_type,
        "missing_ratio": missing_ratio,
        "latency_seconds": latency_seconds,
        "outlier_ratio": outlier_ratio,
        "quality_status": issue,
        "proposed_usage": proposed_usage,
        "auto_quarantine_allowed": False,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "real_world_actions_allowed": False,
    }


def build_data_quality_sentry_report(
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(sources, list):
        raise ValueError("sources must be a list")

    rows = [evaluate_data_source_quality(source) for source in sources]
    warning_count = sum(1 for row in rows if row["quality_status"] != "clean")

    if warning_count:
        report_status = "READY_FOR_OPERATOR_REVIEW_WITH_WARNINGS"
    else:
        report_status = "READY_FOR_OPERATOR_REVIEW"

    return {
        "ok": True,
        "type": "p14_data_quality_sentry_report",
        "current_stage": "P14-D34-D36",
        "report_status": report_status,
        "purpose": "detect missing, stale, or outlier paper data before learning and governor reports",
        "row_count": len(rows),
        "warning_count": warning_count,
        "rows": rows,
        "quality_policy": {
            "auto_quarantine_allowed": False,
            "auto_disable_source_allowed": False,
            "operator_review_required": True,
        },
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "operator_review_required": True,
        "trading_buttons_enabled": False,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_api_key_required": False,
        "wallet_private_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
    }


def write_data_quality_sentry_report(
    sources: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_data_quality_sentry_report(sources)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_data_quality_sentry_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_quarantine_allowed": False,
        "real_world_actions_allowed": False,
    }
