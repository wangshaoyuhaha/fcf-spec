import pytest

from apps.shadow_observation_runtime_app_1 import (
    SHADOW_OBSERVATION_RUNTIME_BOUNDARY,
    ObservationPolicy,
    ObservationRecord,
    ObservationWindow,
    ShadowRuntimeBoundary,
)


def test_d1_boundary_preserves_authority_and_prohibitions():
    boundary = SHADOW_OBSERVATION_RUNTIME_BOUNDARY

    assert boundary.mode == "shadow_observation"
    assert boundary.local_only is True
    assert boundary.read_only_inputs is True
    assert boundary.passive_observation_only is True
    assert boundary.operator_review_required is True
    assert boundary.deterministic_authority is True
    assert boundary.ai_advisory_only is True
    assert boundary.network_access_allowed is False
    assert boundary.real_execution_allowed is False
    assert boundary.automatic_approval_allowed is False
    assert boundary.automatic_promotion_allowed is False
    assert boundary.automatic_baseline_replacement_allowed is False


def test_d1_prohibited_capability_fails_closed():
    with pytest.raises(
        ValueError,
        match="prohibited runtime capability",
    ):
        ShadowRuntimeBoundary(background_scheduler_allowed=True)


def test_d1_window_requires_forward_time_order():
    with pytest.raises(ValueError, match="observation window"):
        ObservationWindow(
            window_id="window-1",
            decision_time_utc="2026-01-02T00:00:00Z",
            observation_start_utc="2026-01-01T00:00:00Z",
            observation_cutoff_utc="2026-01-03T00:00:00Z",
        )


def test_d1_record_preserves_risk_and_contradiction_evidence():
    record = ObservationRecord(
        record_id="record-1",
        correlation_id="corr-1",
        segment="equity",
        decision_time_utc="2026-01-01T00:00:00Z",
        observation_time_utc="2026-01-02T00:00:00Z",
        baseline_score=0.5,
        candidate_score=0.6,
        actual_outcome=1.0,
        risk_flags=("thin_sample",),
        contradiction_evidence=("candidate_conflicts_with_regime",),
    )

    assert record.risk_flags == ("thin_sample",)
    assert record.contradiction_evidence == (
        "candidate_conflicts_with_regime",
    )


def test_d1_policy_rejects_invalid_candidate_coverage():
    with pytest.raises(ValueError, match="candidate_coverage"):
        ObservationPolicy(
            policy_id="policy-1",
            minimum_observed_outcomes=1,
            minimum_candidate_coverage=1.1,
            maximum_candidate_mae_regression=0.0,
        )
