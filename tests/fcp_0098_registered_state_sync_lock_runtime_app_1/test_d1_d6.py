from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from types import MappingProxyType

import pytest

from apps.fcp_0098_registered_state_sync_lock_runtime_app_1 import (
    RegisteredStateSyncArtifact,
    build_reference_artifact_bytes,
    load_registered_state_sync_lock,
)


AS_OF = "2026-07-23T16:10:00Z"


def _artifact(content: bytes) -> RegisteredStateSyncArtifact:
    return RegisteredStateSyncArtifact(
        artifact_id="registered-state-sync-lock-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-23T16:09:00Z",
    )


def _payload() -> dict[str, object]:
    return json.loads(build_reference_artifact_bytes())


def _content(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def test_d1_exact_registered_artifact_is_required() -> None:
    content = build_reference_artifact_bytes()
    artifact = _artifact(content)
    with pytest.raises(ValueError, match="byte length"):
        load_registered_state_sync_lock(content, replace(artifact, byte_length=1), as_of_utc=AS_OF)
    with pytest.raises(ValueError, match="hash mismatch"):
        load_registered_state_sync_lock(
            content,
            replace(artifact, artifact_hash="2" * 64),
            as_of_utc=AS_OF,
        )


def test_d2_closed_ascii_schema_is_enforced() -> None:
    payload = _payload()
    payload["unexpected"] = True
    changed = _content(payload)
    with pytest.raises(ValueError, match="closed registered schema"):
        load_registered_state_sync_lock(changed, _artifact(changed), as_of_utc=AS_OF)
    non_ascii = b'{"name":"\xff"}'
    with pytest.raises(ValueError, match="ASCII JSON"):
        load_registered_state_sync_lock(non_ascii, _artifact(non_ascii), as_of_utc=AS_OF)


def test_d3_lock_view_is_deterministic_and_immutable() -> None:
    content = build_reference_artifact_bytes()
    snapshot = load_registered_state_sync_lock(content, _artifact(content), as_of_utc=AS_OF)
    assert dict(snapshot.current_event_by_instrument) == {
        "BTCUSDT": "event.btc.002",
        "SH600000": "event.ashare.001",
    }
    assert snapshot.superseded_event_ids == ("event.btc.001",)
    assert isinstance(snapshot.anchor_hashes, MappingProxyType)
    with pytest.raises(TypeError):
        snapshot.anchor_hashes["x"] = "y"  # type: ignore[index]


def test_d4_expiry_removes_current_lock() -> None:
    content = build_reference_artifact_bytes()
    snapshot = load_registered_state_sync_lock(
        content,
        _artifact(content),
        as_of_utc="2026-07-23T16:20:00Z",
    )
    assert not snapshot.current_event_by_instrument
    assert snapshot.expired_event_ids == (
        "event.ashare.001",
        "event.btc.001",
        "event.btc.002",
    )


def test_d5_hash_duplicate_and_sequence_drift_fail_closed() -> None:
    payload = _payload()
    anchors = payload["anchors"]
    assert isinstance(anchors, list)
    anchors[0]["state_hash"] = "2" * 64
    changed = _content(payload)
    with pytest.raises(ValueError, match="state_hash"):
        load_registered_state_sync_lock(changed, _artifact(changed), as_of_utc=AS_OF)
    payload = _payload()
    anchors = payload["anchors"]
    assert isinstance(anchors, list)
    anchors[1]["source_sequence"] = anchors[0]["source_sequence"]
    changed = _content(payload)
    with pytest.raises(ValueError, match="state_hash|source sequence"):
        load_registered_state_sync_lock(changed, _artifact(changed), as_of_utc=AS_OF)


def test_d6_snapshot_is_reproducible_and_non_authorizing() -> None:
    content = build_reference_artifact_bytes()
    first = load_registered_state_sync_lock(content, _artifact(content), as_of_utc=AS_OF)
    second = load_registered_state_sync_lock(content, _artifact(content), as_of_utc=AS_OF)
    assert first == second
    assert first.snapshot_hash == second.snapshot_hash
    assert first.operator_review_required and first.read_only
    assert not any(
        (
            first.state_mutation_allowed,
            first.calculation_allowed,
            first.scoring_allowed,
            first.account_authority,
            first.execution_authority,
        )
    )
