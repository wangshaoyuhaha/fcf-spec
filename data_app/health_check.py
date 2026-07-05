"""DATA-APP-D5 Health_Check tri-state gate.

Health states:
- PASS_STRICT
- PASS_LIMITED
- FAIL_QUARANTINE

Read-only gate. No trading action. No core mutation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_app.local_file_adapter import build_local_file_adapter_result
from data_app.manifest import build_data_app_manifest_for_file
from data_app.manifest import validate_data_app_manifest


PASS_STRICT = "PASS_STRICT"
PASS_LIMITED = "PASS_LIMITED"
FAIL_QUARANTINE = "FAIL_QUARANTINE"


def _as_float(value: Any) -> float:
    return float(value)


def _price_sanity_ok(row: dict[str, Any]) -> bool:
    try:
        open_price = _as_float(row["open"])
        high = _as_float(row["high"])
        low = _as_float(row["low"])
        close = _as_float(row["close"])
        prev_close = _as_float(row["prev_close"])
        limit_up = _as_float(row["limit_up_price"])
        limit_down = _as_float(row["limit_down_price"])
    except (KeyError, TypeError, ValueError):
        return False

    if min(open_price, high, low, close, prev_close, limit_up, limit_down) <= 0:
        return False
    if high < max(open_price, close, low):
        return False
    if low > min(open_price, close, high):
        return False
    if limit_up <= prev_close:
        return False
    if limit_down >= prev_close:
        return False
    return True


def _liquidity_ok(row: dict[str, Any]) -> bool:
    try:
        amount = _as_float(row["amount"])
        volume = _as_float(row["volume"])
        turnover_rate = _as_float(row["turnover_rate"])
    except (KeyError, TypeError, ValueError):
        return False

    return amount > 0 and volume > 0 and turnover_rate >= 0


def _row_not_blocked(row: dict[str, Any]) -> bool:
    if bool(row.get("is_st")) is True:
        return False
    if str(row.get("trading_status", "")).strip().lower() != "trading":
        return False
    try:
        if int(row.get("listing_days", 0)) <= 0:
            return False
    except (TypeError, ValueError):
        return False
    return True


def build_data_app_health_check(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)
    adapter = build_local_file_adapter_result(path)
    manifest = build_data_app_manifest_for_file(path)
    manifest_validation = validate_data_app_manifest(manifest)
    rows = adapter["accepted_rows"]

    dates = {str(row.get("date")) for row in rows}
    required_fields_ok = adapter["ok"] is True
    manifest_ok = manifest_validation["ok"] is True
    has_rows = adapter["row_count"] > 0
    no_rejected_rows = adapter["rejected_count"] == 0
    date_consistency_ok = len(dates) == 1 and "" not in dates
    price_sanity_ok = all(_price_sanity_ok(row) for row in rows) if rows else False
    liquidity_ok = all(_liquidity_ok(row) for row in rows) if rows else False
    trading_status_ok = all(_row_not_blocked(row) for row in rows) if rows else False

    hard_checks = {
        "manifest_ok": manifest_ok,
        "has_rows": has_rows,
        "required_fields_ok": required_fields_ok,
        "no_rejected_rows": no_rejected_rows,
        "date_consistency_ok": date_consistency_ok,
        "price_sanity_ok": price_sanity_ok,
        "liquidity_ok": liquidity_ok,
        "trading_status_ok": trading_status_ok,
    }

    if all(hard_checks.values()):
        state = PASS_STRICT
    elif manifest_ok and has_rows and required_fields_ok and price_sanity_ok:
        state = PASS_LIMITED
    else:
        state = FAIL_QUARANTINE

    reason_codes = []
    if state == PASS_STRICT:
        reason_codes.extend(["DATA_OK", "LIQUIDITY_OK", "PRICE_SANITY_OK"])
    if not required_fields_ok:
        reason_codes.append("REQUIRED_FIELDS_FAILED")
    if not date_consistency_ok:
        reason_codes.append("DATA_DATE_MISMATCH")
    if not price_sanity_ok:
        reason_codes.append("PRICE_SANITY_FAILED")
    if not liquidity_ok:
        reason_codes.append("LOW_LIQUIDITY")
    if not trading_status_ok:
        reason_codes.append("TRADING_STATUS_BLOCKED")

    return {
        "app": "DATA-APP",
        "contract_version": "DATA_APP_HEALTH_CHECK_D5",
        "market": "A_SHARE",
        "source_file": path.name,
        "manifest_id": manifest["manifest_id"],
        "checksum_sha256": manifest["checksum_sha256"],
        "state": state,
        "row_count": adapter["row_count"],
        "accepted_count": adapter["accepted_count"],
        "rejected_count": adapter["rejected_count"],
        "hard_checks": hard_checks,
        "reason_codes": reason_codes,
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


def route_by_health_check_state(health_check: dict[str, Any]) -> dict[str, Any]:
    state = health_check.get("state")
    if state == PASS_STRICT:
        destination = "CLEAN_UNIVERSE"
        ranking_allowed = True
    elif state == PASS_LIMITED:
        destination = "WATCHLIST_ONLY"
        ranking_allowed = False
    elif state == FAIL_QUARANTINE:
        destination = "QUARANTINE"
        ranking_allowed = False
    else:
        destination = "QUARANTINE"
        ranking_allowed = False

    return {
        "app": "DATA-APP",
        "contract_version": "DATA_APP_HEALTH_ROUTE_D5",
        "state": state,
        "destination": destination,
        "ranking_allowed": ranking_allowed,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "real_order_allowed": False,
        "real_execution_allowed": False,
        "real_money_impact_allowed": False,
    }
