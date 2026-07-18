from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
    InstitutionalCalendarSource,
)
from apps.v2_r32_local_institutional_crowding_foundation_app_1 import (
    InstitutionalCrowdingRecord,
    LocalInstitutionalCrowdingRegistry,
    RegisteredInstitutionalHoldingDisclosure,
    V2_R32_LOCAL_INSTITUTIONAL_CROWDING_BOUNDARY,
    V2R32LocalInstitutionalCrowdingBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_institutional_crowding,
)


def _event() -> InstitutionalCalendarEvent:
    source = InstitutionalCalendarSource(
        source_id="official-disclosure-source",
        source_kind="OFFICIAL",
        registered_artifact_id="institutional-holding-artifact",
        artifact_version="v1",
        license_id="local-license",
        permitted_use="local-paper-research",
        retention_days=3650,
    )
    return InstitutionalCalendarEvent(
        record_id="institutional-disclosure-event-r0",
        calendar_id="disclosure-calendar-v1",
        event_id="institutional-disclosure-event",
        event_type="MARKET_STRUCTURE_EVENT",
        market="a-share",
        horizon="quarterly",
        event_at_utc="2026-01-01T00:00:00Z",
        publication_at_utc="2026-01-10T00:00:00Z",
        first_legally_available_at_utc="2026-01-10T00:00:00Z",
        retrieved_at_utc="2026-01-10T00:01:00Z",
        ingested_at_utc="2026-01-10T00:02:00Z",
        first_tradable_at_utc="2026-01-10T01:30:00Z",
        source=source,
        content_sha256="f" * 64,
    )


def _disclosure(fund_id: str = "fund-a", **changes: object):
    values: dict[str, object] = {
        "disclosure_id": f"disclosure-{fund_id}",
        "subject_id": "issuer-000001",
        "market": "a-share",
        "fund_id": fund_id,
        "report_period_end_utc": "2026-01-01T00:00:00Z",
        "published_at_utc": "2026-01-10T00:00:00Z",
        "available_at_utc": "2026-01-10T00:02:00Z",
        "shares_held": "30" if fund_id == "fund-a" else "10",
        "prior_shares_held": "20",
        "free_float_shares": "100",
        "average_daily_traded_shares": "20",
        "source_event": _event(),
    }
    values.update(changes)
    return RegisteredInstitutionalHoldingDisclosure(**values)  # type: ignore[arg-type]


def _registry() -> LocalInstitutionalCrowdingRegistry:
    first, second = _disclosure(), _disclosure("fund-b")
    record = InstitutionalCrowdingRecord(
        record_id="crowding-record-r0",
        disclosures=(first, second),
        available_at_utc="2026-01-11T00:02:00Z",
    )
    return (
        LocalInstitutionalCrowdingRegistry()
        .append_disclosure(first)
        .append_disclosure(second)
        .append_record(record)
    )


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R32_LOCAL_INSTITUTIONAL_CROWDING_BOUNDARY
    assert not boundary.current_manager_action_inference_allowed
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R32LocalInstitutionalCrowdingBoundary(
            quarter_end_motive_inference_allowed=True
        )
    with pytest.raises(FrozenInstanceError):
        boundary.manipulation_claim_allowed = True  # type: ignore[misc]


def test_d2_requires_registered_r23_evidence():
    with pytest.raises(ValueError, match="registered R23"):
        _disclosure(source_event=object())


def test_d2_rejects_holding_above_free_float():
    with pytest.raises(ValueError, match="cannot exceed free float"):
        _disclosure(shares_held="101")


def test_d2_non_observed_disclosure_is_explicit():
    item = _disclosure(
        disclosure_state="MISSING",
        missing_fields=("registered-holding-values",),
        shares_held=None,
        prior_shares_held=None,
        free_float_shares=None,
        average_daily_traded_shares=None,
    )
    assert item.disclosure_state == "MISSING"


def test_d3_metrics_are_deterministic():
    record = _registry().records[0]
    assert (
        record.disclosed_ownership_bps,
        record.normalized_concentration_bps,
        record.ownership_change_bps,
        record.exit_days_milli,
        record.disclosure_age_days,
    ) == (4000, 6250, 0, 2000, 10)


def test_d3_duplicate_fund_is_rejected():
    first = _disclosure()
    with pytest.raises(ValueError, match="one disclosure per fund"):
        InstitutionalCrowdingRecord(
            record_id="duplicate-fund-record",
            disclosures=(first, replace(first, disclosure_id="other-disclosure")),
            available_at_utc="2026-01-11T00:02:00Z",
        )


def test_d3_no_action_motive_manipulation_or_factor_claim():
    record = _registry().records[0]
    with pytest.raises(ValueError, match="current manager action"):
        replace(record, current_manager_action_inference=True)
    with pytest.raises(ValueError, match="quarter-end motive"):
        replace(record, quarter_end_motive_inference=True)
    with pytest.raises(ValueError, match="manipulation"):
        replace(record, manipulation_claim=True)
    with pytest.raises(ValueError, match="activate"):
        replace(record, factor_activated=True)


def test_d3_registry_requires_registered_parent_disclosures():
    record = _registry().records[0]
    with pytest.raises(ValueError, match="must be registered"):
        LocalInstitutionalCrowdingRegistry(records=(record,))


def test_d4_missing_resolver_state():
    snapshot = resolve_institutional_crowding(
        LocalInstitutionalCrowdingRegistry(),
        subject_id="issuer-000001",
        market="a-share",
        as_of_utc="2026-01-12T00:00:00Z",
    )
    assert snapshot.state == "MISSING_DISCLOSURE"


def test_d5_future_metrics_are_hidden():
    snapshot = resolve_institutional_crowding(
        _registry(),
        subject_id="issuer-000001",
        market="a-share",
        as_of_utc="2026-01-10T12:00:00Z",
    )
    assert snapshot.state == "MISSING_METRICS"


def test_d5_conflict_state_is_preserved():
    item = _disclosure(
        disclosure_state="CONFLICT",
        missing_fields=("conflicting-holding-values",),
        shares_held=None,
        prior_shares_held=None,
        free_float_shares=None,
        average_daily_traded_shares=None,
    )
    registry = LocalInstitutionalCrowdingRegistry().append_disclosure(item)
    snapshot = resolve_institutional_crowding(
        registry,
        subject_id="issuer-000001",
        market="a-share",
        as_of_utc="2026-01-12T00:00:00Z",
    )
    assert snapshot.state == "CONFLICT"


def test_d5_disclosure_latency_is_preserved():
    snapshot = resolve_institutional_crowding(
        _registry(),
        subject_id="issuer-000001",
        market="a-share",
        as_of_utc="2026-01-12T00:00:00Z",
    )
    assert "DISCLOSURE_LATENCY_PRESERVED" in snapshot.reason_codes


def test_d6_presentation_and_acceptance_are_read_only():
    registry = _registry()
    snapshot = resolve_institutional_crowding(
        registry,
        subject_id="issuer-000001",
        market="a-share",
        as_of_utc="2026-01-12T00:00:00Z",
    )
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(snapshot)
    assert snapshot.state == "RESOLVED"
    assert isinstance(model.payload, MappingProxyType)
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["quarter_end_motive_inference"] = True  # type: ignore[index]
