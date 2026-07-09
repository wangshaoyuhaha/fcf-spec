from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.stale_marker_inventory import (
    ACTIONABLE_STALE_STATE,
    EXPECTED_FINAL_STATE_HISTORY,
    TARGET_HANDOFF_PATHS,
    build_stale_marker_inventory,
    inventory_preserves_read_only_boundary,
    inventory_requires_cleanup,
    is_target_handoff_path,
    scan_text_for_stale_markers,
)


CURRENT_TRUTH_TEXT = """
Completed Phase: CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1
main merge commit: ad16c03
D6 final closeout commit: 42ffeef
final handoff sync commit: 8c18573
validation: 1884 passed
"""


def test_d2_target_scope_is_limited_to_four_handoff_files():
    assert set(TARGET_HANDOFF_PATHS) == {
        "docs/FCF_PROJECT_CONTROL_CENTER.md",
        "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
        "FCF_NEW_WINDOW_CHAT_PROMPT.md",
        "docs/HANDOFF_PROMPT.md",
    }


def test_d2_non_target_path_returns_no_hits():
    hits = scan_text_for_stale_markers(
        "src/core/example.py",
        "Approved but not started\nBegin with D1",
    )
    assert hits == tuple()


def test_d2_current_entry_stale_marker_is_actionable():
    text = """
Next action:
Approved but not started
Begin with D1
Create sidecar branch
"""
    hits = scan_text_for_stale_markers("docs/HANDOFF_PROMPT.md", text)

    assert len(hits) == 3
    assert all(hit.classification_label == ACTIONABLE_STALE_STATE for hit in hits)
    assert all(hit.review_required is True for hit in hits)


def test_d2_historical_stale_marker_is_expected_history():
    text = """
Completed Phase: OLD-PHASE
historical closeout:
Approved but not started
1836 passed
"""
    hits = scan_text_for_stale_markers("docs/FCF_PROJECT_CONTROL_CENTER.md", text)

    assert len(hits) == 2
    assert all(hit.classification_label == EXPECTED_FINAL_STATE_HISTORY for hit in hits)
    assert all(hit.review_required is False for hit in hits)


def test_d2_old_validation_count_detected_as_marker_family():
    text = """
Next action:
1836 passed
"""
    hits = scan_text_for_stale_markers("FCF_NEW_WINDOW_CHAT_PROMPT.md", text)

    assert len(hits) == 1
    assert hits[0].marker_family == "OLD_VALIDATION_COUNT"
    assert hits[0].classification_label == ACTIONABLE_STALE_STATE


def test_d2_old_next_phase_candidate_detected():
    text = """
Next action:
UI-RISK-FLAG-VISIBILITY-APP-1 remains the next large sidecar candidate
"""
    hits = scan_text_for_stale_markers("docs/FCF_PROJECT_CONTROL_CENTER.md", text)

    assert len(hits) == 1
    assert hits[0].marker_family == "OLD_NEXT_PHASE_CANDIDATE"
    assert hits[0].classification_label == ACTIONABLE_STALE_STATE


def test_d2_inventory_counts_actionable_and_expected_hits():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": """
Next action:
Approved but not started
Begin with D1
""" + CURRENT_TRUTH_TEXT,
            "docs/FCF_PROJECT_CONTROL_CENTER.md": """
Completed Phase: OLD-PHASE
historical record
1836 passed
""" + CURRENT_TRUTH_TEXT,
        }
    )

    assert inventory.total_hit_count == 3
    assert inventory.actionable_stale_count == 2
    assert inventory.expected_history_count == 1
    assert inventory_requires_cleanup(inventory) is True


def test_d2_inventory_verifies_current_truth_markers_without_creating_stale_hits():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": CURRENT_TRUTH_TEXT,
            "FCF_NEW_WINDOW_CHAT_PROMPT.md": CURRENT_TRUTH_TEXT,
        }
    )

    assert inventory.current_truth_present is True
    assert inventory.total_hit_count == 0
    assert inventory.cleanup_performed is False


def test_d2_inventory_preserves_read_only_boundary():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": CURRENT_TRUTH_TEXT,
        }
    )

    assert inventory_preserves_read_only_boundary(inventory) is True
    assert inventory.cleanup_performed is False


def test_d2_target_path_checker_rejects_out_of_scope_paths():
    assert is_target_handoff_path("docs/HANDOFF_PROMPT.md") is True
    assert is_target_handoff_path("src/core/example.py") is False
    assert is_target_handoff_path("runtime/operator_console/example.json") is False
