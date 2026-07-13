from apps.shadow_observation_runtime_app_1 import (
    LoadedObservationDataset,
    ObservationPolicy,
    ObservationRecord,
    ObservationWindow,
    RegisteredObservationArtifact,
    ShadowObservationRequest,
    evaluate_shadow_observation,
)


def _request(
    minimum_outcomes=2,
    minimum_coverage=1.0,
    maximum_regression=0.1,
):
    return ShadowObservationRequest(
        run_id="run-1",
        correlation_id="corr-1",
        operator_trigger_id="operator-trigger-1",
        artifact=RegisteredObservationArtifact(
            artifact_id="artifact-1",
            artifact_version="v1",
            correlation_id="corr-1",
            content_sha256="a" * 64,
            relative_path="shadow.json",
        ),
        window=ObservationWindow(
            window_id="window-1",
            decision_time_utc="2026-01-01T00:00:00Z",
            observation_start_utc="2026-01-02T00:00:00Z",
            observation_cutoff_utc="2026-01-10T00:00:00Z",
        ),
        policy=ObservationPolicy(
            policy_id="policy-1",
            minimum_observed_outcomes=minimum_outcomes,
            minimum_candidate_coverage=minimum_coverage,
            maximum_candidate_mae_regression=maximum_regression,
            required_segments=("equity",),
            minimum_segment_outcomes=1,
            maximum_segment_mae_regression=maximum_regression,
        ),
    )


def _record(
    record_id,
    baseline_score,
    candidate_score,
    actual_outcome,
    risk_flags=(),
    contradictions=(),
):
    return ObservationRecord(
        record_id=record_id,
        correlation_id="corr-1",
        segment="equity",
        decision_time_utc="2026-01-01T00:00:00Z",
        observation_time_utc="2026-01-03T00:00:00Z",
        baseline_score=baseline_score,
        candidate_score=candidate_score,
        actual_outcome=actual_outcome,
        risk_flags=risk_flags,
        contradiction_evidence=contradictions,
    )


def _dataset(request, records):
    return LoadedObservationDataset(
        request=request,
        records=tuple(records),
        source_path="shadow.json",
        source_sha256="a" * 64,
    )


def test_d3_good_observation_requires_operator_review():
    request = _request()
    dataset = _dataset(
        request,
        (
            _record("r1", 0.6, 0.8, 1.0),
            _record("r2", 0.4, 0.2, 0.0),
        ),
    )

    packet = evaluate_shadow_observation(dataset)

    assert packet.status == "REVIEW_REQUIRED"
    assert packet.summary.observed_outcomes == 2
    assert packet.summary.candidate_coverage == 1.0
    assert packet.operator_review_required is True
    assert packet.automatic_approval_allowed is False
    assert packet.automatic_promotion_allowed is False


def test_d3_insufficient_observations_are_blocked():
    request = _request(minimum_outcomes=3)
    dataset = _dataset(
        request,
        (_record("r1", 0.5, 0.5, 1.0),),
    )

    packet = evaluate_shadow_observation(dataset)

    assert packet.status == "BLOCKED"
    assert "minimum_observed_outcomes_not_met" in packet.blockers


def test_d3_candidate_regression_is_degraded():
    request = _request(maximum_regression=0.05)
    dataset = _dataset(
        request,
        (
            _record("r1", 1.0, 0.0, 1.0),
            _record("r2", 0.0, 1.0, 0.0),
        ),
    )

    packet = evaluate_shadow_observation(dataset)

    assert packet.status == "DEGRADED"
    assert "candidate_mae_regression_exceeded" in packet.warnings


def test_d3_preserves_risk_and_contradiction_evidence():
    request = _request()
    dataset = _dataset(
        request,
        (
            _record(
                "r1",
                0.6,
                0.8,
                1.0,
                risk_flags=("regime_shift",),
                contradictions=("baseline_candidate_conflict",),
            ),
            _record("r2", 0.4, 0.2, 0.0),
        ),
    )

    packet = evaluate_shadow_observation(dataset)

    assert packet.status == "DEGRADED"
    assert packet.risk_flags == ("regime_shift",)
    assert packet.contradiction_evidence == (
        "baseline_candidate_conflict",
    )
    assert "risk_flags_present" in packet.warnings
    assert "contradiction_evidence_present" in packet.warnings
