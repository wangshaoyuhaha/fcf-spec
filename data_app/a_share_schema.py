"""DATA-APP-D2 A-share minimum schema.

Read-only schema contract for A-share daily candidate universe input.
No trading action, no broker API, no exchange API, no API key.
"""

from __future__ import annotations

from typing import Any


REQUIRED_MARKET_FIELDS = (
    "date",
    "symbol",
    "name",
    "open",
    "high",
    "low",
    "close",
    "prev_close",
    "volume",
    "amount",
)

REQUIRED_STATUS_FIELDS = (
    "turnover_rate",
    "float_market_cap",
    "total_market_cap",
    "listing_days",
    "is_st",
)

REQUIRED_RISK_SECTOR_FIELDS = (
    "limit_up_price",
    "limit_down_price",
    "sector_code",
    "sector_name",
    "trading_status",
)

OPTIONAL_ENRICHMENT_FIELDS = (
    "dragon_tiger_list",
    "announcement_summary",
    "research_summary",
    "northbound_flow",
    "etf_flow",
    "fund_flow_proxy",
    "news_catalyst",
    "limit_up_history",
)

REQUIRED_A_SHARE_FIELDS = (
    *REQUIRED_MARKET_FIELDS,
    *REQUIRED_STATUS_FIELDS,
    *REQUIRED_RISK_SECTOR_FIELDS,
)

NUMERIC_FIELDS = (
    "open",
    "high",
    "low",
    "close",
    "prev_close",
    "volume",
    "amount",
    "turnover_rate",
    "float_market_cap",
    "total_market_cap",
    "listing_days",
    "limit_up_price",
    "limit_down_price",
)


def build_a_share_schema_contract() -> dict[str, Any]:
    return {
        "app": "DATA-APP",
        "contract_version": "DATA_APP_A_SHARE_SCHEMA_D2",
        "market": "A_SHARE",
        "schema_version": "a_share_daily_v1",
        "required_market_fields": list(REQUIRED_MARKET_FIELDS),
        "required_status_fields": list(REQUIRED_STATUS_FIELDS),
        "required_risk_sector_fields": list(REQUIRED_RISK_SECTOR_FIELDS),
        "required_fields": list(REQUIRED_A_SHARE_FIELDS),
        "optional_enrichment_fields": list(OPTIONAL_ENRICHMENT_FIELDS),
        "numeric_fields": list(NUMERIC_FIELDS),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "operator_review_required": True,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "api_key_required": False,
        "real_order_allowed": False,
        "real_execution_allowed": False,
        "real_money_impact_allowed": False,
    }


def validate_a_share_required_fields(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("row must be a dict")

    missing = [field for field in REQUIRED_A_SHARE_FIELDS if field not in row]
    empty = [
        field
        for field in REQUIRED_A_SHARE_FIELDS
        if field in row and row[field] in ("", None)
    ]

    return {
        "ok": not missing and not empty,
        "market": "A_SHARE",
        "schema_version": "a_share_daily_v1",
        "missing_required_fields": missing,
        "empty_required_fields": empty,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "operator_review_required": True,
    }


def validate_a_share_numeric_fields(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("row must be a dict")

    invalid = []
    for field in NUMERIC_FIELDS:
        if field not in row:
            continue
        try:
            value = float(row[field])
        except (TypeError, ValueError):
            invalid.append(field)
            continue
        if value < 0:
            invalid.append(field)

    return {
        "ok": not invalid,
        "invalid_numeric_fields": invalid,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "operator_review_required": True,
    }


def validate_a_share_schema_row(row: dict[str, Any]) -> dict[str, Any]:
    required = validate_a_share_required_fields(row)
    numeric = validate_a_share_numeric_fields(row)

    return {
        "ok": required["ok"] and numeric["ok"],
        "market": "A_SHARE",
        "schema_version": "a_share_daily_v1",
        "required": required,
        "numeric": numeric,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "operator_review_required": True,
        "real_order_allowed": False,
        "real_execution_allowed": False,
        "real_money_impact_allowed": False,
    }
