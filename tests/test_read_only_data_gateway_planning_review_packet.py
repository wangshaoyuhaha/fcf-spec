"""Smoke tests for D5 governance review packet."""

from fcf.sidecars.read_only_data_gateway_planning.contract import (
    build_read_only_data_gateway_boundary_contract,
)
from fcf.sidecars.read_only_data_gateway_planning.credential_isolation import (
    build_credential_isolation_contract,
)
from fcf.sidecars.read_only_data_gateway_planning.normalized_envelope import (
    build_normalized_data_envelope,
)
from fcf.sidecars.read_only_data_gateway_planning.review_packet import (
    build_governance_review_packet,
)
from fcf.sidecars.read_only_data_gateway_planning.source_policy import (
    build_source_policy_decision,
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


def _packet(envelope):
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )

    return build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=(
            build_credential_isolation_contract()
        ),
    )


def test_ready_source_is_ready_for_operator_review():
    packet = _packet(_envelope())

    assert packet["overall_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert packet["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )
    assert packet["operator_decision_status"] == "PENDING"


def test_degraded_source_remains_degraded():
    packet = _packet(
        _envelope(freshness_status="STALE")
    )

    assert packet["overall_status"] == "DEGRADED"
    assert "freshness_stale" in (
        packet["degradation_reasons"]
    )
    assert packet["runtime_activation_allowed"] is False


def test_blocked_source_remains_blocked():
    packet = _packet(
        _envelope(allowed_use="PROHIBITED")
    )

    assert packet["overall_status"] == "BLOCKED"
    assert "source_use_prohibited" in (
        packet["blocking_reasons"]
    )
    assert packet["model_invocation_allowed"] is False
    assert packet["automatic_routing_allowed"] is False
    assert packet["archive_writing_allowed"] is False

from fcf.sidecars.read_only_data_gateway_planning.review_packet import (
    validate_governance_review_packet,
)


def test_valid_packet_passes_validation():
    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    packet = build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )

    assert validate_governance_review_packet(
        packet,
        envelope,
        decision,
        credential_contract,
    ) == []


def test_validation_rejects_runtime_activation():
    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    packet = build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )
    packet["runtime_activation_allowed"] = True

    assert (
        "runtime_activation_allowed_must_be_false"
        in validate_governance_review_packet(
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_model_invocation():
    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    packet = build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )
    packet["model_invocation_allowed"] = True

    assert (
        "model_invocation_allowed_must_be_false"
        in validate_governance_review_packet(
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_source_policy_link_tampering():
    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    packet = build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )
    packet["source_policy_decision_id"] = (
        "decision.tampered.v1"
    )

    assert "source_policy_decision_id_mismatch" in (
        validate_governance_review_packet(
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_non_mapping_packet_is_rejected():
    assert validate_governance_review_packet(
        [],
        _envelope(),
        {},
        {},
    ) == ["packet_must_be_mapping"]

def test_builder_rejects_invalid_review_packet_id():
    import pytest

    from fcf.sidecars.read_only_data_gateway_planning.review_packet import (
        GovernanceReviewPacketViolation,
    )

    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )

    with pytest.raises(GovernanceReviewPacketViolation):
        build_governance_review_packet(
            review_packet_id="invalid packet id",
            normalized_envelope=envelope,
            source_policy_decision=decision,
            credential_isolation_contract=(
                build_credential_isolation_contract()
            ),
        )


def test_builder_rejects_invalid_source_policy_decision():
    import pytest

    from fcf.sidecars.read_only_data_gateway_planning.review_packet import (
        GovernanceReviewPacketViolation,
    )

    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    decision["runtime_activation_allowed"] = True

    with pytest.raises(GovernanceReviewPacketViolation):
        build_governance_review_packet(
            review_packet_id="review.packet.gateway.v1",
            normalized_envelope=envelope,
            source_policy_decision=decision,
            credential_isolation_contract=(
                build_credential_isolation_contract()
            ),
        )


def test_builder_rejects_invalid_credential_contract():
    import pytest

    from fcf.sidecars.read_only_data_gateway_planning.review_packet import (
        GovernanceReviewPacketViolation,
    )

    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    credential_contract["safety_flags"][
        "credential_material_allowed_in_fcf"
    ] = True

    with pytest.raises(GovernanceReviewPacketViolation):
        build_governance_review_packet(
            review_packet_id="review.packet.gateway.v1",
            normalized_envelope=envelope,
            source_policy_decision=decision,
            credential_isolation_contract=credential_contract,
        )


def test_validation_rejects_automatic_routing():
    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    packet = build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )
    packet["automatic_routing_allowed"] = True

    assert (
        "automatic_routing_allowed_must_be_false"
        in validate_governance_review_packet(
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_archive_writing():
    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    packet = build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )
    packet["archive_writing_allowed"] = True

    assert (
        "archive_writing_allowed_must_be_false"
        in validate_governance_review_packet(
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )

def test_ready_packet_has_no_reasons():
    packet = _packet(_envelope())

    assert packet["blocking_reasons"] == []
    assert packet["degradation_reasons"] == []
    assert packet["credential_isolation_status"] == (
        "VALIDATED"
    )


def test_builder_returns_fresh_reason_containers():
    envelope = _envelope()
    first = _packet(envelope)
    second = _packet(envelope)

    first["blocking_reasons"].append(
        "tampered_blocking_reason"
    )
    first["degradation_reasons"].append(
        "tampered_degradation_reason"
    )

    assert second == _packet(envelope)
    assert first != second


def test_validation_rejects_extra_packet_field():
    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    packet = build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )
    packet["unexpected_field"] = "NOT_ALLOWED"

    assert "packet_fields_must_match_schema" in (
        validate_governance_review_packet(
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_credential_link_tampering():
    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    packet = build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )
    packet["credential_isolation_contract_id"] = (
        "credential.contract.tampered.v1"
    )

    assert (
        "credential_isolation_contract_id_mismatch"
        in validate_governance_review_packet(
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_overall_status_tampering():
    envelope = _envelope()
    decision = build_source_policy_decision(
        decision_id="decision.source.policy.v1",
        normalized_envelope=envelope,
    )
    credential_contract = (
        build_credential_isolation_contract()
    )
    packet = build_governance_review_packet(
        review_packet_id="review.packet.gateway.v1",
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )
    packet["overall_status"] = "BLOCKED"

    assert "overall_status_mismatch" in (
        validate_governance_review_packet(
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )