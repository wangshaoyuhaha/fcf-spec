import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from btc_finance_platform.data_schema import validate_paper_batch_schema
from btc_finance_platform.data_schema import validate_paper_input_schema


def _path(file_path: Any) -> Path:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"local paper data file not found: {path}")
    if not path.is_file():
        raise ValueError(f"local paper data path is not a file: {path}")
    return path


def normalize_paper_record(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("paper record must be a dict")

    payload = {
        "symbol": str(record.get("symbol", "")).strip().upper(),
        "price": float(record.get("price")),
        "reference_price": float(record.get("reference_price")),
    }

    validate_paper_input_schema(payload)
    return payload


def load_paper_json(file_path: Any) -> list[dict[str, Any]]:
    path = _path(file_path)
    raw = json.loads(path.read_text(encoding="utf-8-sig"))

    if isinstance(raw, dict) and "items" in raw:
        raw = raw["items"]
    elif isinstance(raw, dict):
        raw = [raw]

    if not isinstance(raw, list):
        raise ValueError("paper json must be a list, a dict, or a dict with items")

    records = [normalize_paper_record(item) for item in raw]
    if not records:
        raise ValueError("paper json must not be empty")
    return records


def load_paper_csv(file_path: Any) -> list[dict[str, Any]]:
    path = _path(file_path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        records = [normalize_paper_record(row) for row in reader]

    if not records:
        raise ValueError("paper csv must not be empty")
    return records


def load_paper_records(file_path: Any) -> list[dict[str, Any]]:
    path = _path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        return load_paper_json(path)
    if suffix == ".csv":
        return load_paper_csv(path)

    raise ValueError(f"unsupported local paper data file type: {suffix}")


def load_paper_batch_from_file(file_path: Any) -> dict[str, Any]:
    path = _path(file_path)
    records = load_paper_records(path)
    validation = validate_paper_batch_schema(records)

    return {
        "ok": True,
        "type": "local_paper_batch_load",
        "source_file": path.name,
        "format": path.suffix.lower().replace(".", ""),
        "count": validation["count"],
        "symbols": validation["symbols"],
        "records": records,
        "validation": validation,
        "paper_only": True,
        "real_exchange_api": False,
        "real_api_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }


def file_sha256(file_path: Any) -> str:
    path = _path(file_path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_local_data_manifest(file_paths: list[Any]) -> dict[str, Any]:
    if not isinstance(file_paths, list):
        raise ValueError("file_paths must be a list")
    if not file_paths:
        raise ValueError("file_paths must not be empty")

    sources = []
    total_records = 0

    for item in file_paths:
        path = _path(item)
        loaded = load_paper_batch_from_file(path)
        total_records += loaded["count"]
        sources.append({
            "source_file": path.name,
            "format": loaded["format"],
            "count": loaded["count"],
            "symbols": loaded["symbols"],
            "sha256": file_sha256(path),
        })

    return {
        "ok": True,
        "type": "local_data_manifest",
        "source_count": len(sources),
        "total_records": total_records,
        "sources": sources,
        "paper_only": True,
        "real_exchange_api": False,
        "real_api_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }
