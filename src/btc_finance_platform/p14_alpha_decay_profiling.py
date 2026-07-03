import json
from pathlib import Path
from typing import Any


def classify_alpha_window(
    best_window_hours: float,
) -> str:
    if not isinstance(best_window_hours, (int, float)):
        raise ValueError("best_window_hours must be numeric")

    if best_window_hours < 0:
        raise ValueError("best_window_hours must be non-negative")

    if best_window_hours <= 4:
        return "ultra_short_term"

    if best_window_hours <= 24:
        return "short_term"

    if best_window_hours <= 168:
        return "medium_term"

    return "long_term"


def estimate_alpha_decay_profile(
    source_id: str,
    source_type: str,
    window_scores: dict[str, float],
) -> dict[str, Any]:
    if not source_id:
        raise ValueError("source_id is required")

    if not source_type:
        raise ValueError("source_type is required")

    if not isinstance(window_scores, dict) or not window_scores:
        raise ValueError("window_scores must be a non-empty dict")

    parsed_windows = []

    for window, score in window_scores.items():
        if not isinstance(score, (int, float)):
            raise ValueError("window score must be numeric")

        try:
            hours = float(str(window).replace("h", ""))
        except ValueError as exc:
            raise ValueError("window key must be numeric hours or like '4h'") from exc

        if hours < 0:
            raise ValueError("window hours must be non-negative")

        parsed_windows.append(
            {
                "window_hours": hours,
                "score": float(score),
            }
        )

    parsed_windows.sort(key=lambda item: item["window_hours"])

    best = max(parsed_windows, key=lambda item: item["score"])
    best_window_hours = best["window_hours"]
    best_score = best["score"]

    if best_score <= 0:
        decay_status = "no_positive_alpha_observed"
        suggested_usage = "review_or_deprioritize"
    else:
        decay_status = "positive_alpha_observed"
        suggested_usage = f"use_for_{classify_alpha_window(best_window_hours)}_paper_context"

    return {
        "ok": True,
        "type": "p14_alpha_decay_profile",
        "source_id": source_id,
        "source_type": source_type,
        "best_window_hours": best_window_hours,
        "best_score": best_score,
        "alpha_window_class": classify_alpha_window(best_window_hours),
        "decay_status": decay_status,
        "suggested_usage": suggested_usage,
        "window_scores": parsed_windows,
        "auto_weight_update_allowed": False,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "real_world_actions_allowed": False,
    }


def build_alpha_decay_report(
    source_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(source_rows, list):
        raise ValueError("source_rows must be a list")

    rows = []

    for row in source_rows:
        if not isinstance(row, dict):
            raise ValueError("source row must be a dict")

        rows.append(
            estimate_alpha_decay_profile(
                source_id=row.get("source_id"),
                source_type=row.get("source_type", "unknown"),
                window_scores=row.get("window_scores"),
            )
        )

    rows.sort(key=lambda item: (item["alpha_window_class"], item["source_id"]))

    return {
        "ok": True,
        "type": "p14_alpha_decay_report",
        "current_stage": "P14-D19-D21",
        "report_status": "READY_FOR_OPERATOR_REVIEW",
        "purpose": "identify the best paper time window for each feature or information source",
        "row_count": len(rows),
        "rows": rows,
        "audit_policy": {
            "auto_weight_update_allowed": False,
            "auto_silence_allowed": False,
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


def write_alpha_decay_report(
    source_rows: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_alpha_decay_report(source_rows)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_alpha_decay_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_weight_update_allowed": False,
        "real_world_actions_allowed": False,
    }
