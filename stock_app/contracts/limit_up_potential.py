"""STOCK-APP-D5 limit-up potential scoring contract.

This module combines sidecar rule outputs into a ranked potential score.
It does not generate buy or sell instructions and does not guarantee limit-up.
"""

from stock_app.contracts.base_candidate_filter import BASE_CANDIDATE
from stock_app.contracts.base_candidate_filter import REJECTED
from stock_app.contracts.base_candidate_filter import WATCH_ONLY
from stock_app.contracts.base_candidate_filter import evaluate_base_candidate
from stock_app.contracts.fund_flow_proxy import evaluate_public_fund_flow_proxy
from stock_app.contracts.sector_theme_linkage import evaluate_sector_theme_linkage
from stock_app.contracts.volume_price_anomaly import evaluate_volume_price_anomaly

PASS_STRICT = "PASS_STRICT"
PASS_LIMITED = "PASS_LIMITED"
FAIL_QUARANTINE = "FAIL_QUARANTINE"

HIGH_POTENTIAL = "HIGH_POTENTIAL"
MEDIUM_POTENTIAL = "MEDIUM_POTENTIAL"
LOW_POTENTIAL = "LOW_POTENTIAL"
WATCH_ONLY_LEVEL = "WATCH_ONLY"
REJECTED_LEVEL = "REJECTED"


def _clamp_score(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number < 0:
        return 0.0
    if number > 100:
        return 100.0
    return number


def _merge_unique(*lists):
    result = []
    seen = set()
    for items in lists:
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
    return sorted(result)


def _risk_penalty(risk_flags):
    penalty = 0
    heavy = {
        "DATA_QUALITY_QUARANTINE",
        "IS_ST_OR_RISK_WARNING",
        "SUSPENDED_OR_NOT_TRADING",
        "PRICE_ABNORMAL_RISK",
    }
    medium = {
        "DATA_QUALITY_LIMITED",
        "LOW_LIQUIDITY_RISK",
        "HIGH_TURNOVER_RISK",
        "LIMIT_UP_TOO_CLOSE_RISK",
        "PASS_LIMITED_CANNOT_HIGH_RANK",
    }
    for flag in set(risk_flags):
        if flag in heavy:
            penalty += 20
        elif flag in medium:
            penalty += 8
        else:
            penalty += 3
    return min(penalty, 40)


def _potential_level(final_score, base_decision, data_quality_state):
    if base_decision == REJECTED or data_quality_state == FAIL_QUARANTINE:
        return REJECTED_LEVEL
    if base_decision == WATCH_ONLY or data_quality_state == PASS_LIMITED:
        return WATCH_ONLY_LEVEL
    if final_score >= 75:
        return HIGH_POTENTIAL
    if final_score >= 55:
        return MEDIUM_POTENTIAL
    if final_score >= 35:
        return LOW_POTENTIAL
    return WATCH_ONLY_LEVEL


def _confidence_level(final_score, potential_level, risk_flags):
    if potential_level == HIGH_POTENTIAL and final_score >= 75 and not risk_flags:
        return "HIGH"
    if potential_level in {HIGH_POTENTIAL, MEDIUM_POTENTIAL}:
        return "MEDIUM"
    if potential_level in {LOW_POTENTIAL, WATCH_ONLY_LEVEL}:
        return "LOW"
    return "INSUFFICIENT_DATA"


def evaluate_limit_up_potential(record):
    """Evaluate final limit-up potential score from sidecar rule outputs."""
    base = evaluate_base_candidate(record)
    sector = evaluate_sector_theme_linkage(record)
    volume_price = evaluate_volume_price_anomaly(record)
    fund_flow = evaluate_public_fund_flow_proxy(record)

    data_quality_state = record.get("data_quality_state")
    base_decision = base["decision"]

    data_quality_score = 15 if data_quality_state == PASS_STRICT else 8 if data_quality_state == PASS_LIMITED else 0
    base_filter_score = 15 if base_decision == BASE_CANDIDATE else 8 if base_decision == WATCH_ONLY else 0
    sector_theme_score = round(_clamp_score(sector["sector_theme_score"]) * 0.20, 2)
    volume_price_score = round(_clamp_score(volume_price["volume_price_score"]) * 0.25, 2)
    fund_flow_proxy_score = round(_clamp_score(fund_flow["fund_flow_proxy_score"]) * 0.20, 2)

    reason_codes = _merge_unique(
        base["reason_codes"],
        sector["reason_codes"],
        volume_price["reason_codes"],
        fund_flow["reason_codes"],
    )
    risk_flags = _merge_unique(
        base["risk_flags"],
        sector["risk_flags"],
        volume_price["risk_flags"],
        fund_flow["risk_flags"],
    )

    risk_penalty = _risk_penalty(risk_flags)
    raw_score = round(
        data_quality_score
        + base_filter_score
        + sector_theme_score
        + volume_price_score
        + fund_flow_proxy_score,
        2,
    )
    final_score = round(max(0.0, min(100.0, raw_score - risk_penalty)), 2)

    potential_level = _potential_level(final_score, base_decision, data_quality_state)

    if potential_level == WATCH_ONLY_LEVEL and "PASS_LIMITED_CANNOT_HIGH_RANK" not in risk_flags:
        if data_quality_state == PASS_LIMITED:
            risk_flags = sorted(set(risk_flags + ["PASS_LIMITED_CANNOT_HIGH_RANK"]))

    if potential_level == HIGH_POTENTIAL:
        reason_codes = sorted(set(reason_codes + ["LIMIT_UP_POTENTIAL_HIGH"]))
    elif potential_level == MEDIUM_POTENTIAL:
        reason_codes = sorted(set(reason_codes + ["LIMIT_UP_POTENTIAL_MEDIUM"]))
    elif potential_level == LOW_POTENTIAL:
        reason_codes = sorted(set(reason_codes + ["LIMIT_UP_POTENTIAL_LOW"]))

    score_breakdown = {
        "data_quality_score": data_quality_score,
        "base_filter_score": base_filter_score,
        "sector_theme_score": sector_theme_score,
        "volume_price_score": volume_price_score,
        "fund_flow_proxy_score": fund_flow_proxy_score,
        "risk_penalty": risk_penalty,
        "raw_score": raw_score,
        "final_score": final_score,
    }

    return {
        "symbol": base["symbol"],
        "name": base["name"],
        "limit_up_potential_score": final_score,
        "potential_level": potential_level,
        "score_breakdown": score_breakdown,
        "reason_codes": reason_codes,
        "risk_flags": risk_flags,
        "data_quality_state": data_quality_state,
        "confidence_level": _confidence_level(final_score, potential_level, risk_flags),
        "data_sources": record.get("data_sources", ["DATA-APP"]),
        "base_filter": base,
        "sector_theme": sector,
        "volume_price": volume_price,
        "fund_flow_proxy": fund_flow,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "guaranteed_limit_up_claim_allowed": False,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }


def build_limit_up_potential_package(records):
    """Build limit-up potential package for STOCK-APP ranked watchlist."""
    evaluations = [evaluate_limit_up_potential(record) for record in records]
    high = [item for item in evaluations if item["potential_level"] == HIGH_POTENTIAL]
    medium = [item for item in evaluations if item["potential_level"] == MEDIUM_POTENTIAL]
    low = [item for item in evaluations if item["potential_level"] == LOW_POTENTIAL]
    watch_only = [item for item in evaluations if item["potential_level"] == WATCH_ONLY_LEVEL]
    rejected = [item for item in evaluations if item["potential_level"] == REJECTED_LEVEL]

    return {
        "app": "STOCK-APP",
        "contract_version": "STOCK_APP_LIMIT_UP_POTENTIAL_V1",
        "stage": "STOCK-APP-D5",
        "input_count": len(records),
        "high_potential_count": len(high),
        "medium_potential_count": len(medium),
        "low_potential_count": len(low),
        "watch_only_count": len(watch_only),
        "rejected_count": len(rejected),
        "evaluations": evaluations,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "guaranteed_limit_up_claim_allowed": False,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }
