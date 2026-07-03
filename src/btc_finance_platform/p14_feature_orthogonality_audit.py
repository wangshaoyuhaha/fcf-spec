import json
from pathlib import Path
from typing import Any


def classify_feature_overlap(
    correlation: float,
    high_threshold: float = 0.85,
    medium_threshold: float = 0.65,
) -> str:
    if not isinstance(correlation, (int, float)):
        raise ValueError("correlation must be numeric")

    if high_threshold <= medium_threshold:
        raise ValueError("high_threshold must be greater than medium_threshold")

    abs_corr = abs(float(correlation))

    if abs_corr >= high_threshold:
        return "high_redundancy_review_required"

    if abs_corr >= medium_threshold:
        return "medium_overlap_watch"

    return "orthogonal_enough"


def recommend_redundant_feature_action(pair: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(pair, dict):
        raise ValueError("pair must be a dict")

    feature_a = pair.get("feature_a")
    feature_b = pair.get("feature_b")
    correlation = pair.get("correlation")

    if not feature_a or not feature_b:
        raise ValueError("feature_a and feature_b are required")

    if correlation is None:
        raise ValueError("correlation is required")

    overlap_class = classify_feature_overlap(float(correlation))

    cost_a = float(pair.get("cost_a", 0.0))
    cost_b = float(pair.get("cost_b", 0.0))
    latency_a_ms = float(pair.get("latency_a_ms", 0.0))
    latency_b_ms = float(pair.get("latency_b_ms", 0.0))

    if overlap_class == "high_redundancy_review_required":
        if cost_a + latency_a_ms / 1000.0 > cost_b + latency_b_ms / 1000.0:
            proposed_review_action = f"review_mute_or_deprioritize:{feature_a}"
        elif cost_b + latency_b_ms / 1000.0 > cost_a + latency_a_ms / 1000.0:
            proposed_review_action = f"review_mute_or_deprioritize:{feature_b}"
        else:
            proposed_review_action = "review_keep_one_of_pair"
    elif overlap_class == "medium_overlap_watch":
        proposed_review_action = "watch_overlap"
    else:
        proposed_review_action = "keep_both"

    return {
        "ok": True,
        "type": "p14_feature_overlap_pair_audit",
        "feature_a": str(feature_a),
        "feature_b": str(feature_b),
        "correlation": float(correlation),
        "abs_correlation": abs(float(correlation)),
        "overlap_class": overlap_class,
        "proposed_review_action": proposed_review_action,
        "auto_mute_allowed": False,
        "auto_prune_allowed": False,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "real_world_actions_allowed": False,
    }


def build_feature_orthogonality_audit_report(
    feature_pairs: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(feature_pairs, list):
        raise ValueError("feature_pairs must be a list")

    rows = [recommend_redundant_feature_action(pair) for pair in feature_pairs]

    high_redundancy_count = sum(
        1 for row in rows if row["overlap_class"] == "high_redundancy_review_required"
    )

    return {
        "ok": True,
        "type": "p14_feature_orthogonality_audit_report",
        "current_stage": "P14-D16-D18",
        "audit_status": "READY_FOR_OPERATOR_REVIEW",
        "purpose": "detect redundant feature pairs so the system seeks incremental alpha rather than repeated noise",
        "row_count": len(rows),
        "high_redundancy_count": high_redundancy_count,
        "rows": rows,
        "audit_policy": {
            "high_correlation_threshold": 0.85,
            "medium_correlation_threshold": 0.65,
            "auto_mute_allowed": False,
            "auto_prune_allowed": False,
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


def write_feature_orthogonality_audit_report(
    feature_pairs: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_feature_orthogonality_audit_report(feature_pairs)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_feature_orthogonality_audit_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_mute_allowed": False,
        "auto_prune_allowed": False,
        "real_world_actions_allowed": False,
    }
