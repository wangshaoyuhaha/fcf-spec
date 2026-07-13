import json
from pathlib import Path

import pytest

from apps.shadow_observation_runtime_app_1 import (
    ObservationPolicy,
    ObservationWindow,
    RegisteredObservationArtifact,
    ShadowObservationRequest,
    load_registered_observation_dataset,
    sha256_file,
)


def _payload():
    return {
        "schema_version": "shadow_observation.v1",
        "artifact": {
            "artifact_id": "artifact-1",
            "artifact_version": "v1",
            "correlation_id": "corr-1",
        },
        "observation_window": {
            "window_id": "window-1",
            "decision_time_utc": "2026-01-01T00:00:00Z",
            "observation_start_utc": "2026-01-02T00:00:00Z",
            "observation_cutoff_utc": "2026-01-10T00:00:00Z",
        },
        "records": [
            {
                "record_id": "record-1",
                "correlation_id": "corr-1",
                "segment": "equity",
                "decision_time_utc": "2026-01-01T00:00:00Z",
                "observation_time_utc": "2026-01-03T00:00:00Z",
                "baseline_score": 0.6,
                "candidate_score": 0.7,
                "actual_outcome": 1.0,
                "risk_flags": [],
                "contradiction_evidence": [],
            }
        ],
    }


def _request(
    relative_path: str,
    digest: str,
):
    return ShadowObservationRequest(
        run_id="run-1",
        correlation_id="corr-1",
        operator_trigger_id="operator-trigger-1",
        artifact=RegisteredObservationArtifact(
            artifact_id="artifact-1",
            artifact_version="v1",
            correlation_id="corr-1",
            content_sha256=digest,
            relative_path=relative_path,
        ),
        window=ObservationWindow(
            window_id="window-1",
            decision_time_utc="2026-01-01T00:00:00Z",
            observation_start_utc="2026-01-02T00:00:00Z",
            observation_cutoff_utc="2026-01-10T00:00:00Z",
        ),
        policy=ObservationPolicy(
            policy_id="policy-1",
            minimum_observed_outcomes=1,
            minimum_candidate_coverage=1.0,
            maximum_candidate_mae_regression=0.1,
            required_segments=("equity",),
        ),
    )


def test_d2_loads_registered_local_dataset(tmp_path: Path):
    path = tmp_path / "shadow.json"
    path.write_text(
        json.dumps(_payload(), sort_keys=True),
        encoding="utf-8",
    )
    request = _request("shadow.json", sha256_file(path))

    dataset = load_registered_observation_dataset(
        request,
        tmp_path,
    )

    assert dataset.source_sha256 == request.artifact.content_sha256
    assert dataset.records[0].record_id == "record-1"
    assert dataset.operator_review_required is True
    assert dataset.read_only_source is True


def test_d2_rejects_hash_mismatch(tmp_path: Path):
    path = tmp_path / "shadow.json"
    path.write_text(
        json.dumps(_payload()),
        encoding="utf-8",
    )
    request = _request("shadow.json", "0" * 64)

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_registered_observation_dataset(
            request,
            tmp_path,
        )


def test_d2_rejects_path_outside_allowed_root(tmp_path: Path):
    root = tmp_path / "allowed"
    root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text(
        json.dumps(_payload()),
        encoding="utf-8",
    )
    request = _request("../outside.json", sha256_file(outside))

    with pytest.raises(ValueError, match="outside the allowed"):
        load_registered_observation_dataset(
            request,
            root,
        )


def test_d2_rejects_observation_outside_window(tmp_path: Path):
    payload = _payload()
    payload["records"][0]["observation_time_utc"] = (
        "2026-01-11T00:00:00Z"
    )
    path = tmp_path / "shadow.json"
    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    request = _request("shadow.json", sha256_file(path))

    with pytest.raises(ValueError, match="outside the observation window"):
        load_registered_observation_dataset(
            request,
            tmp_path,
        )
