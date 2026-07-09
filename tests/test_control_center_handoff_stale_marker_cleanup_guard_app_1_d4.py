from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.stale_marker_inventory import (
    build_stale_marker_inventory,
)
from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.stale_marker_cleanup_plan import (
    CURRENT_STATE_REPLACEMENT_TEXT,
    build_cleanup_plan,
)
from sidecars.control_center_handoff_stale_marker_cleanup_guard_app_1.stale_marker_patch_builder import (
    PATCH_PRESERVE_HISTORY,
    PATCH_REPLACE_WITH_CURRENT_STATE,
    build_cleanup_patch_packet,
    patch_packet_is_not_applied,
    patch_packet_preserves_safety_boundary,
    patch_packet_preserves_visibility,
    patch_packet_requires_review,
)


CURRENT_TRUTH_TEXT = """
Completed Phase: CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1
main merge commit: ad16c03
D6 final closeout commit: 42ffeef
final handoff sync commit: 8c18573
validation: 1884 passed
"""


def test_d4_patch_builder_creates_replace_items_for_actionable_stale_markers():
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
    packet = build_cleanup_patch_packet(plan)

    assert packet.total_plan_items == 2
    assert packet.replace_patch_count == 2
    assert packet.preserve_patch_count == 0
    assert all(item.patch_action == PATCH_REPLACE_WITH_CURRENT_STATE for item in packet.patch_items)
    assert all(item.review_required is True for item in packet.patch_items)


def test_d4_patch_builder_preserves_historical_items():
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
    packet = build_cleanup_patch_packet(plan)

    assert packet.total_plan_items == 1
    assert packet.replace_patch_count == 0
    assert packet.preserve_patch_count == 1
    assert packet.patch_items[0].patch_action == PATCH_PRESERVE_HISTORY
    assert packet.patch_items[0].replacement_text == ""
    assert packet.patch_items[0].review_required is False


def test_d4_patch_packet_preserves_source_path_and_line_number():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": """
Next action:
Create sidecar branch
""" + CURRENT_TRUTH_TEXT,
        }
    )
    plan = build_cleanup_plan(inventory)
    packet = build_cleanup_patch_packet(plan)

    item = packet.patch_items[0]
    assert item.source_path == "docs/HANDOFF_PROMPT.md"
    assert isinstance(item.line_number, int)
    assert item.line_number > 0
    assert "Create sidecar branch" in item.original_line_text


def test_d4_replacement_text_contains_current_truth():
    assert "CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 is completed" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "ad16c03" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "8c18573" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "1884 passed" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "Git status: clean" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "origin/main: synced" in CURRENT_STATE_REPLACEMENT_TEXT
    assert "Next work requires explicit operator approval" in CURRENT_STATE_REPLACEMENT_TEXT


def test_d4_mixed_packet_counts_replace_and_preserve_items():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": """
Next action:
Begin with D1
""" + CURRENT_TRUTH_TEXT,
            "docs/FCF_PROJECT_CONTROL_CENTER.md": """
Completed Phase: OLD-PHASE
historical closeout
1876 passed
""" + CURRENT_TRUTH_TEXT,
        }
    )
    plan = build_cleanup_plan(inventory)
    packet = build_cleanup_patch_packet(plan)

    assert packet.total_plan_items == 2
    assert packet.replace_patch_count == 1
    assert packet.preserve_patch_count == 1
    assert patch_packet_preserves_visibility(packet) is True


def test_d4_patch_packet_is_not_applied_and_does_not_mutate_files():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": """
Next action:
Approved but not started
""" + CURRENT_TRUTH_TEXT,
        }
    )
    plan = build_cleanup_plan(inventory)
    packet = build_cleanup_patch_packet(plan)

    assert packet.patch_applied is False
    assert packet.files_mutated is False
    assert patch_packet_is_not_applied(packet) is True


def test_d4_patch_packet_requires_review_when_replace_items_exist():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": """
Next action:
Approved but not started
""" + CURRENT_TRUTH_TEXT,
        }
    )
    plan = build_cleanup_plan(inventory)
    packet = build_cleanup_patch_packet(plan)

    assert packet.operator_review_required is True
    assert patch_packet_requires_review(packet) is True


def test_d4_empty_patch_packet_has_no_review_requirement():
    inventory = build_stale_marker_inventory(
        {
            "docs/HANDOFF_PROMPT.md": CURRENT_TRUTH_TEXT,
        }
    )
    plan = build_cleanup_plan(inventory)
    packet = build_cleanup_patch_packet(plan)

    assert packet.total_plan_items == 0
    assert packet.replace_patch_count == 0
    assert packet.preserve_patch_count == 0
    assert packet.operator_review_required is False
    assert patch_packet_preserves_safety_boundary(packet) is True
