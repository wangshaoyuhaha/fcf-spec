import hashlib
import json
from dataclasses import FrozenInstanceError

import pytest

from apps.fcp_0096_registered_factor_registry_runtime_app_1.builder import (
    build_reference_runtime_snapshot,
)
from apps.fcp_0102_registered_factor_normalization_missing_state_runtime_app_1 import (
    RegisteredNormalizationArtifact,
    build_reference_artifact_bytes,
    build_reference_normalization_snapshot,
    normalize_registered_factor_series,
    render_normalization_snapshot_json,
)


def _artifact(content: bytes) -> RegisteredNormalizationArtifact:
    return RegisteredNormalizationArtifact(
        artifact_id="registered-normalization-ready-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-06T00:00:00Z",
    )


def test_d1_exact_registered_ascii_artifact_is_required():
    content = build_reference_artifact_bytes()
    artifact = _artifact(content)
    with pytest.raises(ValueError, match="hash mismatch"):
        normalize_registered_factor_series(
            content,
            RegisteredNormalizationArtifact(
                artifact_id=artifact.artifact_id,
                artifact_hash="f" * 64,
                byte_length=len(content),
                rights_id=artifact.rights_id,
                registered_at_utc=artifact.registered_at_utc,
            ),
            build_reference_runtime_snapshot(),
            as_of_utc="2026-07-06T00:00:00Z",
        )


def test_d2_registered_factor_registry_identity_and_membership_are_required():
    content = build_reference_artifact_bytes()
    payload = json.loads(content)
    payload["factor_definition_ref"] = "unregistered-factor@v1"
    changed = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    with pytest.raises(ValueError, match="not in the registered runtime"):
        normalize_registered_factor_series(
            changed,
            _artifact(changed),
            build_reference_runtime_snapshot(),
            as_of_utc="2026-07-06T00:00:00Z",
        )


def test_d3_foundation_robust_normalization_is_composed_exactly():
    snapshot = build_reference_normalization_snapshot()
    assert snapshot.state == "NORMALIZATION_READY"
    assert dict(snapshot.metrics) == {
        "available_sample_count": "5",
        "mad": "1",
        "median": "3",
        "minimum_samples": "3",
        "robust_z_score": "3",
        "winsorized_value": "6",
    }
    assert snapshot.reason_codes == (
        "REGISTERED_LOCAL_ROBUST_NORMALIZATION_READY",
    )


def test_d4_missing_target_is_preserved_without_zero_fill():
    snapshot = build_reference_normalization_snapshot(target_missing=True)
    assert snapshot.state == "MISSING_STATE_RECORDED"
    assert snapshot.missing_state == "NOT_YET_PUBLISHED"
    assert snapshot.reason_codes == ("TARGET_NOT_YET_PUBLISHED",)
    assert all(
        snapshot.metrics[key] is None
        for key in ("mad", "median", "robust_z_score", "winsorized_value")
    )


def test_d5_future_availability_fails_closed():
    content = build_reference_artifact_bytes()
    snapshot = normalize_registered_factor_series(
        content,
        _artifact(content),
        build_reference_runtime_snapshot(),
        as_of_utc="2026-07-04T00:00:00Z",
    )
    assert snapshot.state == "BLOCKED"
    assert snapshot.reason_codes == ("FUTURE_OBSERVATION_BLOCKED",)


def test_d5_snapshot_and_rendering_are_immutable_and_deterministic():
    first = build_reference_normalization_snapshot()
    second = build_reference_normalization_snapshot()
    assert first.snapshot_hash == second.snapshot_hash
    assert render_normalization_snapshot_json(first) == render_normalization_snapshot_json(
        second
    )
    with pytest.raises(TypeError):
        first.metrics["median"] = "0"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        first.read_only = False  # type: ignore[misc]


def test_d6_output_is_path_free_value_bounded_and_non_authorizing():
    snapshot = build_reference_normalization_snapshot()
    rendered = render_normalization_snapshot_json(snapshot)
    assert "C:\\" not in rendered
    assert snapshot.operator_review_required
    assert snapshot.read_only
    assert snapshot.deterministic_engine_authority
    assert not snapshot.scoring_authority
    assert not snapshot.recommendation_authority
    assert not snapshot.account_authority
    assert not snapshot.execution_authority


def test_d6_reference_hashes_are_exact_sha256():
    snapshot = build_reference_normalization_snapshot()
    assert len(snapshot.snapshot_hash) == 64
    assert len(snapshot.evidence_hash) == 64
    assert hashlib.sha256(
        render_normalization_snapshot_json(snapshot).encode("ascii")
    ).hexdigest()
