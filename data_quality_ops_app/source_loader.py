"""Local source loader for DATA-QUALITY-OPS-D2."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .ops_contract import (
    ALLOWED_SOURCE_APP_IDS,
    ALLOWED_SOURCE_TYPES,
    build_data_quality_ops_contract,
    validate_data_quality_ops_contract,
)


ALLOWED_METADATA_EXTENSIONS = (".json", ".md", ".txt")


@dataclass(frozen=True)
class DataQualityOpsSource:
    """Read-only local source metadata payload for data quality operations."""

    source_app_id: str
    source_type: str
    source_path: str
    source_exists: bool
    file_extension: str
    file_size_bytes: int
    payload: dict[str, Any]
    load_errors: tuple[str, ...]

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True

    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    repair_queue_is_execution_instruction: bool = False
    ops_check_is_trade_instruction: bool = False

    trade_action_enabled: bool = False
    real_execution_allowed: bool = False
    buy_button_enabled: bool = False
    sell_button_enabled: bool = False
    order_button_enabled: bool = False
    broker_connection_allowed: bool = False
    exchange_connection_allowed: bool = False
    credential_storage_allowed: bool = False
    wallet_private_key_access_allowed: bool = False
    real_account_access_allowed: bool = False
    real_position_access_allowed: bool = False
    core_mutation_allowed: bool = False
    p48_core_expansion_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["load_errors"] = list(self.load_errors)
        return data


def _read_metadata_payload(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"source file does not exist: {path}"]
    if not path.is_file():
        return {}, [f"source path is not a file: {path}"]

    extension = path.suffix.lower()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {}, [f"source file unreadable: {exc}"]

    if extension == ".json":
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError as exc:
            return {}, [f"invalid json: {exc}"]
        if not isinstance(loaded, dict):
            return {}, ["json payload must be an object"]
        return loaded, []

    return {
        "raw_text_preview": text[:500],
        "raw_text_length": len(text),
    }, []


def load_data_quality_ops_source(
    source_path: str | Path,
    *,
    source_app_id: str,
    source_type: str,
) -> DataQualityOpsSource:
    """Load one local source as read-only metadata."""

    errors: list[str] = []

    contract = build_data_quality_ops_contract()
    contract_errors = validate_data_quality_ops_contract(contract)
    errors.extend(contract_errors)

    if source_app_id not in ALLOWED_SOURCE_APP_IDS:
        errors.append(f"source_app_id is not allowed: {source_app_id}")
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(f"source_type is not allowed: {source_type}")

    path = Path(source_path)
    extension = path.suffix.lower()
    if extension not in ALLOWED_METADATA_EXTENSIONS:
        errors.append(f"file_extension is not allowed: {extension}")

    payload, load_errors = _read_metadata_payload(path)
    errors.extend(load_errors)

    file_size = 0
    if path.exists() and path.is_file():
        file_size = path.stat().st_size

    return DataQualityOpsSource(
        source_app_id=source_app_id,
        source_type=source_type,
        source_path=str(path),
        source_exists=path.exists() and path.is_file(),
        file_extension=extension,
        file_size_bytes=file_size,
        payload=payload,
        load_errors=tuple(errors),
    )


def validate_data_quality_ops_source(source: DataQualityOpsSource) -> list[str]:
    """Validate loaded source safety and schema constraints."""

    errors: list[str] = []

    if source.source_app_id not in ALLOWED_SOURCE_APP_IDS:
        errors.append("source_app_id is not allowed")
    if source.source_type not in ALLOWED_SOURCE_TYPES:
        errors.append("source_type is not allowed")
    if source.file_extension not in ALLOWED_METADATA_EXTENSIONS:
        errors.append("file_extension is not allowed")
    if source.file_size_bytes < 0:
        errors.append("file_size_bytes must be non-negative")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
    )
    for flag_name in required_true_flags:
        if getattr(source, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "repair_queue_is_execution_instruction",
        "ops_check_is_trade_instruction",
        "trade_action_enabled",
        "real_execution_allowed",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "credential_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "core_mutation_allowed",
        "p48_core_expansion_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(source, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def summarize_data_quality_ops_sources(
    sources: tuple[DataQualityOpsSource, ...] | list[DataQualityOpsSource],
) -> dict[str, Any]:
    """Summarize loaded local sources for later quality checks."""

    by_app: dict[str, int] = {}
    by_type: dict[str, int] = {}
    error_count = 0

    for source in sources:
        by_app[source.source_app_id] = by_app.get(source.source_app_id, 0) + 1
        by_type[source.source_type] = by_type.get(source.source_type, 0) + 1
        error_count += len(source.load_errors)

    return {
        "source_count": len(sources),
        "load_error_count": error_count,
        "by_source_app_id": by_app,
        "by_source_type": by_type,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "trade_action_enabled": False,
        "real_execution_allowed": False,
    }
