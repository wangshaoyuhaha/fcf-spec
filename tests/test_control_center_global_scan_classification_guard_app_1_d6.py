from sidecars.control_center_global_scan_classification_guard_app_1.classification_packet import (
    RawScanHit,
)
from sidecars.control_center_global_scan_classification_guard_app_1.final_closeout import (
    COMPLETED_STAGE_IDS,
    PHASE_ID,
    build_final_closeout,
    final_closeout_preserves_safety_boundary,
    final_closeout_ready_for_operator_merge_review,
)
from sidecars.control_center_global_scan_classification_guard_app_1.review_gate import (
    EXPECTED_ONLY_VISIBLE,
    UNSAFE_PERMISSION_BLOCKED,
)


def test_d6_final_closeout_contains_phase_and_all_stages():
    closeout = build_final_closeout((), packet_id="D6-PACKET-001")

    assert closeout.phase_id == PHASE_ID
    assert closeout.completed_stage_ids == COMPLETED_STAGE_IDS
    assert len(closeout.completed_stage_ids) == 6


def test_d6_final_closeout_expected_only_ready_for_operator_merge_review():
    closeout = build_final_closeout(
        (
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no real trading and no broker connection",
            ),
        ),
        packet_id="D6-PACKET-002",
    )

    assert closeout.review_packet.gate_status == EXPECTED_ONLY_VISIBLE
    assert closeout.all_records_visible is True
    assert closeout.actionable_queue_complete is True
    assert final_closeout_ready_for_operator_merge_review(closeout) is True


def test_d6_final_closeout_blocks_unsafe_permission_until_review():
    closeout = build_final_closeout(
        (
            RawScanHit(
                source_path="docs/example.md",
                matched_text="broker API enabled for real trading",
            ),
        ),
        packet_id="D6-PACKET-003",
    )

    assert closeout.review_packet.gate_status == UNSAFE_PERMISSION_BLOCKED
    assert closeout.review_packet.blocked_until_review is True
    assert closeout.unsafe_permission_blocked_until_review is True
    assert final_closeout_ready_for_operator_merge_review(closeout) is True


def test_d6_final_closeout_preserves_record_visibility_for_mixed_hits():
    closeout = build_final_closeout(
        (
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no real execution",
            ),
            RawScanHit(
                source_path="docs/architecture.md",
                matched_text="missing provenance",
            ),
            RawScanHit(
                source_path="docs/example.md",
                matched_text="buy button enabled",
            ),
        ),
        packet_id="D6-PACKET-004",
    )

    assert closeout.review_packet.total_hit_count == 3
    assert closeout.review_packet.records_visible_count == 3
    assert closeout.all_records_visible is True
    assert closeout.actionable_queue_complete is True


def test_d6_final_closeout_preserves_safety_boundary_flags():
    closeout = build_final_closeout((), packet_id="D6-PACKET-005")

    assert closeout.paper_only is True
    assert closeout.local_only is True
    assert closeout.read_only is True
    assert closeout.sidecar_only is True
    assert closeout.operator_review_required is True
    assert final_closeout_preserves_safety_boundary(closeout) is True


def test_d6_final_closeout_forbids_core_and_source_mutation():
    closeout = build_final_closeout((), packet_id="D6-PACKET-006")

    assert closeout.p48_core_expansion_allowed is False
    assert closeout.core_mutation_allowed is False
    assert closeout.source_mutation_allowed is False
    assert closeout.runtime_mutation_allowed is False
    assert closeout.handoff_mutation_allowed is False


def test_d6_final_closeout_forbids_trading_and_credentials():
    closeout = build_final_closeout((), packet_id="D6-PACKET-007")

    assert closeout.real_trading_allowed is False
    assert closeout.broker_api_allowed is False
    assert closeout.exchange_api_allowed is False
    assert closeout.api_key_allowed is False
    assert closeout.wallet_private_key_allowed is False
    assert closeout.buy_sell_order_allowed is False


def test_d6_final_closeout_forbids_tag_release_deploy():
    closeout = build_final_closeout((), packet_id="D6-PACKET-008")

    assert closeout.tag_release_deploy_allowed is False
    assert final_closeout_ready_for_operator_merge_review(closeout) is True
