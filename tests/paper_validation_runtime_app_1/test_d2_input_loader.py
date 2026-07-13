import hashlib
import json
from pathlib import Path

import pytest

from apps.paper_validation_runtime_app_1.domain import (
    ComparisonPolicy,
    EvaluationWindow,
    ValidationRunRequest,
)
from apps.paper_validation_runtime_app_1.input_loader import (
    ArtifactRegistryEntry,
    load_registered_validation_dataset,
)


def _window() -> EvaluationWindow:
    return EvaluationWindow(
        window_id="window-001",
        start_time_utc="2026-01-01T00:00:00Z",
        decision_cutoff_utc="2026-01-31T00:00:00Z",
        observation_cutoff_utc="2026-02-28T00:00:00Z",
        end_time_utc="2026-02-28T00:00:00Z",
    )


def _policy() -> ComparisonPolicy:
    return ComparisonPolicy(
        policy_id="policy-001",
        minimum_eligible_samples=1,
        minimum_candidate_coverage=0.5,
        maximum_mae_regression=0.0,
        minimum_accuracy_delta=0.0,
    )


def _request() -> ValidationRunRequest:
    return ValidationRunRequest(
        run_id="run-001",
        correlation_id="corr-001",
        artifact_id="artifact-001",
        artifact_version="v1",
        window=_window(),
        policy=_policy(),
        operator_trigger_id="operator-trigger-001",
    )


def _payload() -> dict:
    return {
        "artifact_id": "artifact-001",
        "artifact_version": "v1",
        "correlation_id": "corr-001",
        "content_type": "paper_validation_samples",
        "evaluation_window": {
            "window_id": "window-001",
            "start_time_utc": "2026-01-01T00:00:00Z",
            "decision_cutoff_utc": "2026-01-31T00:00:00Z",
            "observation_cutoff_utc": "2026-02-28T00:00:00Z",
            "end_time_utc": "2026-02-28T00:00:00Z",
        },
        "samples": [
            {
                "sample_id": "sample-001",
                "segment": "large_cap",
                "decision_time_utc": "2026-01-20T00:00:00Z",
                "outcome_time_utc": "2026-02-10T00:00:00Z",
                "baseline_score": 0.55,
                "candidate_score": 0.75,
                "actual_outcome": 1.0,
                "eligible": True,
                "exclusion_reason": "",
            },
            {
                "sample_id": "sample-002",
                "segment": "small_cap",
                "decision_time_utc": "2026-01-21T00:00:00Z",
                "outcome_time_utc": "2026-02-11T00:00:00Z",
                "baseline_score": 0.45,
                "candidate_score": None,
                "actual_outcome": 0.0,
                "eligible": True,
                "exclusion_reason": "",
            },
        ],
    }


def _write_artifact(root: Path, payload: dict) -> tuple[Path, str]:
    path = root / "artifact.json"
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    path.write_bytes(raw)
    return path, hashlib.sha256(raw).hexdigest()


def _entry(digest: str) -> ArtifactRegistryEntry:
    return ArtifactRegistryEntry(
        artifact_id="artifact-001",
        artifact_version="v1",
        correlation_id="corr-001",
        relative_path="artifact.json",
        content_sha256=digest,
    )


def test_loader_accepts_registered_local_artifact(tmp_path: Path) -> None:
    _, digest = _write_artifact(tmp_path, _payload())

    dataset = load_registered_validation_dataset(
        request=_request(),
        registry_entry=_entry(digest),
        allowed_root=tmp_path,
    )

    assert dataset.artifact.artifact_id == "artifact-001"
    assert dataset.source_sha256 == digest
    assert len(dataset.samples) == 2
    assert dataset.samples[1].candidate_score is None
    assert dataset.operator_review_required is True
    assert dataset.paper_only is True
    assert dataset.read_only_source is True


def test_loader_rejects_sha256_mismatch(tmp_path: Path) -> None:
    _write_artifact(tmp_path, _payload())

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_registered_validation_dataset(
            request=_request(),
            registry_entry=_entry("0" * 64),
            allowed_root=tmp_path,
        )


def test_loader_rejects_path_outside_allowed_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    digest = hashlib.sha256(outside.read_bytes()).hexdigest()
    entry = ArtifactRegistryEntry(
        artifact_id="artifact-001",
        artifact_version="v1",
        correlation_id="corr-001",
        relative_path="../outside.json",
        content_sha256=digest,
    )

    with pytest.raises(ValueError, match="outside the allowed local root"):
        load_registered_validation_dataset(
            request=_request(),
            registry_entry=entry,
            allowed_root=allowed,
        )


def test_loader_rejects_decision_time_after_cutoff(tmp_path: Path) -> None:
    payload = _payload()
    payload["samples"][0]["decision_time_utc"] = "2026-02-01T00:00:00Z"
    _, digest = _write_artifact(tmp_path, payload)

    with pytest.raises(ValueError, match="decision exceeds decision cutoff"):
        load_registered_validation_dataset(
            request=_request(),
            registry_entry=_entry(digest),
            allowed_root=tmp_path,
        )


def test_loader_rejects_outcome_after_observation_cutoff(tmp_path: Path) -> None:
    payload = _payload()
    payload["samples"][0]["outcome_time_utc"] = "2026-03-01T00:00:00Z"
    _, digest = _write_artifact(tmp_path, payload)

    with pytest.raises(ValueError, match="outcome exceeds observation cutoff"):
        load_registered_validation_dataset(
            request=_request(),
            registry_entry=_entry(digest),
            allowed_root=tmp_path,
        )


def test_loader_rejects_duplicate_sample_id(tmp_path: Path) -> None:
    payload = _payload()
    payload["samples"][1]["sample_id"] = "sample-001"
    _, digest = _write_artifact(tmp_path, payload)

    with pytest.raises(ValueError, match="sample_id values must be unique"):
        load_registered_validation_dataset(
            request=_request(),
            registry_entry=_entry(digest),
            allowed_root=tmp_path,
        )
