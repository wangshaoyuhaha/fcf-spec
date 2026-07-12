from copy import deepcopy
from dataclasses import replace

from apps.ai_comprehensive_report_consumer_activation_app_1 import (
    FULL_CHAIN_CLOSEOUT_ARTIFACT_TYPE,
    FULL_CHAIN_CLOSEOUT_STATUS,
    SOURCE_BINDING_PACKAGE,
    build_full_chain_activation_closeout_receipt,
    validate_full_chain_activation_closeout_receipt,
)


def _binding_payload() -> dict[str, object]:
    return {
        "source_binding_package": SOURCE_BINDING_PACKAGE,
        "artifact_id": "comprehensive-report-001",
        "artifact_type": "ai_comprehensive_report_binding",
        "artifact_digest": "f" * 64,
        "correlation_id": "correlation-001",
        "evidence_ids": [
            "evidence-003",
            "evidence-001",
            "evidence-002",
        ],
        "risk_flags": [
            "risk-volatility",
            "risk-liquidity",
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


def test_d6_builds_full_chain_closeout_receipt() -> None:
    receipt = build_full_chain_activation_closeout_receipt(
        _binding_payload()
    )

    assert (
        receipt.artifact_type
        == FULL_CHAIN_CLOSEOUT_ARTIFACT_TYPE
    )
    assert receipt.status == FULL_CHAIN_CLOSEOUT_STATUS
    assert receipt.validate() == ()
    assert (
        validate_full_chain_activation_closeout_receipt(
            receipt
        )
        == ()
    )


def test_d6_closes_all_reviewed_activation_gaps() -> None:
    receipt = build_full_chain_activation_closeout_receipt(
        _binding_payload()
    )

    assert (
        receipt.gap_1_external_production_consumption_closed
        is True
    )
    assert (
        receipt.gap_2_operator_review_activation_closed
        is True
    )
    assert receipt.gap_3_ui_activation_closed is True
    assert (
        receipt.gap_4_report_archive_activation_closed
        is True
    )
    assert (
        receipt.gap_5_full_bundle_lifecycle_activation_closed
        is True
    )


def test_d6_preserves_production_surface_chain() -> None:
    receipt = build_full_chain_activation_closeout_receipt(
        _binding_payload()
    )

    assert receipt.activated_surfaces == (
        "operator_review",
        "ui",
        "report_archive",
    )
    assert receipt.production_entry_points == (
        "operator_review_app."
        "comprehensive_report_consumer_activation",
        "apps.dashboard_status_app_1."
        "comprehensive_report_consumer_activation",
        "report_archive_app."
        "comprehensive_report_consumer_activation",
    )


def test_d6_preserves_permanent_safety_boundaries() -> None:
    receipt = build_full_chain_activation_closeout_receipt(
        _binding_payload()
    )

    assert receipt.registered_artifact is True
    assert receipt.paper_only is True
    assert receipt.local_only is True
    assert receipt.read_only is True
    assert receipt.sidecar_only is True
    assert receipt.deterministic_only is True
    assert receipt.operator_review_required is True
    assert (
        receipt.manual_archive_authorization_required
        is True
    )
    assert receipt.automatic_approval_allowed is False
    assert receipt.automatic_archive_allowed is False
    assert receipt.archive_write_allowed is False
    assert (
        receipt.runtime_model_invocation_allowed
        is False
    )
    assert receipt.prompt_execution_allowed is False
    assert receipt.automatic_routing_allowed is False
    assert receipt.real_execution_allowed is False
    assert receipt.archive_payload_written is False


def test_d6_does_not_mutate_source_payload() -> None:
    payload = _binding_payload()
    original = deepcopy(payload)

    receipt = build_full_chain_activation_closeout_receipt(
        payload
    )

    assert payload == original
    assert receipt.source_payload_mutated is False


def test_d6_closeout_is_deterministic() -> None:
    first = build_full_chain_activation_closeout_receipt(
        _binding_payload()
    )
    second = build_full_chain_activation_closeout_receipt(
        _binding_payload()
    )

    assert first == second
    assert first.artifact_id == second.artifact_id
    assert first.closeout_digest == second.closeout_digest


def test_d6_detects_closeout_digest_tampering() -> None:
    receipt = build_full_chain_activation_closeout_receipt(
        _binding_payload()
    )
    tampered = replace(
        receipt,
        closeout_digest="0" * 64,
    )

    assert "closeout_digest_mismatch" in tampered.validate()
