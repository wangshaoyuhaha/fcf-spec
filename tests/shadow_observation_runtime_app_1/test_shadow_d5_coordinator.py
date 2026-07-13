import json
from dataclasses import replace
from pathlib import Path

import pytest

from apps.shadow_observation_runtime_app_1 import (
    ObservationPolicy,
    ObservationWindow,
    RegisteredObservationArtifact,
    ShadowObservationRequest,
    run_shadow_observation,
    sha256_file,
    write_shadow_runtime_bundle,
)


def _payload():
    return {
        "schema_version": "shadow_observation.v1",
        "artifact": {
            "artifact_id": "artifact-d5",
            "artifact_version": "v1",
            "correlation_id": "corr-d5",
        },
        "observation_window": {
            "window_id": "window-d5",
            "decision_time_utc": "2026-01-01T00:00:00Z",
            "observation_start_utc": "2026-01-02T00:00:00Z",
            "observation_cutoff_utc": "2026-01-10T00:00:00Z",
        },
        "records": [
            {
                "record_id": "record-1",
                "correlation_id": "corr-d5",
                "segment": "equity",
                "decision_time_utc": "2026-01-01T00:00:00Z",
                "observation_time_utc": "2026-01-03T00:00:00Z",
                "baseline_score": 0.6,
                "candidate_score": 0.8,
                "actual_outcome": 1.0,
                "risk_flags": [],
                "contradiction_evidence": [],
            },
            {
                "record_id": "record-2",
                "correlation_id": "corr-d5",
                "segment": "equity",
                "decision_time_utc": "2026-01-01T00:00:00Z",
                "observation_time_utc": "2026-01-04T00:00:00Z",
                "baseline_score": 0.4,
                "candidate_score": 0.2,
                "actual_outcome": 0.0,
                "risk_flags": [],
                "contradiction_evidence": [],
            },
        ],
    }


def _request(
    root: Path,
    run_id="shadow-run-d5",
    minimum_outcomes=2,
):
    path = root / "shadow.json"
    path.write_text(
        json.dumps(
            _payload(),
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    return ShadowObservationRequest(
        run_id=run_id,
        correlation_id="corr-d5",
        operator_trigger_id="operator-d5",
        artifact=RegisteredObservationArtifact(
            artifact_id="artifact-d5",
            artifact_version="v1",
            correlation_id="corr-d5",
            content_sha256=sha256_file(path),
            relative_path="shadow.json",
        ),
        window=ObservationWindow(
            window_id="window-d5",
            decision_time_utc="2026-01-01T00:00:00Z",
            observation_start_utc="2026-01-02T00:00:00Z",
            observation_cutoff_utc="2026-01-10T00:00:00Z",
        ),
        policy=ObservationPolicy(
            policy_id="policy-d5",
            minimum_observed_outcomes=minimum_outcomes,
            minimum_candidate_coverage=1.0,
            maximum_candidate_mae_regression=0.1,
            required_segments=("equity",),
            minimum_segment_outcomes=1,
            maximum_segment_mae_regression=0.1,
        ),
    )


def test_d5_runs_local_shadow_observation_to_review_packet(
    tmp_path: Path,
):
    request = _request(tmp_path)

    outcome = run_shadow_observation(
        request=request,
        allowed_root=tmp_path,
    )

    assert outcome.result_packet.status == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert outcome.lifecycle.state == "REVIEW_PACKET_READY"
    assert outcome.operator_triggered is True
    assert outcome.network_access_used is False
    assert outcome.real_execution_used is False


def test_d5_blocked_observation_finishes_blocked_review_state(
    tmp_path: Path,
):
    request = _request(
        tmp_path,
        minimum_outcomes=3,
    )

    outcome = run_shadow_observation(
        request=request,
        allowed_root=tmp_path,
    )

    assert outcome.result_packet.status == "BLOCKED"
    assert outcome.lifecycle.state == (
        "BLOCKED_REVIEW_REQUIRED"
    )


def test_d5_writes_atomic_bundle_and_manifest(
    tmp_path: Path,
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()

    request = _request(input_root)
    outcome = run_shadow_observation(
        request=request,
        allowed_root=input_root,
    )

    bundle = write_shadow_runtime_bundle(
        outcome=outcome,
        output_root=output_root,
    )

    run_directory = output_root / request.run_id

    assert bundle.reused_existing_bundle is False
    assert (
        run_directory / "observation_result.json"
    ).is_file()
    assert (
        run_directory / "operator_review.json"
    ).is_file()
    assert (
        run_directory / "lifecycle.json"
    ).is_file()
    assert (
        run_directory / "manifest.json"
    ).is_file()

    manifest = json.loads(
        (run_directory / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["archive_status"] == "NOT_ARCHIVED"
    assert manifest["automatic_approval_allowed"] is False
    assert manifest["automatic_promotion_allowed"] is False
    assert manifest["real_execution_allowed"] is False


def test_d5_reuses_identical_existing_bundle(
    tmp_path: Path,
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()

    request = _request(input_root)
    outcome = run_shadow_observation(
        request=request,
        allowed_root=input_root,
    )

    first = write_shadow_runtime_bundle(
        outcome=outcome,
        output_root=output_root,
    )
    second = write_shadow_runtime_bundle(
        outcome=outcome,
        output_root=output_root,
    )

    assert first.reused_existing_bundle is False
    assert second.reused_existing_bundle is True


def test_d5_rejects_tampered_existing_bundle(
    tmp_path: Path,
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()

    request = _request(input_root)
    outcome = run_shadow_observation(
        request=request,
        allowed_root=input_root,
    )

    write_shadow_runtime_bundle(
        outcome=outcome,
        output_root=output_root,
    )

    result_path = (
        output_root
        / request.run_id
        / "observation_result.json"
    )
    result_path.write_text(
        '{"tampered": true}\n',
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="content mismatch",
    ):
        write_shadow_runtime_bundle(
            outcome=outcome,
            output_root=output_root,
        )


def test_d5_rejects_unsafe_run_id(
    tmp_path: Path,
):
    input_root = tmp_path / "input"
    input_root.mkdir()

    request = _request(
        input_root,
        run_id="unsafe/run",
    )
    outcome = run_shadow_observation(
        request=request,
        allowed_root=input_root,
    )

    with pytest.raises(
        ValueError,
        match="unsafe for local output",
    ):
        write_shadow_runtime_bundle(
            outcome=outcome,
            output_root=tmp_path / "output",
        )


def test_d5_runtime_outcome_rejects_prohibited_behavior(
    tmp_path: Path,
):
    request = _request(tmp_path)
    outcome = run_shadow_observation(
        request=request,
        allowed_root=tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="prohibited runtime behavior",
    ):
        replace(
            outcome,
            automatic_promotion_used=True,
        )
