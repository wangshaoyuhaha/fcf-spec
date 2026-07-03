import json
from pathlib import Path
from typing import Any


def classify_feature_action(
    correlation: float,
    observation_count: int,
    min_observations: int = 20,
    weak_threshold: float = 0.10,
    strong_threshold: float = 0.30,
) -> str:
    if not isinstance(correlation, (int, float)):
        raise ValueError("correlation must be numeric")

    if observation_count < 0:
        raise ValueError("observation_count must be non-negative")

    abs_corr = abs(float(correlation))

    if observation_count < min_observations:
        return "insufficient_data"

    if abs_corr < weak_threshold:
        return "deprioritize_or_silence"

    if abs_corr >= strong_threshold:
        return "keep_high_priority"

    return "keep_watch"


def build_feature_source_audit_report(
    feature_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(feature_rows, list):
        raise ValueError("feature_rows must be a list")

    audited_rows = []

    for row in feature_rows:
        if not isinstance(row, dict):
            raise ValueError("feature row must be a dict")

        feature_id = row.get("feature_id")
        source_type = row.get("source_type", "unknown")
        regime = row.get("regime", "unknown")
        correlation = row.get("correlation")
        observation_count = row.get("observation_count", 0)

        if not feature_id:
            raise ValueError("feature_id is required")

        if correlation is None:
            raise ValueError("correlation is required")

        action = classify_feature_action(
            correlation=float(correlation),
            observation_count=int(observation_count),
        )

        audited_rows.append(
            {
                "feature_id": str(feature_id),
                "source_type": str(source_type),
                "regime": str(regime),
                "correlation": float(correlation),
                "observation_count": int(observation_count),
                "audit_action": action,
                "auto_prune_allowed": False,
                "operator_review_required": True,
                "paper_only": True,
                "real_world_actions_allowed": False,
            }
        )

    audited_rows.sort(key=lambda item: (item["regime"], item["audit_action"], item["feature_id"]))

    return {
        "ok": True,
        "type": "p14_feature_source_audit_report",
        "current_stage": "P14-D10-D12",
        "audit_status": "READY_FOR_OPERATOR_REVIEW",
        "purpose": "identify weak or noisy paper features before governor weighting",
        "row_count": len(audited_rows),
        "rows": audited_rows,
        "audit_policy": {
            "deprioritize_weak_features_allowed": True,
            "auto_prune_allowed": False,
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


def write_feature_source_audit_report(
    feature_rows: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_feature_source_audit_report(feature_rows)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_feature_source_audit_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_prune_allowed": False,
        "real_world_actions_allowed": False,
    }
