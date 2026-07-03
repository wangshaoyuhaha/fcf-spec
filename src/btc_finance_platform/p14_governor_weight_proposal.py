import json
from pathlib import Path
from typing import Any


def normalize_positive_scores(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise ValueError("rows must be a list")

    positive_scores = []

    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("row must be a dict")

        expert_id = row.get("expert_id")
        if not expert_id:
            raise ValueError("expert_id is required")

        score = float(row.get("risk_adjusted_score", row.get("trust_score", 0.0)))
        positive_scores.append(
            {
                "expert_id": str(expert_id),
                "regime": str(row.get("regime", "unknown")),
                "raw_score": score,
                "positive_score": max(score, 0.0),
            }
        )

    total = sum(item["positive_score"] for item in positive_scores)

    if total <= 0:
        equal_weight = 1.0 / len(positive_scores) if positive_scores else 0.0
        return [
            {
                **item,
                "proposed_weight": equal_weight,
                "weight_reason": "equal_weight_due_to_no_positive_scores",
            }
            for item in positive_scores
        ]

    return [
        {
            **item,
            "proposed_weight": item["positive_score"] / total,
            "weight_reason": "normalized_positive_risk_adjusted_score",
        }
        for item in positive_scores
    ]


def apply_meta_anomaly_guard(
    proposed_rows: list[dict[str, Any]],
    meta_anomaly_status: str,
) -> dict[str, Any]:
    if meta_anomaly_status not in {"normal", "heightened_operator_review", "force_shadow_review"}:
        raise ValueError("meta_anomaly_status is invalid")

    if meta_anomaly_status == "force_shadow_review":
        governor_mode = "shadow_review_only"
        max_weight_cap = 0.0
    elif meta_anomaly_status == "heightened_operator_review":
        governor_mode = "heightened_review"
        max_weight_cap = 0.50
    else:
        governor_mode = "normal_review"
        max_weight_cap = 1.0

    guarded_rows = []

    for row in proposed_rows:
        weight = float(row["proposed_weight"])
        guarded_weight = min(weight, max_weight_cap)

        guarded_rows.append(
            {
                **row,
                "guarded_weight": guarded_weight,
                "meta_anomaly_status": meta_anomaly_status,
                "governor_mode": governor_mode,
                "auto_apply_allowed": False,
                "operator_review_required": True,
                "paper_only": True,
                "real_world_actions_allowed": False,
            }
        )

    return {
        "ok": True,
        "type": "p14_governor_weight_guard",
        "meta_anomaly_status": meta_anomaly_status,
        "governor_mode": governor_mode,
        "max_weight_cap": max_weight_cap,
        "rows": guarded_rows,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_apply_allowed": False,
        "real_world_actions_allowed": False,
    }


def build_governor_weight_proposal(
    trust_rows: list[dict[str, Any]],
    regime: str,
    meta_anomaly_status: str = "normal",
) -> dict[str, Any]:
    if not regime:
        raise ValueError("regime is required")

    normalized = normalize_positive_scores(trust_rows)
    guarded = apply_meta_anomaly_guard(normalized, meta_anomaly_status)

    return {
        "ok": True,
        "type": "p14_governor_weight_proposal",
        "current_stage": "P14-D25-D27",
        "proposal_status": "READY_FOR_OPERATOR_REVIEW",
        "regime": regime,
        "meta_anomaly_status": meta_anomaly_status,
        "governor_mode": guarded["governor_mode"],
        "rows": guarded["rows"],
        "row_count": len(guarded["rows"]),
        "proposal_policy": {
            "governor_weight_proposal_allowed": True,
            "governor_weight_auto_apply_allowed": False,
            "auto_mode_switch_allowed": False,
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


def write_governor_weight_proposal(
    trust_rows: list[dict[str, Any]],
    regime: str,
    meta_anomaly_status: str,
    path: str | Path,
) -> dict[str, Any]:
    proposal = build_governor_weight_proposal(
        trust_rows=trust_rows,
        regime=regime,
        meta_anomaly_status=meta_anomaly_status,
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(proposal, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_governor_weight_proposal_written",
        "output_path": str(output),
        "proposal": proposal,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "governor_weight_auto_apply_allowed": False,
        "real_world_actions_allowed": False,
    }
