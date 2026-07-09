from sidecars.control_center_global_scan_classification_guard_app_1.classification_rules import (
    ACTIONABLE_LABELS,
    ACTIONABLE_STALE_STATE,
    ACTIONABLE_STRUCTURE_GAP,
    ACTIONABLE_UNSAFE_PERMISSION,
    EXPECTED_FINAL_STATE_HISTORY,
    EXPECTED_GOVERNANCE_TEXT,
    EXPECTED_SAFETY_BOUNDARY,
    EXPECTED_TEST_ASSERTION,
    LABELS,
    classify_scan_hit,
    is_actionable,
    is_expected,
)


def test_d2_rulebook_has_exactly_seven_labels():
    assert set(LABELS) == {
        EXPECTED_GOVERNANCE_TEXT,
        EXPECTED_TEST_ASSERTION,
        EXPECTED_FINAL_STATE_HISTORY,
        EXPECTED_SAFETY_BOUNDARY,
        ACTIONABLE_STALE_STATE,
        ACTIONABLE_UNSAFE_PERMISSION,
        ACTIONABLE_STRUCTURE_GAP,
    }


def test_d2_actionable_labels_require_review():
    for label in ACTIONABLE_LABELS:
        assert is_actionable(label) is True
        assert is_expected(label) is False


def test_d2_expected_safety_boundary_is_visible_not_actionable():
    hit = classify_scan_hit(
        source_path="docs/HANDOFF_PROMPT.md",
        matched_text="no real trading, no broker connection, no buy sell order",
    )
    assert hit.classification_label == EXPECTED_SAFETY_BOUNDARY
    assert hit.review_required is False


def test_d2_expected_test_assertion_classification():
    hit = classify_scan_hit(
        source_path="tests/test_control_center_guard.py",
        matched_text="assert EXPECTED_GOVERNANCE_TEXT in labels",
    )
    assert hit.classification_label == EXPECTED_TEST_ASSERTION
    assert hit.review_required is False


def test_d2_expected_final_state_history_classification():
    hit = classify_scan_hit(
        source_path="FCF_CURRENT_STATE_MODEL_GOVERNANCE_APP_1_FINAL.md",
        matched_text="final current state validation history",
    )
    assert hit.classification_label == EXPECTED_FINAL_STATE_HISTORY
    assert hit.review_required is False


def test_d2_expected_governance_text_classification():
    hit = classify_scan_hit(
        source_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
        matched_text="governance policy approved by control center",
    )
    assert hit.classification_label == EXPECTED_GOVERNANCE_TEXT
    assert hit.review_required is False


def test_d2_actionable_unsafe_permission_classification():
    hit = classify_scan_hit(
        source_path="docs/example.md",
        matched_text="broker connection allowed for real trading",
    )
    assert hit.classification_label == ACTIONABLE_UNSAFE_PERMISSION
    assert hit.review_required is True


def test_d2_actionable_stale_state_classification():
    hit = classify_scan_hit(
        source_path="FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
        matched_text="obsolete validation count conflicts with current control center",
    )
    assert hit.classification_label == ACTIONABLE_STALE_STATE
    assert hit.review_required is True


def test_d2_actionable_structure_gap_classification():
    hit = classify_scan_hit(
        source_path="docs/architecture.md",
        matched_text="missing provenance and unclear ownership",
    )
    assert hit.classification_label == ACTIONABLE_STRUCTURE_GAP
    assert hit.review_required is True


def test_d2_conservative_priority_keeps_unsafe_permission_actionable():
    hit = classify_scan_hit(
        source_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
        matched_text="broker connection allowed for real trading",
        context="governance documentation",
    )
    assert hit.classification_label == ACTIONABLE_UNSAFE_PERMISSION
    assert hit.review_required is True
