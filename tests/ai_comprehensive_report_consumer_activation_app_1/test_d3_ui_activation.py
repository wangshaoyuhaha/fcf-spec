from copy import deepcopy
from importlib import import_module
from pathlib import Path

import pytest

from apps.ai_comprehensive_report_consumer_activation_app_1 import (
    SOURCE_BINDING_PACKAGE,
    UI_CONSUMER_ID,
    UI_DISPLAY_STATE,
    UI_RENDER_MODE,
    build_activation_contract,
    build_ui_activation_packet,
)

UI_ENTRY_MODULE = "apps.dashboard_status_app_1.comprehensive_report_consumer_activation"
UI_ENTRY_RELATIVE_PATH = "apps/dashboard_status_app_1/comprehensive_report_consumer_activation.py"

ui_entry = import_module(UI_ENTRY_MODULE)

ENTRY_POINT_ID = ui_entry.ENTRY_POINT_ID
BOUND_BINDING_PACKAGE = ui_entry.BOUND_BINDING_PACKAGE
activate_comprehensive_report_for_ui = (
    ui_entry.activate_comprehensive_report_for_ui
)


def _binding_payload() -> dict[str, object]:
    return {
        "source_binding_package": SOURCE_BINDING_PACKAGE,
        "artifact_id": "comprehensive-report-001",
        "artifact_type": "ai_comprehensive_report_binding",
        "artifact_digest": "b" * 64,
        "correlation_id": "correlation-001",
        "evidence_ids": [
            "evidence-002",
            "evidence-001",
            "evidence-001",
        ],
        "risk_flags": [
            "risk-liquidity",
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


def test_d3_production_ui_entry_point_consumes_binding() -> None:
    packet = activate_comprehensive_report_for_ui(
        _binding_payload()
    )

    assert ENTRY_POINT_ID
    assert BOUND_BINDING_PACKAGE == SOURCE_BINDING_PACKAGE
    assert packet.consumer_id == UI_CONSUMER_ID
    assert packet.surface == "ui"
    assert packet.display_state == UI_DISPLAY_STATE
    assert packet.render_mode == UI_RENDER_MODE
    assert packet.validate() == ()


def test_d3_ui_packet_preserves_risk_flags() -> None:
    packet = build_ui_activation_packet(_binding_payload())

    assert packet.risk_flags == (
        "risk-liquidity",
        "risk-volatility",
    )
    assert packet.evidence_ids == (
        "evidence-001",
        "evidence-002",
    )


def test_d3_ui_packet_preserves_safety_boundaries() -> None:
    packet = build_ui_activation_packet(_binding_payload())

    assert packet.registered_artifact is True
    assert packet.paper_only is True
    assert packet.local_only is True
    assert packet.read_only is True
    assert packet.sidecar_only is True
    assert packet.deterministic_only is True
    assert packet.operator_review_required is True
    assert packet.manual_archive_authorization_required is True
    assert packet.action_controls_enabled is False
    assert packet.archive_controls_enabled is False
    assert packet.automatic_refresh_enabled is False
    assert packet.automatic_approval_allowed is False
    assert packet.automatic_archive_allowed is False
    assert packet.archive_write_allowed is False
    assert packet.runtime_model_invocation_allowed is False
    assert packet.prompt_execution_allowed is False
    assert packet.automatic_routing_allowed is False
    assert packet.real_execution_allowed is False


def test_d3_ui_activation_does_not_mutate_source() -> None:
    payload = _binding_payload()
    original = deepcopy(payload)

    packet = activate_comprehensive_report_for_ui(payload)

    assert payload == original
    assert packet.source_payload_mutated is False


def test_d3_ui_rejects_unregistered_artifact() -> None:
    payload = _binding_payload()
    payload["registered_artifact"] = False

    with pytest.raises(
        ValueError,
        match="registered_artifact must be true",
    ):
        activate_comprehensive_report_for_ui(payload)


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
def test_d3_ui_rejects_forbidden_true_flags(
    field_name: str,
) -> None:
    payload = _binding_payload()
    payload[field_name] = True

    with pytest.raises(
        ValueError,
        match=f"{field_name} must be false",
    ):
        activate_comprehensive_report_for_ui(payload)


def test_d3_d1_discovers_real_ui_entry_point() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    contract = build_activation_contract(repo_root)

    matching = [
        candidate
        for candidate in contract.candidates
        if candidate.relative_path == UI_ENTRY_RELATIVE_PATH
    ]

    assert len(matching) == 1
    assert matching[0].surface == "ui"
    assert contract.validate() == ()


def test_d3_ui_entry_point_has_explicit_binding_reference() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    content = (
        repo_root / UI_ENTRY_RELATIVE_PATH
    ).read_text(encoding="utf-8")

    assert (
        "ai_comprehensive_report_consumer_binding_app_1"
        in content
    )
    assert "activate_comprehensive_report_for_ui" in content
