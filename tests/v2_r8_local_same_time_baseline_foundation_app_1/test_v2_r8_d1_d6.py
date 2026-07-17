from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r7_local_market_session_registry_foundation_app_1 import (
    SessionResolutionEvidence,
)
from apps.v2_r8_local_same_time_baseline_foundation_app_1 import (
    V2_R8_LOCAL_SAME_TIME_BASELINE_BOUNDARY,
    RegisteredBaselineObservation,
    SameTimeBaselineLedger,
    SameTimeBaselinePolicy,
    V2R8LocalSameTimeBaselineBoundary,
    build_operator_acceptance,
    build_read_model,
    build_same_time_baseline,
)


def _target(*, state: str = "RESOLVED") -> SessionResolutionEvidence:
    return SessionResolutionEvidence(
        registry_id="registered-market-session",
        definition_hash="d" * 64,
        observed_at_utc="2026-01-05T01:05:00Z",
        evaluated_at_utc="2026-01-05T01:05:01Z",
        state=state,
        phase="CONTINUOUS_SESSION" if state == "RESOLVED" else None,
        interval_id="registered-continuous-session" if state == "RESOLVED" else None,
        reason_codes=("REGISTERED_SESSION_RESOLVED",) if state == "RESOLVED" else ("BLOCKED",),
        operator_review_required=True,
        evidence_hash="e" * 64,
    )


def _policy(*, minimum: int = 3) -> SameTimeBaselinePolicy:
    return SameTimeBaselinePolicy(
        baseline_id="registered-same-time-baseline",
        baseline_version="v1",
        feature_id="registered-volume-pace",
        phase="CONTINUOUS_SESSION",
        interval_id="registered-continuous-session",
        slot_index=5,
        regime_id="registered-normal-regime",
        minimum_samples=minimum,
    )


def _observation(
    sequence: int,
    day: int,
    value: str,
    *,
    available_at: str | None = None,
    slot_index: int = 5,
    phase: str = "CONTINUOUS_SESSION",
) -> RegisteredBaselineObservation:
    observed = f"2026-01-{day:02d}T01:05:00Z"
    return RegisteredBaselineObservation(
        observation_id=f"registered-observation-{sequence}",
        session_evidence_hash=f"{sequence}" * 64,
        feature_id="registered-volume-pace",
        phase=phase,
        interval_id="registered-continuous-session",
        slot_index=slot_index,
        regime_id="registered-normal-regime",
        observed_at_utc=observed,
        available_at_utc=available_at or observed,
        value=Decimal(value),
        source_artifact_hash=f"{sequence + 3}" * 64,
    )


def _sample() -> tuple[RegisteredBaselineObservation, ...]:
    return (
        _observation(1, 1, "10"),
        _observation(2, 2, "20"),
        _observation(3, 3, "30"),
    )


def _build(
    observations: tuple[RegisteredBaselineObservation, ...] | None = None,
    *,
    target_state: str = "RESOLVED",
    minimum: int = 3,
):
    return build_same_time_baseline(
        _target(state=target_state),
        _policy(minimum=minimum),
        observations or _sample(),
        as_of_utc="2026-01-05T01:06:00Z",
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R8_LOCAL_SAME_TIME_BASELINE_BOUNDARY

    assert boundary.local_only is True
    assert boundary.factor_activation_allowed is False
    assert boundary.score_or_rank_allowed is False
    assert boundary.order_or_execution_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R8LocalSameTimeBaselineBoundary(score_or_rank_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.network_access_allowed = True  # type: ignore[misc]


def test_d2_policy_rejects_activation_and_mutable_statistics_policies() -> None:
    with pytest.raises(ValueError, match="research-only scope"):
        replace(_policy(), scoring_allowed=True)
    with pytest.raises(ValueError, match="fixed"):
        replace(_policy(), outlier_policy="TRIM")


def test_d2_observation_rejects_availability_before_observation() -> None:
    with pytest.raises(ValueError, match="precedes"):
        _observation(
            1,
            2,
            "10",
            available_at="2026-01-01T01:05:00Z",
        )


def test_d3_same_time_statistics_are_exact_and_deterministic() -> None:
    evidence = _build()
    repeated = _build()

    assert evidence.state == "BASELINE_READY"
    assert evidence.sample_count == 3
    assert evidence.mean == Decimal("20")
    assert evidence.median == Decimal("20")
    assert evidence.minimum == Decimal("10")
    assert evidence.maximum == Decimal("30")
    assert evidence.evidence_hash == repeated.evidence_hash


def test_d3_even_sample_median_is_exact() -> None:
    sample = (*_sample(), _observation(4, 4, "40"))
    evidence = _build(sample, minimum=4)

    assert evidence.mean == Decimal("25")
    assert evidence.median == Decimal("25")


def test_d4_unresolved_target_and_insufficient_sample_are_blocked() -> None:
    unresolved = _build(target_state="BLOCKED")
    insufficient = _build((_sample()[0],), minimum=3)

    assert unresolved.reason_codes == ("TARGET_SESSION_NOT_RESOLVED",)
    assert insufficient.reason_codes == ("INSUFFICIENT_SAMPLE",)
    assert unresolved.mean is None


def test_d4_future_availability_and_nonhistorical_values_are_blocked() -> None:
    future = _build(
        (
            _observation(
                1,
                1,
                "10",
                available_at="2026-01-05T02:00:00Z",
            ),
        ),
        minimum=2,
    )
    nonhistorical = _build(
        (
            _observation(1, 5, "10"),
            _observation(2, 2, "20"),
        ),
        minimum=2,
    )

    assert future.reason_codes == ("FUTURE_AVAILABILITY_BLOCKED",)
    assert nonhistorical.reason_codes == ("NON_HISTORICAL_OBSERVATION_BLOCKED",)


def test_d4_slot_and_phase_mismatch_fail_closed() -> None:
    slot = _build((replace(_sample()[0], slot_index=6),), minimum=2)
    phase = _build(
        (replace(_sample()[0], phase="LATE_SESSION"),),
        minimum=2,
    )

    assert slot.reason_codes == ("SLOT_MISMATCH",)
    assert phase.reason_codes == ("SESSION_PHASE_MISMATCH",)


def test_d5_ledger_rejects_duplicate_baseline_evidence() -> None:
    evidence = _build()
    ledger = SameTimeBaselineLedger().append(evidence)

    with pytest.raises(ValueError, match="duplicate same-time baseline"):
        ledger.append(evidence)


def test_d6_read_model_and_acceptance_do_not_activate_scoring() -> None:
    evidence = _build()
    model = build_read_model(SameTimeBaselineLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)

    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["factor_activated"] is False
    assert model.payload["score_or_rank"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.score_activated is False
    with pytest.raises(TypeError):
        model.payload["score_or_rank"] = True  # type: ignore[index]
