from copy import deepcopy
from pathlib import Path

import pytest

from apps.ai_comprehensive_report_consumer_activation_app_1 import (
    OPERATOR_REVIEW_CONSUMER_ID,
    OPERATOR_REVIEW_STATUS,
    SOURCE_BINDING_PACKAGE,
    build_activation_contract,
    build_operator_review_activation_packet,
)
from operator_review_app.comprehensive_report_consumer_activation import (
    BOUND_BINDING_PACKAGE,
    ENTRY_POINT_ID,
    activate_comprehensive_report_for_operator_review,
)


def _binding_payload() -> dict[str, object]:
    return {
        "source_binding_package": SOURCE_BINDING_PACKAGE,
        "artifact_id": "comprehensive-report-001",
        "artifact_type": "ai_comprehensive_report_binding",
        "artifact_digest": "a" * 64,
        "correlation_id": "correlation-001",
        "evidence_ids": [
            "evidence-002",
            "evidence-001",
            "evidence-001",
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


def test_d2_production_entry_point_consumes_binding() -> None:
    packet = activate_comprehensive_report_for_operator_review(
        _binding_payload()
    )

    assert ENTRY_POINT_ID
    assert BOUND_BINDING_PACKAGE == SOURCE_BINDING_PACKAGE
    assert packet.consumer_id == OPERATOR_REVIEW_CONSUMER_ID
    assert packet.review_status == OPERATOR_REVIEW_STATUS
    assert packet.surface == "operator_review"
    assert packet.validate() == ()


def test_d2_preserves_safety_boundaries() -> None:
    packet = build_operator_review_activation_packet(
        _binding_payload()
    )

    assert packet.registered_artifact is True
    assert packet.paper_only is True
    assert packet.local_only is True
    assert packet.read_only is True
    assert packet.sidecar_only is True
    assert packet.deterministic_only is True
    assert packet.operator_review_required is True
    assert packet.manual_archive_authorization_required is True
    assert packet.automatic_approval_allowed is False
    assert packet.automatic_archive_allowed is False
    assert packet.archive_write_allowed is False
    assert packet.runtime_model_invocation_allowed is False
    assert packet.prompt_execution_allowed is False
    assert packet.automatic_routing_allowed is False
    assert packet.real_execution_allowed is False
    assert packet.source_payload_mutated is False


def test_d2_does_not_mutate_source_payload() -> None:
    payload = _binding_payload()
    original = deepcopy(payload)

    packet = activate_comprehensive_report_for_operator_review(
        payload
    )

    assert payload == original
    assert packet.evidence_ids == (
        "evidence-001",
        "evidence-002",
    )


def test_d2_rejects_unregistered_artifact() -> None:
    payload = _binding_payload()
    payload["registered_artifact"] = False

    with pytest.raises(
        ValueError,
        match="registered_artifact must be true",
    ):
        activate_comprehensive_report_for_operator_review(payload)


@pytest.mark.parametrize(
    "field_name",
    [
        "automatic_approval_allowed",
        "automatic_archive_allowed",
        "archive_write_allowed",
        "runtime_model_invocation_allowed",
        "prompt_execution_allowed",
        "automatic_routing_allowed",
        "real_execution_allowed",
    ],
)
def test_d2_rejects_forbidden_true_flags(
    field_name: str,
) -> None:
    payload = _binding_payload()
    payload[field_name] = True

    with pytest.raises(
        ValueError,
        match=f"{field_name} must be false",
    ):
        activate_comprehensive_report_for_operator_review(payload)


def test_d2_rejects_invalid_digest() -> None:
    payload = _binding_payload()
    payload["artifact_digest"] = "not-a-sha256"

    with pytest.raises(
        ValueError,
        match="artifact_digest must be a lowercase SHA-256 value",
    ):
        activate_comprehensive_report_for_operator_review(payload)


def test_d2_d1_discovers_real_operator_review_entry_point() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    contract = build_activation_contract(repo_root)

    matching = [
        candidate
        for candidate in contract.candidates
        if candidate.relative_path
        == (
            "operator_review_app/"
            "comprehensive_report_consumer_activation.py"
        )
    ]

    assert len(matching) == 1
    assert matching[0].surface == "operator_review"
    assert contract.validate() == ()
