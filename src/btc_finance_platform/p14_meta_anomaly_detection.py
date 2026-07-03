import json
from pathlib import Path
from typing import Any


def classify_confidence_anomaly(
    average_confidence: float,
    actual_win_rate: float,
    high_confidence_threshold: float = 0.80,
    low_win_rate_threshold: float = 0.45,
) -> str:
    if not isinstance(average_confidence, (int, float)):
        raise ValueError("average_confidence must be numeric")

    if not isinstance(actual_win_rate, (int, float)):
        raise ValueError("actual_win_rate must be numeric")

    if average_confidence < 0 or average_confidence > 1:
        raise ValueError("average_confidence must be between 0 and 1")

    if actual_win_rate < 0 or actual_win_rate > 1:
        raise ValueError("actual_win_rate must be between 0 and 1")

    if average_confidence >= high_confidence_threshold and actual_win_rate <= low_win_rate_threshold:
        return "overconfidence_anomaly"

    if average_confidence >= high_confidence_threshold and actual_win_rate < average_confidence - 0.25:
        return "confidence_calibration_warning"

    return "normal"


def classify_drawdown_anomaly(
    max_paper_drawdown_pct: float,
    warning_threshold: float = 0.15,
    critical_threshold: float = 0.30,
) -> str:
    if not isinstance(max_paper_drawdown_pct, (int, float)):
        raise ValueError("max_paper_drawdown_pct must be numeric")

    if max_paper_drawdown_pct < 0 or max_paper_drawdown_pct > 1:
        raise ValueError("max_paper_drawdown_pct must be between 0 and 1")

    if max_paper_drawdown_pct >= critical_threshold:
        return "critical_paper_drawdown"

    if max_paper_drawdown_pct >= warning_threshold:
        return "paper_drawdown_warning"

    return "normal"


def evaluate_meta_anomaly_window(window: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(window, dict):
        raise ValueError("window must be a dict")

    window_id = window.get("window_id")
    if not window_id:
        raise ValueError("window_id is required")

    average_confidence = float(window.get("average_confidence", 0.0))
    actual_win_rate = float(window.get("actual_win_rate", 0.0))
    max_paper_drawdown_pct = float(window.get("max_paper_drawdown_pct", 0.0))

    confidence_status = classify_confidence_anomaly(average_confidence, actual_win_rate)
    drawdown_status = classify_drawdown_anomaly(max_paper_drawdown_pct)

    anomaly_flags = []
    if confidence_status != "normal":
        anomaly_flags.append(confidence_status)
    if drawdown_status != "normal":
        anomaly_flags.append(drawdown_status)

    if "overconfidence_anomaly" in anomaly_flags or "critical_paper_drawdown" in anomaly_flags:
        proposed_mode = "force_shadow_review"
    elif anomaly_flags:
        proposed_mode = "heightened_operator_review"
    else:
        proposed_mode = "normal_review"

    return {
        "ok": True,
        "type": "p14_meta_anomaly_window",
        "window_id": str(window_id),
        "regime": str(window.get("regime", "unknown")),
        "average_confidence": average_confidence,
        "actual_win_rate": actual_win_rate,
        "max_paper_drawdown_pct": max_paper_drawdown_pct,
        "confidence_status": confidence_status,
        "drawdown_status": drawdown_status,
        "anomaly_flags": anomaly_flags,
        "proposed_mode": proposed_mode,
        "auto_mode_switch_allowed": False,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "real_world_actions_allowed": False,
    }


def build_meta_anomaly_report(windows: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(windows, list):
        raise ValueError("windows must be a list")

    rows = [evaluate_meta_anomaly_window(window) for window in windows]
    anomaly_count = sum(1 for row in rows if row["anomaly_flags"])

    return {
        "ok": True,
        "type": "p14_meta_anomaly_report",
        "current_stage": "P14-D22-D24",
        "report_status": "READY_FOR_OPERATOR_REVIEW",
        "purpose": "detect paper-only confidence inversion, drawdown stress, and meta-level learning anomalies",
        "row_count": len(rows),
        "anomaly_count": anomaly_count,
        "rows": rows,
        "meta_policy": {
            "force_shadow_review_proposal_allowed": True,
            "auto_mode_switch_allowed": False,
            "auto_trading_allowed": False,
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


def write_meta_anomaly_report(
    windows: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_meta_anomaly_report(windows)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_meta_anomaly_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_mode_switch_allowed": False,
        "real_world_actions_allowed": False,
    }
