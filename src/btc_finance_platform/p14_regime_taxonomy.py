import json
from pathlib import Path
from typing import Any


REGIME_TYPES = (
    "trend_up",
    "trend_down",
    "range_chop",
    "high_volatility_breakout",
    "low_volatility_compression",
    "liquidity_stress",
    "unknown",
)


def build_regime_taxonomy() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p14_learning_engine_regime_taxonomy",
        "current_stage": "P14-D1-D3",
        "purpose": "define paper-only market regime buckets before expert trust scoring",
        "why_regime_first": "expert trust scores must be conditioned by market environment",
        "regime_types": list(REGIME_TYPES),
        "regime_inputs_allowed": [
            "paper_price_features",
            "paper_volatility_features",
            "paper_volume_features",
            "paper_funding_features",
            "paper_liquidity_notes",
            "paper_macro_notes",
        ],
        "regime_inputs_forbidden": [
            "real_exchange_api",
            "real_brokerage_api",
            "api_keys",
            "wallet_private_keys",
            "real_balances",
            "real_positions",
        ],
        "learning_engine_order": [
            "define_regime_taxonomy",
            "record_shadow_ledger",
            "score_experts_by_regime",
            "generate_governor_weight_proposal",
            "wait_for_operator_review",
        ],
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


def classify_regime(features: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(features, dict):
        raise ValueError("features must be a dict")

    volatility = str(features.get("volatility", "unknown")).lower()
    trend = str(features.get("trend", "unknown")).lower()
    liquidity = str(features.get("liquidity", "normal")).lower()
    if trend not in {"up", "down", "range", "unknown"}:
        raise ValueError("unsupported trend value")
    if volatility not in {"high", "normal", "low", "unknown"}:
        raise ValueError("unsupported volatility value")
    if liquidity not in {"normal", "stress", "unknown"}:
        raise ValueError("unsupported liquidity value")

    if liquidity == "stress":
        regime = "liquidity_stress"
    elif volatility == "high" and trend in {"up", "down"}:
        regime = "high_volatility_breakout"
    elif volatility == "low":
        regime = "low_volatility_compression"
    elif trend == "up":
        regime = "trend_up"
    elif trend == "down":
        regime = "trend_down"
    elif trend == "range":
        regime = "range_chop"
    else:
        regime = "unknown"

    return {
        "ok": True,
        "type": "p14_regime_classification",
        "classification_version": "regime-taxonomy-v1",
        "regime": regime,
        "confidence": "HIGH" if regime != "unknown" else "LOW",
        "features_used": sorted(features.keys()),
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
    }
def write_regime_taxonomy(path: str | Path) -> dict[str, Any]:
    taxonomy = build_regime_taxonomy()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(taxonomy, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "ok": True,
        "type": "p14_regime_taxonomy_written",
        "output_path": str(output),
        "taxonomy": taxonomy,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
    }
