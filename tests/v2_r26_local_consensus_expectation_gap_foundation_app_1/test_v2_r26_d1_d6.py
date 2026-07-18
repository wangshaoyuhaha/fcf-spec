from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
    InstitutionalCalendarSource,
)
from apps.v2_r26_local_consensus_expectation_gap_foundation_app_1 import (
    V2_R26_LOCAL_CONSENSUS_EXPECTATION_GAP_BOUNDARY,
    ConsensusProvider,
    ExpectationGapRecord,
    LocalConsensusExpectationGapRegistry,
    RegisteredActualObservation,
    RegisteredConsensusSnapshot,
    V2R26LocalConsensusExpectationGapBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_consensus_expectation_gap,
)


def _event() -> InstitutionalCalendarEvent:
    source = InstitutionalCalendarSource(
        source_id="registered-official-source",
        source_kind="OFFICIAL",
        registered_artifact_id="registered-earnings-source",
        artifact_version="artifact-v1",
        license_id="official-local-research-license",
        permitted_use="local-paper-research",
        retention_days=3650,
    )
    return InstitutionalCalendarEvent(
        record_id="earnings-event-r0",
        calendar_id="institutional-calendar-v1",
        event_id="earnings-event",
        event_type="EARNINGS_DISCLOSURE",
        market="a-share",
        horizon="earnings-window",
        event_at_utc="2026-01-02T09:00:00Z",
        publication_at_utc="2026-01-02T08:00:00Z",
        first_legally_available_at_utc="2026-01-02T08:01:00Z",
        retrieved_at_utc="2026-01-02T08:02:00Z",
        ingested_at_utc="2026-01-02T08:03:00Z",
        first_tradable_at_utc="2026-01-02T09:00:00Z",
        source=source,
        content_sha256="a" * 64,
    )


def _provider() -> ConsensusProvider:
    return ConsensusProvider(
        provider_id="registered-consensus-provider",
        source_kind="LICENSED",
        registered_artifact_id="registered-consensus-artifact",
        artifact_version="artifact-v1",
        license_id="licensed-local-research",
        permitted_use="local-paper-research",
    )


def _consensus(**changes: object) -> RegisteredConsensusSnapshot:
    values: dict[str, object] = {
        "snapshot_id": "consensus-r0",
        "subject_id": "issuer-000001",
        "metric_id": "adjusted-profit",
        "market": "a-share",
        "horizon": "earnings-window",
        "unit": "cny-million",
        "period_end_utc": "2025-12-31T00:00:00Z",
        "consensus_as_of_utc": "2026-01-02T07:00:00Z",
        "published_at_utc": "2026-01-02T08:05:00Z",
        "first_legally_available_at_utc": "2026-01-02T08:06:00Z",
        "retrieved_at_utc": "2026-01-02T08:07:00Z",
        "ingested_at_utc": "2026-01-02T08:10:00Z",
        "provider": _provider(),
        "source_event": _event(),
        "estimate_count": 12,
        "coverage_bps": 8000,
        "mean_value": "100",
        "median_value": "98",
        "lower_value": "90",
        "upper_value": "110",
        "dispersion_value": "4",
    }
    values.update(changes)
    return RegisteredConsensusSnapshot(**values)  # type: ignore[arg-type]


def _actual(**changes: object) -> RegisteredActualObservation:
    values: dict[str, object] = {
        "observation_id": "actual-r0",
        "subject_id": "issuer-000001",
        "metric_id": "adjusted-profit",
        "market": "a-share",
        "horizon": "earnings-window",
        "unit": "cny-million",
        "value": "106",
        "observed_at_utc": "2026-01-02T09:00:00Z",
        "available_at_utc": "2026-01-02T09:05:00Z",
        "source_event": _event(),
    }
    values.update(changes)
    return RegisteredActualObservation(**values)  # type: ignore[arg-type]


def _registry(
    consensus: RegisteredConsensusSnapshot | None = None,
    actual: RegisteredActualObservation | None = None,
) -> LocalConsensusExpectationGapRegistry:
    consensus = consensus or _consensus()
    actual = actual or _actual()
    gap = ExpectationGapRecord(
        gap_id="expectation-gap-r0",
        consensus=consensus,
        actual=actual,
        available_at_utc="2026-01-02T09:05:00Z",
    )
    return (
        LocalConsensusExpectationGapRegistry()
        .append_consensus(consensus)
        .append_actual(actual)
        .append_gap(gap)
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R26_LOCAL_CONSENSUS_EXPECTATION_GAP_BOUNDARY

    assert boundary.registered_artifact_only is True
    assert boundary.ai_generated_consensus_allowed is False
    assert boundary.consensus_imputation_allowed is False
    assert boundary.future_revision_allowed is False
    assert boundary.factor_activation_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R26LocalConsensusExpectationGapBoundary(ai_generated_consensus_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.factor_activation_allowed = True  # type: ignore[misc]


def test_d2_available_consensus_requires_coverage_range_and_dispersion() -> None:
    with pytest.raises(ValueError, match="estimates and coverage"):
        _consensus(estimate_count=0)
    with pytest.raises(ValueError, match="range must contain median"):
        _consensus(lower_value="100")
    with pytest.raises(ValueError, match="dispersion must be nonnegative"):
        _consensus(dispersion_value="-1")


def test_d2_missing_consensus_is_explicit_and_cannot_carry_numbers() -> None:
    missing = _consensus(
        consensus_state="MISSING",
        estimate_count=0,
        coverage_bps=0,
        mean_value=None,
        median_value=None,
        lower_value=None,
        upper_value=None,
        dispersion_value=None,
    )
    assert missing.consensus_state == "MISSING"
    with pytest.raises(ValueError, match="cannot contain numeric values"):
        replace(missing, median_value="98")


def test_d3_gap_is_deterministic_and_does_not_activate_factor() -> None:
    gap = _registry().gap_records[0]

    assert gap.gap_value == Decimal("8")
    assert gap.standardized_gap == Decimal("2")
    with pytest.raises(ValueError, match="cannot activate a factor"):
        replace(gap, factor_activated=True)


def test_d3_registry_validates_contiguous_revision_lineage() -> None:
    original = _consensus()
    revision = _consensus(
        snapshot_id="consensus-r1",
        revision_number=1,
        revises_snapshot_hash=original.snapshot_hash,
        median_value="99",
        ingested_at_utc="2026-01-02T08:20:00Z",
    )
    registry = (
        LocalConsensusExpectationGapRegistry()
        .append_consensus(original)
        .append_consensus(revision)
    )

    assert registry.consensus_snapshots == (original, revision)
    with pytest.raises(ValueError, match="predecessor is invalid"):
        LocalConsensusExpectationGapRegistry(
            consensus_snapshots=(original, replace(revision, revises_snapshot_hash="b" * 64))
        )


def test_d4_point_in_time_resolution_blocks_future_revision() -> None:
    original = _consensus()
    revision = _consensus(
        snapshot_id="consensus-r1",
        revision_number=1,
        revises_snapshot_hash=original.snapshot_hash,
        median_value="99",
        ingested_at_utc="2026-01-02T10:00:00Z",
        retrieved_at_utc="2026-01-02T09:59:00Z",
        first_legally_available_at_utc="2026-01-02T09:58:00Z",
        published_at_utc="2026-01-02T09:57:00Z",
    )
    registry = _registry(original)
    registry = replace(registry, consensus_snapshots=(original, revision))
    resolved = resolve_consensus_expectation_gap(
        registry,
        subject_id="issuer-000001",
        metric_id="adjusted-profit",
        market="a-share",
        horizon="earnings-window",
        observed_at_utc="2026-01-02T09:05:00Z",
        as_of_utc="2026-01-02T09:05:00Z",
    )

    assert resolved.state == "RESOLVED"
    assert resolved.consensus is original
    assert resolved.available_revision_hashes == (original.snapshot_hash,)


def test_d4_resolution_reports_missing_consensus_and_actual() -> None:
    empty = resolve_consensus_expectation_gap(
        LocalConsensusExpectationGapRegistry(),
        subject_id="issuer-000001",
        metric_id="adjusted-profit",
        market="a-share",
        horizon="earnings-window",
        observed_at_utc="2026-01-02T08:00:00Z",
        as_of_utc="2026-01-02T08:00:00Z",
    )
    before_actual = resolve_consensus_expectation_gap(
        LocalConsensusExpectationGapRegistry().append_consensus(_consensus()),
        subject_id="issuer-000001",
        metric_id="adjusted-profit",
        market="a-share",
        horizon="earnings-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )

    assert empty.state == "MISSING_CONSENSUS"
    assert before_actual.state == "MISSING_ACTUAL"


def test_d5_zero_dispersion_preserves_unavailable_standardization() -> None:
    consensus = _consensus(dispersion_value="0")
    gap = _registry(consensus).gap_records[0]
    snapshot = resolve_consensus_expectation_gap(
        _registry(consensus),
        subject_id="issuer-000001",
        metric_id="adjusted-profit",
        market="a-share",
        horizon="earnings-window",
        observed_at_utc="2026-01-02T09:05:00Z",
        as_of_utc="2026-01-02T09:05:00Z",
    )

    assert gap.standardized_gap is None
    assert "ZERO_DISPERSION_STANDARDIZED_GAP_UNAVAILABLE" in snapshot.reason_codes


def test_d5_future_observation_is_rejected() -> None:
    with pytest.raises(ValueError, match="future observation"):
        resolve_consensus_expectation_gap(
            _registry(),
            subject_id="issuer-000001",
            metric_id="adjusted-profit",
            market="a-share",
            horizon="earnings-window",
            observed_at_utc="2026-01-02T09:06:00Z",
            as_of_utc="2026-01-02T09:05:00Z",
        )


def test_d6_read_model_and_operator_acceptance_are_read_only() -> None:
    registry = _registry()
    snapshot = resolve_consensus_expectation_gap(
        registry,
        subject_id="issuer-000001",
        metric_id="adjusted-profit",
        market="a-share",
        horizon="earnings-window",
        observed_at_utc="2026-01-02T09:05:00Z",
        as_of_utc="2026-01-02T09:05:00Z",
    )
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(snapshot)

    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["ai_generated_consensus"] is False
    assert model.payload["consensus_imputation"] is False
    assert model.payload["factor_activation"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.automatic_approval is False
    assert acceptance.factor_activated is False
    with pytest.raises(TypeError):
        model.payload["consensus_imputation"] = True  # type: ignore[index]
