from typing import Any

from btc_finance_platform.paper_analysis_pipeline import build_paper_analysis_pipeline_report


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


def classify_market_regime_from_item(analysis_item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(analysis_item, dict):
        raise ValueError("analysis_item must be a dict")

    deviation = analysis_item["deviation"]
    momentum = analysis_item["momentum"]
    risk = analysis_item["risk"]

    magnitude = deviation["magnitude"]
    direction = deviation["direction"]
    momentum_direction = momentum["direction"]
    risk_level = risk["level"]

    if risk_level == "high":
        regime = "stressed"
    elif magnitude in {"medium", "large"} and direction == "above_reference":
        regime = "overextended_upside"
    elif magnitude in {"medium", "large"} and direction == "below_reference":
        regime = "overextended_downside"
    elif momentum_direction == "up":
        regime = "mild_uptrend"
    elif momentum_direction == "down":
        regime = "mild_downtrend"
    else:
        regime = "neutral"

    return {
        "ok": True,
        "type": "paper_market_regime_classification",
        "symbol": analysis_item["symbol"],
        "regime": regime,
        "source_risk_level": risk_level,
        "source_deviation_magnitude": magnitude,
        "source_momentum_direction": momentum_direction,
        **paper_flags(),
    }


def build_risk_governor_decision(analysis_item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(analysis_item, dict):
        raise ValueError("analysis_item must be a dict")

    regime = classify_market_regime_from_item(analysis_item)
    risk = analysis_item["risk"]
    signal = analysis_item["signal"]

    blocked_reasons = []
    warnings = []

    if risk["level"] == "high":
        blocked_reasons.append("high_risk_requires_manual_review_only")

    if regime["regime"] == "stressed":
        blocked_reasons.append("stressed_regime_blocks_escalation")

    if signal == "paper_review_only_high_risk":
        warnings.append("signal_already_marked_review_only")

    if blocked_reasons:
        gate = "blocked_for_escalation"
        allowed_action = "paper_review_only"
    else:
        gate = "paper_allowed_with_operator_review"
        allowed_action = "paper_analysis_review"

    return {
        "ok": True,
        "type": "risk_governor_decision",
        "symbol": analysis_item["symbol"],
        "gate": gate,
        "allowed_action": allowed_action,
        "blocked_reasons": blocked_reasons,
        "warnings": warnings,
        "regime": regime,
        "risk_level": risk["level"],
        "risk_score": risk["score"],
        "signal": signal,
        "decision": "governor_paper_only_no_real_trade",
        **paper_flags(),
    }


def build_policy_gate_for_governor_decision(
    governor_decision: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(governor_decision, dict):
        raise ValueError("governor_decision must be a dict")
    if governor_decision.get("type") != "risk_governor_decision":
        raise ValueError("governor_decision type is invalid")

    checks = {
        "paper_only_preserved": governor_decision["paper_only"] is True,
        "operator_review_required": governor_decision["operator_review_required"] is True,
        "no_real_exchange_api": governor_decision["real_exchange_api"] is False,
        "no_real_api_key_required": governor_decision["real_api_key_required"] is False,
        "no_wallet_private_key_required": governor_decision["wallet_private_key_required"] is False,
        "no_real_order": governor_decision["real_order"] is False,
        "no_real_execution": governor_decision["real_execution"] is False,
        "no_real_balance": governor_decision["real_balance"] is False,
        "no_real_position": governor_decision["real_position"] is False,
        "no_real_money_impact": governor_decision["real_money_impact"] is False,
        "no_escalation_without_operator_review": True,
    }

    approved_for_paper_review = all(checks.values())

    return {
        "ok": approved_for_paper_review,
        "type": "policy_gate_decision",
        "symbol": governor_decision["symbol"],
        "gate": "pass" if approved_for_paper_review else "fail",
        "approved_action": governor_decision["allowed_action"],
        "blocked_real_world_actions": [
            "real_exchange_api",
            "real_api_key",
            "wallet_private_key",
            "real_order",
            "real_execution",
            "real_balance",
            "real_position",
            "real_money_impact",
            "automatic_live_trading",
        ],
        "checks": checks,
        "governor_decision": governor_decision,
        "decision": "policy_gate_paper_only",
        **paper_flags(),
    }


def build_batch_risk_governance_report(file_paths: list[Any]) -> dict[str, Any]:
    pipeline_report = build_paper_analysis_pipeline_report(file_paths)
    analysis_items = pipeline_report["pipeline"]["pipeline_result"]["analysis"]["items"]

    governor_decisions = [
        build_risk_governor_decision(item) for item in analysis_items
    ]
    policy_gates = [
        build_policy_gate_for_governor_decision(item) for item in governor_decisions
    ]

    gate_counts: dict[str, int] = {}
    regime_counts: dict[str, int] = {}

    for decision in governor_decisions:
        gate = decision["gate"]
        regime_name = decision["regime"]["regime"]
        gate_counts[gate] = gate_counts.get(gate, 0) + 1
        regime_counts[regime_name] = regime_counts.get(regime_name, 0) + 1

    return {
        "ok": all(item["ok"] for item in policy_gates),
        "type": "batch_risk_governance_report",
        "count": len(governor_decisions),
        "symbols": [item["symbol"] for item in governor_decisions],
        "gate_counts": gate_counts,
        "regime_counts": regime_counts,
        "governor_decisions": governor_decisions,
        "policy_gates": policy_gates,
        "source_pipeline_report": pipeline_report,
        "decision": "batch_governance_paper_only_no_real_trade",
        **paper_flags(),
    }
