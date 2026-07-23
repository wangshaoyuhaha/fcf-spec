from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from types import MappingProxyType

import pytest

from apps.fcp_0097_registered_target_label_registry_runtime_app_1 import (
    RegisteredTargetLabelArtifact,
    build_reference_artifact_bytes,
    load_registered_target_label_registry,
)


OBSERVED = "2026-07-23T15:00:00Z"


def _artifact(content: bytes) -> RegisteredTargetLabelArtifact:
    return RegisteredTargetLabelArtifact(
        artifact_id="registered-target-label-registry-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-23T14:00:00Z",
    )


def _payload() -> dict[str, object]:
    return json.loads(build_reference_artifact_bytes())


def _content(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def test_d1_exact_registered_artifact_is_required() -> None:
    content = build_reference_artifact_bytes()
    artifact = _artifact(content)
    with pytest.raises(ValueError, match="byte length"):
        load_registered_target_label_registry(
            content,
            replace(artifact, byte_length=1),
            observed_at_utc=OBSERVED,
        )
    with pytest.raises(ValueError, match="hash mismatch"):
        load_registered_target_label_registry(
            content,
            replace(artifact, artifact_hash="2" * 64),
            observed_at_utc=OBSERVED,
        )


def test_d2_closed_ascii_schema_is_enforced() -> None:
    payload = _payload()
    payload["unexpected"] = True
    changed = _content(payload)
    with pytest.raises(ValueError, match="closed registered schema"):
        load_registered_target_label_registry(
            changed,
            _artifact(changed),
            observed_at_utc=OBSERVED,
        )
    non_ascii = b'{"name":"\xff"}'
    with pytest.raises(ValueError, match="ASCII JSON"):
        load_registered_target_label_registry(
            non_ascii,
            _artifact(non_ascii),
            observed_at_utc=OBSERVED,
        )


def test_d3_target_and_label_indexes_are_deterministic_and_immutable() -> None:
    content = build_reference_artifact_bytes()
    snapshot = load_registered_target_label_registry(
        content,
        _artifact(content),
        observed_at_utc=OBSERVED,
    )
    assert tuple(snapshot.target_record_hashes) == (
        "target.return.next-session@v1",
        "target.volatility.five-session@v1",
    )
    assert snapshot.target_to_label_refs["target.return.next-session@v1"] == (
        "label.return.next-session@v1",
    )
    assert isinstance(snapshot.label_to_target_ref, MappingProxyType)
    with pytest.raises(TypeError):
        snapshot.label_to_target_ref["x"] = "y"  # type: ignore[index]


def test_d4_missing_target_and_unlabelled_target_fail_closed() -> None:
    payload = _payload()
    labels = payload["labels"]
    assert isinstance(labels, list)
    labels[0]["target_ref"] = "target.missing@v1"
    changed = _content(payload)
    with pytest.raises(ValueError, match="same artifact"):
        load_registered_target_label_registry(
            changed,
            _artifact(changed),
            observed_at_utc=OBSERVED,
        )

    payload = _payload()
    labels = payload["labels"]
    assert isinstance(labels, list)
    labels.pop()
    changed = _content(payload)
    with pytest.raises(ValueError, match="at least one label"):
        load_registered_target_label_registry(
            changed,
            _artifact(changed),
            observed_at_utc=OBSERVED,
        )


def test_d5_duplicate_targets_and_labels_fail_closed() -> None:
    payload = _payload()
    targets = payload["targets"]
    assert isinstance(targets, list)
    targets.append(dict(targets[0]))
    changed = _content(payload)
    with pytest.raises(ValueError, match="already registered|unique"):
        load_registered_target_label_registry(
            changed,
            _artifact(changed),
            observed_at_utc=OBSERVED,
        )

    payload = _payload()
    labels = payload["labels"]
    assert isinstance(labels, list)
    labels.append(dict(labels[0]))
    changed = _content(payload)
    with pytest.raises(ValueError, match="label references must be unique"):
        load_registered_target_label_registry(
            changed,
            _artifact(changed),
            observed_at_utc=OBSERVED,
        )


def test_d6_snapshot_is_reproducible_and_non_authorizing() -> None:
    content = build_reference_artifact_bytes()
    artifact = _artifact(content)
    first = load_registered_target_label_registry(
        content,
        artifact,
        observed_at_utc=OBSERVED,
    )
    second = load_registered_target_label_registry(
        content,
        artifact,
        observed_at_utc=OBSERVED,
    )
    assert first == second
    assert first.snapshot_hash == second.snapshot_hash
    assert first.operator_review_required
    assert first.read_only
    assert not any(
        (
            first.target_selection_allowed,
            first.label_materialization_allowed,
            first.scoring_allowed,
            first.promotion_allowed,
            first.account_authority,
            first.execution_authority,
        )
    )
