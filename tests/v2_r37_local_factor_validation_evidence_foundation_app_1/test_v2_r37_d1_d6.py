from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorDefinition
from apps.v2_r36_local_institutional_factor_lifecycle_foundation_app_1 import InstitutionalFactorCandidate
from apps.v2_r37_local_factor_validation_evidence_foundation_app_1 import (
    VALIDATION_CHECK_TYPES,
    FactorValidationPacket,
    LocalFactorValidationEvidenceRegistry,
    ValidationCheckEvidence,
    V2_R37_LOCAL_FACTOR_VALIDATION_EVIDENCE_BOUNDARY,
    V2R37LocalFactorValidationEvidenceBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_factor_validation,
)


def _candidate() -> InstitutionalFactorCandidate:
    definition = FactorDefinition(factor_id="validation-factor", version="v1", family="FLOW", lifecycle="RESEARCH", source_type="REGISTERED_DERIVATION", calculation_spec_hash="a" * 64, output_unit="basis-points", asset_scopes=("a-share",), input_field_ids=("registered-flow",))
    return InstitutionalFactorCandidate(candidate_id="validation-candidate", factor_definition=definition, hypothesis_id="validation-hypothesis", submitted_at_utc="2026-07-01T00:00:00Z", expires_at_utc="2026-12-31T00:00:00Z", supporting_evidence_hashes=("b" * 64,))


def _check(check_type: str, outcome: str = "PASSED") -> ValidationCheckEvidence:
    slug = check_type.lower().replace("_", "-")
    return ValidationCheckEvidence(check_id=f"{slug}-check", candidate_id="validation-candidate", check_type=check_type, protocol_id=f"{slug}-protocol", dataset_id="registered-validation-dataset", evaluation_window_id="holdout-window-v1", evaluated_at_utc="2026-07-20T00:00:00Z", evidence_sha256=("c" if outcome == "PASSED" else "d") * 64, outcome=outcome, reason_codes=(f"{slug}-{outcome.lower()}",))


def _checks(failed_type: str | None = None) -> tuple[ValidationCheckEvidence, ...]:
    return tuple(_check(item, "FAILED" if item == failed_type else "PASSED") for item in VALIDATION_CHECK_TYPES)


def _registry(failed_type: str | None = None, include_packet: bool = True) -> LocalFactorValidationEvidenceRegistry:
    checks = _checks(failed_type)
    registry = LocalFactorValidationEvidenceRegistry(checks=checks)
    if include_packet:
        registry = registry.append_packet(FactorValidationPacket("validation-packet-v1", _candidate(), checks, "2026-07-20T00:01:00Z"))
    return registry


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R37_LOCAL_FACTOR_VALIDATION_EVIDENCE_BOUNDARY
    assert not boundary.factor_activation_allowed
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R37LocalFactorValidationEvidenceBoundary(automatic_pass_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.factor_activation_allowed = True  # type: ignore[misc]


def test_d2_unknown_check_type_is_rejected():
    with pytest.raises(ValueError, match="not registered"):
        _check("UNKNOWN")


def test_d2_automatic_pass_is_prohibited():
    with pytest.raises(ValueError, match="automatic"):
        replace(_check("LEAKAGE"), automatic_pass=True)


def test_d2_packet_requires_r36_candidate():
    with pytest.raises(ValueError, match="R36 candidate"):
        FactorValidationPacket("packet", object(), _checks(), "2026-07-20T00:01:00Z")  # type: ignore[arg-type]


def test_d3_packet_requires_exact_seven_class_coverage():
    with pytest.raises(ValueError, match="exact seven-class"):
        FactorValidationPacket("packet", _candidate(), _checks()[:-1], "2026-07-20T00:01:00Z")


def test_d3_failed_check_cannot_be_overwritten():
    failed = _check("LEAKAGE", "FAILED")
    with pytest.raises(ValueError, match="cannot be overwritten"):
        LocalFactorValidationEvidenceRegistry(
            (failed, replace(_check("LEAKAGE"), check_id="leakage-check-replacement"))
        )


def test_d3_packet_checks_must_be_registered():
    packet = FactorValidationPacket("packet", _candidate(), _checks(), "2026-07-20T00:01:00Z")
    with pytest.raises(ValueError, match="must be registered"):
        LocalFactorValidationEvidenceRegistry(packets=(packet,))


def test_d4_missing_validation_state():
    snapshot = resolve_factor_validation(LocalFactorValidationEvidenceRegistry(), candidate_id="validation-candidate", as_of_utc="2026-07-21T00:00:00Z")
    assert snapshot.state == "MISSING"


def test_d4_incomplete_validation_lists_missing_checks():
    registry = LocalFactorValidationEvidenceRegistry((_check("LEAKAGE"),))
    snapshot = resolve_factor_validation(registry, candidate_id="validation-candidate", as_of_utc="2026-07-21T00:00:00Z")
    assert snapshot.state == "INCOMPLETE" and "CAPACITY" in snapshot.missing_check_types


def test_d5_failed_validation_history_is_preserved():
    snapshot = resolve_factor_validation(_registry("LEAKAGE"), candidate_id="validation-candidate", as_of_utc="2026-07-21T00:00:00Z")
    assert snapshot.state == "FAILED" and snapshot.failed_check_types == ("LEAKAGE",)


def test_d5_complete_checks_still_require_registered_packet():
    snapshot = resolve_factor_validation(_registry(include_packet=False), candidate_id="validation-candidate", as_of_utc="2026-07-21T00:00:00Z")
    assert snapshot.state == "INCOMPLETE" and "REGISTERED_VALIDATION_PACKET_MISSING" in snapshot.reason_codes


def test_d5_passed_packet_requires_review_and_does_not_activate():
    snapshot = resolve_factor_validation(_registry(), candidate_id="validation-candidate", as_of_utc="2026-07-21T00:00:00Z")
    assert snapshot.state == "PASSED_REVIEW_REQUIRED" and "NO_FACTOR_ACTIVATION" in snapshot.reason_codes


def test_d6_presentation_and_acceptance_are_read_only():
    registry = _registry()
    snapshot = resolve_factor_validation(registry, candidate_id="validation-candidate", as_of_utc="2026-07-21T00:00:00Z")
    model, acceptance = build_read_model(registry), build_operator_acceptance(snapshot)
    assert isinstance(model.payload, MappingProxyType) and acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["factor_activation"] = True  # type: ignore[index]
