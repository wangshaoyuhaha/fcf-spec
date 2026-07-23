from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from types import MappingProxyType

import pytest

from apps.fcp_0099_registered_macro_micro_transmission_runtime_app_1 import (
    CHAIN_LEVELS,
    REFERENCE_AS_OF_UTC,
    RegisteredTransmissionArtifact,
    build_reference_artifact_bytes,
    load_registered_transmission_registry,
)


def _artifact(content: bytes) -> RegisteredTransmissionArtifact:
    return RegisteredTransmissionArtifact(
        artifact_id="registered-macro-micro-transmission-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T00:10:00Z",
    )


def _payload() -> dict[str, object]:
    return json.loads(build_reference_artifact_bytes())


def _content(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def test_d1_exact_registered_artifact_is_required() -> None:
    content = build_reference_artifact_bytes()
    artifact = _artifact(content)
    with pytest.raises(ValueError, match="byte length"):
        load_registered_transmission_registry(
            content,
            replace(artifact, byte_length=1),
            as_of_utc=REFERENCE_AS_OF_UTC,
        )
    with pytest.raises(ValueError, match="hash mismatch"):
        load_registered_transmission_registry(
            content,
            replace(artifact, artifact_hash="2" * 64),
            as_of_utc=REFERENCE_AS_OF_UTC,
        )


def test_d2_closed_ascii_schema_is_enforced() -> None:
    payload = _payload()
    payload["unexpected"] = True
    changed = _content(payload)
    with pytest.raises(ValueError, match="closed registered schema"):
        load_registered_transmission_registry(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )
    non_ascii = b'{"name":"\xff"}'
    with pytest.raises(ValueError, match="ASCII JSON"):
        load_registered_transmission_registry(
            non_ascii, _artifact(non_ascii), as_of_utc=REFERENCE_AS_OF_UTC
        )


def test_d3_official_chain_is_complete_ordered_and_immutable() -> None:
    content = build_reference_artifact_bytes()
    snapshot = load_registered_transmission_registry(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    assert snapshot.active_transmission_ids == (
        "transmission.ashare.policy.001",
        "transmission.ashare.policy.002",
    )
    assert len(snapshot.chain_subjects["transmission.ashare.policy.001"]) == len(
        CHAIN_LEVELS
    )
    assert isinstance(snapshot.record_hashes, MappingProxyType)
    with pytest.raises(TypeError):
        snapshot.record_hashes["x"] = "y"  # type: ignore[index]


def test_d4_missing_or_reordered_chain_level_fails_closed() -> None:
    payload = _payload()
    records = payload["transmissions"]
    assert isinstance(records, list)
    records[0]["chain"] = list(reversed(records[0]["chain"]))
    changed = _content(payload)
    with pytest.raises(ValueError, match="official level"):
        load_registered_transmission_registry(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )


def test_d5_lineage_contradiction_and_lifecycle_are_enforced() -> None:
    payload = _payload()
    records = payload["transmissions"]
    assert isinstance(records, list)
    records[0]["contradicting_evidence_hashes"] = []
    changed = _content(payload)
    with pytest.raises(ValueError, match="source, support, and contradiction"):
        load_registered_transmission_registry(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )
    content = build_reference_artifact_bytes()
    expired = load_registered_transmission_registry(
        content,
        _artifact(content),
        as_of_utc="2026-07-27T00:00:00Z",
    )
    assert not expired.active_transmission_ids
    assert expired.expired_transmission_ids == (
        "transmission.ashare.policy.001",
        "transmission.ashare.policy.002",
    )


def test_d6_snapshot_is_reproducible_and_non_authorizing() -> None:
    content = build_reference_artifact_bytes()
    first = load_registered_transmission_registry(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    second = load_registered_transmission_registry(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    assert first == second
    assert first.snapshot_hash == second.snapshot_hash
    assert first.operator_review_required and first.read_only
    assert not any(
        (
            first.calculation_allowed,
            first.scoring_allowed,
            first.causal_truth_authority,
            first.account_authority,
            first.execution_authority,
        )
    )
