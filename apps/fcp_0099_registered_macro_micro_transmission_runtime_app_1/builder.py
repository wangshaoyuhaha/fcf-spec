from __future__ import annotations

import hashlib
import json

from .contracts import RegisteredTransmissionArtifact, RegisteredTransmissionSnapshot
from .runtime import load_registered_transmission_registry


REFERENCE_AS_OF_UTC = "2026-07-24T00:20:00Z"


def _hash(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _record(
    transmission_id: str,
    market: str,
    instrument: str,
    minute: int,
) -> dict[str, object]:
    source = sorted(
        (
            _hash(f"{transmission_id}.contradiction"),
            _hash(f"{transmission_id}.support"),
        )
    )
    return {
        "available_at_utc": f"2026-07-24T00:{minute + 1:02d}:00Z",
        "causal_truth_claimed": False,
        "chain": [
            {"level": "MACRO", "subject_id": "macro.policy-window"},
            {"level": "ASSET_CLASS", "subject_id": "asset-class.equity"},
            {"level": "MARKET", "subject_id": market},
            {"level": "SECTOR", "subject_id": "sector.registered-technology"},
            {"level": "INSTRUMENT", "subject_id": instrument},
            {
                "level": "MICROSTRUCTURE",
                "subject_id": "microstructure.registered-liquidity",
            },
        ],
        "contradicting_evidence_hashes": (source[0],),
        "correlation_id": "correlation.policy-liquidity-v1",
        "decay_seconds": 86400,
        "expected_value_id": "expected.policy-neutral",
        "expires_at_utc": "2026-07-26T00:00:00Z",
        "horizon_id": "horizon.short-equity",
        "hypothesized_direction": "MIXED",
        "invalidation_ids": ("invalidation.policy-reversal",),
        "macro_event_id": "macro-event.registered-policy-v1",
        "mechanism_id": "mechanism.policy-capital-liquidity",
        "observed_value_id": "observed.policy-supportive",
        "operator_registered": True,
        "publication_time_utc": f"2026-07-24T00:{minute:02d}:00Z",
        "regime_ids": ("regime.policy-window",),
        "source_evidence_hashes": source,
        "state_hash": _hash(f"{transmission_id}.state"),
        "supporting_evidence_hashes": (source[1],),
        "surprise_definition_id": "surprise.policy-language-delta",
        "transmission_id": transmission_id,
        "transmission_version": "v1",
        "uncertainty_bps": 3500,
    }


def build_reference_artifact_bytes() -> bytes:
    payload = {
        "registry_id": "fcf-macro-micro-transmission-registry",
        "registry_version": "v1",
        "schema_version": "fcf-registered-macro-micro-transmission-runtime-v1",
        "transmissions": [
            _record("transmission.ashare.policy.001", "market.ashare", "SH600000", 0),
            _record("transmission.ashare.policy.002", "market.ashare", "SZ000001", 5),
        ],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def build_reference_transmission_snapshot() -> RegisteredTransmissionSnapshot:
    content = build_reference_artifact_bytes()
    artifact = RegisteredTransmissionArtifact(
        artifact_id="registered-macro-micro-transmission-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T00:10:00Z",
    )
    return load_registered_transmission_registry(
        content,
        artifact,
        as_of_utc=REFERENCE_AS_OF_UTC,
    )


def render_transmission_snapshot_json(
    snapshot: RegisteredTransmissionSnapshot,
) -> str:
    return json.dumps(
        {
            "active_transmission_ids": snapshot.active_transmission_ids,
            "artifact_hash": snapshot.artifact_hash,
            "artifact_id": snapshot.artifact_id,
            "as_of_utc": snapshot.as_of_utc,
            "chain_subjects": dict(snapshot.chain_subjects),
            "expired_transmission_ids": snapshot.expired_transmission_ids,
            "operator_review_required": snapshot.operator_review_required,
            "read_only": snapshot.read_only,
            "record_hashes": dict(snapshot.record_hashes),
            "registry_id": snapshot.registry_id,
            "registry_version": snapshot.registry_version,
            "schema_version": snapshot.schema_version,
            "snapshot_hash": snapshot.snapshot_hash,
        },
        indent=2,
        sort_keys=True,
    )
