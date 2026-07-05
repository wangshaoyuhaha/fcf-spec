"""STOCK-APP-D1 base candidate filter contract.

This module filters DATA-APP A-share records into a base candidate pool.
It is sidecar-only and does not import the frozen FCF core.
"""

REJECTED = "REJECTED"
WATCH_ONLY = "WATCH_ONLY"
BASE_CANDIDATE = "BASE_CANDIDATE"

REQUIRED_FIELDS = (
    "symbol",
    "name",
    "trading_status",
    "is_st",
    "listing_days",
    "turnover_rate",
    "amount",
    "close",
    "limit_up_price",
    "data_quality_state",
)

PASS_STRICT = "PASS_STRICT"
PASS_LIMITED = "PASS_LIMITED"
FAIL_QUARANTINE = "FAIL_QUARANTINE"

TRADING_ACTIVE_VALUES = {"TRADING", "ACTIVE", "OPEN"}


def _missing_required_fields(record):
    return [field for field in REQUIRED_FIELDS if field not in record]


def _as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def evaluate_base_candidate(record):
    """Evaluate one stock record and return a base filter decision."""
    missing = _missing_required_fields(record)
    reason_codes = []
    risk_flags = []

    if missing:
        return {
            "symbol": record.get("symbol"),
            "name": record.get("name"),
            "decision": REJECTED,
            "base_filter_pass": False,
            "reason_codes": ["MISSING_REQUIRED_FIELDS"],
            "risk_flags": ["DATA_QUALITY_LIMITED"],
            "excluded_reasons": ["missing_required_fields"],
            "missing_fields": missing,
            "data_quality_state": record.get("data_quality_state"),
            "operator_review_required": True,
            "paper_only": True,
            "real_action_blocked": True,
        }

    symbol = str(record.get("symbol", "")).strip().upper()
    name = str(record.get("name", "")).strip()
    data_quality_state = record.get("data_quality_state")
    trading_status = str(record.get("trading_status", "")).strip().upper()
    is_st = bool(record.get("is_st"))
    listing_days = _as_int(record.get("listing_days"))
    turnover_rate = _as_float(record.get("turnover_rate"))
    amount = _as_float(record.get("amount"))
    close = _as_float(record.get("close"))
    limit_up_price = _as_float(record.get("limit_up_price"))

    excluded_reasons = []

    if data_quality_state == FAIL_QUARANTINE:
        excluded_reasons.append("fail_quarantine")
        risk_flags.append("DATA_QUALITY_QUARANTINE")
    elif data_quality_state == PASS_LIMITED:
        reason_codes.append("DATA_QUALITY_PASS_LIMITED")
        risk_flags.append("DATA_QUALITY_LIMITED")
    elif data_quality_state == PASS_STRICT:
        reason_codes.append("DATA_QUALITY_PASS_STRICT")
    else:
        excluded_reasons.append("unknown_data_quality_state")
        risk_flags.append("DATA_QUALITY_LIMITED")

    if is_st:
        excluded_reasons.append("st_or_risk_warning")
        risk_flags.append("IS_ST_OR_RISK_WARNING")
    else:
        reason_codes.append("NOT_ST_STOCK")

    if trading_status not in TRADING_ACTIVE_VALUES:
        excluded_reasons.append("not_trading_active")
        risk_flags.append("SUSPENDED_OR_NOT_TRADING")
    else:
        reason_codes.append("TRADING_ACTIVE")

    if listing_days < 60:
        excluded_reasons.append("listing_days_too_short")
        risk_flags.append("NEW_LISTING_RISK")
    else:
        reason_codes.append("LISTING_DAYS_OK")

    if turnover_rate <= 0 or amount <= 0:
        excluded_reasons.append("low_liquidity")
        risk_flags.append("LOW_LIQUIDITY_RISK")
    else:
        reason_codes.append("LIQUIDITY_OK")

    if close <= 0 or limit_up_price <= 0:
        excluded_reasons.append("price_abnormal")
        risk_flags.append("PRICE_ABNORMAL_RISK")

    if excluded_reasons:
        decision = REJECTED
        base_filter_pass = False
    elif data_quality_state == PASS_LIMITED:
        decision = WATCH_ONLY
        base_filter_pass = True
    else:
        decision = BASE_CANDIDATE
        base_filter_pass = True

    return {
        "symbol": symbol,
        "name": name,
        "decision": decision,
        "base_filter_pass": base_filter_pass,
        "reason_codes": sorted(set(reason_codes)),
        "risk_flags": sorted(set(risk_flags)),
        "excluded_reasons": excluded_reasons,
        "missing_fields": [],
        "data_quality_state": data_quality_state,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }


def build_base_candidate_pool(records):
    """Build base candidate, watch-only, and rejected pools."""
    evaluations = [evaluate_base_candidate(record) for record in records]
    base_candidates = [item for item in evaluations if item["decision"] == BASE_CANDIDATE]
    watch_only = [item for item in evaluations if item["decision"] == WATCH_ONLY]
    rejected = [item for item in evaluations if item["decision"] == REJECTED]

    return {
        "app": "STOCK-APP",
        "contract_version": "STOCK_APP_BASE_FILTER_V1",
        "stage": "STOCK-APP-D1",
        "input_count": len(records),
        "base_candidate_count": len(base_candidates),
        "watch_only_count": len(watch_only),
        "rejected_count": len(rejected),
        "base_candidates": base_candidates,
        "watch_only": watch_only,
        "rejected": rejected,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }
