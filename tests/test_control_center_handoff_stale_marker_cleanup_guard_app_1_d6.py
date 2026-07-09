from pathlib import Path

from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.final_closeout import (
    COMPLETED_STAGE_IDS,
    PHASE_ID,
    build_final_closeout,
    final_closeout_preserves_safety_boundary,
    final_closeout_ready_for_merge_review,
)


TARGET_FILES = [
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
    Path("docs/HANDOFF_PROMPT.md"),
]


def test_d6_final_closeout_contains_phase_and_all_stages():
    closeout = build_final_closeout()

    assert closeout.phase_id == PHASE_ID
    assert closeout.completed_stage_ids == COMPLETED_STAGE_IDS
    assert len(closeout.completed_stage_ids) == 6


def test_d6_all_target_handoff_files_have_current_truth_header():
    for path in TARGET_FILES:
        text = path.read_text(encoding="utf-8")
        assert "FCF CURRENT HANDOFF TRUTH - STALE MARKER CLEANUP APPLIED" in text


def test_d6_current_truth_header_contains_completed_global_scan_phase():
    for path in TARGET_FILES:
        text = path.read_text(encoding="utf-8")
        assert "CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 is completed" in text


def test_d6_current_truth_header_contains_commits_and_validation():
    for path in TARGET_FILES:
        text = path.read_text(encoding="utf-8")
        assert "ad16c03" in text
        assert "8c18573" in text
        assert "1884 passed" in text
        assert "git status: clean" in text
        assert "origin/main: synced" in text


def test_d6_stale_marker_rule_is_visible():
    for path in TARGET_FILES:
        text = path.read_text(encoding="utf-8")
        assert "historical unless explicitly re-approved by the operator" in text
        assert "Architecture gap review or explicitly approved next phase only" in text


def test_d6_final_closeout_preserves_safety_boundary():
    closeout = build_final_closeout()

    assert closeout.paper_only is True
    assert closeout.local_only is True
    assert closeout.read_only is True
    assert closeout.sidecar_only is True
    assert closeout.operator_review_required is True
    assert final_closeout_preserves_safety_boundary(closeout) is True


def test_d6_final_closeout_forbids_unsafe_actions():
    closeout = build_final_closeout()

    assert closeout.p48_allowed is False
    assert closeout.core_mutation_allowed is False
    assert closeout.runtime_mutation_allowed is False
    assert closeout.real_trading_allowed is False
    assert closeout.broker_api_allowed is False
    assert closeout.exchange_api_allowed is False
    assert closeout.api_key_allowed is False
    assert closeout.wallet_private_key_allowed is False
    assert closeout.buy_sell_order_allowed is False


def test_d6_final_closeout_forbids_tag_release_deploy():
    closeout = build_final_closeout()

    assert closeout.tag_release_deploy_allowed is False
    assert final_closeout_ready_for_merge_review(closeout) is True
