from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.controlled_handoff_cleanup import (
    CURRENT_TRUTH_HEADER,
    CURRENT_TRUTH_HEADER_TITLE,
    TARGET_HANDOFF_PATHS,
    apply_current_truth_header,
    cleanup_is_idempotent,
    has_current_truth_header,
    historical_content_preserved,
    safety_boundary_present,
)


def test_d5_target_paths_are_limited_to_four_handoff_files():
    assert set(TARGET_HANDOFF_PATHS) == {
        "docs/FCF_PROJECT_CONTROL_CENTER.md",
        "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
        "FCF_NEW_WINDOW_CHAT_PROMPT.md",
        "docs/HANDOFF_PROMPT.md",
    }


def test_d5_header_contains_current_truth_markers():
    assert "CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 is completed" in CURRENT_TRUTH_HEADER
    assert "ad16c03" in CURRENT_TRUTH_HEADER
    assert "8c18573" in CURRENT_TRUTH_HEADER
    assert "1884 passed" in CURRENT_TRUTH_HEADER
    assert "git status: clean" in CURRENT_TRUTH_HEADER
    assert "origin/main: synced" in CURRENT_TRUTH_HEADER


def test_d5_header_marks_old_stale_markers_as_historical():
    assert "Approved but not started" in CURRENT_TRUTH_HEADER
    assert "APPROVED NEXT PHASE" in CURRENT_TRUTH_HEADER
    assert "Begin with D1" in CURRENT_TRUTH_HEADER
    assert "Create sidecar branch" in CURRENT_TRUTH_HEADER
    assert "historical unless explicitly re-approved" in CURRENT_TRUTH_HEADER


def test_d5_apply_header_to_plain_text():
    original = "old handoff body"
    updated = apply_current_truth_header(original)

    assert CURRENT_TRUTH_HEADER_TITLE in updated
    assert updated.endswith(original)
    assert historical_content_preserved(original, updated) is True


def test_d5_apply_header_is_idempotent():
    original = "old handoff body"
    assert cleanup_is_idempotent(original) is True


def test_d5_existing_header_is_not_duplicated():
    original = CURRENT_TRUTH_HEADER + "\nold handoff body"
    updated = apply_current_truth_header(original)

    assert updated.count(CURRENT_TRUTH_HEADER_TITLE) == 1


def test_d5_safety_boundary_present_in_header():
    assert safety_boundary_present(CURRENT_TRUTH_HEADER) is True


def test_d5_header_declares_no_active_unapproved_next_phase():
    assert "Architecture gap review or explicitly approved next phase only" in CURRENT_TRUTH_HEADER
