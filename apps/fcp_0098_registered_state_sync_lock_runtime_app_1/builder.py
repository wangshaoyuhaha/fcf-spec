from __future__ import annotations

import hashlib
import json

from apps.v2_r1_factor_contract_foundation_app_1 import build_state_sync_anchor

from .contracts import RegisteredStateSyncArtifact, RegisteredStateSyncLockSnapshot
from .runtime import load_registered_state_sync_lock


REFERENCE_AS_OF_UTC = "2026-07-23T16:10:00Z"


def _anchor(event_id: str, instrument_id: str, sequence: int, minute: int):
    timestamp = f"2026-07-23T16:{minute:02d}:00Z"
    return build_state_sync_anchor(
        event_id=event_id,
        instrument_id=instrument_id,
        event_time_utc=timestamp,
        source_time_utc=timestamp,
        ingest_time_utc=timestamp,
        processing_time_utc=timestamp,
        snapshot_time_utc=timestamp,
        ttl_seconds=420,
        baseline_id="baseline.registered.v1",
        source_sequence=sequence,
        factor_version="factor-set.v1",
        data_quality_status="registered-valid",
        data_latency_ms=0,
        registered_artifact_id="artifact.registered.snapshot.v1",
        payload={"close": f"{100 + sequence}.00", "volume": str(1000 + sequence)},
    )


def _plain(anchor) -> dict[str, object]:
    return {
        **{
            key: value
            for key, value in anchor.hash_payload().items()
            if key != "payload"
        },
        "payload": dict(anchor.payload),
        "state_hash": anchor.state_hash,
    }


def build_reference_artifact_bytes() -> bytes:
    payload = {
        "anchors": [
            _plain(_anchor("event.btc.001", "BTCUSDT", 1, 0)),
            _plain(_anchor("event.btc.002", "BTCUSDT", 2, 5)),
            _plain(_anchor("event.ashare.001", "SH600000", 1, 4)),
        ],
        "registry_id": "fcf-state-sync-registry",
        "registry_version": "v1",
        "schema_version": "fcf-registered-state-sync-lock-runtime-v1",
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def build_reference_lock_snapshot() -> RegisteredStateSyncLockSnapshot:
    content = build_reference_artifact_bytes()
    artifact = RegisteredStateSyncArtifact(
        artifact_id="registered-state-sync-lock-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-23T16:09:00Z",
    )
    return load_registered_state_sync_lock(
        content,
        artifact,
        as_of_utc=REFERENCE_AS_OF_UTC,
    )


def render_lock_snapshot_json(snapshot: RegisteredStateSyncLockSnapshot) -> str:
    return json.dumps(
        {
            "anchor_hashes": dict(snapshot.anchor_hashes),
            "artifact_hash": snapshot.artifact_hash,
            "artifact_id": snapshot.artifact_id,
            "as_of_utc": snapshot.as_of_utc,
            "current_event_by_instrument": dict(snapshot.current_event_by_instrument),
            "expired_event_ids": snapshot.expired_event_ids,
            "operator_review_required": snapshot.operator_review_required,
            "read_only": snapshot.read_only,
            "registry_id": snapshot.registry_id,
            "registry_version": snapshot.registry_version,
            "schema_version": snapshot.schema_version,
            "snapshot_hash": snapshot.snapshot_hash,
            "superseded_event_ids": snapshot.superseded_event_ids,
        },
        indent=2,
        sort_keys=True,
    )
