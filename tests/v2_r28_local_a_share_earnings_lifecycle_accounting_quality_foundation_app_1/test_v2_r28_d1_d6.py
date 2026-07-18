from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import InstitutionalCalendarEvent, InstitutionalCalendarSource
from apps.v2_r28_local_a_share_earnings_lifecycle_accounting_quality_foundation_app_1 import (
    V2_R28_LOCAL_A_SHARE_EARNINGS_ACCOUNTING_BOUNDARY,
    AccountingQualityChallengeRecord,
    LocalEarningsAccountingQualityRegistry,
    RegisteredAccountingObservation,
    RegisteredEarningsLifecycleStage,
    V2R28LocalAShareEarningsAccountingBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_earnings_accounting_quality,
)


def _event() -> InstitutionalCalendarEvent:
    source = InstitutionalCalendarSource(source_id="official-earnings-source", source_kind="OFFICIAL", registered_artifact_id="earnings-artifact", artifact_version="artifact-v1", license_id="official-local-license", permitted_use="local-paper-research", retention_days=3650)
    return InstitutionalCalendarEvent(record_id="earnings-event-r0", calendar_id="institutional-calendar-v1", event_id="earnings-event", event_type="EARNINGS_DISCLOSURE", market="a-share", horizon="earnings-window", event_at_utc="2026-01-03T09:00:00Z", publication_at_utc="2026-01-03T08:00:00Z", first_legally_available_at_utc="2026-01-03T08:01:00Z", retrieved_at_utc="2026-01-03T08:02:00Z", ingested_at_utc="2026-01-03T08:03:00Z", first_tradable_at_utc="2026-01-03T09:30:00Z", source=source, content_sha256="b" * 64)


def _stage(**changes: object) -> RegisteredEarningsLifecycleStage:
    values: dict[str, object] = {"stage_id": "logic-rebuild-r0", "subject_id": "issuer-000001", "market": "a-share", "horizon": "earnings-window", "stage_kind": "LOGIC_REBUILD", "effective_from_utc": "2026-01-03T09:30:00Z", "effective_to_utc": "2026-01-15T15:00:00Z", "matures_at_utc": "2026-01-16T00:00:00Z", "available_at_utc": "2026-01-03T08:04:00Z", "source_event": _event()}
    values.update(changes)
    return RegisteredEarningsLifecycleStage(**values)  # type: ignore[arg-type]


def _observation(**changes: object) -> RegisteredAccountingObservation:
    values: dict[str, object] = {"observation_id": "accounting-r0", "stage": _stage(), "period_end_utc": "2025-12-31T00:00:00Z", "observed_at_utc": "2026-01-15T15:00:00Z", "available_at_utc": "2026-01-15T15:01:00Z", "reported_profit": "100", "adjusted_profit": "60", "operating_cash_flow": "20", "revenue": "120", "receivables": "60", "gross_profit": "30", "government_grants": "10", "asset_disposal_gains": "15", "other_nonrecurring": "15", "prior_revenue": "100", "prior_receivables": "40", "prior_gross_margin_bps": 3500}
    values.update(changes)
    return RegisteredAccountingObservation(**values)  # type: ignore[arg-type]


def _registry(observation: RegisteredAccountingObservation | None = None) -> LocalEarningsAccountingQualityRegistry:
    observation = observation or _observation()
    challenge = AccountingQualityChallengeRecord(challenge_id="challenge-r0", observation=observation, available_at_utc="2026-01-16T00:01:00Z")
    return LocalEarningsAccountingQualityRegistry().append_stage(observation.stage).append_observation(observation).append_challenge(challenge)


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R28_LOCAL_A_SHARE_EARNINGS_ACCOUNTING_BOUNDARY
    assert boundary.fraud_conclusion_allowed is False
    assert boundary.ai_audit_verdict_allowed is False
    assert boundary.factor_activation_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R28LocalAShareEarningsAccountingBoundary(fraud_conclusion_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.fraud_conclusion_allowed = True  # type: ignore[misc]


def test_d2_stage_requires_registered_kind_and_ordered_times() -> None:
    with pytest.raises(ValueError, match="not registered"):
        _stage(stage_kind="UNKNOWN")
    with pytest.raises(ValueError, match="times must be ordered"):
        _stage(effective_to_utc="2026-01-03T09:00:00Z")


def test_d2_immediate_reaction_requires_r27_lineage() -> None:
    with pytest.raises(ValueError, match="requires R27 reaction evidence"):
        _stage(stage_kind="IMMEDIATE_REACTION")


def test_d2_observed_accounting_requires_complete_measurements() -> None:
    with pytest.raises(ValueError, match="complete measurements"):
        _observation(reported_profit=None)
    with pytest.raises(ValueError, match="revenue values must be positive"):
        _observation(revenue="0")


def test_d2_missing_accounting_is_explicit_and_has_no_partial_values() -> None:
    changes = {name: None for name in ("reported_profit", "adjusted_profit", "operating_cash_flow", "revenue", "receivables", "gross_profit", "government_grants", "asset_disposal_gains", "other_nonrecurring", "prior_revenue", "prior_receivables", "prior_gross_margin_bps")}
    missing = _observation(accounting_state="MISSING", missing_fields=("registered-financial-statements",), **changes)
    assert missing.accounting_state == "MISSING"
    with pytest.raises(ValueError, match="cannot carry partial measurements"):
        replace(missing, reported_profit="1")


def test_d3_challenge_metrics_are_deterministic_and_complete() -> None:
    challenge = _registry().challenges[0]
    assert challenge.nonrecurring_share_bps == 4000
    assert challenge.cash_conversion_bps == 3333
    assert challenge.receivables_growth_spread_bps == 3000
    assert challenge.gross_margin_change_bps == -1000
    assert challenge.challenge_labels == ("NONRECURRING_SHARE_HIGH", "CASH_PROFIT_DIVERGENCE", "RECEIVABLES_GROWTH_PRESSURE", "MARGIN_COMPRESSION")


def test_d3_healthy_observation_preserves_no_registered_challenge() -> None:
    observation = _observation(reported_profit="100", adjusted_profit="95", operating_cash_flow="100", receivables="42", gross_profit="42")
    challenge = AccountingQualityChallengeRecord(challenge_id="challenge-clean", observation=observation, available_at_utc="2026-01-16T00:01:00Z")
    assert challenge.challenge_labels == ("NO_REGISTERED_CHALLENGE",)


def test_d3_challenge_cannot_claim_fraud_or_activate_factor() -> None:
    challenge = _registry().challenges[0]
    with pytest.raises(ValueError, match="fraud conclusion"):
        replace(challenge, fraud_conclusion=True)
    with pytest.raises(ValueError, match="activate a factor"):
        replace(challenge, factor_activated=True)


def test_d3_registry_requires_registered_parent_lineage() -> None:
    observation = _observation()
    with pytest.raises(ValueError, match="stage must be registered"):
        LocalEarningsAccountingQualityRegistry(observations=(observation,))


def test_d4_resolver_preserves_immature_and_missing_states() -> None:
    stage = _stage()
    immature = resolve_earnings_accounting_quality(LocalEarningsAccountingQualityRegistry().append_stage(stage), subject_id="issuer-000001", market="a-share", horizon="earnings-window", as_of_utc="2026-01-15T16:00:00Z")
    missing = resolve_earnings_accounting_quality(LocalEarningsAccountingQualityRegistry(), subject_id="issuer-000001", market="a-share", horizon="earnings-window", as_of_utc="2026-01-17T00:00:00Z")
    assert immature.state == "IMMATURE"
    assert missing.state == "MISSING_STAGE"


def test_d5_future_challenge_is_not_visible_at_as_of() -> None:
    snapshot = resolve_earnings_accounting_quality(_registry(), subject_id="issuer-000001", market="a-share", horizon="earnings-window", as_of_utc="2026-01-16T00:00:30Z")
    assert snapshot.state == "MISSING_CHALLENGE"


def test_d5_stale_accounting_remains_blocked() -> None:
    changes = {name: None for name in ("reported_profit", "adjusted_profit", "operating_cash_flow", "revenue", "receivables", "gross_profit", "government_grants", "asset_disposal_gains", "other_nonrecurring", "prior_revenue", "prior_receivables", "prior_gross_margin_bps")}
    observation = _observation(accounting_state="STALE", missing_fields=("fresh-source",), **changes)
    registry = LocalEarningsAccountingQualityRegistry().append_stage(observation.stage).append_observation(observation)
    snapshot = resolve_earnings_accounting_quality(registry, subject_id="issuer-000001", market="a-share", horizon="earnings-window", as_of_utc="2026-01-17T00:00:00Z")
    assert snapshot.state == "STALE"


def test_d6_read_model_and_operator_acceptance_are_read_only() -> None:
    registry = _registry()
    snapshot = resolve_earnings_accounting_quality(registry, subject_id="issuer-000001", market="a-share", horizon="earnings-window", as_of_utc="2026-01-17T00:00:00Z")
    model, acceptance = build_read_model(registry), build_operator_acceptance(snapshot)
    assert snapshot.state == "RESOLVED"
    assert "NO_FRAUD_CONCLUSION" in snapshot.reason_codes
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["fraud_conclusion"] is False
    assert model.payload["factor_activation"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["fraud_conclusion"] = True  # type: ignore[index]
