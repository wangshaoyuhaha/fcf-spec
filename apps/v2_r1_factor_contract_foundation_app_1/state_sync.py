from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from types import MappingProxyType
from typing import Any

from .contracts import (
    freeze_json,
    parse_utc_timestamp,
    require_identifier,
    require_utc_timestamp,
)


def _plain_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _plain_json(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (tuple, list)):
        return [_plain_json(item) for item in value]
    if isinstance(value, Decimal):
        return format(value, "f")
    return value


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        _plain_json(value),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def state_hash(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


@dataclass(frozen=True)
class StateSyncAnchor:
    event_id: str
    instrument_id: str
    event_time_utc: str
    source_time_utc: str
    ingest_time_utc: str
    processing_time_utc: str
    snapshot_time_utc: str
    ttl_seconds: int
    baseline_id: str
    source_sequence: int
    factor_version: str
    data_quality_status: str
    data_latency_ms: int
    registered_artifact_id: str
    payload: Mapping[str, Any]
    state_hash: str

    def __post_init__(self) -> None:
        for field_name in (
            "event_id",
            "instrument_id",
            "baseline_id",
            "factor_version",
            "data_quality_status",
            "registered_artifact_id",
        ):
            object.__setattr__(
                self,
                field_name,
                require_identifier(getattr(self, field_name), field_name),
            )
        for field_name in (
            "event_time_utc",
            "source_time_utc",
            "ingest_time_utc",
            "processing_time_utc",
            "snapshot_time_utc",
        ):
            object.__setattr__(
                self,
                field_name,
                require_utc_timestamp(getattr(self, field_name), field_name),
            )
        if isinstance(self.ttl_seconds, bool) or self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        for field_name in ("source_sequence", "data_latency_ms"):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative integer")
        event_time = parse_utc_timestamp(self.event_time_utc)
        source_time = parse_utc_timestamp(self.source_time_utc)
        ingest_time = parse_utc_timestamp(self.ingest_time_utc)
        processing_time = parse_utc_timestamp(self.processing_time_utc)
        snapshot_time = parse_utc_timestamp(self.snapshot_time_utc)
        if not (
            event_time <= source_time <= ingest_time <= processing_time <= snapshot_time
        ):
            raise ValueError("State-Sync timestamps are out of order")
        payload = freeze_json(self.payload)
        if not isinstance(payload, MappingProxyType):
            raise ValueError("payload must be a mapping")
        object.__setattr__(self, "payload", payload)
        if len(self.state_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.state_hash
        ):
            raise ValueError("state_hash must be lowercase SHA-256")
        if self.state_hash != state_hash(self.hash_payload()):
            raise ValueError("state_hash does not match State-Sync anchor")

    def hash_payload(self) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "baseline_id": self.baseline_id,
                "data_latency_ms": self.data_latency_ms,
                "data_quality_status": self.data_quality_status,
                "event_id": self.event_id,
                "event_time_utc": self.event_time_utc,
                "factor_version": self.factor_version,
                "ingest_time_utc": self.ingest_time_utc,
                "instrument_id": self.instrument_id,
                "payload": self.payload,
                "processing_time_utc": self.processing_time_utc,
                "registered_artifact_id": self.registered_artifact_id,
                "snapshot_time_utc": self.snapshot_time_utc,
                "source_sequence": self.source_sequence,
                "source_time_utc": self.source_time_utc,
                "ttl_seconds": self.ttl_seconds,
            }
        )

    @property
    def expires_at_utc(self) -> str:
        expires = parse_utc_timestamp(self.snapshot_time_utc) + timedelta(
            seconds=self.ttl_seconds
        )
        return expires.isoformat().replace("+00:00", "Z")

    def status_at(self, as_of_utc: str) -> str:
        as_of = parse_utc_timestamp(require_utc_timestamp(as_of_utc, "as_of_utc"))
        if as_of < parse_utc_timestamp(self.snapshot_time_utc):
            raise ValueError("as_of_utc cannot precede snapshot_time_utc")
        return (
            "ACTIVE"
            if as_of <= parse_utc_timestamp(self.expires_at_utc)
            else "STATE_EXPIRED"
        )


def build_state_sync_anchor(
    *,
    event_id: str,
    instrument_id: str,
    event_time_utc: str,
    source_time_utc: str,
    ingest_time_utc: str,
    processing_time_utc: str,
    snapshot_time_utc: str,
    ttl_seconds: int,
    baseline_id: str,
    source_sequence: int,
    factor_version: str,
    data_quality_status: str,
    data_latency_ms: int,
    registered_artifact_id: str,
    payload: Mapping[str, Any],
) -> StateSyncAnchor:
    values: dict[str, Any] = {
        "baseline_id": require_identifier(baseline_id, "baseline_id"),
        "data_latency_ms": data_latency_ms,
        "data_quality_status": require_identifier(
            data_quality_status, "data_quality_status"
        ),
        "event_id": require_identifier(event_id, "event_id"),
        "event_time_utc": require_utc_timestamp(event_time_utc, "event_time_utc"),
        "factor_version": require_identifier(factor_version, "factor_version"),
        "ingest_time_utc": require_utc_timestamp(
            ingest_time_utc, "ingest_time_utc"
        ),
        "instrument_id": require_identifier(instrument_id, "instrument_id"),
        "payload": payload,
        "processing_time_utc": require_utc_timestamp(
            processing_time_utc, "processing_time_utc"
        ),
        "registered_artifact_id": require_identifier(
            registered_artifact_id, "registered_artifact_id"
        ),
        "snapshot_time_utc": require_utc_timestamp(
            snapshot_time_utc, "snapshot_time_utc"
        ),
        "source_sequence": source_sequence,
        "source_time_utc": require_utc_timestamp(
            source_time_utc, "source_time_utc"
        ),
        "ttl_seconds": ttl_seconds,
    }
    digest = state_hash(values)
    return StateSyncAnchor(state_hash=digest, **values)


@dataclass(frozen=True)
class StateSyncEvaluation:
    anchor: StateSyncAnchor
    as_of_utc: str
    status: str

    def __post_init__(self) -> None:
        if not isinstance(self.anchor, StateSyncAnchor):
            raise ValueError("anchor must be StateSyncAnchor")
        normalized = require_utc_timestamp(self.as_of_utc, "as_of_utc")
        object.__setattr__(self, "as_of_utc", normalized)
        expected = self.anchor.status_at(normalized)
        if self.status != expected:
            raise ValueError("State-Sync evaluation status is inconsistent")


def evaluate_state_sync(
    anchor: StateSyncAnchor, as_of_utc: str
) -> StateSyncEvaluation:
    return StateSyncEvaluation(
        anchor=anchor,
        as_of_utc=as_of_utc,
        status=anchor.status_at(as_of_utc),
    )
