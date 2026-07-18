from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import InstitutionalCalendarEvent, InstitutionalCalendarSource
from apps.v2_r34_local_policy_window_language_evidence_foundation_app_1 import (
    LocalPolicyLanguageEvidenceRegistry,
    PolicyLanguageChangeRecord,
    RegisteredPolicyDocumentObservation,
    V2_R34_LOCAL_POLICY_WINDOW_LANGUAGE_EVIDENCE_BOUNDARY,
    V2R34LocalPolicyWindowLanguageEvidenceBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_policy_language_evidence,
)


def _event(year: int) -> InstitutionalCalendarEvent:
    source = InstitutionalCalendarSource(source_id=f"official-policy-source-{year}", source_kind="OFFICIAL", registered_artifact_id=f"policy-artifact-{year}", artifact_version="v1", license_id="local-license", permitted_use="local-paper-research", retention_days=3650)
    return InstitutionalCalendarEvent(record_id=f"policy-event-r{year}", calendar_id="policy-calendar-v1", event_id=f"july-politburo-{year}", event_type="POLICY_MEETING", market="a-share", horizon="annual", event_at_utc=f"{year}-07-30T00:00:00Z", publication_at_utc=f"{year}-07-30T01:00:00Z", first_legally_available_at_utc=f"{year}-07-30T01:00:00Z", retrieved_at_utc=f"{year}-07-30T01:01:00Z", ingested_at_utc=f"{year}-07-30T01:02:00Z", first_tradable_at_utc=f"{year}-07-31T01:30:00Z", source=source, content_sha256=("b" if year == 2025 else "c") * 64)


def _document(year: int = 2026, **changes: object):
    values: dict[str, object] = {"document_id": f"policy-document-{year}", "document_series_id": "july-politburo-language", "market": "a-share", "horizon": "annual", "window_type": "JULY_POLITBURO", "published_at_utc": f"{year}-07-30T01:00:00Z", "available_at_utc": f"{year}-07-30T01:02:00Z", "content_sha256": ("d" if year == 2025 else "e") * 64, "canonical_tokens": ("economy", "innovation", "stability") if year == 2025 else ("consumption", "economy", "innovation"), "source_event": _event(year)}
    values.update(changes)
    return RegisteredPolicyDocumentObservation(**values)  # type: ignore[arg-type]


def _registry() -> LocalPolicyLanguageEvidenceRegistry:
    prior, current = _document(2025), _document(2026)
    record = PolicyLanguageChangeRecord(record_id="policy-language-change-r0", prior_document=prior, current_document=current, available_at_utc="2026-07-30T01:03:00Z")
    return LocalPolicyLanguageEvidenceRegistry().append_document(prior).append_document(current).append_record(record)


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R34_LOCAL_POLICY_WINDOW_LANGUAGE_EVIDENCE_BOUNDARY
    assert not boundary.semantic_direction_allowed
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R34LocalPolicyWindowLanguageEvidenceBoundary(industry_benefit_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.policy_causation_allowed = True  # type: ignore[misc]


def test_d2_requires_registered_policy_event():
    with pytest.raises(ValueError, match="R23 POLICY_MEETING"):
        _document(source_event=object())


def test_d2_rejects_invalid_digest():
    with pytest.raises(ValueError, match="sha256"):
        _document(content_sha256="invalid")


def test_d2_rejects_duplicate_tokens():
    with pytest.raises(ValueError, match="unique canonical tokens"):
        _document(canonical_tokens=("economy", "economy"))


def test_d2_non_observed_state_is_explicit():
    item = _document(document_state="MISSING", missing_fields=("official-policy-document",), content_sha256=None, canonical_tokens=())
    assert item.document_state == "MISSING"


def test_d3_metrics_are_deterministic():
    item = _registry().records[0]
    assert (item.added_token_count, item.removed_token_count, item.retained_token_count, item.union_token_count, item.novelty_bps, item.retention_bps) == (1, 1, 2, 4, 5000, 6667)


def test_d3_no_semantic_benefit_causation_mapping_or_factor_claim():
    item = _registry().records[0]
    for field, match in (("semantic_direction", "semantic direction"), ("industry_benefit", "industry benefit"), ("policy_causation", "policy causation"), ("automatic_taxonomy_mapping", "taxonomy mapping"), ("factor_activated", "activate")):
        with pytest.raises(ValueError, match=match):
            replace(item, **{field: True})


def test_d3_registry_requires_registered_documents():
    item = _registry().records[0]
    with pytest.raises(ValueError, match="must be registered"):
        LocalPolicyLanguageEvidenceRegistry(records=(item,))


def test_d4_missing_resolver_state():
    snapshot = resolve_policy_language_evidence(LocalPolicyLanguageEvidenceRegistry(), document_series_id="july-politburo-language", market="a-share", as_of_utc="2026-08-01T00:00:00Z")
    assert snapshot.state == "MISSING_DOCUMENT"


def test_d5_future_comparison_is_hidden():
    snapshot = resolve_policy_language_evidence(_registry(), document_series_id="july-politburo-language", market="a-share", as_of_utc="2026-07-30T01:02:30Z")
    assert snapshot.state == "MISSING_COMPARISON"


def test_d5_conflict_state_is_preserved():
    item = _document(document_state="CONFLICT", missing_fields=("conflicting-policy-document",), content_sha256=None, canonical_tokens=())
    snapshot = resolve_policy_language_evidence(LocalPolicyLanguageEvidenceRegistry().append_document(item), document_series_id="july-politburo-language", market="a-share", as_of_utc="2026-08-01T00:00:00Z")
    assert snapshot.state == "CONFLICT"


def test_d5_resolved_state_preserves_no_direction():
    snapshot = resolve_policy_language_evidence(_registry(), document_series_id="july-politburo-language", market="a-share", as_of_utc="2026-08-01T00:00:00Z")
    assert "NO_SEMANTIC_DIRECTION" in snapshot.reason_codes


def test_d6_presentation_and_acceptance_are_read_only():
    registry = _registry()
    snapshot = resolve_policy_language_evidence(registry, document_series_id="july-politburo-language", market="a-share", as_of_utc="2026-08-01T00:00:00Z")
    model, acceptance = build_read_model(registry), build_operator_acceptance(snapshot)
    assert snapshot.state == "RESOLVED" and isinstance(model.payload, MappingProxyType) and acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["industry_benefit"] = True  # type: ignore[index]
