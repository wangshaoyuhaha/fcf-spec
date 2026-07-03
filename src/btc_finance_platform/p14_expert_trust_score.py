import json
import math
from pathlib import Path
from typing import Any


def score_expert_outcome(
    direction: str,
    outcome: str,
    confidence: float,
    age_days: float = 0.0,
    half_life_days: float = 30.0,
) -> dict[str, Any]:
    if direction not in {"long", "short", "flat", "observe"}:
        raise ValueError("direction is invalid")

    if outcome not in {"win", "loss", "neutral", "unknown"}:
        raise ValueError("outcome is invalid")

    if not isinstance(confidence, (int, float)):
        raise ValueError("confidence must be numeric")

    if confidence < 0 or confidence > 1:
        raise ValueError("confidence must be between 0 and 1")

    if half_life_days <= 0:
        raise ValueError("half_life_days must be positive")

    decay = 0.5 ** (max(age_days, 0.0) / half_life_days)

    if outcome == "win":
        raw_score = confidence
    elif outcome == "loss":
        raw_score = -confidence
    elif outcome == "neutral":
        raw_score = 0.0
    else:
        raw_score = 0.0

    weighted_score = raw_score * decay

    return {
        "ok": True,
        "type": "p14_expert_outcome_score",
        "direction": direction,
        "outcome": outcome,
        "confidence": float(confidence),
        "age_days": float(age_days),
        "half_life_days": float(half_life_days),
        "decay": decay,
        "raw_score": raw_score,
        "weighted_score": weighted_score,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
    }


def build_expert_trust_report(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(observations, list):
        raise ValueError("observations must be a list")

    buckets: dict[str, dict[str, Any]] = {}

    for observation in observations:
        if not isinstance(observation, dict):
            raise ValueError("observation must be a dict")

        expert_id = observation.get("expert_id")
        regime = observation.get("regime", "unknown")

        if not expert_id:
            raise ValueError("expert_id is required")

        score = score_expert_outcome(
            direction=observation.get("direction", "observe"),
            outcome=observation.get("outcome", "unknown"),
            confidence=observation.get("confidence", 0.0),
            age_days=observation.get("age_days", 0.0),
            half_life_days=observation.get("half_life_days", 30.0),
        )

        key = f"{regime}::{expert_id}"
        if key not in buckets:
            buckets[key] = {
                "expert_id": expert_id,
                "regime": regime,
                "observation_count": 0,
                "weighted_score_sum": 0.0,
                "confidence_sum": 0.0,
            }

        buckets[key]["observation_count"] += 1
        buckets[key]["weighted_score_sum"] += score["weighted_score"]
        buckets[key]["confidence_sum"] += float(observation.get("confidence", 0.0))

    rows = []
    for item in buckets.values():
        count = item["observation_count"]
        avg_score = item["weighted_score_sum"] / count if count else 0.0
        avg_confidence = item["confidence_sum"] / count if count else 0.0

        rows.append(
            {
                "expert_id": item["expert_id"],
                "regime": item["regime"],
                "observation_count": count,
                "trust_score": avg_score,
                "average_confidence": avg_confidence,
                "trust_score_mode": "paper_half_life_weighted",
                "governor_weight_proposal_allowed": True,
                "governor_weight_auto_apply_allowed": False,
            }
        )

    rows.sort(key=lambda row: (row["regime"], -row["trust_score"], row["expert_id"]))

    return {
        "ok": True,
        "type": "p14_expert_trust_report",
        "current_stage": "P14-D7-D9",
        "report_status": "READY_FOR_OPERATOR_REVIEW",
        "trust_score_formula": "weighted_score = outcome_score * 0.5 ** (age_days / half_life_days)",
        "rows": rows,
        "row_count": len(rows),
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "governor_weight_proposal_allowed": True,
        "governor_weight_auto_apply_allowed": False,
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
    }


def write_expert_trust_report(
    observations: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_expert_trust_report(observations)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_expert_trust_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "governor_weight_auto_apply_allowed": False,
        "real_world_actions_allowed": False,
    }
