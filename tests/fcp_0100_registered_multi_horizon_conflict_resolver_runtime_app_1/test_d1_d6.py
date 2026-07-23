from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from types import MappingProxyType

import pytest

from apps.fcp_0100_registered_multi_horizon_conflict_resolver_runtime_app_1 import (
    REFERENCE_AS_OF_UTC,
    RegisteredConflictArtifact,
    build_reference_artifact_bytes,
    load_registered_conflict_registry,
)


def _artifact(content: bytes) -> RegisteredConflictArtifact:
    return RegisteredConflictArtifact(
        artifact_id="registered-multi-horizon-conflict-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-24T01:10:00Z",
    )


def _payload() -> dict[str, object]:
    return json.loads(build_reference_artifact_bytes())


def _content(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def test_d1_exact_registered_artifact_is_required() -> None:
    content = build_reference_artifact_bytes()
    artifact = _artifact(content)
    with pytest.raises(ValueError, match="byte length"):
        load_registered_conflict_registry(
            content,
            replace(artifact, byte_length=1),
            as_of_utc=REFERENCE_AS_OF_UTC,
        )
    with pytest.raises(ValueError, match="hash mismatch"):
        load_registered_conflict_registry(
            content,
            replace(artifact, artifact_hash="2" * 64),
            as_of_utc=REFERENCE_AS_OF_UTC,
        )


def test_d2_closed_ascii_schema_is_enforced() -> None:
    payload = _payload()
    payload["unexpected"] = True
    changed = _content(payload)
    with pytest.raises(ValueError, match="closed registered schema"):
        load_registered_conflict_registry(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )
    non_ascii = b'{"name":"\xff"}'
    with pytest.raises(ValueError, match="ASCII JSON"):
        load_registered_conflict_registry(
            non_ascii, _artifact(non_ascii), as_of_utc=REFERENCE_AS_OF_UTC
        )


def test_d3_horizons_are_preserved_without_mixed_score() -> None:
    content = build_reference_artifact_bytes()
    snapshot = load_registered_conflict_registry(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    rows = snapshot.presentation_rows["conflict-set.ashare.600000.v1"]
    assert rows == (
        ("EQUITY_MEDIUM", "SUPPORTING", "result.ashare.medium"),
        ("EQUITY_SHORT", "OPPOSING", "result.ashare.short"),
        ("ASHARE_INTRADAY", "BLOCKED", "result.ashare.intraday"),
    )
    assert snapshot.conflicting_set_ids == ("conflict-set.ashare.600000.v1",)
    assert not snapshot.mixed_score_allowed
    assert not snapshot.consensus_collapse_allowed


def test_d4_duplicate_horizon_and_missing_evidence_fail_closed() -> None:
    payload = _payload()
    sets = payload["conflict_sets"]
    assert isinstance(sets, list)
    sets[0]["results"][1]["horizon_id"] = "EQUITY_MEDIUM"
    changed = _content(payload)
    with pytest.raises(ValueError, match="duplicate horizons"):
        load_registered_conflict_registry(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )
    payload = _payload()
    sets = payload["conflict_sets"]
    assert isinstance(sets, list)
    sets[0]["results"][0]["evidence_hashes"] = []
    changed = _content(payload)
    with pytest.raises(ValueError, match="requires evidence"):
        load_registered_conflict_registry(
            changed, _artifact(changed), as_of_utc=REFERENCE_AS_OF_UTC
        )


def test_d5_stale_missing_and_blocked_are_not_silently_deleted() -> None:
    content = build_reference_artifact_bytes()
    snapshot = load_registered_conflict_registry(
        content,
        _artifact(content),
        as_of_utc="2026-07-26T01:00:00Z",
    )
    groups = snapshot.grouped_result_ids["conflict-set.ashare.600000.v1"]
    assert groups["STALE"] == (
        "result.ashare.medium",
        "result.ashare.short",
    )
    assert groups["BLOCKED"] == ("result.ashare.intraday",)
    btc = snapshot.grouped_result_ids["conflict-set.btc.reference.v1"]
    assert btc["MISSING"] == ("result.btc.short",)


def test_d6_snapshot_is_immutable_reproducible_and_non_authorizing() -> None:
    content = build_reference_artifact_bytes()
    first = load_registered_conflict_registry(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    second = load_registered_conflict_registry(
        content, _artifact(content), as_of_utc=REFERENCE_AS_OF_UTC
    )
    assert first == second
    assert first.snapshot_hash == second.snapshot_hash
    assert isinstance(first.grouped_result_ids, MappingProxyType)
    with pytest.raises(TypeError):
        first.grouped_result_ids["x"] = {}  # type: ignore[index]
    assert first.operator_review_required and first.read_only
    assert not any(
        (
            first.calculation_authority,
            first.account_authority,
            first.execution_authority,
        )
    )
