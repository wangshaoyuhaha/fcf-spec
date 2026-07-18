import json
import subprocess
from pathlib import Path

import scripts.control_center_project_memory_guard as memory_guard

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
    GAP_ROADMAP_R15_FINAL_LINES,
    GAP_ROADMAP_R16_APPROVAL_LINES,
    GAP_ROADMAP_R16_DELIVERY_LINES,
    GAP_ROADMAP_R16_FINAL_LINES,
    GAP_ROADMAP_R17_APPROVAL_LINES,
    GAP_ROADMAP_R17_DELIVERY_LINES,
    GAP_ROADMAP_R17_FINAL_LINES,
    GAP_ROADMAP_R18_APPROVAL_LINES,
    GAP_ROADMAP_R18_DELIVERY_LINES,
    GAP_ROADMAP_R18_FINAL_LINES,
    GAP_ROADMAP_R19_APPROVAL_LINES,
    GAP_ROADMAP_R19_DELIVERY_LINES,
    GAP_ROADMAP_R19_FINAL_LINES,
    GAP_ROADMAP_R20_APPROVAL_LINES,
    GAP_ROADMAP_R20_DELIVERY_LINES,
    GAP_ROADMAP_R20_FINAL_LINES,
    GAP_ROADMAP_R21_APPROVAL_LINES,
    GAP_ROADMAP_R21_DELIVERY_LINES,
    GAP_ROADMAP_R21_FINAL_LINES,
    GAP_ROADMAP_R22_APPROVAL_LINES,
    GAP_ROADMAP_R22_DELIVERY_LINES,
    GAP_ROADMAP_R22_FINAL_LINES,
    GAP_ROADMAP_R23_DELIVERY_LINES,
    GAP_ROADMAP_R23_FINAL_LINES,
    GAP_ROADMAP_R24_DELIVERY_LINES,
    GAP_ROADMAP_R24_FINAL_LINES,
    GAP_ROADMAP_R25_APPROVAL_LINES,
    GAP_ROADMAP_R25_DELIVERY_LINES,
    GAP_ROADMAP_R25_FINAL_LINES,
    GAP_ROADMAP_R26_APPROVAL_LINES,
    GAP_ROADMAP_R26_DELIVERY_LINES,
    GAP_ROADMAP_R26_FINAL_LINES,
    GAP_ROADMAP_R27_APPROVAL_LINES,
    GAP_ROADMAP_R27_DELIVERY_LINES,
    GAP_ROADMAP_R27_FINAL_LINES,
    GAP_ROADMAP_R28_APPROVAL_LINES,
    GAP_ROADMAP_R28_DELIVERY_LINES,
    GAP_ROADMAP_R28_FINAL_LINES,
    GAP_ROADMAP_R29_APPROVAL_LINES,
    GAP_ROADMAP_R29_DELIVERY_LINES,
    GAP_ROADMAP_R29_FINAL_LINES,
    GAP_ROADMAP_R30_APPROVAL_LINES,
    GAP_ROADMAP_R30_DELIVERY_LINES,
    GAP_ROADMAP_R30_FINAL_LINES,
    GAP_ROADMAP_R31_APPROVAL_LINES,
    GAP_ROADMAP_R31_DELIVERY_LINES,
    GAP_ROADMAP_R31_FINAL_LINES,
    GAP_ROADMAP_R32_APPROVAL_LINES,
    GAP_ROADMAP_R32_DELIVERY_LINES,
    GAP_ROADMAP_R32_FINAL_LINES,
    GAP_ROADMAP_R33_APPROVAL_LINES,
    GAP_ROADMAP_R33_DELIVERY_LINES,
    GAP_ROADMAP_R33_FINAL_LINES,
    GAP_ROADMAP_R34_APPROVAL_LINES,
    GAP_ROADMAP_R34_DELIVERY_LINES,
    GAP_ROADMAP_R34_FINAL_LINES,
    GAP_ROADMAP_R35_APPROVAL_LINES,
    GAP_ROADMAP_R35_DELIVERY_LINES,
    GAP_ROADMAP_R35_FINAL_LINES,
    GAP_ROADMAP_R36_APPROVAL_LINES,
    GAP_ROADMAP_R36_DELIVERY_LINES,
    GAP_ROADMAP_R36_FINAL_LINES,
    GAP_ROADMAP_R37_APPROVAL_LINES,
    GAP_ROADMAP_R37_DELIVERY_LINES,
    GAP_ROADMAP_R37_FINAL_LINES,
    GAP_ROADMAP_R38_APPROVAL_LINES,
    GAP_ROADMAP_R38_DELIVERY_LINES,
    GAP_ROADMAP_R38_FINAL_LINES,
    GAP_ROADMAP_R39_APPROVAL_LINES,
    GAP_ROADMAP_R39_DELIVERY_LINES,
    GAP_ROADMAP_R39_FINAL_LINES,
    GAP_ROADMAP_R40_APPROVAL_LINES,
    GAP_ROADMAP_R40_DELIVERY_LINES,
    GAP_ROADMAP_R40_FINAL_LINES,
    GAP_ROADMAP_R41_APPROVAL_LINES,
    GAP_ROADMAP_R41_DELIVERY_LINES,
    GAP_ROADMAP_R41_FINAL_LINES,
    GAP_ROADMAP_R42_APPROVAL_LINES,
    GAP_ROADMAP_R42_DELIVERY_LINES,
    GAP_ROADMAP_R42_FINAL_LINES,
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
    V2_R15_FINAL_END,
    V2_R15_FINAL_EVIDENCE_COMMITS,
    V2_R15_FINAL_ROADMAP,
    V2_R15_FINAL_START,
    V2_R15_FINAL_STATE,
    V2_R15_LOCK_END,
    V2_R15_LOCK_START,
    V2_R15_VALIDATED_ROADMAP,
    V2_R15_VALIDATED_STATE,
    V2_R16_APPROVAL_END,
    V2_R16_APPROVAL_ROADMAP,
    V2_R16_APPROVAL_START,
    V2_R16_APPROVAL_STATE,
    V2_R16_DELIVERY_ROADMAP,
    V2_R16_DELIVERY_STATE,
    V2_R16_FINAL_END,
    V2_R16_FINAL_EVIDENCE_COMMITS,
    V2_R16_FINAL_ROADMAP,
    V2_R16_FINAL_START,
    V2_R16_FINAL_STATE,
    V2_R16_LOCK_END,
    V2_R16_LOCK_START,
    V2_R16_VALIDATED_ROADMAP,
    V2_R16_VALIDATED_STATE,
    V2_R17_APPROVAL_END,
    V2_R17_APPROVAL_ROADMAP,
    V2_R17_APPROVAL_START,
    V2_R17_APPROVAL_STATE,
    V2_R17_DELIVERY_ROADMAP,
    V2_R17_DELIVERY_STATE,
    V2_R17_FINAL_END,
    V2_R17_FINAL_EVIDENCE_COMMITS,
    V2_R17_FINAL_ROADMAP,
    V2_R17_FINAL_START,
    V2_R17_FINAL_STATE,
    V2_R17_LOCK_END,
    V2_R17_LOCK_START,
    V2_R18_APPROVAL_END,
    V2_R18_APPROVAL_ROADMAP,
    V2_R18_APPROVAL_START,
    V2_R18_APPROVAL_STATE,
    V2_R18_DELIVERY_ROADMAP,
    V2_R18_DELIVERY_STATE,
    V2_R18_FINAL_END,
    V2_R18_FINAL_EVIDENCE_COMMITS,
    V2_R18_FINAL_ROADMAP,
    V2_R18_FINAL_START,
    V2_R18_FINAL_STATE,
    V2_R18_LOCK_END,
    V2_R18_LOCK_START,
    V2_R19_APPROVAL_END,
    V2_R19_APPROVAL_ROADMAP,
    V2_R19_APPROVAL_START,
    V2_R19_APPROVAL_STATE,
    V2_R19_DELIVERY_ROADMAP,
    V2_R19_DELIVERY_STATE,
    V2_R19_FINAL_END,
    V2_R19_FINAL_EVIDENCE_COMMITS,
    V2_R19_FINAL_ROADMAP,
    V2_R19_FINAL_START,
    V2_R19_FINAL_STATE,
    V2_R19_LOCK_END,
    V2_R19_LOCK_START,
    V2_R20_APPROVAL_END,
    V2_R20_APPROVAL_ROADMAP,
    V2_R20_APPROVAL_START,
    V2_R20_APPROVAL_STATE,
    V2_R20_DELIVERY_ROADMAP,
    V2_R20_DELIVERY_STATE,
    V2_R20_FINAL_END,
    V2_R20_FINAL_EVIDENCE_COMMITS,
    V2_R20_FINAL_ROADMAP,
    V2_R20_FINAL_START,
    V2_R20_FINAL_STATE,
    V2_R20_LOCK_END,
    V2_R20_LOCK_START,
    V2_R21_APPROVAL_END,
    V2_R21_APPROVAL_ROADMAP,
    V2_R21_APPROVAL_START,
    V2_R21_APPROVAL_STATE,
    V2_R21_DELIVERY_ROADMAP,
    V2_R21_DELIVERY_STATE,
    V2_R21_FINAL_END,
    V2_R21_FINAL_EVIDENCE_COMMITS,
    V2_R21_FINAL_ROADMAP,
    V2_R21_FINAL_START,
    V2_R21_FINAL_STATE,
    V2_R21_LOCK_END,
    V2_R21_LOCK_START,
    V2_R22_APPROVAL_END, V2_R22_APPROVAL_ROADMAP, V2_R22_APPROVAL_START, V2_R22_APPROVAL_STATE,
    V2_R22_DELIVERY_ROADMAP, V2_R22_DELIVERY_STATE,
    V2_R22_FINAL_END, V2_R22_FINAL_EVIDENCE_COMMITS, V2_R22_FINAL_ROADMAP, V2_R22_FINAL_START, V2_R22_FINAL_STATE, V2_R22_LOCK_END, V2_R22_LOCK_START,
    V2_R23_DELIVERY_ROADMAP,
    V2_R23_DELIVERY_STATE,
    V2_R23_FINAL_EVIDENCE_COMMITS,
    V2_R23_FINAL_ROADMAP,
    V2_R23_FINAL_STATE,
    V2_R24_DELIVERY_ROADMAP,
    V2_R24_DELIVERY_STATE,
    V2_R24_FINAL_EVIDENCE_COMMITS,
    V2_R24_FINAL_ROADMAP,
    V2_R24_FINAL_STATE,
    V2_R25_APPROVAL_ROADMAP,
    V2_R25_APPROVAL_STATE,
    V2_R25_DELIVERY_ROADMAP,
    V2_R25_DELIVERY_STATE,
    V2_R25_FINAL_ROADMAP,
    V2_R25_FINAL_STATE,
    V2_R26_APPROVAL_ROADMAP,
    V2_R26_APPROVAL_STATE,
    V2_R26_DELIVERY_ROADMAP,
    V2_R26_DELIVERY_STATE,
    V2_R26_FINAL_ROADMAP,
    V2_R26_FINAL_STATE,
    V2_R27_APPROVAL_ROADMAP,
    V2_R27_APPROVAL_STATE,
    V2_R27_DELIVERY_ROADMAP,
    V2_R27_DELIVERY_STATE,
    V2_R27_FINAL_ROADMAP,
    V2_R27_FINAL_STATE,
    V2_R28_APPROVAL_ROADMAP,
    V2_R28_APPROVAL_STATE,
    V2_R28_DELIVERY_ROADMAP,
    V2_R28_DELIVERY_STATE,
    V2_R28_FINAL_ROADMAP,
    V2_R28_FINAL_STATE,
    V2_R29_APPROVAL_ROADMAP,
    V2_R29_APPROVAL_STATE,
    V2_R29_DELIVERY_ROADMAP,
    V2_R29_DELIVERY_STATE,
    V2_R29_FINAL_ROADMAP,
    V2_R29_FINAL_STATE,
    V2_R30_APPROVAL_ROADMAP,
    V2_R30_APPROVAL_STATE,
    V2_R30_DELIVERY_ROADMAP,
    V2_R30_DELIVERY_STATE,
    V2_R30_FINAL_ROADMAP,
    V2_R30_FINAL_STATE,
    V2_R31_APPROVAL_ROADMAP,
    V2_R31_APPROVAL_STATE,
    V2_R31_DELIVERY_ROADMAP,
    V2_R31_DELIVERY_STATE,
    V2_R31_FINAL_ROADMAP,
    V2_R31_FINAL_STATE,
    V2_R32_APPROVAL_ROADMAP,
    V2_R32_APPROVAL_STATE,
    V2_R32_DELIVERY_ROADMAP,
    V2_R32_DELIVERY_STATE,
    V2_R32_FINAL_ROADMAP,
    V2_R32_FINAL_STATE,
    V2_R33_APPROVAL_ROADMAP,
    V2_R33_APPROVAL_STATE,
    V2_R33_DELIVERY_ROADMAP,
    V2_R33_DELIVERY_STATE,
    V2_R33_FINAL_ROADMAP,
    V2_R33_FINAL_STATE,
    V2_R34_APPROVAL_ROADMAP,
    V2_R34_APPROVAL_STATE,
    V2_R34_DELIVERY_ROADMAP,
    V2_R34_DELIVERY_STATE,
    V2_R34_FINAL_ROADMAP,
    V2_R34_FINAL_STATE,
    V2_R35_APPROVAL_ROADMAP,
    V2_R35_APPROVAL_STATE,
    V2_R35_DELIVERY_ROADMAP,
    V2_R35_DELIVERY_STATE,
    V2_R35_FINAL_ROADMAP,
    V2_R35_FINAL_STATE,
    V2_R36_APPROVAL_ROADMAP,
    V2_R36_APPROVAL_STATE,
    V2_R36_DELIVERY_ROADMAP,
    V2_R36_DELIVERY_STATE,
    V2_R36_FINAL_ROADMAP,
    V2_R36_FINAL_STATE,
    V2_R37_APPROVAL_ROADMAP,
    V2_R37_APPROVAL_STATE,
    V2_R37_DELIVERY_ROADMAP,
    V2_R37_DELIVERY_STATE,
    V2_R37_FINAL_ROADMAP,
    V2_R37_FINAL_STATE,
    V2_R38_APPROVAL_ROADMAP,
    V2_R38_APPROVAL_STATE,
    V2_R38_DELIVERY_ROADMAP,
    V2_R38_DELIVERY_STATE,
    V2_R38_FINAL_ROADMAP,
    V2_R38_FINAL_STATE,
    V2_R39_APPROVAL_ROADMAP,
    V2_R39_APPROVAL_STATE,
    V2_R39_DELIVERY_ROADMAP,
    V2_R39_DELIVERY_STATE,
    V2_R39_FINAL_ROADMAP,
    V2_R39_FINAL_STATE,
    V2_R40_APPROVAL_ROADMAP,
    V2_R40_APPROVAL_STATE,
    V2_R40_DELIVERY_ROADMAP,
    V2_R40_DELIVERY_STATE,
    V2_R40_FINAL_ROADMAP,
    V2_R40_FINAL_STATE,
    V2_R41_APPROVAL_ROADMAP,
    V2_R41_APPROVAL_STATE,
    V2_R41_DELIVERY_ROADMAP,
    V2_R41_DELIVERY_STATE,
    V2_R41_FINAL_ROADMAP,
    V2_R41_FINAL_STATE,
    V2_R42_APPROVAL_ROADMAP,
    V2_R42_APPROVAL_STATE,
    V2_R42_DELIVERY_ROADMAP,
    V2_R42_DELIVERY_STATE,
    V2_R42_FINAL_ROADMAP,
    V2_R42_FINAL_STATE,
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


def test_current_state_manifest_records_exact_v2_r42_delivery_state():
    manifest = load_manifest(ROOT)
    truth = manifest["current_truth"]

    assert truth == V2_R42_DELIVERY_STATE
    assert manifest["roadmap"] == V2_R42_DELIVERY_ROADMAP


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
    assert all(line in gap for line in GAP_ROADMAP_R42_DELIVERY_LINES)


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
    assert blocks_are_exact(texts, V2_R15_LOCK_START, V2_R15_LOCK_END)
    assert blocks_are_exact(texts, V2_R15_FINAL_START, V2_R15_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R15_FINAL_START, V2_R15_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R15_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R16_APPROVAL_START, V2_R16_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R16_LOCK_START, V2_R16_LOCK_END)
    assert blocks_are_exact(texts, V2_R16_FINAL_START, V2_R16_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R16_FINAL_START, V2_R16_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R16_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R17_APPROVAL_START, V2_R17_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R17_LOCK_START, V2_R17_LOCK_END)
    assert blocks_are_exact(texts, V2_R17_FINAL_START, V2_R17_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R17_FINAL_START, V2_R17_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R17_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R18_APPROVAL_START, V2_R18_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R18_LOCK_START, V2_R18_LOCK_END)
    assert blocks_are_exact(texts, V2_R18_FINAL_START, V2_R18_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R18_FINAL_START, V2_R18_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R18_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R19_APPROVAL_START, V2_R19_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R19_LOCK_START, V2_R19_LOCK_END)
    assert blocks_are_exact(texts, V2_R19_FINAL_START, V2_R19_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R19_FINAL_START, V2_R19_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R19_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(
        texts, V2_R20_APPROVAL_START, V2_R20_APPROVAL_END
    )
    assert blocks_are_exact(texts, V2_R20_LOCK_START, V2_R20_LOCK_END)
    assert blocks_are_exact(texts, V2_R20_FINAL_START, V2_R20_FINAL_END)
    blocks = tuple(
        extract_single_block(text, V2_R20_FINAL_START, V2_R20_FINAL_END)
        for text in texts
    )
    assert all(block is not None for block in blocks)
    assert all(
        all(commit in block for commit in V2_R20_FINAL_EVIDENCE_COMMITS)
        for block in blocks
        if block is not None
    )
    assert blocks_are_exact(texts, V2_R21_APPROVAL_START, V2_R21_APPROVAL_END)
    assert blocks_are_exact(texts, V2_R21_LOCK_START, V2_R21_LOCK_END)
    assert blocks_are_exact(texts, V2_R21_FINAL_START, V2_R21_FINAL_END)
    blocks = tuple(extract_single_block(text, V2_R21_FINAL_START, V2_R21_FINAL_END) for text in texts)
    assert all(block is not None for block in blocks)
    assert all(all(commit in block for commit in V2_R21_FINAL_EVIDENCE_COMMITS) for block in blocks if block is not None)
    assert blocks_are_exact(texts, V2_R22_APPROVAL_START, V2_R22_APPROVAL_END)
    assert blocks_are_exact(texts, V2_R22_LOCK_START, V2_R22_LOCK_END)
    assert blocks_are_exact(texts, V2_R22_FINAL_START, V2_R22_FINAL_END)
    blocks = tuple(extract_single_block(text, V2_R22_FINAL_START, V2_R22_FINAL_END) for text in texts)
    assert all(all(commit in block for commit in V2_R22_FINAL_EVIDENCE_COMMITS) for block in blocks if block is not None)


def test_manifest_is_deterministic_json_and_historical_order_is_not_current():
    path = ROOT / "FCF_CURRENT_STATE_MANIFEST.json"
    text = path.read_text(encoding="ascii")
    parsed = json.loads(text)

    assert text.endswith("\n")
    assert parsed["historical_registry"]["status"] == (
        "HISTORICAL_COMPLETED_SEQUENCE_NOT_CURRENT_NEXT_PHASE_AUTHORITY"
    )
    assert parsed["current_truth"]["next_product_phase_approval"] == (
        V2_R42_DELIVERY_STATE["next_product_phase_approval"]
    )


def test_all_recorded_final_evidence_commits_resolve_in_git_history():
    commit_groups = {
        name: value
        for name, value in vars(memory_guard).items()
        if name.endswith("_FINAL_EVIDENCE_COMMITS")
        or name in {"FINAL_EVIDENCE_COMMITS", "SESSION_FINAL_EVIDENCE_COMMITS"}
    }

    assert commit_groups
    for group_name, commits in commit_groups.items():
        for commit in commits:
            result = subprocess.run(
                ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
                cwd=ROOT,
                capture_output=True,
                check=False,
            )
            assert result.returncode == 0, f"{group_name} has unknown commit {commit}"


def test_v2_r16_evidence_commit_subjects_are_exact():
    expected = {
        "ece983a153c11fd93463638ff388892d481951ee": (
            "docs(v2-r16): approve local range channel indicator foundation"
        ),
        "3245368fca7c19312c93c5dcd1fdbfaaf3f16a46": (
            "feat(v2-r16): add local range channel indicator foundation"
        ),
        "552a1068ac136a09a107f0f6cdfb5251842467d1": (
            "merge: complete v2-r16 local range channel indicator foundation"
        ),
    }

    for commit, subject in expected.items():
        result = subprocess.run(
            ["git", "show", "-s", "--format=%s", commit],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
        )
        assert result.stdout.strip() == subject
