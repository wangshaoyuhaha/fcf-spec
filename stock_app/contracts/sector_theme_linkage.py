"""STOCK-APP-D2 sector and theme linkage contract.

This module scores sector and theme linkage for sidecar stock screening.
It does not import the frozen FCF core and does not create trade signals.
"""

PASS_STRICT = "PASS_STRICT"
PASS_LIMITED = "PASS_LIMITED"
FAIL_QUARANTINE = "FAIL_QUARANTINE"

STRONG_LINKAGE = "STRONG_LINKAGE"
MEDIUM_LINKAGE = "MEDIUM_LINKAGE"
WEAK_LINKAGE = "WEAK_LINKAGE"
NO_LINKAGE = "NO_LINKAGE"


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


def _normalize_theme_tags(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _level_from_score(score):
    if score >= 75:
        return STRONG_LINKAGE
    if score >= 50:
        return MEDIUM_LINKAGE
    if score >= 25:
        return WEAK_LINKAGE
    return NO_LINKAGE


def evaluate_sector_theme_linkage(record):
    """Evaluate one candidate record for sector and theme linkage."""
    symbol = str(record.get("symbol", "")).strip().upper()
    name = str(record.get("name", "")).strip()
    data_quality_state = record.get("data_quality_state")
    sector_code = str(record.get("sector_code", "")).strip()
    sector_name = str(record.get("sector_name", "")).strip()
    theme_tags = _normalize_theme_tags(record.get("theme_tags"))

    sector_strength_score = _clamp_score(record.get("sector_strength_score"))
    theme_heat_score = _clamp_score(record.get("theme_heat_score"))
    market_breadth_score = _clamp_score(record.get("market_breadth_score"))

    reason_codes = []
    risk_flags = []

    if data_quality_state == FAIL_QUARANTINE:
        return {
            "symbol": symbol,
            "name": name,
            "sector_code": sector_code,
            "sector_name": sector_name,
            "theme_tags": theme_tags,
            "sector_theme_score": 0.0,
            "sector_theme_level": NO_LINKAGE,
            "reason_codes": [],
            "risk_flags": ["DATA_QUALITY_QUARANTINE"],
            "data_quality_state": data_quality_state,
            "confidence_level": "INSUFFICIENT_DATA",
            "operator_review_required": True,
            "paper_only": True,
            "real_action_blocked": True,
        }

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

    if sector_code and sector_name:
        reason_codes.append("SECTOR_INFO_PRESENT")
    else:
        risk_flags.append("MISSING_SECTOR_INFO")

    if theme_tags:
        reason_codes.append("THEME_TAGS_PRESENT")
    else:
        risk_flags.append("MISSING_THEME_TAGS")

    if sector_strength_score >= 60:
        reason_codes.append("SECTOR_ACTIVE")
    if theme_heat_score >= 60:
        reason_codes.append("THEME_HEAT_DETECTED")
    if market_breadth_score >= 60:
        reason_codes.append("SECTOR_BREADTH_POSITIVE")

    raw_score = (
        sector_strength_score * 0.40
        + theme_heat_score * 0.35
        + market_breadth_score * 0.25
    )
    final_score = round(raw_score * data_quality_factor, 2)
    level = _level_from_score(final_score)

    if final_score >= 75 and theme_tags and sector_code:
        reason_codes.append("THEME_LINKAGE_CONFIRMED")
    if final_score < 25:
        risk_flags.append("PUBLIC_SIGNAL_WEAK")

    if data_quality_state == PASS_LIMITED and final_score >= 75:
        risk_flags.append("PASS_LIMITED_CANNOT_HIGH_RANK")

    if final_score >= 75 and data_quality_state == PASS_STRICT:
        confidence_level = "HIGH"
    elif final_score >= 50:
        confidence_level = "MEDIUM"
    elif final_score >= 25:
        confidence_level = "LOW"
    else:
        confidence_level = "INSUFFICIENT_DATA"

    return {
        "symbol": symbol,
        "name": name,
        "sector_code": sector_code,
        "sector_name": sector_name,
        "theme_tags": theme_tags,
        "sector_strength_score": sector_strength_score,
        "theme_heat_score": theme_heat_score,
        "market_breadth_score": market_breadth_score,
        "sector_theme_score": final_score,
        "sector_theme_level": level,
        "reason_codes": sorted(set(reason_codes)),
        "risk_flags": sorted(set(risk_flags)),
        "data_quality_state": data_quality_state,
        "confidence_level": confidence_level,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }


def build_sector_theme_linkage_package(records):
    """Build sector/theme linkage package for STOCK-APP scoring."""
    evaluations = [evaluate_sector_theme_linkage(record) for record in records]
    strong = [item for item in evaluations if item["sector_theme_level"] == STRONG_LINKAGE]
    medium = [item for item in evaluations if item["sector_theme_level"] == MEDIUM_LINKAGE]
    weak = [item for item in evaluations if item["sector_theme_level"] == WEAK_LINKAGE]
    none = [item for item in evaluations if item["sector_theme_level"] == NO_LINKAGE]

    return {
        "app": "STOCK-APP",
        "contract_version": "STOCK_APP_SECTOR_THEME_V1",
        "stage": "STOCK-APP-D2",
        "input_count": len(records),
        "strong_linkage_count": len(strong),
        "medium_linkage_count": len(medium),
        "weak_linkage_count": len(weak),
        "no_linkage_count": len(none),
        "evaluations": evaluations,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }
