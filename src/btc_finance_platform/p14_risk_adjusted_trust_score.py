import json
from pathlib import Path
from typing import Any

from btc_finance_platform.p14_expert_trust_score import score_expert_outcome


def apply_drawdown_penalty(
    weighted_score: float,
    max_paper_drawdown_pct: float,
    penalty_multiplier: float = 2.0,
) -> dict[str, Any]:
    if not isinstance(weighted_score, (int, float)):
        raise ValueError("weighted_score must be numeric")

    if not isinstance(max_paper_drawdown_pct, (int, float)):
        raise ValueError("max_paper_drawdown_pct must be numeric")

    if max_paper_drawdown_pct < 0:
        raise ValueError("max_paper_drawdown_pct must be non-negative")

    if max_paper_drawdown_pct > 1:
        raise ValueError("max_paper_drawdown_pct must be between 0 and 1")

    if penalty_multiplier < 0:
        raise ValueError("penalty_multiplier must be non-negative")

    penalty_factor = 1.0 / (1.0 + max_paper_drawdown_pct * penalty_multiplier)
    risk_adjusted_score = float(weighted_score) * penalty_factor

    return {
        "ok": True,
        "type": "p14_drawdown_penalty",
        "weighted_score": float(weighted_score),
        "max_paper_drawdown_pct": float(max_paper_drawdown_pct),
        "penalty_multiplier": float(penalty_multiplier),
        "penalty_factor": penalty_factor,
        "risk_adjusted_score": risk_adjusted_score,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
    }


def score_risk_adjusted_expert_outcome(
    direction: str,
    outcome: str,
    confidence: float,
    age_days: float = 0.0,
    half_life_days: float = 30.0,
    max_paper_drawdown_pct: float = 0.0,
    penalty_multiplier: float = 2.0,
) -> dict[str, Any]:
    base = score_expert_outcome(
        direction=direction,
        outcome=outcome,
        confidence=confidence,
        age_days=age_days,
        half_life_days=half_life_days,
    )

    penalty = apply_drawdown_penalty(
        weighted_score=base["weighted_score"],
        max_paper_drawdown_pct=max_paper_drawdown_pct,
        penalty_multiplier=penalty_multiplier,
    )

    return {
        "ok": True,
        "type": "p14_risk_adjusted_expert_outcome_score",
        "direction": direction,
        "outcome": outcome,
        "confidence": float(confidence),
        "age_days": float(age_days),
        "half_life_days": float(half_life_days),
        "max_paper_drawdown_pct": float(max_paper_drawdown_pct),
        "base_weighted_score": base["weighted_score"],
        "drawdown_penalty_factor": penalty["penalty_factor"],
        "risk_adjusted_score": penalty["risk_adjusted_score"],
        "risk_adjustment_formula": "risk_adjusted_score = weighted_score / (1 + max_paper_drawdown_pct * penalty_multiplier)",
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }


def build_risk_adjusted_trust_report(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(observations, list):
        raise ValueError("observations must be a list")

    rows = []

    for observation in observations:
        if not isinstance(observation, dict):
            raise ValueError("observation must be a dict")

        expert_id = observation.get("expert_id")
        regime = observation.get("regime", "unknown")

        if not expert_id:
            raise ValueError("expert_id is required")

        score = score_risk_adjusted_expert_outcome(
            direction=observation.get("direction", "observe"),
            outcome=observation.get("outcome", "unknown"),
            confidence=observation.get("confidence", 0.0),
            age_days=observation.get("age_days", 0.0),
            half_life_days=observation.get("half_life_days", 30.0),
            max_paper_drawdown_pct=observation.get("max_paper_drawdown_pct", 0.0),
            penalty_multiplier=observation.get("penalty_multiplier", 2.0),
        )

        rows.append(
            {
                "expert_id": str(expert_id),
                "regime": str(regime),
                "direction": score["direction"],
                "outcome": score["outcome"],
                "confidence": score["confidence"],
                "base_weighted_score": score["base_weighted_score"],
                "max_paper_drawdown_pct": score["max_paper_drawdown_pct"],
                "drawdown_penalty_factor": score["drawdown_penalty_factor"],
                "risk_adjusted_score": score["risk_adjusted_score"],
                "operator_review_required": True,
                "governor_weight_auto_apply_allowed": False,
                "paper_only": True,
                "real_world_actions_allowed": False,
            }
        )

    rows.sort(key=lambda row: (row["regime"], -row["risk_adjusted_score"], row["expert_id"]))

    return {
        "ok": True,
        "type": "p14_risk_adjusted_trust_report",
        "current_stage": "P14-D13-D15",
        "report_status": "READY_FOR_OPERATOR_REVIEW",
        "purpose": "penalize expert paper predictions that were correct only after unsafe paper drawdown",
        "formula": "risk_adjusted_score = weighted_score / (1 + max_paper_drawdown_pct * penalty_multiplier)",
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
        "deployment_allowed_now": False,
    }


def write_risk_adjusted_trust_report(
    observations: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_risk_adjusted_trust_report(observations)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_risk_adjusted_trust_report_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "governor_weight_auto_apply_allowed": False,
        "real_world_actions_allowed": False,
    }
