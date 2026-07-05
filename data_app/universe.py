"""DATA-APP-D6 Clean Universe and Quarantine Report.

Final DATA-APP-1 output layer.
Routes A-share rows into Clean Universe, Watchlist, or Quarantine.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from data_app.health_check import FAIL_QUARANTINE
from data_app.health_check import PASS_LIMITED
from data_app.health_check import PASS_STRICT
from data_app.health_check import build_data_app_health_check
from data_app.health_check import route_by_health_check_state
from data_app.local_file_adapter import build_local_file_adapter_result


def build_data_app_universe_contract() -> dict[str, Any]:
    return {
        "app": "DATA-APP",
        "contract_version": "DATA_APP_UNIVERSE_D6",
        "market": "A_SHARE",
        "outputs": ["clean_universe", "watchlist_only", "quarantine_report"],
        "allowed_states": [PASS_STRICT, PASS_LIMITED, FAIL_QUARANTINE],
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


def _build_quarantine_entries(
    adapter_result: dict[str, Any],
    reason_codes: list[str],
) -> list[dict[str, Any]]:
    entries = []

    for item in adapter_result.get("rejected_rows", []):
        entry = dict(item)
        entry["source"] = "schema_validation"
        entry["reason_codes"] = list(reason_codes)
        entries.append(entry)

    if entries:
        return entries

    for index, row in enumerate(adapter_result.get("accepted_rows", [])):
        entries.append({
            "source": "health_check",
            "row_index": index,
            "row": row,
            "reason_codes": list(reason_codes),
        })

    return entries


def build_data_app_universe_package(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)
    adapter = build_local_file_adapter_result(path)
    health = build_data_app_health_check(path)
    route = route_by_health_check_state(health)
    state = health["state"]

    clean_universe = []
    watchlist_only = []
    quarantine_report = []

    if state == PASS_STRICT:
        clean_universe = list(adapter["accepted_rows"])
    elif state == PASS_LIMITED:
        watchlist_only = list(adapter["accepted_rows"])
    else:
        quarantine_report = _build_quarantine_entries(adapter, health["reason_codes"])

    return {
        "app": "DATA-APP",
        "contract_version": "DATA_APP_UNIVERSE_D6",
        "market": "A_SHARE",
        "source_file": path.name,
        "manifest_id": health["manifest_id"],
        "checksum_sha256": health["checksum_sha256"],
        "data_quality_state": state,
        "destination": route["destination"],
        "ranking_allowed": route["ranking_allowed"],
        "row_count": adapter["row_count"],
        "accepted_count": adapter["accepted_count"],
        "rejected_count": adapter["rejected_count"],
        "clean_universe_count": len(clean_universe),
        "watchlist_only_count": len(watchlist_only),
        "quarantine_count": len(quarantine_report),
        "clean_universe": clean_universe,
        "watchlist_only": watchlist_only,
        "quarantine_report": quarantine_report,
        "health_check": health,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "api_key_required": False,
        "real_order_allowed": False,
        "real_execution_allowed": False,
        "real_money_impact_allowed": False,
    }


def write_data_app_universe_package(
    file_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    package = build_data_app_universe_package(file_path)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(package, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "app": "DATA-APP",
        "contract_version": "DATA_APP_UNIVERSE_WRITE_D6",
        "output_file": str(path),
        "package": package,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "operator_review_required": True,
        "real_order_allowed": False,
        "real_execution_allowed": False,
        "real_money_impact_allowed": False,
    }
