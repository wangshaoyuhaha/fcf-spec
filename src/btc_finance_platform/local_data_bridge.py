import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.local_data_loader import build_local_data_manifest
from btc_finance_platform.local_data_loader import load_paper_batch_from_file


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_api_key_required": False,
    "wallet_private_key_required": False,
    "real_order": False,
    "real_execution": False,
    "real_balance": False,
    "real_position": False,
    "real_money_impact": False,
    "operator_review_required": True,
}


def _require_file_paths(file_paths: list[Any]) -> list[Any]:
    if not isinstance(file_paths, list):
        raise ValueError("file_paths must be a list")
    if not file_paths:
        raise ValueError("file_paths must not be empty")
    return file_paths


def _paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def build_local_paper_dataset(file_paths: list[Any]) -> dict[str, Any]:
    file_paths = _require_file_paths(file_paths)
    manifest = build_local_data_manifest(file_paths)

    records = []
    for item in file_paths:
        loaded = load_paper_batch_from_file(item)
        for record in loaded["records"]:
            enriched = dict(record)
            enriched["source_file"] = loaded["source_file"]
            records.append(enriched)

    symbols = [record["symbol"] for record in records]

    return {
        "ok": True,
        "type": "local_paper_dataset",
        "source_count": manifest["source_count"],
        "total_records": len(records),
        "symbols": symbols,
        "records": records,
        "manifest": manifest,
        **_paper_flags(),
    }


def build_local_paper_analysis_inputs(file_paths: list[Any]) -> dict[str, Any]:
    dataset = build_local_paper_dataset(file_paths)

    items = [
        {
            "symbol": record["symbol"],
            "price": record["price"],
            "reference_price": record["reference_price"],
        }
        for record in dataset["records"]
    ]

    return {
        "ok": True,
        "type": "local_paper_analysis_inputs",
        "count": len(items),
        "symbols": [item["symbol"] for item in items],
        "items": items,
        "source_manifest": dataset["manifest"],
        **_paper_flags(),
    }


def build_local_data_audit_report(file_paths: list[Any]) -> dict[str, Any]:
    dataset = build_local_paper_dataset(file_paths)
    manifest = dataset["manifest"]

    checks = {
        "paper_only_preserved": dataset["paper_only"] is True,
        "no_real_exchange_api": dataset["real_exchange_api"] is False,
        "no_real_api_key_required": dataset["real_api_key_required"] is False,
        "no_wallet_private_key_required": dataset["wallet_private_key_required"] is False,
        "no_real_order": dataset["real_order"] is False,
        "no_real_execution": dataset["real_execution"] is False,
        "no_real_balance": dataset["real_balance"] is False,
        "no_real_position": dataset["real_position"] is False,
        "no_real_money_impact": dataset["real_money_impact"] is False,
        "operator_review_required": dataset["operator_review_required"] is True,
        "source_files_have_sha256": all(
            len(source["sha256"]) == 64 for source in manifest["sources"]
        ),
        "record_count_matches_manifest": dataset["total_records"] == manifest["total_records"],
    }

    return {
        "ok": all(checks.values()),
        "type": "local_data_audit_report",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_count": dataset["source_count"],
        "total_records": dataset["total_records"],
        "symbols": dataset["symbols"],
        "checks": checks,
        "manifest": manifest,
        **_paper_flags(),
    }


def write_local_data_audit_report(file_paths: list[Any], output_path: Any) -> dict[str, Any]:
    report = build_local_data_audit_report(file_paths)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "local_data_audit_report_written",
        "output_file": str(path),
        "report": report,
        **_paper_flags(),
    }
