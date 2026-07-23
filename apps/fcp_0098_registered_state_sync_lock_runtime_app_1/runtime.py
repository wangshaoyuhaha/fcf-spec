from __future__ import annotations

import hashlib
import json

from apps.v2_r1_factor_contract_foundation_app_1 import StateSyncAnchor

from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    RegisteredStateSyncArtifact,
    RegisteredStateSyncLockSnapshot,
)


TOP_LEVEL_FIELDS = {
    "anchors",
    "registry_id",
    "registry_version",
    "schema_version",
}
ANCHOR_FIELDS = {
    "baseline_id",
    "data_latency_ms",
    "data_quality_status",
    "event_id",
    "event_time_utc",
    "factor_version",
    "ingest_time_utc",
    "instrument_id",
    "payload",
    "processing_time_utc",
    "registered_artifact_id",
    "snapshot_time_utc",
    "source_sequence",
    "source_time_utc",
    "state_hash",
    "ttl_seconds",
}


def _closed_object(value: object, fields: set[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{name} must use the closed registered schema")
    return value


def load_registered_state_sync_lock(
    content: bytes,
    artifact: RegisteredStateSyncArtifact,
    *,
    as_of_utc: str,
) -> RegisteredStateSyncLockSnapshot:
    if type(content) is not bytes:
        raise TypeError("content must be exact bytes")
    if len(content) != artifact.byte_length:
        raise ValueError("registered State-Sync artifact byte length mismatch")
    if hashlib.sha256(content).hexdigest() != artifact.artifact_hash:
        raise ValueError("registered State-Sync artifact hash mismatch")
    try:
        payload = json.loads(content.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("registered State-Sync artifact must be ASCII JSON") from exc
    payload = _closed_object(payload, TOP_LEVEL_FIELDS, "registry")
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError("registered State-Sync schema version mismatch")
    raw_anchors = payload["anchors"]
    if type(raw_anchors) is not list or not raw_anchors:
        raise ValueError("registry anchors must be a nonempty list")

    anchors = tuple(
        StateSyncAnchor(**_closed_object(raw, ANCHOR_FIELDS, "State-Sync anchor"))
        for raw in raw_anchors
    )
    event_ids = tuple(anchor.event_id for anchor in anchors)
    if len(set(event_ids)) != len(event_ids):
        raise ValueError("State-Sync event ids must be unique")
    by_instrument: dict[str, list[StateSyncAnchor]] = {}
    for anchor in anchors:
        by_instrument.setdefault(anchor.instrument_id, []).append(anchor)

    current: dict[str, str] = {}
    expired: set[str] = set()
    superseded: set[str] = set()
    for instrument_id, records in by_instrument.items():
        ordered = sorted(records, key=lambda item: (item.source_sequence, item.snapshot_time_utc))
        sequences = tuple(item.source_sequence for item in ordered)
        if len(set(sequences)) != len(sequences):
            raise ValueError("source sequence must be unique per instrument")
        snapshots = tuple(item.snapshot_time_utc for item in ordered)
        if snapshots != tuple(sorted(snapshots)):
            raise ValueError("source sequence and snapshot time must be monotonic")
        for record in ordered:
            if record.status_at(as_of_utc) == "STATE_EXPIRED":
                expired.add(record.event_id)
        latest = ordered[-1]
        superseded.update(item.event_id for item in ordered[:-1])
        if latest.event_id not in expired:
            current[instrument_id] = latest.event_id

    return RegisteredStateSyncLockSnapshot(
        artifact_id=artifact.artifact_id,
        artifact_hash=artifact.artifact_hash,
        registry_id=payload["registry_id"],
        registry_version=payload["registry_version"],
        anchor_hashes={anchor.event_id: anchor.state_hash for anchor in anchors},
        current_event_by_instrument=current,
        expired_event_ids=tuple(sorted(expired)),
        superseded_event_ids=tuple(sorted(superseded)),
        as_of_utc=as_of_utc,
    )
