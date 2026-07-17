from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r8_local_same_time_baseline_foundation_app_1 import (
    SameTimeBaselineEvidence,
)
from apps.v2_r9_local_volume_ratio_research_foundation_app_1 import (
    V2_R9_LOCAL_VOLUME_RATIO_RESEARCH_BOUNDARY,
    RegisteredCurrentVolumeObservation,
    V2R9LocalVolumeRatioResearchBoundary,
    VolumeRatioLedger,
    VolumeRatioPolicy,
    build_operator_acceptance,
    build_read_model,
    build_volume_ratio,
)


def _policy(**changes: object) -> VolumeRatioPolicy:
    values: dict[str, object] = {
        "ratio_id": "registered-volume-ratio",
        "ratio_version": "v1",
        "baseline_id": "registered-same-time-volume-baseline",
        "baseline_version": "v1",
        "feature_id": "registered-interval-volume",
        "phase": "CONTINUOUS_SESSION",
        "interval_id": "registered-continuous-session",
        "slot_index": 5,
        "regime_id": "registered-normal-regime",
        "volume_basis": "INTERVAL",
        "baseline_statistic": "MEAN",
        "decimal_places": 4,
    }
    values.update(changes)
    return VolumeRatioPolicy(**values)  # type: ignore[arg-type]


def _observation(**changes: object) -> RegisteredCurrentVolumeObservation:
    values: dict[str, object] = {
        "observation_id": "registered-current-volume",
        "session_evidence_hash": "a" * 64,
        "feature_id": "registered-interval-volume",
        "phase": "CONTINUOUS_SESSION",
        "interval_id": "registered-continuous-session",
        "slot_index": 5,
        "regime_id": "registered-normal-regime",
        "volume_basis": "INTERVAL",
        "observed_at_utc": "2026-01-05T01:05:00Z",
        "available_at_utc": "2026-01-05T01:05:01Z",
        "volume": Decimal("30"),
        "source_artifact_hash": "b" * 64,
    }
    values.update(changes)
    return RegisteredCurrentVolumeObservation(**values)  # type: ignore[arg-type]


def _baseline(**changes: object) -> SameTimeBaselineEvidence:
    values: dict[str, object] = {
        "baseline_id": "registered-same-time-volume-baseline",
        "baseline_version": "v1",
        "target_session_evidence_hash": "a" * 64,
        "state": "BASELINE_READY",
        "sample_count": 3,
        "mean": Decimal("20"),
        "median": Decimal("18"),
        "minimum": Decimal("10"),
        "maximum": Decimal("30"),
        "reason_codes": ("REGISTERED_SAME_TIME_BASELINE_READY",),
        "evaluated_at_utc": "2026-01-05T01:05:02Z",
        "operator_review_required": True,
        "evidence_hash": "c" * 64,
    }
    values.update(changes)
    return SameTimeBaselineEvidence(**values)  # type: ignore[arg-type]


def _build(**changes: object):
    return build_volume_ratio(
        changes.pop("observation", _observation()),
        changes.pop("baseline", _baseline()),
        changes.pop("policy", _policy()),
        as_of_utc=str(changes.pop("as_of_utc", "2026-01-05T01:06:00Z")),
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R9_LOCAL_VOLUME_RATIO_RESEARCH_BOUNDARY

    assert boundary.local_only is True
    assert boundary.factor_activation_allowed is False
    assert boundary.score_or_rank_allowed is False
    assert boundary.order_or_execution_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R9LocalVolumeRatioResearchBoundary(score_or_rank_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.network_access_allowed = True  # type: ignore[misc]


def test_d2_policy_rejects_unsafe_basis_and_activation() -> None:
    with pytest.raises(ValueError, match="INTERVAL or CUMULATIVE"):
        _policy(volume_basis="MIXED")
    with pytest.raises(ValueError, match="research-only scope"):
        _policy(scoring_allowed=True)


def test_d2_current_observation_rejects_negative_and_early_availability() -> None:
    with pytest.raises(ValueError, match="between zero"):
        _observation(volume=Decimal("-1"))
    with pytest.raises(ValueError, match="precedes"):
        _observation(available_at_utc="2026-01-05T01:04:59Z")


def test_d3_mean_ratio_is_exact_rounded_and_deterministic() -> None:
    evidence = _build()
    repeated = _build()

    assert evidence.state == "VOLUME_RATIO_READY"
    assert evidence.current_volume == Decimal("30")
    assert evidence.baseline_value == Decimal("20")
    assert evidence.ratio == Decimal("1.5000")
    assert evidence.evidence_hash == repeated.evidence_hash


def test_d3_median_and_cumulative_basis_are_explicit() -> None:
    policy = _policy(
        baseline_statistic="MEDIAN",
        volume_basis="CUMULATIVE",
        decimal_places=3,
    )
    observation = _observation(volume_basis="CUMULATIVE", volume=Decimal("27"))
    evidence = _build(policy=policy, observation=observation)

    assert evidence.volume_basis == "CUMULATIVE"
    assert evidence.baseline_statistic == "MEDIAN"
    assert evidence.ratio == Decimal("1.500")


def test_d4_unready_and_future_baselines_are_blocked() -> None:
    unready = _build(
        baseline=_baseline(
            state="BLOCKED",
            mean=None,
            median=None,
            minimum=None,
            maximum=None,
        )
    )
    future = _build(baseline=_baseline(evaluated_at_utc="2026-01-05T02:00:00Z"))

    assert unready.reason_codes == ("BASELINE_NOT_READY",)
    assert future.reason_codes == ("FUTURE_BASELINE_BLOCKED",)
    assert unready.ratio is None


def test_d4_future_availability_and_basis_mismatch_are_blocked() -> None:
    future = _build(
        observation=_observation(available_at_utc="2026-01-05T02:00:00Z")
    )
    mismatch = _build(observation=_observation(volume_basis="CUMULATIVE"))

    assert future.reason_codes == ("FUTURE_AVAILABILITY_BLOCKED",)
    assert mismatch.reason_codes == ("VOLUME_BASIS_MISMATCH",)


def test_d4_session_identity_and_zero_baseline_fail_closed() -> None:
    identity = _build(observation=_observation(session_evidence_hash="d" * 64))
    zero = _build(baseline=_baseline(mean=Decimal("0")))

    assert identity.reason_codes == ("SESSION_EVIDENCE_MISMATCH",)
    assert zero.reason_codes == ("ZERO_OR_NEGATIVE_BASELINE_BLOCKED",)


def test_d5_ledger_rejects_duplicate_evidence() -> None:
    evidence = _build()
    ledger = VolumeRatioLedger().append(evidence)

    with pytest.raises(ValueError, match="duplicate volume-ratio"):
        ledger.append(evidence)


def test_d6_read_model_and_acceptance_remain_non_activating() -> None:
    evidence = _build()
    model = build_read_model(VolumeRatioLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)

    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["factor_activated"] is False
    assert model.payload["score_or_rank"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.factor_activated is False
    with pytest.raises(TypeError):
        model.payload["factor_activated"] = True  # type: ignore[index]
