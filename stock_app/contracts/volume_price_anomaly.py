"""STOCK-APP-D3 volume-price anomaly rules.

This module detects short-term volume-price anomaly features.
It is sidecar-only and never creates buy or sell instructions.
"""

PASS_STRICT = "PASS_STRICT"
PASS_LIMITED = "PASS_LIMITED"
FAIL_QUARANTINE = "FAIL_QUARANTINE"

STRONG_ANOMALY = "STRONG_ANOMALY"
MEDIUM_ANOMALY = "MEDIUM_ANOMALY"
WEAK_ANOMALY = "WEAK_ANOMALY"
NO_ANOMALY = "NO_ANOMALY"


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


def _level_from_score(score):
    if score >= 75:
        return STRONG_ANOMALY
    if score >= 50:
        return MEDIUM_ANOMALY
    if score >= 25:
        return WEAK_ANOMALY
    return NO_ANOMALY


def _confidence_from_score(score, data_quality_state):
    if score >= 75 and data_quality_state == PASS_STRICT:
        return "HIGH"
    if score >= 50:
        return "MEDIUM"
    if score >= 25:
        return "LOW"
    return "INSUFFICIENT_DATA"


def evaluate_volume_price_anomaly(record):
    """Evaluate one candidate for volume-price anomaly signals."""
    symbol = str(record.get("symbol", "")).strip().upper()
    name = str(record.get("name", "")).strip()
    data_quality_state = record.get("data_quality_state")

    close = _as_float(record.get("close"))
    prev_close = _as_float(record.get("prev_close"))
    high = _as_float(record.get("high"))
    low = _as_float(record.get("low"))
    limit_up_price = _as_float(record.get("limit_up_price"))
    volume = _as_float(record.get("volume"))
    avg_volume_5d = _as_float(record.get("avg_volume_5d"))
    turnover_rate = _as_float(record.get("turnover_rate"))
    avg_turnover_5d = _as_float(record.get("avg_turnover_5d"))
    high_20d = _as_float(record.get("high_20d"))

    reason_codes = []
    risk_flags = []

    if data_quality_state == FAIL_QUARANTINE:
        return {
            "symbol": symbol,
            "name": name,
            "volume_price_score": 0.0,
            "volume_price_level": NO_ANOMALY,
            "price_change_pct": 0.0,
            "volume_expansion_ratio": 0.0,
            "turnover_expansion_ratio": 0.0,
            "reason_codes": [],
            "risk_flags": ["DATA_QUALITY_QUARANTINE"],
            "data_quality_state": data_quality_state,
            "confidence_level": "INSUFFICIENT_DATA",
            "operator_review_required": True,
            "paper_only": True,
            "real_action_blocked": True,
        }

    if close <= 0 or prev_close <= 0 or high <= 0 or low <= 0:
        risk_flags.append("PRICE_ABNORMAL_RISK")

    price_change_pct = 0.0
    if prev_close > 0:
        price_change_pct = round(((close - prev_close) / prev_close) * 100.0, 2)

    volume_expansion_ratio = 0.0
    if avg_volume_5d > 0:
        volume_expansion_ratio = round(volume / avg_volume_5d, 2)
    else:
        risk_flags.append("MISSING_VOLUME_BASELINE")

    turnover_expansion_ratio = 0.0
    if avg_turnover_5d > 0:
        turnover_expansion_ratio = round(turnover_rate / avg_turnover_5d, 2)
    else:
        risk_flags.append("MISSING_TURNOVER_BASELINE")

    score = 0.0

    if price_change_pct >= 7:
        score += 20
        reason_codes.append("PRICE_MOMENTUM_STRONG")
    elif price_change_pct >= 4:
        score += 14
        reason_codes.append("PRICE_MOMENTUM_POSITIVE")
    elif price_change_pct >= 2:
        score += 8
        reason_codes.append("PRICE_MOMENTUM_WEAK")

    if limit_up_price > 0 and close >= limit_up_price * 0.97:
        score += 20
        reason_codes.append("NEAR_LIMIT_UP_PRICE")

    if limit_up_price > 0 and close >= limit_up_price * 0.995:
        risk_flags.append("LIMIT_UP_TOO_CLOSE_RISK")

    if volume_expansion_ratio >= 2.0:
        score += 20
        reason_codes.append("VOLUME_EXPANSION")
    elif volume_expansion_ratio >= 1.5:
        score += 14
        reason_codes.append("VOLUME_EXPANSION_WEAK")

    if turnover_expansion_ratio >= 1.5:
        score += 15
        reason_codes.append("TURNOVER_EXPANSION")
    elif turnover_expansion_ratio >= 1.2:
        score += 10
        reason_codes.append("TURNOVER_EXPANSION_WEAK")

    if high > 0 and close >= high * 0.97:
        score += 10
        reason_codes.append("CLOSE_NEAR_HIGH")

    if high_20d > 0 and close >= high_20d * 0.98:
        score += 15
        reason_codes.append("PRICE_BREAKOUT")

    if turnover_rate >= 20:
        risk_flags.append("HIGH_TURNOVER_RISK")

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

    if final_score < 25:
        risk_flags.append("PUBLIC_SIGNAL_WEAK")

    if data_quality_state == PASS_LIMITED and final_score >= 50:
        risk_flags.append("PASS_LIMITED_CANNOT_HIGH_RANK")

    return {
        "symbol": symbol,
        "name": name,
        "volume_price_score": final_score,
        "volume_price_level": level,
        "price_change_pct": price_change_pct,
        "volume_expansion_ratio": volume_expansion_ratio,
        "turnover_expansion_ratio": turnover_expansion_ratio,
        "reason_codes": sorted(set(reason_codes)),
        "risk_flags": sorted(set(risk_flags)),
        "data_quality_state": data_quality_state,
        "confidence_level": _confidence_from_score(final_score, data_quality_state),
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }


def build_volume_price_anomaly_package(records):
    """Build volume-price anomaly package for STOCK-APP scoring."""
    evaluations = [evaluate_volume_price_anomaly(record) for record in records]
    strong = [item for item in evaluations if item["volume_price_level"] == STRONG_ANOMALY]
    medium = [item for item in evaluations if item["volume_price_level"] == MEDIUM_ANOMALY]
    weak = [item for item in evaluations if item["volume_price_level"] == WEAK_ANOMALY]
    none = [item for item in evaluations if item["volume_price_level"] == NO_ANOMALY]

    return {
        "app": "STOCK-APP",
        "contract_version": "STOCK_APP_VOLUME_PRICE_V1",
        "stage": "STOCK-APP-D3",
        "input_count": len(records),
        "strong_anomaly_count": len(strong),
        "medium_anomaly_count": len(medium),
        "weak_anomaly_count": len(weak),
        "no_anomaly_count": len(none),
        "evaluations": evaluations,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }

