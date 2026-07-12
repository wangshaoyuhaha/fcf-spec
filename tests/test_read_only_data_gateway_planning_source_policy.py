"""Incremental tests for D3 source policy."""

from copy import deepcopy

from fcf.sidecars.read_only_data_gateway_planning.contract import (
    build_read_only_data_gateway_boundary_contract,
)
from fcf.sidecars.read_only_data_gateway_planning.normalized_envelope import (
    build_normalized_data_envelope,
)
from fcf.sidecars.read_only_data_gateway_planning.source_policy import (
    build_source_policy_decision,
    validate_source_policy_decision,
)


def _envelope(**overrides):
    values = {
        "envelope_id": "envelope.public.report.v1",
        "boundary_contract": (
            build_read_only_data_gateway_boundary_contract()
        ),
        "source_id": "source.public.report.v1",
        "source_class": "A",
        "trust_level": "HIGH",
        "published_at": "2026-07-12T00:00:00+00:00",
        "retrieved_at": "2026-07-12T01:00:00+00:00",
        "evidence_id": "evidence.public.report.v1",
        "checksum": "sha256:" + ("a" * 64),
        "freshness_status": "FRESH",
        "license_type": "PUBLIC",
        "allowed_use": "ALLOWED",
        "cloud_processing_allowed": True,
        "retention_period": "policy.retention.v1",
        "redistribution_allowed": False,
        "training_allowed": False,
        "data_format": "json",
        "payload_reference": "payload.normalized.v1",
        "normalization_status": "VALIDATED",
        "credential_scan_status": "CLEAR",
    }

    values.update(overrides)

    return build_normalized_data_envelope(**values)


def _decision(envelope):
    return build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )


def test_ready_public_source_is_cloud_eligible():
    decision = _decision(_envelope())

    assert decision["source_policy_status"] == (
        "CLOUD_ELIGIBLE"
    )
    assert decision["cloud_eligible"] is True
    assert decision["local_processing_required"] is False


def test_cloud_disabled_source_is_local_only():
    decision = _decision(
        _envelope(cloud_processing_allowed=False)
    )

    assert decision["source_policy_status"] == "LOCAL_ONLY"
    assert decision["cloud_eligible"] is False
    assert decision["local_processing_required"] is True


def test_restricted_use_is_degraded_and_local():
    decision = _decision(
        _envelope(allowed_use="RESTRICTED")
    )

    assert decision["source_policy_status"] == "DEGRADED"
    assert decision["cloud_eligible"] is False
    assert decision["local_processing_required"] is True
    assert "source_use_restricted" in (
        decision["degradation_reasons"]
    )


def test_prohibited_use_is_blocked():
    decision = _decision(
        _envelope(allowed_use="PROHIBITED")
    )

    assert decision["source_policy_status"] == "BLOCKED"
    assert decision["cloud_eligible"] is False
    assert decision["local_processing_required"] is True
    assert "source_use_prohibited" in (
        decision["blocking_reasons"]
    )


def test_blocked_envelope_is_blocked():
    envelope = _envelope(
        normalization_status="BLOCKED"
    )
    decision = _decision(envelope)

    assert envelope["gateway_status"] == "BLOCKED"
    assert decision["source_policy_status"] == "BLOCKED"
    assert "source_envelope_blocked" in (
        decision["blocking_reasons"]
    )


def test_credential_scan_not_clear_is_blocked():
    decision = _decision(
        _envelope(credential_scan_status="NOT_RUN")
    )

    assert decision["source_policy_status"] == "BLOCKED"
    assert "credential_scan_not_clear" in (
        decision["blocking_reasons"]
    )


def test_stale_freshness_is_degraded():
    decision = _decision(
        _envelope(freshness_status="STALE")
    )

    assert decision["source_policy_status"] == "DEGRADED"
    assert decision["cloud_eligible"] is False
    assert "freshness_stale" in (
        decision["degradation_reasons"]
    )


def test_unknown_trust_is_degraded():
    decision = _decision(
        _envelope(trust_level="UNKNOWN")
    )

    assert decision["source_policy_status"] == "DEGRADED"
    assert decision["cloud_eligible"] is False
    assert "source_trust_unknown" in (
        decision["degradation_reasons"]
    )

def test_valid_decision_passes_validation():
    envelope = _envelope()
    decision = _decision(envelope)

    assert validate_source_policy_decision(
        decision,
        envelope,
    ) == []


def test_validation_rejects_runtime_activation():
    envelope = _envelope()
    decision = _decision(envelope)
    decision["runtime_activation_allowed"] = True

    assert (
        "runtime_activation_allowed_must_be_false"
        in validate_source_policy_decision(
            decision,
            envelope,
        )
    )


def test_validation_rejects_cloud_mismatch():
    envelope = _envelope(
        cloud_processing_allowed=False
    )
    decision = _decision(envelope)
    decision["cloud_eligible"] = True

    assert "cloud_eligibility_mismatch" in (
        validate_source_policy_decision(
            decision,
            envelope,
        )
    )


def test_validation_rejects_ready_with_reasons():
    envelope = _envelope()
    decision = _decision(envelope)
    decision["degradation_reasons"] = [
        "unexpected_reason"
    ]

    assert "ready_decision_must_not_include_reasons" in (
        validate_source_policy_decision(
            decision,
            envelope,
        )
    )


def test_builder_returns_fresh_nested_containers():
    envelope = _envelope()
    first = _decision(envelope)
    second = _decision(envelope)
    mutated = deepcopy(first)

    mutated["blocking_reasons"].append(
        "unexpected_reason"
    )
    mutated["degradation_reasons"].append(
        "unexpected_degradation"
    )

    assert second == _decision(envelope)
    assert mutated != second

def test_degraded_envelope_remains_degraded():
    decision = _decision(
        _envelope(normalization_status="DEGRADED")
    )

    assert decision["source_policy_status"] == "DEGRADED"
    assert decision["cloud_eligible"] is False
    assert decision["local_processing_required"] is True
    assert "normalization_degraded" in (
        decision["degradation_reasons"]
    )


def test_unknown_license_is_degraded_and_local():
    decision = _decision(
        _envelope(
            license_type="UNKNOWN",
            cloud_processing_allowed=False,
        )
    )

    assert decision["source_policy_status"] == "DEGRADED"
    assert decision["cloud_eligible"] is False
    assert decision["local_processing_required"] is True
    assert "license_unknown" in (
        decision["degradation_reasons"]
    )


def test_builder_rejects_invalid_decision_id():
    import pytest

    from fcf.sidecars.read_only_data_gateway_planning.source_policy import (
        SourcePolicyDecisionViolation,
    )

    with pytest.raises(SourcePolicyDecisionViolation):
        build_source_policy_decision(
            decision_id="invalid decision id",
            normalized_envelope=_envelope(),
        )


def test_builder_rejects_invalid_envelope():
    import pytest

    from fcf.sidecars.read_only_data_gateway_planning.source_policy import (
        SourcePolicyDecisionViolation,
    )

    envelope = _envelope()
    envelope["stage_id"] = "INVALID"

    with pytest.raises(SourcePolicyDecisionViolation):
        build_source_policy_decision(
            decision_id="decision.source.policy.v1",
            normalized_envelope=envelope,
        )


def test_non_mapping_decision_is_rejected():
    assert validate_source_policy_decision(
        [],
        _envelope(),
    ) == ["decision_must_be_mapping"]