from copy import deepcopy
from dataclasses import replace

import pytest

from apps.ai_comprehensive_report_consumer_activation_app_1 import (
    CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE,
    CROSS_SURFACE_VALIDATION_STATUS,
    SOURCE_BINDING_PACKAGE,
    build_registered_cross_surface_activation_artifact,
    validate_registered_cross_surface_activation_artifact,
)
from apps.dashboard_status_app_1.comprehensive_report_consumer_activation import (
    activate_comprehensive_report_for_ui,
)
from operator_review_app.comprehensive_report_consumer_activation import (
    activate_comprehensive_report_for_operator_review,
)
from report_archive_app.comprehensive_report_consumer_activation import (
    activate_comprehensive_report_for_report_archive,
)


def _binding_payload() -> dict[str, object]:
    return {
        "source_binding_package": SOURCE_BINDING_PACKAGE,
        "artifact_id": "comprehensive-report-001",
        "artifact_type": "ai_comprehensive_report_binding",
        "artifact_digest": "d" * 64,
        "correlation_id": "correlation-001",
        "evidence_ids": [
            "evidence-003",
            "evidence-001",
            "evidence-002",
            "evidence-001",
        ],
        "risk_flags": [
            "risk-volatility",
            "risk-liquidity",
            "risk-volatility",
        ],
        "registered_artifact": True,
        "operator_review_required": True,
        "manual_archive_authorization_required": True,
        "automatic_approval_allowed": False,
        "automatic_archive_allowed": False,
        "archive_write_allowed": False,
        "runtime_model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "automatic_routing_allowed": False,
        "real_execution_allowed": False,
    }


def _surface_packets():
    payload = _binding_payload()

    operator_packet = (
        activate_comprehensive_report_for_operator_review(
            payload
        )
    )
    ui_packet = activate_comprehensive_report_for_ui(
        payload
    )
    archive_packet = (
        activate_comprehensive_report_for_report_archive(
            payload
        )
    )

    return operator_packet, ui_packet, archive_packet


def test_d5_builds_registered_validation_artifact() -> None:
    packets = _surface_packets()

    artifact = (
        build_registered_cross_surface_activation_artifact(
            *packets
        )
    )

    assert (
        artifact.artifact_type
        == CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE
    )
    assert artifact.status == CROSS_SURFACE_VALIDATION_STATUS
    assert artifact.registered_artifact is True
    assert artifact.validate() == ()
    assert (
        validate_registered_cross_surface_activation_artifact(
            artifact
        )
        == ()
    )


def test_d5_preserves_cross_surface_identity() -> None:
    artifact = (
        build_registered_cross_surface_activation_artifact(
            *_surface_packets()
        )
    )

    assert artifact.source_artifact_id == (
        "comprehensive-report-001"
    )
    assert artifact.source_artifact_type == (
        "ai_comprehensive_report_binding"
    )
    assert artifact.source_artifact_digest == "d" * 64
    assert artifact.correlation_id == "correlation-001"
    assert artifact.evidence_ids == (
        "evidence-001",
        "evidence-002",
        "evidence-003",
    )
    assert artifact.risk_flags == (
        "risk-liquidity",
        "risk-volatility",
    )


def test_d5_validates_all_three_production_surfaces() -> None:
    artifact = (
        build_registered_cross_surface_activation_artifact(
            *_surface_packets()
        )
    )

    assert artifact.surfaces == (
        "operator_review",
        "ui",
        "report_archive",
    )
    assert len(artifact.surface_consumer_ids) == 3
    assert artifact.surface_states == (
        "REVIEW_REQUIRED",
        "READ_ONLY_REVIEW_REQUIRED",
        "MANUAL_AUTHORIZATION_REQUIRED",
    )


def test_d5_artifact_is_deterministic() -> None:
    first = (
        build_registered_cross_surface_activation_artifact(
            *_surface_packets()
        )
    )
    second = (
        build_registered_cross_surface_activation_artifact(
            *_surface_packets()
        )
    )

    assert first == second
    assert first.artifact_id == second.artifact_id
    assert (
        first.validation_digest
        == second.validation_digest
    )


def test_d5_preserves_safety_boundaries() -> None:
    artifact = (
        build_registered_cross_surface_activation_artifact(
            *_surface_packets()
        )
    )

    assert artifact.paper_only is True
    assert artifact.local_only is True
    assert artifact.read_only is True
    assert artifact.sidecar_only is True
    assert artifact.deterministic_only is True
    assert artifact.operator_review_required is True
    assert (
        artifact.manual_archive_authorization_required
        is True
    )
    assert artifact.archive_payload_written is False
    assert artifact.automatic_approval_allowed is False
    assert artifact.automatic_archive_allowed is False
    assert artifact.archive_write_allowed is False
    assert (
        artifact.runtime_model_invocation_allowed
        is False
    )
    assert artifact.prompt_execution_allowed is False
    assert artifact.automatic_routing_allowed is False
    assert artifact.real_execution_allowed is False


def test_d5_does_not_mutate_source_payload() -> None:
    payload = _binding_payload()
    original = deepcopy(payload)

    operator_packet = (
        activate_comprehensive_report_for_operator_review(
            payload
        )
    )
    ui_packet = activate_comprehensive_report_for_ui(
        payload
    )
    archive_packet = (
        activate_comprehensive_report_for_report_archive(
            payload
        )
    )

    artifact = (
        build_registered_cross_surface_activation_artifact(
            operator_packet,
            ui_packet,
            archive_packet,
        )
    )

    assert payload == original
    assert artifact.source_payload_mutated is False


def test_d5_rejects_cross_surface_correlation_mismatch() -> None:
    operator_packet, ui_packet, archive_packet = (
        _surface_packets()
    )
    invalid_ui_packet = replace(
        ui_packet,
        correlation_id="correlation-mismatch",
    )

    with pytest.raises(
        ValueError,
        match="cross_surface_correlation_id_mismatch",
    ):
        build_registered_cross_surface_activation_artifact(
            operator_packet,
            invalid_ui_packet,
            archive_packet,
        )


def test_d5_rejects_cross_surface_digest_mismatch() -> None:
    operator_packet, ui_packet, archive_packet = (
        _surface_packets()
    )
    invalid_archive_packet = replace(
        archive_packet,
        source_artifact_digest="e" * 64,
    )

    with pytest.raises(
        ValueError,
        match="cross_surface_source_artifact_digest_mismatch",
    ):
        build_registered_cross_surface_activation_artifact(
            operator_packet,
            ui_packet,
            invalid_archive_packet,
        )


def test_d5_rejects_cross_surface_risk_flag_mismatch() -> None:
    operator_packet, ui_packet, archive_packet = (
        _surface_packets()
    )
    invalid_archive_packet = replace(
        archive_packet,
        risk_flags=("risk-other",),
    )

    with pytest.raises(
        ValueError,
        match="cross_surface_risk_flags_mismatch",
    ):
        build_registered_cross_surface_activation_artifact(
            operator_packet,
            ui_packet,
            invalid_archive_packet,
        )


def test_d5_detects_validation_digest_tampering() -> None:
    artifact = (
        build_registered_cross_surface_activation_artifact(
            *_surface_packets()
        )
    )
    tampered = replace(
        artifact,
        validation_digest="f" * 64,
    )

    assert "validation_digest_mismatch" in tampered.validate()
