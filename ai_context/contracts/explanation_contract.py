"""AI-CONTEXT explanation contract.

This module is sidecar-only.
It reads structured DATA-APP / STOCK-APP outputs and creates read-only explanations.
It must not mutate scores, reason codes, risk flags, or trading state.
"""

from __future__ import annotations

from typing import Any


CONTRACT_VERSION = "AI_CONTEXT_EXPLANATION_V1"

READ_ONLY_SAFETY = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "score_mutation_allowed": False,
    "reason_code_fabrication_allowed": False,
    "risk_flag_suppression_allowed": False,
    "buy_sell_instruction_allowed": False,
    "limit_up_guarantee_allowed": False,
    "real_trading_allowed": False,
    "real_action_blocked": True,
    "operator_review_required": True,
}

REASON_CODE_EXPLANATIONS = {
    "BASE_FILTER_PASS": "The candidate passed the basic sidecar filter.",
    "NOT_ST_STOCK": "The candidate is not marked as ST or risk warning in the input.",
    "TRADING_ACTIVE": "The candidate is marked as actively tradable in the paper data.",
    "LIQUIDITY_OK": "The candidate passed the liquidity filter.",
    "MARKET_CAP_OK": "The candidate passed the market capitalization filter.",
    "SECTOR_ACTIVE": "The candidate belongs to an active sector signal group.",
    "THEME_HEAT_DETECTED": "Theme heat was detected by deterministic sidecar rules.",
    "SECTOR_BREADTH_POSITIVE": "Sector breadth was positive in the sidecar input.",
    "NEAR_LIMIT_UP_PRICE": "The latest price was near the limit-up reference level.",
    "VOLUME_EXPANSION": "Volume expansion was detected by rule-based checks.",
    "TURNOVER_EXPANSION": "Turnover expansion was detected by rule-based checks.",
    "CLOSE_NEAR_HIGH": "The close price was near the high price in the input period.",
    "PRICE_BREAKOUT": "A price breakout signal was detected by deterministic rules.",
    "FUND_FLOW_PROXY_POSITIVE": "A public fund-flow proxy signal was positive.",
    "DRAGON_TIGER_SIGNAL": "A dragon-tiger-list style public signal was present.",
    "NORTHBOUND_SIGNAL": "A northbound-flow style public signal was present.",
    "ETF_FLOW_SIGNAL": "An ETF-flow style public signal was present.",
    "DATA_QUALITY_PASS_STRICT": "The data quality state was PASS_STRICT.",
    "DATA_QUALITY_PASS_LIMITED": "The data quality state was PASS_LIMITED.",
    "MANIFEST_CHECKSUM_OK": "The upstream manifest checksum was available and traceable.",
}

RISK_FLAG_EXPLANATIONS = {
    "IS_ST_OR_RISK_WARNING": "The candidate may have ST or risk-warning characteristics.",
    "SUSPENDED_OR_NOT_TRADING": "The candidate may be suspended or not actively tradable.",
    "NEW_LISTING_RISK": "The listing age may be too short for stable interpretation.",
    "LOW_LIQUIDITY_RISK": "Liquidity may be insufficient for reliable paper analysis.",
    "PRICE_ABNORMAL_RISK": "The price input may contain abnormal values.",
    "LIMIT_UP_TOO_CLOSE_RISK": "The price may already be too close to the limit-up reference.",
    "HIGH_TURNOVER_RISK": "Turnover may be unusually high and requires operator review.",
    "MARKET_CAP_TOO_SMALL_RISK": "Market capitalization may be too small for stable interpretation.",
    "DATA_QUALITY_LIMITED": "The upstream data quality was limited.",
    "MISSING_OPTIONAL_SIGNALS": "Optional enhancement signals were missing.",
    "PUBLIC_SIGNAL_WEAK": "Public signal strength was weak.",
    "NO_FUND_FLOW_CONFIRMATION": "No public fund-flow confirmation was available.",
    "OPERATOR_REVIEW_REQUIRED": "Human operator review is required before any use.",
}


def _copy_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("expected a list")
    return list(value)


def _copy_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("expected a dict")
    return dict(value)


def explain_reason_code(code: str) -> dict[str, Any]:
    return {
        "code": code,
        "known": code in REASON_CODE_EXPLANATIONS,
        "explanation": REASON_CODE_EXPLANATIONS.get(
            code,
            "Unknown reason code. AI-CONTEXT must not invent a new reason.",
        ),
    }


def explain_risk_flag(flag: str) -> dict[str, Any]:
    return {
        "flag": flag,
        "known": flag in RISK_FLAG_EXPLANATIONS,
        "explanation": RISK_FLAG_EXPLANATIONS.get(
            flag,
            "Unknown risk flag. AI-CONTEXT must preserve it and require review.",
        ),
    }


def build_candidate_explanation(candidate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        raise ValueError("candidate must be a dict")
    if not candidate.get("symbol"):
        raise ValueError("candidate.symbol is required")

    reason_codes = _copy_list(candidate.get("reason_codes"))
    risk_flags = _copy_list(candidate.get("risk_flags"))
    score_breakdown = _copy_dict(candidate.get("score_breakdown"))

    return {
        "contract_version": CONTRACT_VERSION,
        "symbol": candidate.get("symbol"),
        "name": candidate.get("name", ""),
        "rank": candidate.get("rank"),
        "potential_level": candidate.get("potential_level"),
        "limit_up_potential_score": candidate.get("limit_up_potential_score"),
        "score_breakdown": score_breakdown,
        "reason_codes": reason_codes,
        "risk_flags": risk_flags,
        "reason_explanations": [explain_reason_code(code) for code in reason_codes],
        "risk_explanations": [explain_risk_flag(flag) for flag in risk_flags],
        "data_quality_state": candidate.get("data_quality_state"),
        "confidence_level": candidate.get("confidence_level"),
        "data_sources": _copy_list(candidate.get("data_sources")),
        "operator_review_required": True,
        "ai_context_summary": "Read-only explanation generated from deterministic sidecar fields.",
        **READ_ONLY_SAFETY,
    }


def validate_no_ai_mutation(candidate: dict[str, Any], explanation: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "score_preserved": candidate.get("limit_up_potential_score") == explanation.get("limit_up_potential_score"),
        "score_breakdown_preserved": _copy_dict(candidate.get("score_breakdown")) == explanation.get("score_breakdown"),
        "reason_codes_preserved": _copy_list(candidate.get("reason_codes")) == explanation.get("reason_codes"),
        "risk_flags_preserved": _copy_list(candidate.get("risk_flags")) == explanation.get("risk_flags"),
        "operator_review_required": explanation.get("operator_review_required") is True,
        "buy_sell_instruction_blocked": explanation.get("buy_sell_instruction_allowed") is False,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        **READ_ONLY_SAFETY,
    }


def build_ai_context_report(stock_app_contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(stock_app_contract, dict):
        raise ValueError("stock_app_contract must be a dict")

    candidates = _copy_list(stock_app_contract.get("ranked_watchlist"))
    explanations = [build_candidate_explanation(candidate) for candidate in candidates]
    mutation_checks = [
        validate_no_ai_mutation(candidate, explanation)
        for candidate, explanation in zip(candidates, explanations)
    ]

    return {
        "app": "AI-CONTEXT",
        "contract_version": CONTRACT_VERSION,
        "source_app": stock_app_contract.get("app", "STOCK-APP"),
        "source_contract_version": stock_app_contract.get("contract_version"),
        "market": stock_app_contract.get("market"),
        "trade_date": stock_app_contract.get("trade_date"),
        "input_manifest_id": stock_app_contract.get("input_manifest_id"),
        "candidate_count": len(explanations),
        "candidate_explanations": explanations,
        "mutation_guard": {
            "ok": all(item["ok"] for item in mutation_checks),
            "checks": mutation_checks,
        },
        "operator_review_summary": {
            "operator_review_required": True,
            "candidate_count": len(explanations),
            "high_potential_count": sum(
                1 for item in explanations if item.get("potential_level") == "HIGH_POTENTIAL"
            ),
            "risk_flag_count": sum(len(item.get("risk_flags", [])) for item in explanations),
            "no_buy_sell_instruction": True,
            "no_limit_up_guarantee": True,
        },
        **READ_ONLY_SAFETY,
    }
