"""STOCK-APP-D4 public fund-flow proxy inference.

This module infers public fund-flow direction from public signals only.
It cannot claim hidden positions, insider flows, or guaranteed institutional buying.
"""

PASS_STRICT = "PASS_STRICT"
PASS_LIMITED = "PASS_LIMITED"
FAIL_QUARANTINE = "FAIL_QUARANTINE"

STRONG_PUBLIC_FLOW = "STRONG_PUBLIC_FLOW"
MEDIUM_PUBLIC_FLOW = "MEDIUM_PUBLIC_FLOW"
WEAK_PUBLIC_FLOW = "WEAK_PUBLIC_FLOW"
NO_PUBLIC_FLOW = "NO_PUBLIC_FLOW"


def _as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp_score(value):
    number = _as_float(value)
    if number < 0:
        return 0.0
    if number > 100:
        return 100.0
    return number


def _is_positive_signal(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "positive", "detected"}
    return False


def _level_from_score(score):
    if score >= 75:
        return STRONG_PUBLIC_FLOW
    if score >= 50:
        return MEDIUM_PUBLIC_FLOW
    if score >= 25:
        return WEAK_PUBLIC_FLOW
    return NO_PUBLIC_FLOW


def _confidence_from_score(score, data_quality_state):
    if score >= 75 and data_quality_state == PASS_STRICT:
        return "HIGH"
    if score >= 50:
        return "MEDIUM"
    if score >= 25:
        return "LOW"
    return "INSUFFICIENT_DATA"


def evaluate_public_fund_flow_proxy(record):
    """Evaluate public fund-flow proxy signals for one stock record."""
    symbol = str(record.get("symbol", "")).strip().upper()
    name = str(record.get("name", "")).strip()
    data_quality_state = record.get("data_quality_state")

    dragon_tiger_signal = _is_positive_signal(record.get("dragon_tiger_signal"))
    northbound_flow_score = _clamp_score(record.get("northbound_flow_score"))
    etf_flow_score = _clamp_score(record.get("etf_flow_score"))
    large_trade_proxy_score = _clamp_score(record.get("large_trade_proxy_score"))
    amount_expansion_score = _clamp_score(record.get("amount_expansion_score"))
    sector_fund_heat_score = _clamp_score(record.get("sector_fund_heat_score"))

    reason_codes = []
    risk_flags = []

    if data_quality_state == FAIL_QUARANTINE:
        return {
            "symbol": symbol,
            "name": name,
            "fund_flow_proxy_score": 0.0,
            "fund_flow_proxy_level": NO_PUBLIC_FLOW,
            "reason_codes": [],
            "risk_flags": ["DATA_QUALITY_QUARANTINE"],
            "data_quality_state": data_quality_state,
            "confidence_level": "INSUFFICIENT_DATA",
            "public_signal_only": True,
            "hidden_position_claim_allowed": False,
            "operator_review_required": True,
            "paper_only": True,
            "real_action_blocked": True,
        }

    score = 0.0

    if dragon_tiger_signal:
        score += 20
        reason_codes.append("DRAGON_TIGER_SIGNAL")
    else:
        risk_flags.append("NO_DRAGON_TIGER_CONFIRMATION")

    if northbound_flow_score >= 60:
        score += 18
        reason_codes.append("NORTHBOUND_SIGNAL")
    elif northbound_flow_score > 0:
        score += 8
        reason_codes.append("NORTHBOUND_SIGNAL_WEAK")

    if etf_flow_score >= 60:
        score += 14
        reason_codes.append("ETF_FLOW_SIGNAL")
    elif etf_flow_score > 0:
        score += 6
        reason_codes.append("ETF_FLOW_SIGNAL_WEAK")

    if large_trade_proxy_score >= 60:
        score += 20
        reason_codes.append("LARGE_TRADE_PROXY_SIGNAL")
    elif large_trade_proxy_score > 0:
        score += 8
        reason_codes.append("LARGE_TRADE_PROXY_WEAK")

    if amount_expansion_score >= 60:
        score += 14
        reason_codes.append("AMOUNT_EXPANSION_SIGNAL")
    elif amount_expansion_score > 0:
        score += 6
        reason_codes.append("AMOUNT_EXPANSION_WEAK")

    if sector_fund_heat_score >= 60:
        score += 14
        reason_codes.append("SECTOR_FUND_HEAT_SIGNAL")
    elif sector_fund_heat_score > 0:
        score += 6
        reason_codes.append("SECTOR_FUND_HEAT_WEAK")

    if score > 0:
        reason_codes.append("FUND_FLOW_PROXY_POSITIVE")
    else:
        risk_flags.append("NO_FUND_FLOW_CONFIRMATION")

    if data_quality_state == PASS_STRICT:
        reason_codes.append("DATA_QUALITY_PASS_STRICT")
        data_quality_factor = 1.0
    elif data_quality_state == PASS_LIMITED:
        reason_codes.append("DATA_QUALITY_PASS_LIMITED")
        risk_flags.append("DATA_QUALITY_LIMITED")
        data_quality_factor = 0.75
    else:
        risk_flags.append("DATA_QUALITY_LIMITED")
        data_quality_factor = 0.5

    final_score = round(_clamp_score(score) * data_quality_factor, 2)
    level = _level_from_score(final_score)

    if data_quality_state == PASS_LIMITED and level == STRONG_PUBLIC_FLOW:
        level = MEDIUM_PUBLIC_FLOW

    if final_score < 25:
        risk_flags.append("PUBLIC_SIGNAL_WEAK")

    if data_quality_state == PASS_LIMITED and final_score >= 50:
        risk_flags.append("PASS_LIMITED_CANNOT_HIGH_RANK")

    return {
        "symbol": symbol,
        "name": name,
        "fund_flow_proxy_score": final_score,
        "fund_flow_proxy_level": level,
        "dragon_tiger_signal": dragon_tiger_signal,
        "northbound_flow_score": northbound_flow_score,
        "etf_flow_score": etf_flow_score,
        "large_trade_proxy_score": large_trade_proxy_score,
        "amount_expansion_score": amount_expansion_score,
        "sector_fund_heat_score": sector_fund_heat_score,
        "reason_codes": sorted(set(reason_codes)),
        "risk_flags": sorted(set(risk_flags)),
        "data_quality_state": data_quality_state,
        "confidence_level": _confidence_from_score(final_score, data_quality_state),
        "public_signal_only": True,
        "hidden_position_claim_allowed": False,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }


def build_public_fund_flow_proxy_package(records):
    """Build public fund-flow proxy package for STOCK-APP scoring."""
    evaluations = [evaluate_public_fund_flow_proxy(record) for record in records]
    strong = [item for item in evaluations if item["fund_flow_proxy_level"] == STRONG_PUBLIC_FLOW]
    medium = [item for item in evaluations if item["fund_flow_proxy_level"] == MEDIUM_PUBLIC_FLOW]
    weak = [item for item in evaluations if item["fund_flow_proxy_level"] == WEAK_PUBLIC_FLOW]
    none = [item for item in evaluations if item["fund_flow_proxy_level"] == NO_PUBLIC_FLOW]

    return {
        "app": "STOCK-APP",
        "contract_version": "STOCK_APP_FUND_FLOW_PROXY_V1",
        "stage": "STOCK-APP-D4",
        "input_count": len(records),
        "strong_public_flow_count": len(strong),
        "medium_public_flow_count": len(medium),
        "weak_public_flow_count": len(weak),
        "no_public_flow_count": len(none),
        "evaluations": evaluations,
        "public_signal_only": True,
        "hidden_position_claim_allowed": False,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }
