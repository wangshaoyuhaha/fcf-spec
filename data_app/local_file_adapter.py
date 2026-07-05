"""DATA-APP-D3 local file adapter.

Read-only CSV and JSON file adapter for A-share DATA-APP input.
Excel is reserved but not enabled in D3 to avoid implicit dependencies.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from data_app.a_share_schema import NUMERIC_FIELDS
from data_app.a_share_schema import validate_a_share_schema_row


ACTIVE_INPUT_TYPES = ("csv", "json")
RESERVED_INPUT_TYPES = ("excel",)


def build_local_file_adapter_contract() -> dict[str, Any]:
    return {
        "app": "DATA-APP",
        "contract_version": "DATA_APP_LOCAL_FILE_ADAPTER_D3",
        "market": "A_SHARE",
        "active_input_types": list(ACTIVE_INPUT_TYPES),
        "reserved_input_types": list(RESERVED_INPUT_TYPES),
        "excel_enabled": False,
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


def _require_file_path(file_path: str | Path) -> Path:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"local file not found: {path}")
    if not path.is_file():
        raise ValueError(f"local path is not a file: {path}")
    return path


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes", "y", "st")
    return bool(value)


def normalize_a_share_file_row(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("row must be a dict")

    normalized: dict[str, Any] = {}
    for key, value in row.items():
        clean_key = str(key).strip()
        if isinstance(value, str):
            value = value.strip()
        normalized[clean_key] = value

    for field in NUMERIC_FIELDS:
        if field in normalized and normalized[field] not in ("", None):
            if field == "listing_days":
                normalized[field] = int(float(normalized[field]))
            else:
                normalized[field] = float(normalized[field])

    if "is_st" in normalized:
        normalized["is_st"] = _parse_bool(normalized["is_st"])

    if "symbol" in normalized:
        normalized["symbol"] = str(normalized["symbol"]).strip().upper()

    return normalized


def load_a_share_rows_from_csv(file_path: str | Path) -> list[dict[str, Any]]:
    path = _require_file_path(file_path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [normalize_a_share_file_row(row) for row in csv.DictReader(handle)]
    if not rows:
        raise ValueError("csv file must not be empty")
    return rows


def load_a_share_rows_from_json(file_path: str | Path) -> list[dict[str, Any]]:
    path = _require_file_path(file_path)
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(raw, dict) and "rows" in raw:
        raw = raw["rows"]
    elif isinstance(raw, dict) and "items" in raw:
        raw = raw["items"]
    elif isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raise ValueError("json file must be a list, object, or object with rows/items")
    rows = [normalize_a_share_file_row(row) for row in raw]
    if not rows:
        raise ValueError("json file must not be empty")
    return rows


def load_a_share_rows_from_local_file(file_path: str | Path) -> list[dict[str, Any]]:
    path = _require_file_path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_a_share_rows_from_csv(path)
    if suffix == ".json":
        return load_a_share_rows_from_json(path)
    if suffix in (".xls", ".xlsx"):
        raise ValueError("excel input is reserved but not enabled in DATA-APP-D3")
    raise ValueError(f"unsupported local file type: {suffix}")


def build_local_file_adapter_result(file_path: str | Path) -> dict[str, Any]:
    path = _require_file_path(file_path)
    rows = load_a_share_rows_from_local_file(path)
    accepted_rows = []
    rejected_rows = []
    for index, row in enumerate(rows):
        validation = validate_a_share_schema_row(row)
        if validation["ok"] is True:
            accepted_rows.append(row)
        else:
            rejected_rows.append({
                "row_index": index,
                "validation": validation,
            })

    return {
        "ok": not rejected_rows,
        "app": "DATA-APP",
        "contract_version": "DATA_APP_LOCAL_FILE_ADAPTER_D3",
        "market": "A_SHARE",
        "source_file": path.name,
        "source_type": path.suffix.lower().replace(".", ""),
        "row_count": len(rows),
        "accepted_count": len(accepted_rows),
        "rejected_count": len(rejected_rows),
        "accepted_rows": accepted_rows,
        "rejected_rows": rejected_rows,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "operator_review_required": True,
        "real_order_allowed": False,
        "real_execution_allowed": False,
        "real_money_impact_allowed": False,
    }
