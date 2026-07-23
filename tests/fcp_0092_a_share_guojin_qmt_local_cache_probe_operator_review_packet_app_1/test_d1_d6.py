from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError, replace

import pytest

from apps.fcp_0092_a_share_guojin_qmt_local_cache_probe_operator_review_packet_app_1 import (
    DEFAULT_EVIDENCE_REFERENCE,
    NEXT_ACTION_IDS,
    REVIEW_ITEM_IDS,
    ProbeOperatorReviewItem,
    build_operator_review_packet,
    render_operator_review_packet_json,
)


def packet():
    return build_operator_review_packet()


def test_d1_reference_is_exact_and_hash_locked():
    reference = DEFAULT_EVIDENCE_REFERENCE
    assert reference.call_state == "NOT_RUN"
    assert reference.call_attempted is False
    assert reference.call_count == 0
    assert reference.row_count == 0
    assert reference.blockers == (
        "MINIQMT_ENTITLEMENT_UNPROVEN",
        "QMT_TERMINAL_NOT_OBSERVED",
        "RIGHTS_AND_RETENTION_UNPROVEN",
    )
    assert reference.reference_hash == (
        "3c866b54a9aec1b00c203430ba76e74271106d6642be4b7c8eb2646e7c1df1dc"
    )


def test_d1_reference_mutation_fails_closed():
    with pytest.raises(ValueError, match="must match FCP-0091 delivery"):
        replace(DEFAULT_EVIDENCE_REFERENCE, call_count=1)
    with pytest.raises(ValueError, match="must match FCP-0091 delivery"):
        replace(DEFAULT_EVIDENCE_REFERENCE, evidence_hash="0" * 64)


def test_d2_review_items_are_closed_order_and_undecided():
    result = packet()
    assert tuple(item.item_id for item in result.review_items) == REVIEW_ITEM_IDS
    assert all(item.review_state == "OPERATOR_REVIEW_REQUIRED" for item in result.review_items)
    assert all(item.approved is False and item.rejected is False for item in result.review_items)


def test_d2_unknown_or_decided_review_item_fails_closed():
    with pytest.raises(ValueError, match="not registered"):
        ProbeOperatorReviewItem("unknown", "0" * 64)
    with pytest.raises(ValueError, match="cannot assign a disposition"):
        ProbeOperatorReviewItem("terminal-liveness", "0" * 64, approved=True)


def test_d3_acceptance_is_blocked_and_next_actions_are_closed():
    result = packet()
    assert result.acceptance_gate == "BLOCKED_PENDING_REGISTERED_TERMINAL_PROBE"
    assert result.review_state == "OPERATOR_ACTION_REQUIRED"
    assert result.next_action_ids == NEXT_ACTION_IDS
    with pytest.raises(ValueError, match="closed order"):
        replace(result, next_action_ids=("RUN_ARBITRARY_COMMAND",))


def test_d3_packet_is_path_free_and_value_free():
    rendered = render_operator_review_packet_json(packet()).lower()
    for forbidden in (
        '"path":',
        '"file_path":',
        '"price":',
        '"volume":',
        '"amount":',
        '"timestamp":',
        '"account_id":',
        '"credential":',
    ):
        assert forbidden not in rendered


def test_d4_packet_cannot_assign_disposition_or_authority():
    baseline = packet()
    for field_name in (
        "disposition_assigned",
        "evidence_accepted",
        "provider_selected",
        "realtime_activated",
        "data_promotion_allowed",
        "product_authority",
        "execution_authority",
    ):
        with pytest.raises(ValueError, match="cannot decide, activate, promote, or act"):
            replace(baseline, **{field_name: True})


def test_d4_packet_cannot_claim_runtime_use():
    baseline = packet()
    for field_name in (
        "sdk_used",
        "network_used",
        "credentials_used",
        "account_api_used",
        "trading_api_used",
    ):
        with pytest.raises(ValueError, match="cannot decide, activate, promote, or act"):
            replace(baseline, **{field_name: True})


def test_d5_packet_is_immutable_and_gap_remains_open():
    result = packet()
    assert result.gap_104_status == "RESEARCH_REQUIRED"
    assert result.operator_review_required is True
    with pytest.raises(FrozenInstanceError):
        result.packet_id = "changed"  # type: ignore[misc]


def test_d5_authority_identities_are_fixed():
    result = packet()
    assert result.calculation_authority == "DETERMINISTIC_ENGINE"
    assert result.evidence_authority == "REGISTERED_EVIDENCE"
    assert result.ai_role == "ADVISORY_ONLY"
    with pytest.raises(ValueError, match="authority identities are immutable"):
        replace(result, ai_role="AUTHORITATIVE")


def test_d6_renderer_is_canonical_ascii_and_hash_locked():
    result = packet()
    rendered = render_operator_review_packet_json(result)
    assert rendered.encode("ascii").decode("ascii") == rendered
    assert rendered.endswith("\n")
    assert json.loads(rendered)["packet_hash"] == result.packet_hash
    assert result.packet_hash == (
        "5dd514d530d33c8256f160141ca3c0e6ee81a0b0f253f65917b7bdfd8f9225a0"
    )
    assert hashlib.sha256(rendered.encode("ascii")).hexdigest() == (
        "3cd0f9d2006774e02011698543d47dddbe45a707e54e0339b3695e4794b6196e"
    )


def test_d6_builder_and_renderer_require_exact_types():
    with pytest.raises(TypeError, match="exact ProbeEvidenceReference"):
        build_operator_review_packet(object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="exact LocalCacheProbeOperatorReviewPacket"):
        render_operator_review_packet_json(object())  # type: ignore[arg-type]
