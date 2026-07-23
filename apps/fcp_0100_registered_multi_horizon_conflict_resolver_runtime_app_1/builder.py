from __future__ import annotations

import hashlib
import json

from .contracts import RegisteredConflictArtifact, RegisteredConflictSnapshot
from .runtime import load_registered_conflict_registry


REFERENCE_AS_OF_UTC = "2026-07-24T01:15:00Z"


def _hash(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _result(
    result_id: str,
    horizon_id: str,
    direction: str,
    evidence_state: str = "OBSERVED",
    *,
    hard_risk_block: bool = False,
) -> dict[str, object]:
    return {
        "available_at_utc": "2026-07-24T01:00:00Z",
        "correlation_id": "correlation.registered-horizon-v1",
        "evidence_hashes": (
            [] if evidence_state == "MISSING" else [_hash(f"{result_id}.evidence")]
        ),
        "evidence_state": evidence_state,
        "expires_at_utc": "2026-07-25T01:00:00Z",
        "hard_risk_block": hard_risk_block,
        "horizon_id": horizon_id,
        "invalidation_ids": ["invalidation.registered-state-change"],
        "result_id": result_id,
        "signal_direction": direction,
        "state_hash": _hash(f"{result_id}.state"),
    }


def build_reference_artifact_bytes() -> bytes:
    payload = {
        "conflict_sets": [
            {
                "conflict_set_id": "conflict-set.ashare.600000.v1",
                "instrument_id": "SH600000",
                "market_id": "market.ashare",
                "results": [
                    _result("result.ashare.medium", "EQUITY_MEDIUM", "UP"),
                    _result("result.ashare.short", "EQUITY_SHORT", "DOWN"),
                    _result(
                        "result.ashare.intraday",
                        "ASHARE_INTRADAY",
                        "DOWN",
                        hard_risk_block=True,
                    ),
                ],
                "thesis_direction": "UP",
            },
            {
                "conflict_set_id": "conflict-set.btc.reference.v1",
                "instrument_id": "BTC-REFERENCE",
                "market_id": "market.btc-reference",
                "results": [
                    _result(
                        "result.btc.short",
                        "BTC_SHORT",
                        "UNKNOWN",
                        evidence_state="MISSING",
                    )
                ],
                "thesis_direction": "UP",
            },
        ],
        "registry_id": "fcf-multi-horizon-conflict-registry",
        "registry_version": "v1",
        "schema_version": "fcf-registered-multi-horizon-conflict-runtime-v1",
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def build_reference_conflict_snapshot() -> RegisteredConflictSnapshot:
    content = build_reference_artifact_bytes()
    artifact = RegisteredConflictArtifact(
        artifact_id="registered-multi-horizon-conflict-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T01:10:00Z",
    )
    return load_registered_conflict_registry(
        content,
        artifact,
        as_of_utc=REFERENCE_AS_OF_UTC,
    )


def render_conflict_snapshot_json(snapshot: RegisteredConflictSnapshot) -> str:
    return json.dumps(
        {
            "artifact_hash": snapshot.artifact_hash,
            "artifact_id": snapshot.artifact_id,
            "as_of_utc": snapshot.as_of_utc,
            "conflicting_set_ids": snapshot.conflicting_set_ids,
            "grouped_result_ids": {
                key: dict(value)
                for key, value in snapshot.grouped_result_ids.items()
            },
            "operator_review_required": snapshot.operator_review_required,
            "presentation_rows": dict(snapshot.presentation_rows),
            "read_only": snapshot.read_only,
            "registry_id": snapshot.registry_id,
            "registry_version": snapshot.registry_version,
            "schema_version": snapshot.schema_version,
            "set_hashes": dict(snapshot.set_hashes),
            "snapshot_hash": snapshot.snapshot_hash,
        },
        indent=2,
        sort_keys=True,
    )
