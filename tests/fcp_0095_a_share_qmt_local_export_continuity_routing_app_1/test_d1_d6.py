from dataclasses import replace
import hashlib
import json

import pytest

from apps.fcp_0095_a_share_qmt_local_export_continuity_routing_app_1 import (
    PHASE_ID,
    build_continuity_route,
    build_registered_runtime_evidence,
    render_continuity_route_json,
)


def test_d1_exact_registered_runtime_evidence() -> None:
    evidence = build_registered_runtime_evidence()

    assert evidence.terminal_state == "TERMINAL_OBSERVED"
    assert evidence.observed_family == "XT_IT_CLIENT"
    assert evidence.loopback_call_state == "CALL_FAILED"
    assert evidence.loopback_call_count == 1
    assert evidence.loopback_row_count == 0
    assert evidence.gap_104_status == "RESEARCH_REQUIRED"


def test_d1_runtime_evidence_rejects_tampering() -> None:
    evidence = build_registered_runtime_evidence()

    with pytest.raises(ValueError):
        replace(evidence, loopback_call_count=2)
    with pytest.raises(ValueError):
        replace(evidence, evidence_hash="0" * 64)


def test_d2_route_degrades_miniqmt_without_blocking_local_export() -> None:
    route = build_continuity_route()

    assert route.phase_id == PHASE_ID
    assert route.routing_state == "LOCAL_EXPORT_RESEARCH_CONTINUITY"
    assert route.active_research_route == "REGISTERED_QMT_LOCAL_EXPORT"
    assert route.miniqmt_route_state == "DEFERRED_NON_BLOCKING"


def test_d3_candidates_remain_supplements_not_selected_providers() -> None:
    route = build_continuity_route()

    assert route.candidate_supplement_routes == (
        "RQDATA_TRIAL_CANDIDATE",
        "TUSHARE_CANDIDATE",
    )
    assert route.provider_selection_authority is False
    assert route.data_promotion_authority is False


def test_d4_next_actions_are_closed_and_ordered() -> None:
    route = build_continuity_route()

    assert route.next_actions == (
        "REGISTER_LOCAL_EXPORT_BATCH",
        "VALIDATE_BATCH_COVERAGE",
        "RECONCILE_INDEPENDENT_CANDIDATE",
    )
    assert route.open_gaps == tuple(
        f"V2-FR-GAP-{number:03d}" for number in range(93, 110)
    )


def test_d5_route_grants_no_product_account_or_execution_authority() -> None:
    route = build_continuity_route()

    assert route.realtime_activation_authority is False
    assert route.product_authority is False
    assert route.account_authority is False
    assert route.execution_authority is False


def test_d5_route_rejects_authority_escalation() -> None:
    route = build_continuity_route()

    with pytest.raises(ValueError):
        replace(route, execution_authority=True)
    with pytest.raises(ValueError):
        replace(route, provider_selection_authority=True)


def test_d6_render_is_ascii_canonical_and_value_free() -> None:
    route = build_continuity_route()
    rendered = render_continuity_route_json(route)

    assert rendered.encode("ascii").decode("ascii") == rendered
    assert json.loads(rendered)["route_hash"] == route.route_hash
    assert "\\" not in rendered
    assert "8890715548" not in rendered
    assert "password" not in rendered.lower()
    assert "price" not in rendered.lower()


def test_d6_render_hash_is_stable() -> None:
    rendered = render_continuity_route_json(build_continuity_route())

    assert hashlib.sha256(rendered.encode("ascii")).hexdigest() == (
        "f3d2d4e57f570ed3a0cced83101fc6c99233e5358ed46fce745e9724d458de74"
    )


def test_d6_type_and_registry_guards_fail_closed() -> None:
    route = build_continuity_route()

    with pytest.raises(TypeError):
        render_continuity_route_json(object())
    with pytest.raises(ValueError):
        replace(route, active_research_route="UNKNOWN")
