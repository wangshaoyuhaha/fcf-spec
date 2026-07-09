from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.stale_marker_inventory import (
    ACTIONABLE_STALE_STATE,
    EXPECTED_FINAL_STATE_HISTORY,
    build_stale_marker_inventory,
)
from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.stale_marker_cleanup_plan import (
    CURRENT_STATE_REPLACEMENT_TEXT,
    PRESERVE_HISTORY,
    REPLACE_WITH_CURRENT_STATE,
    build_cleanup_plan,
    cleanup_plan_is_read_only,
    cleanup_plan_preserves_history,
    cleanup_plan_requires_review,
)


CURRENT_TRUTH_TEXT = """
Completed Phase: CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1
main merge commit: ad16c03
D6 final closeout commit: 42ffeef
final handoff sync commit: 8c18573
validation: 1884 passed
"""


def test_d3_cleanup_plan_replaces_actionable_stale_markers():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": """
Next action:
Approved but not started
Begin with D1
""" + CURRENT_TRUTH_TEXT,
        }
    )

    plan = build_cleanup_plan(inventory)

    assert plan.total_inventory_hits == 2
    assert plan.cleanup_action_count == 2
    assert plan.operator_review_required is True
    assert all(item.planned_action == REPLACE_WITH_CURRENT_STATE for item in plan.items)
    assert all(item.classification_label == ACTIONABLE_STALE_STATE for item in plan.items)


def test_d3_cleanup_plan_preserves_historical_markers():
    inventory = build_stale_marker_inventory(
        {
            "docs/FCF_PROJECT_CONTROL_CENTER.md": """
Completed Phase: OLD-PHASE
historical record
1836 passed
""" + CURRENT_TRUTH_TEXT,
        }
    )

    plan = build_cleanup_plan(inventory)

    assert plan.total_inventory_hits == 1
    assert plan.cleanup_action_count == 0
    assert plan.preserved_history_count == 1
    assert plan.items[0].planned_action == PRESERVE_HISTORY
    assert plan.items[0].classification_label == EXPECTED_FINAL_STATE_HISTORY
    assert cleanup_plan_preserves_history(plan) is True


def test_d3_current_state_replacement_text_contains_truth_markers():
    assert "CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 is completed" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "ad16c03" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "8c18573" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "1884 passed" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "Git status: clean" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "origin/main: synced" in CURRENT_STATE_REPLACEMENT_TEXT


def test_d3_mixed_inventory_routes_actionable_and_history_separately():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": """
Next action:
Create sidecar branch
""" + CURRENT_TRUTH_TEXT,
            "docs/FCF_PROJECT_CONTROL_CENTER.md": """
Completed Phase: OLD-PHASE
historical closeout
1836 passed
""" + CURRENT_TRUTH_TEXT,
        }
    )

    plan = build_cleanup_plan(inventory)

    actions = [item.planned_action for item in plan.items]
    assert actions.count(REPLACE_WITH_CURRENT_STATE) == 1
    assert actions.count(PRESERVE_HISTORY) == 1
    assert plan.cleanup_action_count == 1
    assert plan.preserved_history_count == 1


def test_d3_plan_is_read_only_and_does_not_mutate_files():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": """
Next action:
Approved but not started
""" + CURRENT_TRUTH_TEXT,
        }
    )

    plan = build_cleanup_plan(inventory)

    assert plan.files_mutated is False
    assert plan.safety_boundary_preserved is True
    assert cleanup_plan_is_read_only(plan) is True


def test_d3_empty_inventory_has_no_actions_and_no_review():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": CURRENT_TRUTH_TEXT,
        }
    )

    plan = build_cleanup_plan(inventory)

    assert plan.total_inventory_hits == 0
    assert plan.cleanup_action_count == 0
    assert plan.preserved_history_count == 0
    assert plan.operator_review_required is False
    assert cleanup_plan_is_read_only(plan) is True


def test_d3_cleanup_plan_requires_review_when_actions_exist():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": """
Next action:
Begin with D1
""" + CURRENT_TRUTH_TEXT,
        }
    )

    plan = build_cleanup_plan(inventory)

    assert cleanup_plan_requires_review(plan) is True
    assert plan.items[0].review_required is True


def test_d3_historical_items_do_not_require_review():
    inventory = build_stale_marker_inventory(
        {
            "docs/FCF_PROJECT_CONTROL_CENTER.md": """
Completed Phase: OLD-PHASE
historical record
1876 passed
""" + CURRENT_TRUTH_TEXT,
        }
    )

    plan = build_cleanup_plan(inventory)

    assert plan.items[0].review_required is False
    assert plan.items[0].replacement_text == ""
