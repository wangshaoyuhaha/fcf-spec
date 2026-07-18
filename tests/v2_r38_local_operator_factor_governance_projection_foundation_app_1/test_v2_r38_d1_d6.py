from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorDefinition
from apps.v2_r35_local_evidence_integrity_foundation_app_1 import (
    EvidenceFreshnessPolicy,
    LocalEvidenceIntegrityRegistry,
    RegisteredEvidenceArtifact,
    canonical_payload_sha256,
    resolve_evidence_integrity,
)
from apps.v2_r36_local_institutional_factor_lifecycle_foundation_app_1 import (
    InstitutionalFactorCandidate,
    LocalInstitutionalFactorLifecycleRegistry,
    OperatorLifecycleDecision,
    resolve_factor_lifecycle,
)
from apps.v2_r37_local_factor_validation_evidence_foundation_app_1 import (
    VALIDATION_CHECK_TYPES,
    FactorValidationPacket,
    LocalFactorValidationEvidenceRegistry,
    ValidationCheckEvidence,
    resolve_factor_validation,
)
from apps.v2_r38_local_operator_factor_governance_projection_foundation_app_1 import (
    GovernanceProjectionField,
    LocalOperatorFactorGovernanceProjectionRegistry,
    V2_R38_LOCAL_OPERATOR_FACTOR_GOVERNANCE_PROJECTION_BOUNDARY,
    V2R38LocalOperatorFactorGovernanceProjectionBoundary,
    build_governance_projection,
    build_operator_acceptance,
    build_read_model,
)


AS_OF = "2026-07-21T00:00:00Z"


def _candidate(candidate_id: str = "projection-candidate") -> InstitutionalFactorCandidate:
    definition = FactorDefinition(
        factor_id="projection-factor",
        version="v1",
        family="FLOW",
        lifecycle="RESEARCH",
        source_type="REGISTERED_DERIVATION",
        calculation_spec_hash="a" * 64,
        output_unit="basis-points",
        asset_scopes=("a-share",),
        input_field_ids=("registered-flow",),
    )
    return InstitutionalFactorCandidate(
        candidate_id=candidate_id,
        factor_definition=definition,
        hypothesis_id="projection-hypothesis",
        submitted_at_utc="2026-07-01T00:00:00Z",
        expires_at_utc="2026-12-31T00:00:00Z",
        supporting_evidence_hashes=("b" * 64,),
    )


def _evidence_registry() -> LocalEvidenceIntegrityRegistry:
    fields = (("registered-value", "value-1"),)
    record = RegisteredEvidenceArtifact(
        record_id="projection-record",
        evidence_series_id="projection-series",
        evidence_type="factor-governance-input",
        market="a-share",
        horizon="daily",
        source_id="registered-source",
        registered_artifact_id="projection-artifact",
        artifact_version="v1",
        effective_at_utc="2026-07-20T00:00:00Z",
        published_at_utc="2026-07-20T00:01:00Z",
        retrieved_at_utc="2026-07-20T00:02:00Z",
        ingested_at_utc="2026-07-20T00:03:00Z",
        available_at_utc="2026-07-20T00:04:00Z",
        canonical_fields=fields,
        content_sha256=canonical_payload_sha256(fields),
    )
    return LocalEvidenceIntegrityRegistry((record,))


def _evidence(*, max_age_seconds: int = 172800, registry: LocalEvidenceIntegrityRegistry | None = None):
    return resolve_evidence_integrity(
        _evidence_registry() if registry is None else registry,
        evidence_series_id="projection-series",
        market="a-share",
        as_of_utc=AS_OF,
        freshness_policy=EvidenceFreshnessPolicy("projection-freshness", max_age_seconds),
    )


def _lifecycle(*, rejected: bool = False, candidate_id: str = "projection-candidate"):
    candidate = _candidate(candidate_id)
    decisions = ()
    if rejected:
        decisions = (
            OperatorLifecycleDecision(
                decision_id="projection-rejection",
                candidate_id=candidate_id,
                from_state="RESEARCH_PROPOSAL",
                to_state="REJECTED",
                decided_at_utc="2026-07-20T00:00:00Z",
                operator_id="primary-operator",
                rationale_codes=("registered-rejection",),
            ),
        )
    return resolve_factor_lifecycle(
        LocalInstitutionalFactorLifecycleRegistry((candidate,), decisions),
        candidate_id=candidate_id,
        as_of_utc=AS_OF,
    )


def _check(check_type: str, outcome: str = "PASSED") -> ValidationCheckEvidence:
    slug = check_type.lower().replace("_", "-")
    return ValidationCheckEvidence(
        check_id=f"projection-{slug}-check",
        candidate_id="projection-candidate",
        check_type=check_type,
        protocol_id=f"projection-{slug}-protocol",
        dataset_id="projection-dataset",
        evaluation_window_id="projection-holdout",
        evaluated_at_utc="2026-07-20T00:00:00Z",
        evidence_sha256=("c" if outcome == "PASSED" else "d") * 64,
        outcome=outcome,
        reason_codes=(f"projection-{slug}-{outcome.lower()}",),
    )


def _validation(*, failed_type: str | None = None, complete: bool = True):
    check_types = VALIDATION_CHECK_TYPES if complete else VALIDATION_CHECK_TYPES[:1]
    checks = tuple(
        _check(item, "FAILED" if item == failed_type else "PASSED")
        for item in check_types
    )
    registry = LocalFactorValidationEvidenceRegistry(checks=checks)
    if complete:
        registry = registry.append_packet(
            FactorValidationPacket(
                "projection-validation-packet",
                _candidate(),
                checks,
                "2026-07-20T00:01:00Z",
            )
        )
    return resolve_factor_validation(
        registry,
        candidate_id="projection-candidate",
        as_of_utc=AS_OF,
    )


def _projection(**changes: object):
    values = {
        "projection_id": "projection-v1",
        "evidence": _evidence(),
        "lifecycle": _lifecycle(),
        "validation": _validation(),
    }
    values.update(changes)
    return build_governance_projection(**values)  # type: ignore[arg-type]


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R38_LOCAL_OPERATOR_FACTOR_GOVERNANCE_PROJECTION_BOUNDARY
    assert not boundary.projection_mutation_allowed
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R38LocalOperatorFactorGovernanceProjectionBoundary(automatic_approval_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.factor_activation_allowed = True  # type: ignore[misc]


def test_d2_projection_field_requires_explicit_registered_origin():
    with pytest.raises(ValueError, match="origin"):
        GovernanceProjectionField("field", "value", "UNKNOWN", "HIGH", ("a" * 64,))


def test_d2_projection_cannot_create_approval_or_action():
    with pytest.raises(ValueError, match="cannot approve"):
        replace(_projection(), automatic_approval=True)


def test_d2_candidate_identity_mismatch_is_rejected():
    mismatched = replace(_validation(), candidate_id="other-candidate")
    with pytest.raises(ValueError, match="identities do not match"):
        _projection(validation=mismatched)


def test_d3_snapshots_must_share_one_as_of_instant():
    mismatched = replace(_validation(), evaluated_at_utc="2026-07-22T00:00:00Z")
    with pytest.raises(ValueError, match="one as-of"):
        _projection(validation=mismatched)


def test_d3_registry_prevents_same_candidate_as_of_overwrite():
    first = _projection()
    second = replace(first, projection_id="projection-v2")
    with pytest.raises(ValueError, match="cannot be overwritten"):
        LocalOperatorFactorGovernanceProjectionRegistry((first, second))


def test_d4_missing_input_fails_closed():
    missing = _evidence(registry=LocalEvidenceIntegrityRegistry())
    assert _projection(evidence=missing).state == "BLOCKED_MISSING"


def test_d4_stale_evidence_fails_closed():
    assert _projection(evidence=_evidence(max_age_seconds=60)).state == "BLOCKED_INTEGRITY"


def test_d4_terminal_lifecycle_fails_closed():
    assert _projection(lifecycle=_lifecycle(rejected=True)).state == "BLOCKED_LIFECYCLE"


def test_d5_failed_validation_is_preserved():
    projection = _projection(validation=_validation(failed_type="LEAKAGE"))
    assert projection.state == "BLOCKED_VALIDATION"


def test_d5_incomplete_validation_remains_incomplete():
    assert _projection(validation=_validation(complete=False)).state == "INCOMPLETE"


def test_d5_passed_validation_still_requires_operator_review():
    projection = _projection()
    assert projection.state == "REVIEW_REQUIRED"
    assert "NO_FACTOR_ACTIVATION" in projection.reason_codes


def test_d6_presentation_and_acceptance_are_read_only():
    projection = _projection()
    registry = LocalOperatorFactorGovernanceProjectionRegistry().append(projection)
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(projection)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["observed_inferred_explicit"] is True
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["factor_activation"] = True  # type: ignore[index]
