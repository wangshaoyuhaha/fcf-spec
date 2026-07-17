from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from types import MappingProxyType
from typing import Mapping


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,159}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_CLOCK_QUALITY = {"SYNCED", "DEGRADED", "UNKNOWN"}
_CORRECTION_KIND = {"ORIGINAL", "CORRECTION", "BACKFILL", "CANCEL"}


def identifier(value: object, name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a safe identifier")
    return normalized


def utc(value: object, name: str) -> str:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{name} must be UTC")
    return parsed.isoformat().replace("+00:00", "Z")


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _decimal(value: object, name: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be decimal-compatible") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


def _decimal_text(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == 0:
        return "0"
    return format(normalized, "f")


def _payload_scalar(value: object, name: str) -> tuple[object, str, str]:
    if value is None:
        return None, "null", ""
    if isinstance(value, bool):
        return value, "bool", "true" if value else "false"
    if isinstance(value, int):
        return value, "int", str(value)
    if isinstance(value, Decimal):
        normalized = _decimal(value, name)
        return normalized, "decimal", _decimal_text(normalized)
    if isinstance(value, float):
        raise ValueError(f"{name} must not use binary float")
    if isinstance(value, str):
        if len(value) > 512:
            raise ValueError(f"{name} exceeds 512 characters")
        try:
            value.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ValueError(f"{name} must be ASCII") from exc
        if any(
            ord(character) < 32 or ord(character) == 127 for character in value
        ):
            raise ValueError(f"{name} contains a control character")
        return value, "str", value
    raise ValueError(f"{name} has an unsupported scalar type")


def _normalize_payload(
    payload: Mapping[str, object],
) -> tuple[Mapping[str, object], tuple[tuple[str, str, str], ...]]:
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be a mapping")
    if not 1 <= len(payload) <= 64:
        raise ValueError("payload must contain between 1 and 64 fields")
    normalized: dict[str, object] = {}
    canonical: list[tuple[str, str, str]] = []
    for raw_key in sorted(payload, key=str):
        key = identifier(raw_key, "payload key")
        if key in normalized:
            raise ValueError("payload keys must be unique after normalization")
        value, type_name, value_text = _payload_scalar(payload[raw_key], key)
        normalized[key] = value
        canonical.append((key, type_name, value_text))
    return MappingProxyType(normalized), tuple(canonical)


def _hash(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LocalEventRights:
    license_id: str
    permitted_use: str
    retention_days: int
    operator_confirmed: bool = True
    local_artifact_only: bool = True
    redistribution_allowed: bool = False
    network_retrieval_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "license_id", identifier(self.license_id, "license_id"))
        object.__setattr__(
            self, "permitted_use", identifier(self.permitted_use, "permitted_use")
        )
        if self.permitted_use.upper() in {"NONE", "DENIED", "PROHIBITED"}:
            raise ValueError("permitted_use denies local event research")
        if (
            isinstance(self.retention_days, bool)
            or not isinstance(self.retention_days, int)
            or self.retention_days <= 0
        ):
            raise ValueError("retention_days must be positive")
        if self.operator_confirmed is not True or self.local_artifact_only is not True:
            raise ValueError("local event rights require Operator confirmation")
        if self.redistribution_allowed or self.network_retrieval_allowed:
            raise ValueError("V2-R3 rights exceed local-only scope")


@dataclass(frozen=True)
class LocalEventEnvelope:
    event_id: str
    stream_id: str
    source_id: str
    registered_artifact_id: str
    event_type: str
    source_sequence: int
    event_at_utc: str
    received_at_utc: str
    processed_at_utc: str
    payload: Mapping[str, object]
    rights: LocalEventRights
    clock_quality: str = "SYNCED"
    correction_kind: str = "ORIGINAL"
    schema_version: int = 1
    declared_payload_sha256: str | None = None
    payload_sha256: str = field(init=False)
    event_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "event_id",
            "stream_id",
            "source_id",
            "registered_artifact_id",
            "event_type",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        if isinstance(self.source_sequence, bool) or self.source_sequence <= 0:
            raise ValueError("source_sequence must be positive")
        if isinstance(self.schema_version, bool) or self.schema_version <= 0:
            raise ValueError("schema_version must be positive")
        if self.clock_quality not in _CLOCK_QUALITY:
            raise ValueError("clock_quality is not allowed")
        if self.correction_kind not in _CORRECTION_KIND:
            raise ValueError("correction_kind is not allowed")
        event_at = utc(self.event_at_utc, "event_at_utc")
        received_at = utc(self.received_at_utc, "received_at_utc")
        processed_at = utc(self.processed_at_utc, "processed_at_utc")
        if not instant(event_at) <= instant(received_at) <= instant(processed_at):
            raise ValueError("event, receive, and processing time must be ordered")
        object.__setattr__(self, "event_at_utc", event_at)
        object.__setattr__(self, "received_at_utc", received_at)
        object.__setattr__(self, "processed_at_utc", processed_at)
        if not isinstance(self.rights, LocalEventRights):
            raise ValueError("rights must be LocalEventRights")
        payload, payload_records = _normalize_payload(self.payload)
        payload_sha256 = _hash(payload_records)
        if self.declared_payload_sha256 is not None:
            declared = str(self.declared_payload_sha256).strip().lower()
            if _SHA256.fullmatch(declared) is None or declared != payload_sha256:
                raise ValueError("declared payload SHA-256 does not match")
        object.__setattr__(self, "payload", payload)
        object.__setattr__(self, "payload_sha256", payload_sha256)
        event_record = {
            "clock_quality": self.clock_quality,
            "correction_kind": self.correction_kind,
            "event_at_utc": event_at,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "license_id": self.rights.license_id,
            "payload_sha256": payload_sha256,
            "permitted_use": self.rights.permitted_use,
            "processed_at_utc": processed_at,
            "received_at_utc": received_at,
            "registered_artifact_id": self.registered_artifact_id,
            "schema_version": self.schema_version,
            "source_id": self.source_id,
            "source_sequence": self.source_sequence,
            "stream_id": self.stream_id,
        }
        object.__setattr__(self, "event_hash", _hash(event_record))
