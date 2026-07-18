from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r35_local_evidence_integrity_foundation_app_1 import (
    EvidenceFreshnessPolicy,
    LocalEvidenceIntegrityRegistry,
    RegisteredEvidenceArtifact,
    V2_R35_LOCAL_EVIDENCE_INTEGRITY_BOUNDARY,
    V2R35LocalEvidenceIntegrityBoundary,
    build_operator_acceptance,
    build_read_model,
    canonical_payload_sha256,
    resolve_evidence_integrity,
)


def _artifact(revision: int = 0, predecessor: str | None = None, **changes: object) -> RegisteredEvidenceArtifact:
    fields = (("currency", "cny"), ("value", "seven-point-one"))
    values: dict[str, object] = {
        "record_id": f"fx-fixing-r{revision}",
        "evidence_series_id": "usd-cny-fixing",
        "evidence_type": "fx-fixing",
        "market": "a-share",
        "horizon": "daily",
        "source_id": "official-fx-source",
        "registered_artifact_id": f"fx-artifact-r{revision}",
        "artifact_version": f"v{revision + 1}",
        "effective_at_utc": "2026-07-18T01:00:00Z",
        "published_at_utc": "2026-07-18T01:01:00Z",
        "retrieved_at_utc": "2026-07-18T01:02:00Z",
        "ingested_at_utc": "2026-07-18T01:03:00Z",
        "available_at_utc": f"2026-07-18T01:0{4 + revision}:00Z",
        "canonical_fields": fields,
        "content_sha256": canonical_payload_sha256(tuple(sorted(fields))),
        "revision_number": revision,
        "revises_record_hash": predecessor,
    }
    values.update(changes)
    return RegisteredEvidenceArtifact(**values)  # type: ignore[arg-type]


def _registry() -> LocalEvidenceIntegrityRegistry:
    original = _artifact()
    revised_fields = (("currency", "cny"), ("value", "seven-point-two"))
    revised = _artifact(
        1,
        original.record_hash,
        canonical_fields=revised_fields,
        content_sha256=canonical_payload_sha256(tuple(sorted(revised_fields))),
    )
    return LocalEvidenceIntegrityRegistry().append(original).append(revised)


def _policy(max_age_seconds: int = 3600) -> EvidenceFreshnessPolicy:
    return EvidenceFreshnessPolicy("daily-evidence-freshness", max_age_seconds)


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R35_LOCAL_EVIDENCE_INTEGRITY_BOUNDARY
    assert not boundary.inferred_as_observed_allowed
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R35LocalEvidenceIntegrityBoundary(digest_bypass_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.network_access_allowed = True  # type: ignore[misc]


def test_d2_digest_must_match_canonical_fields():
    with pytest.raises(ValueError, match="digest does not match"):
        _artifact(content_sha256="a" * 64)


def test_d2_observed_evidence_cannot_carry_inference_lineage():
    with pytest.raises(ValueError, match="cannot carry inference lineage"):
        _artifact(derivation_id="derived-method", source_record_hashes=("a" * 64,))


def test_d2_inferred_evidence_requires_derivation_and_sources():
    with pytest.raises(ValueError, match="requires derivation"):
        _artifact(origin="INFERRED")


def test_d3_revision_lineage_is_contiguous_and_hash_linked():
    original = _artifact()
    with pytest.raises(ValueError, match="predecessor hash mismatch"):
        LocalEvidenceIntegrityRegistry((original, _artifact(1, "a" * 64)))


def test_d3_inference_sources_must_already_be_registered():
    fields = (("basis", "normalized"),)
    inferred = _artifact(
        origin="INFERRED",
        derivation_id="registered-deterministic-derivation",
        source_record_hashes=("a" * 64,),
        canonical_fields=fields,
        content_sha256=canonical_payload_sha256(tuple(sorted(fields))),
    )
    with pytest.raises(ValueError, match="already be registered"):
        LocalEvidenceIntegrityRegistry((inferred,))


def test_d3_records_and_registry_are_immutable():
    registry = _registry()
    assert registry.records[0].record_hash != registry.records[1].record_hash
    with pytest.raises(FrozenInstanceError):
        registry.records = ()  # type: ignore[misc]


def test_d4_missing_state_is_explicit():
    snapshot = resolve_evidence_integrity(LocalEvidenceIntegrityRegistry(), evidence_series_id="usd-cny-fixing", market="a-share", as_of_utc="2026-07-18T02:00:00Z", freshness_policy=_policy())
    assert snapshot.state == "MISSING"


def test_d4_future_availability_is_not_visible():
    snapshot = resolve_evidence_integrity(LocalEvidenceIntegrityRegistry((_artifact(),)), evidence_series_id="usd-cny-fixing", market="a-share", as_of_utc="2026-07-18T01:03:30Z", freshness_policy=_policy())
    assert snapshot.state == "FUTURE_ONLY" and snapshot.record is None


def test_d5_stale_evidence_cannot_resolve_as_fresh():
    snapshot = resolve_evidence_integrity(_registry(), evidence_series_id="usd-cny-fixing", market="a-share", as_of_utc="2026-07-18T03:00:00Z", freshness_policy=_policy(60))
    assert snapshot.state == "STALE" and "FRESHNESS_LIMIT_EXCEEDED" in snapshot.reason_codes


def test_d5_observed_state_is_explicit():
    snapshot = resolve_evidence_integrity(_registry(), evidence_series_id="usd-cny-fixing", market="a-share", as_of_utc="2026-07-18T01:10:00Z", freshness_policy=_policy())
    assert snapshot.state == "RESOLVED_OBSERVED" and "OBSERVED_SOURCE_VALUE" in snapshot.reason_codes


def test_d5_inferred_state_cannot_masquerade_as_observed():
    source = _artifact()
    fields = (("basis", "normalized"),)
    inferred = _artifact(
        record_id="fx-derived-r0",
        evidence_series_id="usd-cny-derived",
        evidence_type="fx-derived",
        origin="INFERRED",
        derivation_id="registered-deterministic-derivation",
        source_record_hashes=(source.record_hash,),
        canonical_fields=fields,
        content_sha256=canonical_payload_sha256(tuple(sorted(fields))),
    )
    registry = LocalEvidenceIntegrityRegistry((source, inferred))
    snapshot = resolve_evidence_integrity(registry, evidence_series_id="usd-cny-derived", market="a-share", as_of_utc="2026-07-18T01:10:00Z", freshness_policy=_policy())
    assert snapshot.state == "RESOLVED_INFERRED" and "REGISTERED_INFERENCE" in snapshot.reason_codes


def test_d6_presentation_and_acceptance_are_read_only():
    registry = _registry()
    snapshot = resolve_evidence_integrity(registry, evidence_series_id="usd-cny-fixing", market="a-share", as_of_utc="2026-07-18T01:10:00Z", freshness_policy=_policy())
    model, acceptance = build_read_model(registry), build_operator_acceptance(snapshot)
    assert isinstance(model.payload, MappingProxyType) and acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["digest_bypass"] = True  # type: ignore[index]
