import json
from pathlib import Path

from scripts.control_center_project_memory_guard import (
    AUTHORITY_PATHS,
    EXPECTED_FILE_ROLES,
    EXPECTED_FUTURE_ARCHITECTURE,
    EXPECTED_SAFETY,
    FINAL_EVIDENCE_COMMITS,
    FUTURE_STATUSES,
    GAP_ROADMAP_FINAL_LINES,
    GAP_ROADMAP_R7_APPROVAL_LINES,
    GAP_ROADMAP_R7_DELIVERY_LINES,
    GAP_ROADMAP_R7_FINAL_LINES,
    GAP_ROADMAP_R8_APPROVAL_LINES,
    GAP_ROADMAP_R8_DELIVERY_LINES,
    GAP_ROADMAP_R8_FINAL_LINES,
    GAP_ROADMAP_R9_APPROVAL_LINES,
    GAP_ROADMAP_R9_DELIVERY_LINES,
    GAP_ROADMAP_R9_FINAL_LINES,
    GAP_ROADMAP_R10_APPROVAL_LINES,
    GAP_ROADMAP_R10_DELIVERY_LINES,
    GAP_ROADMAP_R10_FINAL_LINES,
    GAP_ROADMAP_R11_APPROVAL_LINES,
    GAP_ROADMAP_R11_DELIVERY_LINES,
    GAP_ROADMAP_R11_FINAL_LINES,
    GAP_ROADMAP_R12_APPROVAL_LINES,
    GAP_ROADMAP_R12_DELIVERY_LINES,
    GAP_ROADMAP_R12_FINAL_LINES,
    GAP_ROADMAP_R13_APPROVAL_LINES,
    GAP_ROADMAP_R13_DELIVERY_LINES,
    GAP_ROADMAP_R13_FINAL_LINES,
    GAP_ROADMAP_R14_APPROVAL_LINES,
    GAP_ROADMAP_R14_DELIVERY_LINES,
    GAP_ROADMAP_R14_FINAL_LINES,
    GAP_ROADMAP_R15_APPROVAL_LINES,
    GAP_ROADMAP_R15_DELIVERY_LINES,
    MEMORY_FINAL_END,
    MEMORY_FINAL_START,
    MEMORY_LOCK_END,
    MEMORY_LOCK_START,
    SESSION_APPROVAL_END,
    SESSION_APPROVAL_START,
    SESSION_LOCK_END,
    SESSION_LOCK_START,
    SESSION_FINAL_END,
    SESSION_FINAL_EVIDENCE_COMMITS,
    SESSION_FINAL_START,
    ROADMAP_PHASES,
    ROADMAP_STATUS,
    V2_R1_APPROVAL_END,
    V2_R1_APPROVAL_ROADMAP,
    V2_R1_APPROVAL_START,
    V2_R1_APPROVAL_STATE,
    V2_R1_FINAL_END,
    V2_R1_FINAL_EVIDENCE_COMMITS,
    V2_R1_FINAL_ROADMAP,
    V2_R1_FINAL_START,
    V2_R1_FINAL_STATE,
    V2_R1_LOCK_END,
    V2_R1_LOCK_START,
    V2_R2_APPROVAL_END,
    V2_R2_APPROVAL_ROADMAP,
    V2_R2_APPROVAL_START,
    V2_R2_APPROVAL_STATE,
    V2_R2_FINAL_END,
    V2_R2_FINAL_EVIDENCE_COMMITS,
    V2_R2_FINAL_ROADMAP,
    V2_R2_FINAL_START,
    V2_R2_FINAL_STATE,
    V2_R2_VALIDATED_ROADMAP,
    V2_R2_VALIDATED_STATE,
    V2_R2_LOCK_END,
    V2_R2_LOCK_START,
    V2_R3_APPROVAL_END,
    V2_R3_APPROVAL_ROADMAP,
    V2_R3_APPROVAL_START,
    V2_R3_APPROVAL_STATE,
    V2_R3_DELIVERY_ROADMAP,
    V2_R3_DELIVERY_STATE,
    V2_R3_FINAL_END,
    V2_R3_FINAL_EVIDENCE_COMMITS,
    V2_R3_FINAL_ROADMAP,
    V2_R3_FINAL_START,
    V2_R3_FINAL_STATE,
    V2_R3_LOCK_END,
    V2_R3_LOCK_START,
    V2_R3_VALIDATED_ROADMAP,
    V2_R3_VALIDATED_STATE,
    V2_R4_APPROVAL_END,
    V2_R4_APPROVAL_ROADMAP,
    V2_R4_APPROVAL_START,
    V2_R4_APPROVAL_STATE,
    V2_R4_DELIVERY_ROADMAP,
    V2_R4_DELIVERY_STATE,
    V2_R4_FINAL_END,
    V2_R4_FINAL_EVIDENCE_COMMITS,
    V2_R4_FINAL_ROADMAP,
    V2_R4_FINAL_START,
    V2_R4_FINAL_STATE,
    V2_R4_LOCK_END,
    V2_R4_LOCK_START,
    V2_R4_VALIDATED_ROADMAP,
    V2_R4_VALIDATED_STATE,
    V2_R5_APPROVAL_END,
    V2_R5_APPROVAL_ROADMAP,
    V2_R5_APPROVAL_START,
    V2_R5_APPROVAL_STATE,
    V2_R5_DELIVERY_ROADMAP,
    V2_R5_DELIVERY_STATE,
    V2_R5_FINAL_END,
    V2_R5_FINAL_EVIDENCE_COMMITS,
    V2_R5_FINAL_ROADMAP,
    V2_R5_FINAL_START,
    V2_R5_FINAL_STATE,
    V2_R5_LOCK_END,
    V2_R5_LOCK_START,
    V2_R5_VALIDATED_ROADMAP,
    V2_R5_VALIDATED_STATE,
    V2_R6_APPROVAL_END,
    V2_R6_APPROVAL_ROADMAP,
    V2_R6_APPROVAL_START,
    V2_R6_APPROVAL_STATE,
    V2_R6_DELIVERY_ROADMAP,
    V2_R6_DELIVERY_STATE,
    V2_R6_FINAL_END,
    V2_R6_FINAL_EVIDENCE_COMMITS,
    V2_R6_FINAL_ROADMAP,
    V2_R6_FINAL_START,
    V2_R6_FINAL_STATE,
    V2_R6_LOCK_END,
    V2_R6_LOCK_START,
    V2_R6_VALIDATED_ROADMAP,
    V2_R6_VALIDATED_STATE,
    V2_R7_APPROVAL_END,
    V2_R7_APPROVAL_ROADMAP,
    V2_R7_APPROVAL_START,
    V2_R7_APPROVAL_STATE,
    V2_R7_DELIVERY_ROADMAP,
    V2_R7_DELIVERY_STATE,
    V2_R7_LOCK_END,
    V2_R7_LOCK_START,
    V2_R7_FINAL_END,
    V2_R7_FINAL_EVIDENCE_COMMITS,
    V2_R7_FINAL_ROADMAP,
    V2_R7_FINAL_START,
    V2_R7_FINAL_STATE,
    V2_R7_VALIDATED_ROADMAP,
    V2_R7_VALIDATED_STATE,
    V2_R8_APPROVAL_END,
    V2_R8_APPROVAL_ROADMAP,
    V2_R8_APPROVAL_START,
    V2_R8_APPROVAL_STATE,
    V2_R8_DELIVERY_ROADMAP,
    V2_R8_DELIVERY_STATE,
    V2_R8_LOCK_END,
    V2_R8_LOCK_START,
    V2_R8_FINAL_END,
    V2_R8_FINAL_EVIDENCE_COMMITS,
    V2_R8_FINAL_ROADMAP,
    V2_R8_FINAL_START,
    V2_R8_FINAL_STATE,
    V2_R8_VALIDATED_ROADMAP,
    V2_R8_VALIDATED_STATE,
    V2_R9_APPROVAL_END,
    V2_R9_APPROVAL_ROADMAP,
    V2_R9_APPROVAL_START,
    V2_R9_APPROVAL_STATE,
    V2_R9_DELIVERY_ROADMAP,
    V2_R9_DELIVERY_STATE,
    V2_R9_LOCK_END,
    V2_R9_LOCK_START,
    V2_R9_FINAL_END,
    V2_R9_FINAL_EVIDENCE_COMMITS,
    V2_R9_FINAL_ROADMAP,
    V2_R9_FINAL_START,
    V2_R9_FINAL_STATE,
    V2_R9_VALIDATED_ROADMAP,
    V2_R9_VALIDATED_STATE,
    V2_R10_APPROVAL_END,
    V2_R10_APPROVAL_ROADMAP,
    V2_R10_APPROVAL_START,
    V2_R10_APPROVAL_STATE,
    V2_R10_DELIVERY_ROADMAP,
    V2_R10_DELIVERY_STATE,
    V2_R10_FINAL_END,
    V2_R10_FINAL_EVIDENCE_COMMITS,
    V2_R10_FINAL_ROADMAP,
    V2_R10_FINAL_START,
    V2_R10_FINAL_STATE,
    V2_R10_LOCK_END,
    V2_R10_LOCK_START,
    V2_R10_VALIDATED_ROADMAP,
    V2_R10_VALIDATED_STATE,
    V2_R11_APPROVAL_END,
    V2_R11_APPROVAL_ROADMAP,
    V2_R11_APPROVAL_START,
    V2_R11_APPROVAL_STATE,
    V2_R11_DELIVERY_ROADMAP,
    V2_R11_DELIVERY_STATE,
    V2_R11_FINAL_END,
    V2_R11_FINAL_EVIDENCE_COMMITS,
    V2_R11_FINAL_ROADMAP,
    V2_R11_FINAL_START,
    V2_R11_FINAL_STATE,
    V2_R11_LOCK_END,
    V2_R11_LOCK_START,
    V2_R11_VALIDATED_ROADMAP,
    V2_R11_VALIDATED_STATE,
    V2_R12_APPROVAL_END,
    V2_R12_APPROVAL_ROADMAP,
    V2_R12_APPROVAL_START,
    V2_R12_APPROVAL_STATE,
    V2_R12_DELIVERY_ROADMAP,
    V2_R12_DELIVERY_STATE,
    V2_R12_FINAL_END,
    V2_R12_FINAL_EVIDENCE_COMMITS,
    V2_R12_FINAL_ROADMAP,
    V2_R12_FINAL_START,
    V2_R12_FINAL_STATE,
    V2_R12_LOCK_END,
    V2_R12_LOCK_START,
    V2_R12_VALIDATED_ROADMAP,
    V2_R12_VALIDATED_STATE,
    V2_R13_APPROVAL_END,
    V2_R13_APPROVAL_ROADMAP,
    V2_R13_APPROVAL_START,
    V2_R13_APPROVAL_STATE,
    V2_R13_DELIVERY_ROADMAP,
    V2_R13_DELIVERY_STATE,
    V2_R13_LOCK_END,
    V2_R13_LOCK_START,
    V2_R13_FINAL_END,
    V2_R13_FINAL_EVIDENCE_COMMITS,
    V2_R13_FINAL_ROADMAP,
    V2_R13_FINAL_START,
    V2_R13_FINAL_STATE,
    V2_R13_VALIDATED_ROADMAP,
    V2_R13_VALIDATED_STATE,
    V2_R14_APPROVAL_END,
    V2_R14_APPROVAL_ROADMAP,
    V2_R14_APPROVAL_START,
    V2_R14_APPROVAL_STATE,
    V2_R14_DELIVERY_ROADMAP,
    V2_R14_DELIVERY_STATE,
    V2_R14_FINAL_END,
    V2_R14_FINAL_EVIDENCE_COMMITS,
    V2_R14_FINAL_ROADMAP,
    V2_R14_FINAL_START,
    V2_R14_FINAL_STATE,
    V2_R14_LOCK_END,
    V2_R14_LOCK_START,
    V2_R14_VALIDATED_ROADMAP,
    V2_R14_VALIDATED_STATE,
    V2_R15_APPROVAL_END,
    V2_R15_APPROVAL_ROADMAP,
    V2_R15_APPROVAL_START,
    V2_R15_APPROVAL_STATE,
    V2_R15_DELIVERY_ROADMAP,
    V2_R15_DELIVERY_STATE,
    V2_R15_VALIDATED_ROADMAP,
    V2_R15_VALIDATED_STATE,
    blocks_are_exact,
    build_project_memory_guard_report,
    extract_single_block,
    extract_gap_rows,
    gap_statuses_are_valid,
    load_manifest,
    main,
)


ROOT = Path(__file__).resolve().parents[1]


def test_project_memory_guard_passes_repository():
    report = build_project_memory_guard_report(ROOT)

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_project_memory_guard_main_passes():
    assert main() == 0


def test_current_state_manifest_has_exact_file_roles_and_safety():
    manifest = load_manifest(ROOT)

    assert manifest["active_authority_sources"] == [
        path.as_posix() for path in AUTHORITY_PATHS
    ]
    assert manifest["canonical_file_roles"] == EXPECTED_FILE_ROLES
    assert (
        manifest["accepted_future_architecture"]
        == EXPECTED_FUTURE_ARCHITECTURE
    )
    assert manifest["safety_boundaries"] == EXPECTED_SAFETY
    assert all((ROOT / path).is_file() for path in EXPECTED_FILE_ROLES.values())


def test_current_state_manifest_records_exact_v2_r15_validated_state():
    manifest = load_manifest(ROOT)
    truth = manifest["current_truth"]

    assert truth == V2_R15_VALIDATED_STATE
    assert manifest["roadmap"] == V2_R15_VALIDATED_ROADMAP


def test_future_status_vocabulary_is_closed_and_excluded_gaps_are_preserved():
    manifest = load_manifest(ROOT)
    gap = (
        ROOT / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
    ).read_text(encoding="ascii")
    rows = dict(extract_gap_rows(gap))

    assert manifest["future_capability_statuses"] == list(FUTURE_STATUSES)
    assert gap_statuses_are_valid(gap)
    assert rows["V2-FR-GAP-041"] == "OUTSIDE_CURRENT_AUTHORIZATION"
    assert rows["V2-FR-GAP-065"] == "OUTSIDE_CURRENT_AUTHORIZATION"
    assert all(line in gap for line in GAP_ROADMAP_R15_DELIVERY_LINES)


def test_unknown_gap_status_is_rejected():
    gap = (
        ROOT / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
    ).read_text(encoding="ascii")
    unsafe = gap.replace(
        "| V2-FR-GAP-041 | Paper order and virtual-account runtime | "
        "OUTSIDE_CURRENT_AUTHORIZATION |",
        "| V2-FR-GAP-041 | Paper order and virtual-account runtime | UNKNOWN |",
    )

    assert gap_statuses_are_valid(unsafe) is False


def test_memory_lock_is_exact_across_all_authority_sources():
    texts = tuple(
        (ROOT / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS
    )

    assert blocks_are_exact(texts, MEMORY_LOCK_START, MEMORY_LOCK_END)


def test_memory_final_sync_is_exact_across_all_authority_sources():
    texts = tuple(
        (ROOT / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS
    )

    assert blocks_are_exact(texts, MEMORY_FINAL_START, MEMORY_FINAL_END)
    blocks = tuple(
        extract_single_block(text, MEMORY_FINAL_START, MEMORY_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )


def test_market_session_approval_and_lock_are_exact_across_authorities():
    texts = tuple(
        (ROOT / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS
    )

    assert blocks_are_exact(
        texts, SESSION_APPROVAL_START, SESSION_APPROVAL_END
    )
    assert blocks_are_exact(texts, SESSION_LOCK_START, SESSION_LOCK_END)
    assert blocks_are_exact(texts, SESSION_FINAL_START, SESSION_FINAL_END)
    blocks = tuple(
        extract_single_block(text, SESSION_FINAL_START, SESSION_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in SESSION_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )


def test_v2_r1_approval_is_exact_across_authorities():
    texts = tuple(
        (ROOT / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS
    )

    assert blocks_are_exact(
        texts, V2_R1_APPROVAL_START, V2_R1_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R1_LOCK_START, V2_R1_LOCK_END)
    assert blocks_are_exact(texts, V2_R1_FINAL_START, V2_R1_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R1_FINAL_START, V2_R1_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R1_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R2_APPROVAL_START, V2_R2_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R2_LOCK_START, V2_R2_LOCK_END)
    assert blocks_are_exact(texts, V2_R2_FINAL_START, V2_R2_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R2_FINAL_START, V2_R2_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R2_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R3_APPROVAL_START, V2_R3_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R3_LOCK_START, V2_R3_LOCK_END)
    assert blocks_are_exact(texts, V2_R3_FINAL_START, V2_R3_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R3_FINAL_START, V2_R3_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R3_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R4_APPROVAL_START, V2_R4_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R4_LOCK_START, V2_R4_LOCK_END)
    assert blocks_are_exact(texts, V2_R4_FINAL_START, V2_R4_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R4_FINAL_START, V2_R4_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R4_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R5_APPROVAL_START, V2_R5_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R5_LOCK_START, V2_R5_LOCK_END)
    assert blocks_are_exact(texts, V2_R5_FINAL_START, V2_R5_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R5_FINAL_START, V2_R5_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R5_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R6_APPROVAL_START, V2_R6_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R6_LOCK_START, V2_R6_LOCK_END)
    assert blocks_are_exact(texts, V2_R6_FINAL_START, V2_R6_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R6_FINAL_START, V2_R6_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R6_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R7_APPROVAL_START, V2_R7_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R7_LOCK_START, V2_R7_LOCK_END)
    assert blocks_are_exact(texts, V2_R7_FINAL_START, V2_R7_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R7_FINAL_START, V2_R7_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R7_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R8_APPROVAL_START, V2_R8_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R8_LOCK_START, V2_R8_LOCK_END)
    assert blocks_are_exact(texts, V2_R8_FINAL_START, V2_R8_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R8_FINAL_START, V2_R8_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R8_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R9_APPROVAL_START, V2_R9_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R9_LOCK_START, V2_R9_LOCK_END)
    assert blocks_are_exact(texts, V2_R9_FINAL_START, V2_R9_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R9_FINAL_START, V2_R9_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R9_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R10_APPROVAL_START, V2_R10_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R10_LOCK_START, V2_R10_LOCK_END)
    assert blocks_are_exact(texts, V2_R10_FINAL_START, V2_R10_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R10_FINAL_START, V2_R10_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R10_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R11_APPROVAL_START, V2_R11_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R11_LOCK_START, V2_R11_LOCK_END)
    assert blocks_are_exact(texts, V2_R11_FINAL_START, V2_R11_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R11_FINAL_START, V2_R11_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R11_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R12_APPROVAL_START, V2_R12_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R12_LOCK_START, V2_R12_LOCK_END)
    assert blocks_are_exact(texts, V2_R12_FINAL_START, V2_R12_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R12_FINAL_START, V2_R12_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R12_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R13_APPROVAL_START, V2_R13_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R13_LOCK_START, V2_R13_LOCK_END)
    assert blocks_are_exact(texts, V2_R13_FINAL_START, V2_R13_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R13_FINAL_START, V2_R13_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R13_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R14_APPROVAL_START, V2_R14_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R14_LOCK_START, V2_R14_LOCK_END)
    assert blocks_are_exact(texts, V2_R14_FINAL_START, V2_R14_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R14_FINAL_START, V2_R14_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R14_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R15_APPROVAL_START, V2_R15_APPROVAL_END
    )


def test_manifest_is_deterministic_json_and_historical_order_is_not_current():
    path = ROOT / "FCF_CURRENT_STATE_MANIFEST.json"
    text = path.read_text(encoding="ascii")
    parsed = json.loads(text)

    assert text.endswith("\n")
    assert parsed["historical_registry"]["status"] == (
        "HISTORICAL_COMPLETED_SEQUENCE_NOT_CURRENT_NEXT_PHASE_AUTHORITY"
    )
    assert parsed["current_truth"]["next_product_phase_approval"] == (
        V2_R15_DELIVERY_STATE["next_product_phase_approval"]
    )
