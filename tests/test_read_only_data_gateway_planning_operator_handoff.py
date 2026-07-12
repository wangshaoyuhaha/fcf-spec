"""Smoke tests for D6 final Operator handoff."""

from fcf.sidecars.read_only_data_gateway_planning.contract import (
    build_read_only_data_gateway_boundary_contract,
)
from fcf.sidecars.read_only_data_gateway_planning.credential_isolation import (
    build_credential_isolation_contract,
)
from fcf.sidecars.read_only_data_gateway_planning.normalized_envelope import (
    build_normalized_data_envelope,
)
from fcf.sidecars.read_only_data_gateway_planning.operator_handoff import (
    build_final_operator_handoff,
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


def _handoff(envelope):
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

    return build_final_operator_handoff(
        handoff_id="handoff.gateway.final.v1",
        review_packet=packet,
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )


def test_ready_packet_is_ready_for_merge_review():
    handoff = _handoff(_envelope())

    assert handoff["handoff_status"] == (
        "READY_FOR_OPERATOR_MERGE_REVIEW"
    )
    assert handoff["main_merge_review_eligible"] is True
    assert handoff["repair_required"] is False
    assert (
        "APPROVE_MAIN_MERGE_REVIEW"
        in handoff["allowed_operator_actions"]
    )


def test_degraded_packet_requires_repair():
    handoff = _handoff(
        _envelope(freshness_status="STALE")
    )

    assert handoff["handoff_status"] == (
        "DEGRADED_OPERATOR_REVIEW_REQUIRED"
    )
    assert handoff["main_merge_review_eligible"] is False
    assert handoff["repair_required"] is True


def test_blocked_packet_forbids_execution_and_merge():
    handoff = _handoff(
        _envelope(allowed_use="PROHIBITED")
    )

    assert handoff["handoff_status"] == (
        "BLOCKED_REPAIR_REQUIRED"
    )
    assert handoff["main_merge_review_eligible"] is False
    assert handoff["model_invocation_allowed"] is False
    assert handoff["prompt_execution_allowed"] is False
    assert handoff["automatic_routing_allowed"] is False
    assert handoff["runtime_activation_allowed"] is False
    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False

from fcf.sidecars.read_only_data_gateway_planning.operator_handoff import (
    validate_final_operator_handoff,
)


def _validation_bundle():
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
    handoff = build_final_operator_handoff(
        handoff_id="handoff.gateway.final.v1",
        review_packet=packet,
        normalized_envelope=envelope,
        source_policy_decision=decision,
        credential_isolation_contract=credential_contract,
    )

    return (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    )


def test_valid_handoff_passes_validation():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    assert validate_final_operator_handoff(
        handoff,
        packet,
        envelope,
        decision,
        credential_contract,
    ) == []


def test_validation_rejects_runtime_activation():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    handoff["runtime_activation_allowed"] = True

    assert "runtime_activation_allowed_must_be_false" in (
        validate_final_operator_handoff(
            handoff,
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_automatic_routing():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    handoff["automatic_routing_allowed"] = True

    assert "automatic_routing_allowed_must_be_false" in (
        validate_final_operator_handoff(
            handoff,
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_merge_without_confirmation():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    handoff[
        "main_merge_allowed_without_operator_confirmation"
    ] = True

    assert (
        "main_merge_allowed_without_operator_confirmation_must_be_false"
        in validate_final_operator_handoff(
            handoff,
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_non_mapping_handoff_is_rejected():
    assert validate_final_operator_handoff(
        [],
        {},
        {},
        {},
        {},
    ) == ["handoff_must_be_mapping"]

def test_builder_rejects_invalid_handoff_id():
    import pytest

    from fcf.sidecars.read_only_data_gateway_planning.operator_handoff import (
        FinalOperatorHandoffViolation,
    )

    (
        envelope,
        decision,
        credential_contract,
        packet,
        _,
    ) = _validation_bundle()

    with pytest.raises(FinalOperatorHandoffViolation):
        build_final_operator_handoff(
            handoff_id="invalid handoff id",
            review_packet=packet,
            normalized_envelope=envelope,
            source_policy_decision=decision,
            credential_isolation_contract=credential_contract,
        )


def test_builder_rejects_invalid_review_packet():
    import pytest

    from fcf.sidecars.read_only_data_gateway_planning.operator_handoff import (
        FinalOperatorHandoffViolation,
    )

    (
        envelope,
        decision,
        credential_contract,
        packet,
        _,
    ) = _validation_bundle()

    packet["runtime_activation_allowed"] = True

    with pytest.raises(FinalOperatorHandoffViolation):
        build_final_operator_handoff(
            handoff_id="handoff.gateway.final.v1",
            review_packet=packet,
            normalized_envelope=envelope,
            source_policy_decision=decision,
            credential_isolation_contract=credential_contract,
        )


def test_validation_rejects_model_invocation():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    handoff["model_invocation_allowed"] = True

    assert "model_invocation_allowed_must_be_false" in (
        validate_final_operator_handoff(
            handoff,
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_archive_writing():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    handoff["archive_writing_allowed"] = True

    assert "archive_writing_allowed_must_be_false" in (
        validate_final_operator_handoff(
            handoff,
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_tag_release_and_deploy():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    handoff["tag_allowed"] = True
    handoff["release_allowed"] = True
    handoff["deploy_allowed"] = True

    errors = validate_final_operator_handoff(
        handoff,
        packet,
        envelope,
        decision,
        credential_contract,
    )

    assert "tag_allowed_must_be_false" in errors
    assert "release_allowed_must_be_false" in errors
    assert "deploy_allowed_must_be_false" in errors

def test_ready_handoff_has_expected_actions():
    handoff = _handoff(_envelope())

    assert handoff["allowed_operator_actions"] == [
        "ACKNOWLEDGE_PACKET",
        "APPROVE_MAIN_MERGE_REVIEW",
        "REJECT_PACKET",
        "REQUEST_REPAIR",
    ]
    assert handoff["operator_action_required"] is True
    assert handoff["operator_decision_status"] == "PENDING"
    assert (
        handoff[
            "main_merge_allowed_without_operator_confirmation"
        ]
        is False
    )


def test_builder_returns_fresh_action_container():
    first = _handoff(_envelope())
    second = _handoff(_envelope())

    first["allowed_operator_actions"].append(
        "UNSAFE_AUTOMATIC_ACTION"
    )

    assert second == _handoff(_envelope())
    assert first != second


def test_validation_rejects_extra_handoff_field():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    handoff["unexpected_field"] = "NOT_ALLOWED"

    assert "handoff_fields_must_match_schema" in (
        validate_final_operator_handoff(
            handoff,
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_review_packet_link_tampering():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    handoff["source_review_packet_id"] = (
        "review.packet.tampered.v1"
    )

    assert "source_review_packet_id_mismatch" in (
        validate_final_operator_handoff(
            handoff,
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )


def test_validation_rejects_handoff_status_tampering():
    (
        envelope,
        decision,
        credential_contract,
        packet,
        handoff,
    ) = _validation_bundle()

    handoff["handoff_status"] = "BLOCKED_REPAIR_REQUIRED"

    assert "handoff_status_mismatch" in (
        validate_final_operator_handoff(
            handoff,
            packet,
            envelope,
            decision,
            credential_contract,
        )
    )