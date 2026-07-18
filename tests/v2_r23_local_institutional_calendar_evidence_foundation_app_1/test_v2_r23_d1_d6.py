from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    V2_R23_LOCAL_INSTITUTIONAL_CALENDAR_EVIDENCE_BOUNDARY,
    CalendarFreshnessPolicy,
    InstitutionalCalendarEvent,
    InstitutionalCalendarSource,
    LocalInstitutionalCalendarRegistry,
    V2R23LocalInstitutionalCalendarEvidenceBoundary,
    build_operator_acceptance,
    build_read_model,
)


def _source() -> InstitutionalCalendarSource:
    return InstitutionalCalendarSource(
        source_id="registered-official-source",
        source_kind="OFFICIAL",
        registered_artifact_id="registered-calendar-artifact",
        artifact_version="artifact-v1",
        license_id="official-local-research-license",
        permitted_use="local-paper-research",
        retention_days=3650,
    )


def _event(**changes: object) -> InstitutionalCalendarEvent:
    values: dict[str, object] = {
        "record_id": "policy-event-r0",
        "calendar_id": "institutional-calendar-v1",
        "event_id": "policy-event-2026-01",
        "event_type": "POLICY_MEETING",
        "market": "a-share",
        "horizon": "event-window",
        "event_at_utc": "2026-01-02T10:00:00Z",
        "publication_at_utc": "2026-01-02T08:00:00Z",
        "first_legally_available_at_utc": "2026-01-02T08:01:00Z",
        "retrieved_at_utc": "2026-01-02T08:02:00Z",
        "ingested_at_utc": "2026-01-02T08:03:00Z",
        "first_tradable_at_utc": "2026-01-02T08:05:00Z",
        "source": _source(),
        "content_sha256": "a" * 64,
    }
    values.update(changes)
    return InstitutionalCalendarEvent(**values)  # type: ignore[arg-type]


def _revision(original: InstitutionalCalendarEvent) -> InstitutionalCalendarEvent:
    return _event(
        record_id="policy-event-r1",
        publication_at_utc="2026-01-02T09:00:00Z",
        first_legally_available_at_utc="2026-01-02T09:01:00Z",
        retrieved_at_utc="2026-01-02T09:02:00Z",
        ingested_at_utc="2026-01-02T09:03:00Z",
        first_tradable_at_utc="2026-01-02T09:05:00Z",
        content_sha256="b" * 64,
        revision_number=1,
        revision_state="REVISED",
        revises_record_hash=original.record_hash,
    )


def _policy(max_age_seconds: int = 7200) -> CalendarFreshnessPolicy:
    return CalendarFreshnessPolicy(
        policy_id="registered-calendar-freshness-v1",
        max_age_seconds=max_age_seconds,
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R23_LOCAL_INSTITUTIONAL_CALENDAR_EVIDENCE_BOUNDARY

    assert boundary.registered_artifact_only is True
    assert boundary.network_access_allowed is False
    assert boundary.live_calendar_service_allowed is False
    assert boundary.revision_replacement_allowed is False
    assert boundary.factor_or_score_allowed is False
    assert boundary.order_or_execution_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R23LocalInstitutionalCalendarEvidenceBoundary(
            live_calendar_service_allowed=True
        )
    with pytest.raises(FrozenInstanceError):
        boundary.network_access_allowed = True  # type: ignore[misc]


def test_d2_source_rights_are_registered_local_only() -> None:
    with pytest.raises(ValueError, match="exceeds registered-local"):
        replace(_source(), network_retrieval_allowed=True)
    with pytest.raises(ValueError, match="OFFICIAL or LICENSED"):
        replace(_source(), source_kind="UNREGISTERED")
    with pytest.raises(ValueError, match="denies local calendar research"):
        replace(_source(), permitted_use="DENIED")


def test_d2_event_requires_confirmed_evidence_and_ordered_times() -> None:
    with pytest.raises(ValueError, match="confirmed registered evidence"):
        _event(observed_not_inferred=False)
    with pytest.raises(ValueError, match="confirmed registered evidence"):
        _event(confirmed_schedule=False)
    with pytest.raises(ValueError, match="must be ordered"):
        _event(retrieved_at_utc="2026-01-02T07:59:00Z")
    with pytest.raises(ValueError, match="cannot precede legal availability"):
        _event(first_tradable_at_utc="2026-01-02T08:00:00Z")


def test_d2_event_hash_commits_to_source_rights() -> None:
    original = _event()
    changed_rights = _event(
        record_id="policy-event-other-rights",
        source=replace(_source(), retention_days=730),
    )

    assert original.record_hash != changed_rights.record_hash


def test_d3_registry_preserves_contiguous_revision_lineage() -> None:
    original = _event()
    revision = _revision(original)
    registry = LocalInstitutionalCalendarRegistry().append(original).append(revision)

    assert registry.history(original.calendar_id, original.event_id) == (
        original,
        revision,
    )
    with pytest.raises(ValueError, match="predecessor hash mismatch"):
        registry.append(replace(revision, record_id="bad-r2", revision_number=2))
    with pytest.raises(ValueError, match="revision sequence"):
        LocalInstitutionalCalendarRegistry().append(revision)


def test_d3_registry_rejects_duplicate_record_and_identity_change() -> None:
    original = _event()
    registry = LocalInstitutionalCalendarRegistry().append(original)

    with pytest.raises(ValueError, match="duplicate calendar record id"):
        registry.append(original)
    with pytest.raises(ValueError, match="identity cannot change"):
        registry.append(replace(_revision(original), market="btc"))


def test_d4_point_in_time_resolution_does_not_leak_future_revision() -> None:
    original = _event()
    revision = _revision(original)
    registry = LocalInstitutionalCalendarRegistry().append(original).append(revision)

    before_revision = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T08:30:00Z",
        freshness_policy=_policy(),
    )
    before_tradable = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T09:04:00Z",
        freshness_policy=_policy(),
    )
    after_revision = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T09:06:00Z",
        freshness_policy=_policy(),
    )

    assert before_revision.state == "RESOLVED"
    assert before_revision.revision_number == 0
    assert before_tradable.state == "BLOCKED"
    assert before_tradable.reason_codes == ("FIRST_TRADABLE_TIME_NOT_REACHED",)
    assert after_revision.state == "RESOLVED"
    assert after_revision.revision_number == 1


def test_d4_missing_and_cancelled_events_fail_closed() -> None:
    original = _event()
    revision = _revision(original)
    cancelled = _event(
        record_id="policy-event-r2",
        publication_at_utc="2026-01-02T10:00:00Z",
        first_legally_available_at_utc="2026-01-02T10:01:00Z",
        retrieved_at_utc="2026-01-02T10:02:00Z",
        ingested_at_utc="2026-01-02T10:03:00Z",
        first_tradable_at_utc="2026-01-02T10:05:00Z",
        content_sha256="c" * 64,
        revision_number=2,
        revision_state="CANCELLED",
        revises_record_hash=revision.record_hash,
    )
    registry = (
        LocalInstitutionalCalendarRegistry()
        .append(original)
        .append(revision)
        .append(cancelled)
    )

    missing = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T08:00:30Z",
        freshness_policy=_policy(),
    )
    blocked = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T10:06:00Z",
        freshness_policy=_policy(),
    )

    assert missing.state == "MISSING"
    assert missing.reason_codes == ("EVENT_NOT_AVAILABLE_AT_AS_OF",)
    assert blocked.state == "BLOCKED"
    assert blocked.reason_codes == ("LATEST_AVAILABLE_REVISION_CANCELLED",)


def test_d5_stale_evidence_is_blocked_and_hash_is_deterministic() -> None:
    original = _event()
    registry = LocalInstitutionalCalendarRegistry().append(original)
    first = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T09:03:01Z",
        freshness_policy=_policy(max_age_seconds=3600),
    )
    repeated = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T09:03:01Z",
        freshness_policy=_policy(max_age_seconds=3600),
    )

    assert first.state == "BLOCKED"
    assert first.reason_codes == ("REGISTERED_EVIDENCE_STALE",)
    assert first.evidence_hash == repeated.evidence_hash
    with pytest.raises(ValueError, match="stale calendar evidence"):
        replace(_policy(), stale_data_allowed=True)


def test_d5_evidence_hash_commits_to_freshness_threshold() -> None:
    original = _event()
    registry = LocalInstitutionalCalendarRegistry().append(original)
    first = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T08:30:00Z",
        freshness_policy=_policy(max_age_seconds=3600),
    )
    second = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T08:30:00Z",
        freshness_policy=_policy(max_age_seconds=7200),
    )

    assert first.state == second.state == "RESOLVED"
    assert first.evidence_hash != second.evidence_hash


def test_d6_read_model_and_operator_acceptance_are_read_only() -> None:
    original = _event()
    registry = LocalInstitutionalCalendarRegistry().append(original)
    resolution = registry.resolve(
        original.calendar_id,
        original.event_id,
        as_of_utc="2026-01-02T08:30:00Z",
        freshness_policy=_policy(),
    )
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(resolution)

    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["network_source"] is False
    assert model.payload["revision_replacement"] is False
    assert model.payload["factor_or_score"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.automatic_approval is False
    assert acceptance.action_created is False
    with pytest.raises(TypeError):
        model.payload["network_source"] = True  # type: ignore[index]
