from __future__ import annotations

import hashlib
import json

from .contracts import (
    RegisteredTargetLabelArtifact,
    RegisteredTargetLabelRuntimeSnapshot,
)
from .runtime import load_registered_target_label_registry


REFERENCE_OBSERVED_AT_UTC = "2026-07-23T15:00:00Z"


def _target(
    target_id: str,
    horizon: str,
    maturity_rule: str,
    target_type: str,
    formula: str,
) -> dict[str, object]:
    return {
        "abstention_behavior": "retain-audit-record",
        "asset_class": "multi-asset",
        "basis": "ABSOLUTE",
        "benchmark_policy": "none",
        "capacity_treatment": "record-not-score",
        "censored_behavior": "flag",
        "cost_treatment": "exclude-research-only",
        "decision_time_basis": "registered-snapshot-close",
        "effective_at_utc": "2026-07-23T00:00:00Z",
        "evaluation_metrics": ["mae", "rank-ic"],
        "evidence_refs": [f"evidence.{target_id}"],
        "forecast_horizon": horizon,
        "formula": formula,
        "instrument_scope": "registered-instruments",
        "invalid_behavior": "reject",
        "label_availability_rule": "maturity-plus-source-finality",
        "market": "registered-market",
        "maturity_rule": maturity_rule,
        "minimum_sample": 100,
        "missing_behavior": "abstain",
        "neutralization_policy": "none",
        "objective": "research-evaluation-only",
        "owner": "target-governance",
        "slippage_treatment": "exclude-research-only",
        "target_id": target_id,
        "target_type": target_type,
        "target_version": "v1",
    }


def _label(
    label_id: str,
    target_reference: str,
    maturity_rule: str,
) -> dict[str, object]:
    return {
        "available_time_field": "available_at_utc",
        "censored_behavior": "retain-censored",
        "decision_time_field": "decision_at_utc",
        "effective_at_utc": "2026-07-23T00:00:00Z",
        "first_tradable_time_field": "first_tradable_at_utc",
        "invalid_behavior": "reject",
        "label_id": label_id,
        "label_version": "v1",
        "maturity_rule": maturity_rule,
        "maturity_time_field": "matured_at_utc",
        "missing_behavior": "abstain",
        "observation_key_rule": "instrument-plus-decision-time",
        "published_time_field": "published_at_utc",
        "revision_policy": "append-only",
        "source_evidence_rule": "registered-evidence-required",
        "target_ref": target_reference,
        "value_type": "decimal",
    }


def build_reference_artifact_bytes() -> bytes:
    payload = {
        "labels": [
            _label(
                "label.return.next-session",
                "target.return.next-session@v1",
                "next-session-close",
            ),
            _label(
                "label.volatility.five-session",
                "target.volatility.five-session@v1",
                "fifth-session-close",
            ),
        ],
        "registry_id": "fcf-target-label-registry",
        "registry_version": "v1",
        "schema_version": "fcf-registered-target-label-registry-runtime-v1",
        "targets": [
            _target(
                "target.return.next-session",
                "next-session",
                "next-session-close",
                "RETURN",
                "matured_close / decision_close - 1",
            ),
            _target(
                "target.volatility.five-session",
                "five-session",
                "fifth-session-close",
                "VOLATILITY",
                "registered_five_session_realized_volatility",
            ),
        ],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def build_reference_runtime_snapshot() -> RegisteredTargetLabelRuntimeSnapshot:
    content = build_reference_artifact_bytes()
    artifact = RegisteredTargetLabelArtifact(
        artifact_id="registered-target-label-registry-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-23T14:00:00Z",
    )
    return load_registered_target_label_registry(
        content,
        artifact,
        observed_at_utc=REFERENCE_OBSERVED_AT_UTC,
    )


def render_runtime_snapshot_json(
    snapshot: RegisteredTargetLabelRuntimeSnapshot,
) -> str:
    return json.dumps(
        {
            "artifact_hash": snapshot.artifact_hash,
            "artifact_id": snapshot.artifact_id,
            "label_record_hashes": dict(snapshot.label_record_hashes),
            "label_to_target_ref": dict(snapshot.label_to_target_ref),
            "observed_at_utc": snapshot.observed_at_utc,
            "operator_review_required": snapshot.operator_review_required,
            "read_only": snapshot.read_only,
            "registry_id": snapshot.registry_id,
            "registry_version": snapshot.registry_version,
            "schema_version": snapshot.schema_version,
            "snapshot_hash": snapshot.snapshot_hash,
            "target_record_hashes": dict(snapshot.target_record_hashes),
            "target_to_label_refs": dict(snapshot.target_to_label_refs),
        },
        indent=2,
        sort_keys=True,
    )
