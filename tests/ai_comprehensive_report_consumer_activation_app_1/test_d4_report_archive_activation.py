from copy import deepcopy
from pathlib import Path

import pytest

from apps.ai_comprehensive_report_consumer_activation_app_1 import (
    REPORT_ARCHIVE_CONSUMER_ID,
    REPORT_ARCHIVE_STATUS,
    SOURCE_BINDING_PACKAGE,
    build_activation_contract,
    build_report_archive_activation_packet,
)
from report_archive_app.comprehensive_report_consumer_activation import (
    BOUND_BINDING_PACKAGE,
    ENTRY_POINT_ID,
    activate_comprehensive_report_for_report_archive,
)


def _binding_payload() -> dict[str, object]:
    return {
        "source_binding_package": SOURCE_BINDING_PACKAGE,
        "artifact_id": "comprehensive-report-001",
        "artifact_type": "ai_comprehensive_report_binding",
        "artifact_digest": "c" * 64,
        "correlation_id": "correlation-001",
        "evidence_ids": [
            "evidence-002",
            "evidence-001",
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


def test_d4_production_archive_entry_point_consumes_binding() -> None:
    packet = activate_comprehensive_report_for_report_archive(
        _binding_payload()
    )

    assert ENTRY_POINT_ID
    assert BOUND_BINDING_PACKAGE == SOURCE_BINDING_PACKAGE
    assert packet.consumer_id == REPORT_ARCHIVE_CONSUMER_ID
    assert packet.surface == "report_archive"
    assert packet.archive_status == REPORT_ARCHIVE_STATUS
    assert packet.validate() == ()


def test_d4_archive_packet_requires_manual_authorization() -> None:
    packet = build_report_archive_activation_packet(
        _binding_payload()
    )

    assert packet.manual_archive_authorization_required is True
    assert packet.archive_payload_written is False
    assert packet.archive_write_allowed is False
    assert packet.automatic_archive_allowed is False
    assert packet.automatic_approval_allowed is False
    assert packet.archive_path is None


def test_d4_preserves_safety_boundaries() -> None:
    packet = build_report_archive_activation_packet(
        _binding_payload()
    )

    assert packet.registered_artifact is True
    assert packet.paper_only is True
    assert packet.local_only is True
    assert packet.read_only is True
    assert packet.sidecar_only is True
    assert packet.deterministic_only is True
    assert packet.operator_review_required is True
    assert packet.runtime_model_invocation_allowed is False
    assert packet.prompt_execution_allowed is False
    assert packet.automatic_routing_allowed is False
    assert packet.real_execution_allowed is False


def test_d4_does_not_mutate_source_payload() -> None:
    payload = _binding_payload()
    original = deepcopy(payload)

    packet = activate_comprehensive_report_for_report_archive(
        payload
    )

    assert payload == original
    assert packet.source_payload_mutated is False


def test_d4_rejects_missing_manual_authorization() -> None:
    payload = _binding_payload()
    payload["manual_archive_authorization_required"] = False

    with pytest.raises(
        ValueError,
        match="manual_archive_authorization_required must be true",
    ):
        activate_comprehensive_report_for_report_archive(payload)


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
def test_d4_rejects_forbidden_true_flags(
    field_name: str,
) -> None:
    payload = _binding_payload()
    payload[field_name] = True

    with pytest.raises(
        ValueError,
        match=f"{field_name} must be false",
    ):
        activate_comprehensive_report_for_report_archive(payload)


def test_d4_d1_discovers_report_archive_entry_point() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    contract = build_activation_contract(repo_root)

    matching = [
        candidate
        for candidate in contract.candidates
        if candidate.relative_path
        == (
            "report_archive_app/"
            "comprehensive_report_consumer_activation.py"
        )
    ]

    assert len(matching) == 1
    assert matching[0].surface == "report_archive"
    assert contract.validate() == ()


def test_d4_entry_point_contains_no_archive_writer_call() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    entry_path = (
        repo_root
        / "report_archive_app"
        / "comprehensive_report_consumer_activation.py"
    )
    content = entry_path.read_text(encoding="utf-8")

    assert "write_paper_archive_packet" not in content
    assert "activate_comprehensive_report_for_report_archive" in content
