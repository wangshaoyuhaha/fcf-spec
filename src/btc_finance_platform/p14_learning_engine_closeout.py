import json
from pathlib import Path
from typing import Any


REQUIRED_MODULE_KEYS = (
    "regime_taxonomy",
    "shadow_ledger",
    "expert_trust_scoring",
    "feature_source_audit",
    "risk_adjusted_trust_scoring",
    "feature_orthogonality_audit",
    "alpha_decay_profiling",
    "meta_anomaly_detection",
    "governor_weight_proposal",
    "scenario_engine",
    "patch_proposal_sandbox",
    "data_quality_sentry",
    "explanation_consistency_check",
)


def normalize_closeout_module(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("module row must be a dict")

    module_key = row.get("module_key")
    if not module_key:
        raise ValueError("module_key is required")

    return {
        "module_key": str(module_key),
        "stage": str(row.get("stage", "unknown")),
        "status": str(row.get("status", "completed")),
        "paper_only": bool(row.get("paper_only", True)),
        "operator_review_required": bool(row.get("operator_review_required", True)),
        "auto_apply_allowed": bool(row.get("auto_apply_allowed", False)),
        "real_world_actions_allowed": bool(row.get("real_world_actions_allowed", False)),
    }


def build_learning_engine_closeout_report(
    module_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(module_rows, list):
        raise ValueError("module_rows must be a list")

    rows = [normalize_closeout_module(row) for row in module_rows]
    present = {row["module_key"] for row in rows}
    missing_modules = [key for key in REQUIRED_MODULE_KEYS if key not in present]

    unsafe_rows = [
        row for row in rows
        if row["paper_only"] is not True
        or row["operator_review_required"] is not True
        or row["auto_apply_allowed"] is not False
        or row["real_world_actions_allowed"] is not False
    ]

    if missing_modules:
        closeout_status = "BLOCKED_MISSING_REQUIRED_MODULES"
    elif unsafe_rows:
        closeout_status = "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    else:
        closeout_status = "READY_FOR_OPERATOR_REVIEW"

    return {
        "ok": True,
        "type": "p14_learning_engine_closeout_report",
        "current_stage": "P14-D40-D42",
        "closeout_status": closeout_status,
        "purpose": "final review-only closeout summary for P14 paper learning engine",
        "required_module_count": len(REQUIRED_MODULE_KEYS),
        "completed_module_count": len(present),
        "missing_modules": missing_modules,
        "unsafe_module_count": len(unsafe_rows),
        "unsafe_modules": unsafe_rows,
        "rows": rows,
        "closeout_policy": {
            "p14_can_be_closed_after_operator_review": closeout_status == "READY_FOR_OPERATOR_REVIEW",
            "merge_to_main_allowed_now": False,
            "release_allowed_now": False,
            "auto_apply_allowed": False,
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


def default_p14_closeout_modules() -> list[dict[str, Any]]:
    return [
        {"module_key": "regime_taxonomy", "stage": "P14-D1-D3"},
        {"module_key": "shadow_ledger", "stage": "P14-D4-D6"},
        {"module_key": "expert_trust_scoring", "stage": "P14-D7-D9"},
        {"module_key": "feature_source_audit", "stage": "P14-D10-D12"},
        {"module_key": "risk_adjusted_trust_scoring", "stage": "P14-D13-D15"},
        {"module_key": "feature_orthogonality_audit", "stage": "P14-D16-D18"},
        {"module_key": "alpha_decay_profiling", "stage": "P14-D19-D21"},
        {"module_key": "meta_anomaly_detection", "stage": "P14-D22-D24"},
        {"module_key": "governor_weight_proposal", "stage": "P14-D25-D27"},
        {"module_key": "scenario_engine", "stage": "P14-D28-D30"},
        {"module_key": "patch_proposal_sandbox", "stage": "P14-D31-D33"},
        {"module_key": "data_quality_sentry", "stage": "P14-D34-D36"},
        {"module_key": "explanation_consistency_check", "stage": "P14-D37-D39"},
    ]


def write_learning_engine_closeout_report(
    module_rows: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_learning_engine_closeout_report(module_rows)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_learning_engine_closeout_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_apply_allowed": False,
        "real_world_actions_allowed": False,
    }
