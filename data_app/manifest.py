"""DATA-APP-D4 manifest and checksum.

Read-only manifest builder for local DATA-APP inputs.
No core mutation, no trading action, no broker API, no exchange API.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from data_app.local_file_adapter import build_local_file_adapter_result


def file_sha256(file_path: str | Path) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"local file not found: {path}")
    if not path.is_file():
        raise ValueError(f"local path is not a file: {path}")

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_data_app_manifest_for_file(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)
    checksum = file_sha256(path)
    adapter_result = build_local_file_adapter_result(path)
    row_count = adapter_result["row_count"]
    manifest_id = f"DATAAPP-A-SHARE-{checksum[:12]}-{row_count}"

    return {
        "app": "DATA-APP",
        "contract_version": "DATA_APP_MANIFEST_D4",
        "manifest_id": manifest_id,
        "market": "A_SHARE",
        "source_file": path.name,
        "source_type": adapter_result["source_type"],
        "schema_version": "a_share_daily_v1",
        "checksum_sha256": checksum,
        "row_count": adapter_result["row_count"],
        "accepted_count": adapter_result["accepted_count"],
        "rejected_count": adapter_result["rejected_count"],
        "adapter_ok": adapter_result["ok"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
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


def build_data_app_manifest_for_files(file_paths: list[str | Path]) -> dict[str, Any]:
    if not isinstance(file_paths, list):
        raise ValueError("file_paths must be a list")
    if not file_paths:
        raise ValueError("file_paths must not be empty")

    sources = [build_data_app_manifest_for_file(path) for path in file_paths]
    aggregate_seed = "|".join(source["checksum_sha256"] for source in sources)
    aggregate_checksum = hashlib.sha256(aggregate_seed.encode("utf-8")).hexdigest()

    return {
        "app": "DATA-APP",
        "contract_version": "DATA_APP_MANIFEST_D4",
        "manifest_id": f"DATAAPP-A-SHARE-BATCH-{aggregate_checksum[:12]}-{len(sources)}",
        "market": "A_SHARE",
        "source_count": len(sources),
        "row_count": sum(source["row_count"] for source in sources),
        "accepted_count": sum(source["accepted_count"] for source in sources),
        "rejected_count": sum(source["rejected_count"] for source in sources),
        "checksum_sha256": aggregate_checksum,
        "sources": sources,
        "all_sources_ok": all(source["adapter_ok"] for source in sources),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
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


def validate_data_app_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a dict")

    checks = {
        "app_is_data_app": manifest.get("app") == "DATA-APP",
        "market_is_a_share": manifest.get("market") == "A_SHARE",
        "manifest_id_present": bool(manifest.get("manifest_id")),
        "checksum_is_sha256": len(str(manifest.get("checksum_sha256", ""))) == 64,
        "row_count_non_negative": int(manifest.get("row_count", -1)) >= 0,
        "accepted_count_non_negative": int(manifest.get("accepted_count", -1)) >= 0,
        "rejected_count_non_negative": int(manifest.get("rejected_count", -1)) >= 0,
        "paper_only": manifest.get("paper_only") is True,
        "local_only": manifest.get("local_only") is True,
        "read_only": manifest.get("read_only") is True,
        "operator_review_required": manifest.get("operator_review_required") is True,
        "no_real_exchange_api": manifest.get("real_exchange_api") is False,
        "no_real_brokerage_api": manifest.get("real_brokerage_api") is False,
        "no_api_key_required": manifest.get("api_key_required") is False,
        "no_real_order": manifest.get("real_order_allowed") is False,
        "no_real_execution": manifest.get("real_execution_allowed") is False,
        "no_real_money_impact": manifest.get("real_money_impact_allowed") is False,
    }

    return {
        "ok": all(checks.values()),
        "app": manifest.get("app"),
        "manifest_id": manifest.get("manifest_id"),
        "checksum_sha256": manifest.get("checksum_sha256"),
        "checks": checks,
    }

