from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = Path("FCF_CURRENT_STATE_MANIFEST.json")
PROTOCOL_PATH = Path("docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md")
ARCHITECTURE_PATH = Path(
    "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
)
ADR_PATH = Path("docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md")
GAP_PATH = Path("docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md")
CONTROL_CENTER_PATH = Path("docs/FCF_PROJECT_CONTROL_CENTER.md")
AUTHORITY_PATHS = (
    CONTROL_CENTER_PATH,
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
MEMORY_LOCK_START = (
    "<!-- PROJECT-MEMORY-CONTINUITY-HARDENING-APP-1 LOCK START -->"
)
MEMORY_LOCK_END = (
    "<!-- PROJECT-MEMORY-CONTINUITY-HARDENING-APP-1 LOCK END -->"
)
MEMORY_FINAL_START = (
    "<!-- PROJECT-MEMORY-CONTINUITY-HARDENING-APP-1 FINAL SYNC START -->"
)
MEMORY_FINAL_END = (
    "<!-- PROJECT-MEMORY-CONTINUITY-HARDENING-APP-1 FINAL SYNC END -->"
)
SESSION_APPROVAL_START = (
    "<!-- FCF V2 MARKET SESSION RESEARCH ARCHITECTURE SYNC APPROVAL START -->"
)
SESSION_APPROVAL_END = (
    "<!-- FCF V2 MARKET SESSION RESEARCH ARCHITECTURE SYNC APPROVAL END -->"
)
SESSION_LOCK_START = (
    "<!-- FCF V2 MARKET SESSION RESEARCH ARCHITECTURE SYNC LOCK START -->"
)
SESSION_LOCK_END = (
    "<!-- FCF V2 MARKET SESSION RESEARCH ARCHITECTURE SYNC LOCK END -->"
)
SESSION_FINAL_START = (
    "<!-- FCF V2 MARKET SESSION RESEARCH ARCHITECTURE SYNC FINAL START -->"
)
SESSION_FINAL_END = (
    "<!-- FCF V2 MARKET SESSION RESEARCH ARCHITECTURE SYNC FINAL END -->"
)
V2_R1_APPROVAL_START = (
    "<!-- V2-R1 FACTOR CONTRACT FOUNDATION APP 1 APPROVAL START -->"
)
V2_R1_APPROVAL_END = (
    "<!-- V2-R1 FACTOR CONTRACT FOUNDATION APP 1 APPROVAL END -->"
)
V2_R1_LOCK_START = (
    "<!-- V2-R1 FACTOR CONTRACT FOUNDATION APP 1 LOCK START -->"
)
V2_R1_LOCK_END = (
    "<!-- V2-R1 FACTOR CONTRACT FOUNDATION APP 1 LOCK END -->"
)
V2_R1_FINAL_START = (
    "<!-- V2-R1 FACTOR CONTRACT FOUNDATION APP 1 FINAL START -->"
)
V2_R1_FINAL_END = (
    "<!-- V2-R1 FACTOR CONTRACT FOUNDATION APP 1 FINAL END -->"
)
V2_R1_FINAL_EVIDENCE_COMMITS = (
    "77defa87ceba3b291d8302ffe252acd953957e9f",
    "cc09888aa6c29a01ee2eab9f5ee9f62c547f49be",
    "f8bf985c9d14a6aa0c3dc9b0b5da3384c86bedc2",
)
V2_R2_APPROVAL_START = (
    "<!-- V2-R2 HISTORICAL FACTOR BASELINE APP 1 APPROVAL START -->"
)
V2_R2_APPROVAL_END = (
    "<!-- V2-R2 HISTORICAL FACTOR BASELINE APP 1 APPROVAL END -->"
)
V2_R2_LOCK_START = (
    "<!-- V2-R2 HISTORICAL FACTOR BASELINE APP 1 LOCK START -->"
)
V2_R2_LOCK_END = (
    "<!-- V2-R2 HISTORICAL FACTOR BASELINE APP 1 LOCK END -->"
)
V2_R2_FINAL_START = (
    "<!-- V2-R2 HISTORICAL FACTOR BASELINE APP 1 FINAL START -->"
)
V2_R2_FINAL_END = (
    "<!-- V2-R2 HISTORICAL FACTOR BASELINE APP 1 FINAL END -->"
)
V2_R2_FINAL_EVIDENCE_COMMITS = (
    "62fddb0dcbd1bfed03c788409c450040baa03d5d",
    "02b8a1059c3740b12668931d11879784c4f3535c",
    "ad70ca629b0576d1e4076dec87131781e5c38d53",
)
V2_R3_APPROVAL_START = (
    "<!-- V2-R3 LOCAL EVENT INGRESS FOUNDATION APP 1 APPROVAL START -->"
)
V2_R3_APPROVAL_END = (
    "<!-- V2-R3 LOCAL EVENT INGRESS FOUNDATION APP 1 APPROVAL END -->"
)
V2_R3_LOCK_START = (
    "<!-- V2-R3 LOCAL EVENT INGRESS FOUNDATION APP 1 LOCK START -->"
)
V2_R3_LOCK_END = (
    "<!-- V2-R3 LOCAL EVENT INGRESS FOUNDATION APP 1 LOCK END -->"
)
V2_R3_FINAL_START = (
    "<!-- V2-R3 LOCAL EVENT INGRESS FOUNDATION APP 1 FINAL START -->"
)
V2_R3_FINAL_END = (
    "<!-- V2-R3 LOCAL EVENT INGRESS FOUNDATION APP 1 FINAL END -->"
)
V2_R3_FINAL_EVIDENCE_COMMITS = (
    "bb48a47ae377ab87af2ece237d379ee78b994082",
    "24a52cc7f8ab0aa64ba8990b193980c42cfdf43d",
    "157ff5938f34c4ce987ad889fa9f3c410d82f84c",
)
V2_R4_APPROVAL_START = (
    "<!-- V2-R4 LOCAL ANOMALY RADAR FOUNDATION APP 1 APPROVAL START -->"
)
V2_R4_APPROVAL_END = (
    "<!-- V2-R4 LOCAL ANOMALY RADAR FOUNDATION APP 1 APPROVAL END -->"
)
V2_R4_LOCK_START = (
    "<!-- V2-R4 LOCAL ANOMALY RADAR FOUNDATION APP 1 LOCK START -->"
)
V2_R4_LOCK_END = (
    "<!-- V2-R4 LOCAL ANOMALY RADAR FOUNDATION APP 1 LOCK END -->"
)
V2_R4_FINAL_START = (
    "<!-- V2-R4 LOCAL ANOMALY RADAR FOUNDATION APP 1 FINAL START -->"
)
V2_R4_FINAL_END = (
    "<!-- V2-R4 LOCAL ANOMALY RADAR FOUNDATION APP 1 FINAL END -->"
)
V2_R4_FINAL_EVIDENCE_COMMITS = (
    "af7f4656fae290a6c2c2186e4e82a2cf5d09adbf",
    "621e67fc51151b39521c7498d672f6a611f57e85",
    "49ca381a8f8fcbfd72ceca1afd42ccd216dc790f",
)
V2_R5_APPROVAL_START = (
    "<!-- V2-R5 LOCAL COGNITIVE SHIELD FOUNDATION APP 1 APPROVAL START -->"
)
V2_R5_APPROVAL_END = (
    "<!-- V2-R5 LOCAL COGNITIVE SHIELD FOUNDATION APP 1 APPROVAL END -->"
)
V2_R5_LOCK_START = (
    "<!-- V2-R5 LOCAL COGNITIVE SHIELD FOUNDATION APP 1 LOCK START -->"
)
V2_R5_LOCK_END = (
    "<!-- V2-R5 LOCAL COGNITIVE SHIELD FOUNDATION APP 1 LOCK END -->"
)
V2_R5_FINAL_START = (
    "<!-- V2-R5 LOCAL COGNITIVE SHIELD FOUNDATION APP 1 FINAL START -->"
)
V2_R5_FINAL_END = (
    "<!-- V2-R5 LOCAL COGNITIVE SHIELD FOUNDATION APP 1 FINAL END -->"
)
V2_R5_FINAL_EVIDENCE_COMMITS = (
    "a303f3f8b622b3c86b6570ebafc33de97defaf64",
    "256a98c0a33c2fb750522ece6dfd5d757bc2384b",
    "03df9e0fdbd26b5bab1fd7eeb24edc5e6cec337d",
)
V2_R6_APPROVAL_START = (
    "<!-- V2-R6 LOCAL PAPER SCENARIO RESEARCH FOUNDATION APP 1 APPROVAL START -->"
)
V2_R6_APPROVAL_END = (
    "<!-- V2-R6 LOCAL PAPER SCENARIO RESEARCH FOUNDATION APP 1 APPROVAL END -->"
)
V2_R6_LOCK_START = (
    "<!-- V2-R6 LOCAL PAPER SCENARIO RESEARCH FOUNDATION APP 1 LOCK START -->"
)
V2_R6_LOCK_END = (
    "<!-- V2-R6 LOCAL PAPER SCENARIO RESEARCH FOUNDATION APP 1 LOCK END -->"
)
V2_R6_FINAL_START = (
    "<!-- V2-R6 LOCAL PAPER SCENARIO RESEARCH FOUNDATION APP 1 FINAL START -->"
)
V2_R6_FINAL_END = (
    "<!-- V2-R6 LOCAL PAPER SCENARIO RESEARCH FOUNDATION APP 1 FINAL END -->"
)
V2_R6_FINAL_EVIDENCE_COMMITS = (
    "75af2de9a05b0de0ae607f65c7e1c54868169e7d",
    "d75984e94b869dba2896438ccca49537d8988b93",
    "1da960b316838ec47dc328d30393d54b45901e6a",
)
V2_R7_APPROVAL_START = (
    "<!-- V2-R7 LOCAL MARKET SESSION REGISTRY FOUNDATION APP 1 APPROVAL START -->"
)
V2_R7_APPROVAL_END = (
    "<!-- V2-R7 LOCAL MARKET SESSION REGISTRY FOUNDATION APP 1 APPROVAL END -->"
)
V2_R7_LOCK_START = (
    "<!-- V2-R7 LOCAL MARKET SESSION REGISTRY FOUNDATION APP 1 LOCK START -->"
)
V2_R7_LOCK_END = (
    "<!-- V2-R7 LOCAL MARKET SESSION REGISTRY FOUNDATION APP 1 LOCK END -->"
)
V2_R7_FINAL_START = (
    "<!-- V2-R7 LOCAL MARKET SESSION REGISTRY FOUNDATION APP 1 FINAL START -->"
)
V2_R7_FINAL_END = (
    "<!-- V2-R7 LOCAL MARKET SESSION REGISTRY FOUNDATION APP 1 FINAL END -->"
)
V2_R7_FINAL_EVIDENCE_COMMITS = (
    "605e23116095876551ac2c87dcb7b5e1b6fabcf3",
    "4a40616e62972476e693ce6ecaecbc05637a776b",
    "1f9214fc3b3d751e641a26b3612423b5729e0ab4",
)
V2_R8_APPROVAL_START = (
    "<!-- V2-R8 LOCAL SAME TIME BASELINE FOUNDATION APP 1 APPROVAL START -->"
)
V2_R8_APPROVAL_END = (
    "<!-- V2-R8 LOCAL SAME TIME BASELINE FOUNDATION APP 1 APPROVAL END -->"
)
V2_R8_LOCK_START = (
    "<!-- V2-R8 LOCAL SAME TIME BASELINE FOUNDATION APP 1 LOCK START -->"
)
V2_R8_LOCK_END = (
    "<!-- V2-R8 LOCAL SAME TIME BASELINE FOUNDATION APP 1 LOCK END -->"
)
V2_R8_FINAL_START = (
    "<!-- V2-R8 LOCAL SAME TIME BASELINE FOUNDATION APP 1 FINAL START -->"
)
V2_R8_FINAL_END = (
    "<!-- V2-R8 LOCAL SAME TIME BASELINE FOUNDATION APP 1 FINAL END -->"
)
V2_R8_FINAL_EVIDENCE_COMMITS = (
    "e1cd98758b62f84313347c33c6f3a7a4652ab18d",
    "3b60227126ff03eb324cb95123176144a261782f",
    "b80383e7ce41e99ece33641cf7c1fbb92abc3582",
)
V2_R9_APPROVAL_START = (
    "<!-- V2-R9 LOCAL VOLUME RATIO RESEARCH FOUNDATION APP 1 APPROVAL START -->"
)
V2_R9_APPROVAL_END = (
    "<!-- V2-R9 LOCAL VOLUME RATIO RESEARCH FOUNDATION APP 1 APPROVAL END -->"
)
V2_R9_LOCK_START = (
    "<!-- V2-R9 LOCAL VOLUME RATIO RESEARCH FOUNDATION APP 1 LOCK START -->"
)
V2_R9_LOCK_END = (
    "<!-- V2-R9 LOCAL VOLUME RATIO RESEARCH FOUNDATION APP 1 LOCK END -->"
)
V2_R9_FINAL_START = (
    "<!-- V2-R9 LOCAL VOLUME RATIO RESEARCH FOUNDATION APP 1 FINAL START -->"
)
V2_R9_FINAL_END = (
    "<!-- V2-R9 LOCAL VOLUME RATIO RESEARCH FOUNDATION APP 1 FINAL END -->"
)
V2_R9_FINAL_EVIDENCE_COMMITS = (
    "082639a712a78589067fdac04d5a0fd4f081a51e",
    "c061ce7c300c34d09fd3704cec768cd6d4c8fea4",
    "c4538c47acb4ead95b5c1a53bbc6d74a72d8338f",
)
V2_R10_APPROVAL_START = (
    "<!-- V2-R10 LOCAL TURNOVER DEFINITION RESEARCH FOUNDATION APP 1 APPROVAL START -->"
)
V2_R10_APPROVAL_END = (
    "<!-- V2-R10 LOCAL TURNOVER DEFINITION RESEARCH FOUNDATION APP 1 APPROVAL END -->"
)
V2_R10_LOCK_START = (
    "<!-- V2-R10 LOCAL TURNOVER DEFINITION RESEARCH FOUNDATION APP 1 LOCK START -->"
)
V2_R10_LOCK_END = (
    "<!-- V2-R10 LOCAL TURNOVER DEFINITION RESEARCH FOUNDATION APP 1 LOCK END -->"
)
V2_R10_FINAL_START = (
    "<!-- V2-R10 LOCAL TURNOVER DEFINITION RESEARCH FOUNDATION APP 1 FINAL START -->"
)
V2_R10_FINAL_END = (
    "<!-- V2-R10 LOCAL TURNOVER DEFINITION RESEARCH FOUNDATION APP 1 FINAL END -->"
)
V2_R10_FINAL_EVIDENCE_COMMITS = (
    "91667cfd52e468416c42e91a3d2bf6c42300aabc",
    "197c37c224da0553960ef5827935ed99c0557b42",
    "220c7ac70b767d7703f6b0d9dcb60e6a68cde825",
)
V2_R11_APPROVAL_START = (
    "<!-- V2-R11 LOCAL FACTOR REGISTRY FOUNDATION APP 1 APPROVAL START -->"
)
V2_R11_APPROVAL_END = (
    "<!-- V2-R11 LOCAL FACTOR REGISTRY FOUNDATION APP 1 APPROVAL END -->"
)
V2_R11_LOCK_START = (
    "<!-- V2-R11 LOCAL FACTOR REGISTRY FOUNDATION APP 1 LOCK START -->"
)
V2_R11_LOCK_END = (
    "<!-- V2-R11 LOCAL FACTOR REGISTRY FOUNDATION APP 1 LOCK END -->"
)
V2_R11_FINAL_START = (
    "<!-- V2-R11 LOCAL FACTOR REGISTRY FOUNDATION APP 1 FINAL START -->"
)
V2_R11_FINAL_END = (
    "<!-- V2-R11 LOCAL FACTOR REGISTRY FOUNDATION APP 1 FINAL END -->"
)
V2_R11_FINAL_EVIDENCE_COMMITS = (
    "d19a911e35dca594446c95564395b1f808123d53",
    "b20cb1b2ac449899cd33a1c4b61c8403488fa0b0",
    "0a0b6887eeec95dc0ad42e97bf7d43e31ce7d6db",
)
V2_R12_APPROVAL_START = (
    "<!-- V2-R12 LOCAL TECHNICAL INDICATOR FOUNDATION APP 1 APPROVAL START -->"
)
V2_R12_APPROVAL_END = (
    "<!-- V2-R12 LOCAL TECHNICAL INDICATOR FOUNDATION APP 1 APPROVAL END -->"
)
V2_R12_LOCK_START = (
    "<!-- V2-R12 LOCAL TECHNICAL INDICATOR FOUNDATION APP 1 LOCK START -->"
)
V2_R12_LOCK_END = (
    "<!-- V2-R12 LOCAL TECHNICAL INDICATOR FOUNDATION APP 1 LOCK END -->"
)
V2_R12_FINAL_START = (
    "<!-- V2-R12 LOCAL TECHNICAL INDICATOR FOUNDATION APP 1 FINAL START -->"
)
V2_R12_FINAL_END = (
    "<!-- V2-R12 LOCAL TECHNICAL INDICATOR FOUNDATION APP 1 FINAL END -->"
)
V2_R12_FINAL_EVIDENCE_COMMITS = (
    "a344a636d71d914b71c3451315846c50cafa4700",
    "b8fc91bb1c7a81ba8d3a1a76c9761774ebc424a0",
    "225be920334df30009db9ecfb880c42602fcac55",
)
V2_R13_APPROVAL_START = (
    "<!-- V2-R13 LOCAL MOMENTUM INDICATOR FOUNDATION APP 1 APPROVAL START -->"
)
V2_R13_APPROVAL_END = (
    "<!-- V2-R13 LOCAL MOMENTUM INDICATOR FOUNDATION APP 1 APPROVAL END -->"
)
V2_R13_LOCK_START = (
    "<!-- V2-R13 LOCAL MOMENTUM INDICATOR FOUNDATION APP 1 LOCK START -->"
)
V2_R13_LOCK_END = (
    "<!-- V2-R13 LOCAL MOMENTUM INDICATOR FOUNDATION APP 1 LOCK END -->"
)
V2_R13_FINAL_START = (
    "<!-- V2-R13 LOCAL MOMENTUM INDICATOR FOUNDATION APP 1 FINAL START -->"
)
V2_R13_FINAL_END = (
    "<!-- V2-R13 LOCAL MOMENTUM INDICATOR FOUNDATION APP 1 FINAL END -->"
)
V2_R13_FINAL_EVIDENCE_COMMITS = (
    "0a63511c89b47ad840aeab8ad67486c30988e462",
    "1feca38325ccdbb923032c685996f5c0f461a0df",
    "bdb619ceabcab373a3e572f5909d0c0397909a03",
)
V2_R14_APPROVAL_START = (
    "<!-- V2-R14 LOCAL TREND INDICATOR FOUNDATION APP 1 APPROVAL START -->"
)
V2_R14_APPROVAL_END = (
    "<!-- V2-R14 LOCAL TREND INDICATOR FOUNDATION APP 1 APPROVAL END -->"
)
V2_R14_LOCK_START = (
    "<!-- V2-R14 LOCAL TREND INDICATOR FOUNDATION APP 1 LOCK START -->"
)
V2_R14_LOCK_END = (
    "<!-- V2-R14 LOCAL TREND INDICATOR FOUNDATION APP 1 LOCK END -->"
)
V2_R14_FINAL_START = (
    "<!-- V2-R14 LOCAL TREND INDICATOR FOUNDATION APP 1 FINAL START -->"
)
V2_R14_FINAL_END = (
    "<!-- V2-R14 LOCAL TREND INDICATOR FOUNDATION APP 1 FINAL END -->"
)
V2_R14_FINAL_EVIDENCE_COMMITS = (
    "f96e83f43dc082c6d41c0949a91276f86df86e8c",
    "bdc8b95383ca6a2c7aa0a20aa344d0d67a10f2e3",
    "7c241ea371ed2846edf3a4ae1e968b0e377c6635",
)
V2_R15_APPROVAL_START = (
    "<!-- V2-R15 LOCAL VOLATILITY INDICATOR FOUNDATION APP 1 APPROVAL START -->"
)
V2_R15_APPROVAL_END = (
    "<!-- V2-R15 LOCAL VOLATILITY INDICATOR FOUNDATION APP 1 APPROVAL END -->"
)
V2_R15_LOCK_START = (
    "<!-- V2-R15 LOCAL VOLATILITY INDICATOR FOUNDATION APP 1 LOCK START -->"
)
V2_R15_LOCK_END = (
    "<!-- V2-R15 LOCAL VOLATILITY INDICATOR FOUNDATION APP 1 LOCK END -->"
)
V2_R15_FINAL_START = (
    "<!-- V2-R15 LOCAL VOLATILITY INDICATOR FOUNDATION APP 1 FINAL START -->"
)
V2_R15_FINAL_END = (
    "<!-- V2-R15 LOCAL VOLATILITY INDICATOR FOUNDATION APP 1 FINAL END -->"
)
V2_R15_FINAL_EVIDENCE_COMMITS = (
    "f64200fab5de7cc13043aa8521b1b05fd375dc86",
    "17b9c63a8b3dd77a5d72ce81d853079332a3dbba",
    "85ca0ab57c5455ff3c8b1573c5716a5381474e28",
)
V2_R16_APPROVAL_START = (
    "<!-- V2-R16 LOCAL RANGE CHANNEL INDICATOR FOUNDATION APP 1 APPROVAL START -->"
)
V2_R16_APPROVAL_END = (
    "<!-- V2-R16 LOCAL RANGE CHANNEL INDICATOR FOUNDATION APP 1 APPROVAL END -->"
)
V2_R16_LOCK_START = (
    "<!-- V2-R16 LOCAL RANGE CHANNEL INDICATOR FOUNDATION APP 1 LOCK START -->"
)
V2_R16_LOCK_END = (
    "<!-- V2-R16 LOCAL RANGE CHANNEL INDICATOR FOUNDATION APP 1 LOCK END -->"
)
V2_R16_FINAL_START = (
    "<!-- V2-R16 LOCAL RANGE CHANNEL INDICATOR FOUNDATION APP 1 FINAL START -->"
)
V2_R16_FINAL_END = (
    "<!-- V2-R16 LOCAL RANGE CHANNEL INDICATOR FOUNDATION APP 1 FINAL END -->"
)
V2_R16_FINAL_EVIDENCE_COMMITS = (
    "ece983a153c11fd93463638ff388892d481951ee",
    "3245368fca7c19312c93c5dcd1fdbfaaf3f16a46",
    "552a1068ac136a09a107f0f6cdfb5251842467d1",
)
FINAL_EVIDENCE_COMMITS = (
    "c3ee5b730e16fa4c89e6cf52f80586b55674203d",
    "29fc7b0ee0b84490de6629cfb385ef0fef625159",
    "291cad1ecc84a09e71c63973cd10de1e7b88a4bf",
)
SESSION_FINAL_EVIDENCE_COMMITS = (
    "be04f64a38f1d54a4aa7b09f85e8eac005819f9b",
    "49707a03f1e0bc41e53b5a88e888602a434bc638",
    "9d95ed2f40483b41004b81c02da5fb8dd1d7c088",
)
V2_BLOCKS = (
    (
        "<!-- FCF V2 FACTOR REALTIME COGNITIVE ARCHITECTURE "
        "SYNC APPROVAL START -->",
        "<!-- FCF V2 FACTOR REALTIME COGNITIVE ARCHITECTURE "
        "SYNC APPROVAL END -->",
    ),
    (
        "<!-- FCF V2 FACTOR REALTIME COGNITIVE ARCHITECTURE LOCK START -->",
        "<!-- FCF V2 FACTOR REALTIME COGNITIVE ARCHITECTURE LOCK END -->",
    ),
    (
        "<!-- FCF V2 FACTOR REALTIME COGNITIVE ARCHITECTURE "
        "FINAL SYNC START -->",
        "<!-- FCF V2 FACTOR REALTIME COGNITIVE ARCHITECTURE "
        "FINAL SYNC END -->",
    ),
)
EXPECTED_FILE_ROLES = {
    "architecture_decisions": ADR_PATH.as_posix(),
    "control_center": CONTROL_CENTER_PATH.as_posix(),
    "current_machine_truth": MANIFEST_PATH.as_posix(),
    "execution_safety_protocol": "docs/FCF_EXECUTION_SAFETY_PROTOCOL.md",
    "future_product_structure": ARCHITECTURE_PATH.as_posix(),
    "future_capability_change_protocol": (
        "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md"
    ),
    "future_capability_intake_register": (
        "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json"
    ),
    "handoff_prompt": "docs/HANDOFF_PROMPT.md",
    "memory_continuity_protocol": PROTOCOL_PATH.as_posix(),
    "unfinished_work_register": GAP_PATH.as_posix(),
}
EXPECTED_FUTURE_ARCHITECTURE = [
    {
        "architecture_id": "FCF-V2-FACTOR-REALTIME-COGNITIVE-EXPANSION",
        "implementation_status": "NOT_IMPLEMENTED",
        "status": "ACCEPTED_ARCHITECTURE",
    },
    {
        "architecture_id": (
            "FCF-V2-MARKET-SESSION-MICROSTRUCTURE-RESEARCH-EXTENSION"
        ),
        "implementation_status": "NOT_IMPLEMENTED",
        "status": "ACCEPTED_ARCHITECTURE",
    },
]
FUTURE_STATUSES = (
    "ACCEPTED_ARCHITECTURE",
    "PLANNED",
    "BACKLOG",
    "RESEARCH_REQUIRED",
    "NOT_IMPLEMENTED",
    "OUTSIDE_CURRENT_AUTHORIZATION",
)
ROADMAP_PHASES = tuple(f"V2-R{index}" for index in range(1, 17))
ROADMAP_STATUS = "PLANNED_NOT_APPROVED_NOT_STARTED"
GAP_IDS = tuple(f"V2-FR-GAP-{index:03d}" for index in range(1, 71))
GAP_ROADMAP_FINAL_LINES = (
    "| V2-R1 | Factor Contract Foundation | "
    "COMPLETED / CONTRACT_FOUNDATION_ONLY |",
    "| V2-R2 | Historical Factor Baseline | "
    "COMPLETED / REGISTERED_LOCAL_ARTIFACT_ONLY |",
    "| V2-R3 | Realtime Ingestion Foundation | "
    "COMPLETED / LOCAL_REGISTERED_EVENT_ONLY |",
    "| V2-R4 | Intraday Anomaly Radar | "
    "COMPLETED / LOCAL_REGISTERED_ANOMALY_RESEARCH_ONLY |",
    "| V2-R5 | Realtime Cognitive Shield | "
    "COMPLETED / LOCAL_REGISTERED_COGNITIVE_SHIELD_ONLY |",
    "| V2-R6 | Paper Simulation Research | "
    "COMPLETED / LOCAL_REGISTERED_SCENARIO_RESEARCH_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R7_APPROVAL_LINES = (
    "| V2-R7 | Local Market Session Registry Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_CALENDAR_ONLY |",
    "Next product implementation phase: V2-R7 / APPROVED.",
    "No successor phase after V2-R7 starts automatically.",
)
GAP_ROADMAP_R7_DELIVERY_LINES = (
    "| V2-R7 | Local Market Session Registry Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_CALENDAR_ONLY |",
    "Next product implementation phase: V2-R7 / APPROVED.",
    "No successor phase after V2-R7 starts automatically.",
)
GAP_ROADMAP_R7_FINAL_LINES = (
    "| V2-R7 | Local Market Session Registry Foundation | "
    "COMPLETED / REGISTERED_LOCAL_CALENDAR_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R8_APPROVAL_LINES = (
    "| V2-R8 | Local Same-Time Baseline Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_HISTORY_ONLY |",
    "Next product implementation phase: V2-R8 / APPROVED.",
    "No successor phase after V2-R8 starts automatically.",
)
GAP_ROADMAP_R8_DELIVERY_LINES = (
    "| V2-R8 | Local Same-Time Baseline Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_HISTORY_ONLY |",
    "Next product implementation phase: V2-R8 / APPROVED.",
    "No successor phase after V2-R8 starts automatically.",
)
GAP_ROADMAP_R8_FINAL_LINES = (
    "| V2-R8 | Local Same-Time Baseline Foundation | "
    "COMPLETED / REGISTERED_LOCAL_HISTORY_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R9_APPROVAL_LINES = (
    "| V2-R9 | Local Volume-Ratio Research Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_VOLUME_EVIDENCE_ONLY |",
    "Next product implementation phase: V2-R9 / APPROVED.",
    "No successor phase after V2-R9 starts automatically.",
)
GAP_ROADMAP_R9_DELIVERY_LINES = (
    "| V2-R9 | Local Volume-Ratio Research Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_VOLUME_EVIDENCE_ONLY |",
    "Next product implementation phase: V2-R9 / APPROVED.",
    "No successor phase after V2-R9 starts automatically.",
)
GAP_ROADMAP_R9_FINAL_LINES = (
    "| V2-R9 | Local Volume-Ratio Research Foundation | "
    "COMPLETED / REGISTERED_LOCAL_VOLUME_EVIDENCE_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R10_APPROVAL_LINES = (
    "| V2-R10 | Local Turnover-Definition Research Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_TURNOVER_EVIDENCE_ONLY |",
    "Next product implementation phase: V2-R10 / APPROVED.",
    "No successor phase after V2-R10 starts automatically.",
)
GAP_ROADMAP_R10_DELIVERY_LINES = (
    "| V2-R10 | Local Turnover-Definition Research Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_TURNOVER_EVIDENCE_ONLY |",
    "Next product implementation phase: V2-R10 / APPROVED.",
    "No successor phase after V2-R10 starts automatically.",
)
GAP_ROADMAP_R10_FINAL_LINES = (
    "| V2-R10 | Local Turnover-Definition Research Foundation | "
    "COMPLETED / REGISTERED_LOCAL_TURNOVER_EVIDENCE_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R11_APPROVAL_LINES = (
    "| V2-R11 | Local Factor Registry Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_FACTOR_DEFINITION_ONLY |",
    "Next product implementation phase: V2-R11 / APPROVED.",
    "No successor phase after V2-R11 starts automatically.",
)
GAP_ROADMAP_R11_DELIVERY_LINES = (
    "| V2-R11 | Local Factor Registry Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_FACTOR_DEFINITION_ONLY |",
    "Next product implementation phase: V2-R11 / APPROVED.",
    "No successor phase after V2-R11 starts automatically.",
)
GAP_ROADMAP_R11_FINAL_LINES = (
    "| V2-R11 | Local Factor Registry Foundation | "
    "COMPLETED / REGISTERED_LOCAL_FACTOR_DEFINITION_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R12_APPROVAL_LINES = (
    "| V2-R12 | Local Technical Indicator Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_TECHNICAL_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R12 / APPROVED.",
    "No successor phase after V2-R12 starts automatically.",
)
GAP_ROADMAP_R12_DELIVERY_LINES = (
    "| V2-R12 | Local Technical Indicator Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_TECHNICAL_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R12 / APPROVED.",
    "No successor phase after V2-R12 starts automatically.",
)
GAP_ROADMAP_R12_FINAL_LINES = (
    "| V2-R12 | Local Technical Indicator Foundation | "
    "COMPLETED / REGISTERED_LOCAL_TECHNICAL_CALCULATION_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R13_APPROVAL_LINES = (
    "| V2-R13 | Local Momentum Indicator Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_MOMENTUM_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R13 / APPROVED.",
    "No successor phase after V2-R13 starts automatically.",
)
GAP_ROADMAP_R13_DELIVERY_LINES = (
    "| V2-R13 | Local Momentum Indicator Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_MOMENTUM_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R13 / APPROVED.",
    "No successor phase after V2-R13 starts automatically.",
)
GAP_ROADMAP_R13_FINAL_LINES = (
    "| V2-R13 | Local Momentum Indicator Foundation | "
    "COMPLETED / REGISTERED_LOCAL_MOMENTUM_CALCULATION_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R14_APPROVAL_LINES = (
    "| V2-R14 | Local Trend Indicator Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_TREND_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R14 / APPROVED.",
    "No successor phase after V2-R14 starts automatically.",
)
GAP_ROADMAP_R14_DELIVERY_LINES = (
    "| V2-R14 | Local Trend Indicator Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_TREND_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R14 / APPROVED.",
    "No successor phase after V2-R14 starts automatically.",
)
GAP_ROADMAP_R14_FINAL_LINES = (
    "| V2-R14 | Local Trend Indicator Foundation | "
    "COMPLETED / REGISTERED_LOCAL_TREND_CALCULATION_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R15_APPROVAL_LINES = (
    "| V2-R15 | Local Volatility Indicator Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_VOLATILITY_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R15 / APPROVED.",
    "No successor phase after V2-R15 starts automatically.",
)
GAP_ROADMAP_R15_DELIVERY_LINES = (
    "| V2-R15 | Local Volatility Indicator Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_VOLATILITY_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R15 / APPROVED.",
    "No successor phase after V2-R15 starts automatically.",
)
GAP_ROADMAP_R15_FINAL_LINES = (
    "| V2-R15 | Local Volatility Indicator Foundation | "
    "COMPLETED / REGISTERED_LOCAL_VOLATILITY_CALCULATION_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
GAP_ROADMAP_R16_APPROVAL_LINES = (
    "| V2-R16 | Local Range Channel Indicator Foundation | "
    "APPROVED / NOT_STARTED / REGISTERED_LOCAL_CHANNEL_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R16 / APPROVED.",
    "No successor phase after V2-R16 starts automatically.",
)
GAP_ROADMAP_R16_DELIVERY_LINES = (
    "| V2-R16 | Local Range Channel Indicator Foundation | "
    "IMPLEMENTED_PENDING_VALIDATION / REGISTERED_LOCAL_CHANNEL_CALCULATION_ONLY |",
    "Next product implementation phase: V2-R16 / APPROVED.",
    "No successor phase after V2-R16 starts automatically.",
)
GAP_ROADMAP_R16_FINAL_LINES = (
    "| V2-R16 | Local Range Channel Indicator Foundation | "
    "COMPLETED / REGISTERED_LOCAL_CHANNEL_CALCULATION_ONLY |",
    "Next product implementation phase: NOT_SELECTED / NOT_APPROVED.",
    "No successor phase starts automatically.",
)
DELIVERY_STATE = {
    "current_governance_phase_id": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "current_governance_phase_status": (
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "PROJECT-MEMORY-CONTINUITY-HARDENING-APP-1"
    ),
    "latest_completed_product_phase": (
        "SYSTEM-INTEGRITY-PRODUCT-HARDENING-STAGE-13"
    ),
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
FINAL_STATE = {
    **DELIVERY_STATE,
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
}
V2_R1_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R1-FACTOR-CONTRACT-FOUNDATION-APP-1"
    ),
    "current_governance_phase_status": (
        "PRODUCT_PHASE_APPROVED_NOT_STARTED"
    ),
    "current_product_implementation_phase": "V2-R1",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "SYSTEM-INTEGRITY-PRODUCT-HARDENING-STAGE-13"
    ),
    "next_product_implementation_phase": "V2-R1",
    "next_product_phase_approval": "APPROVED",
}
V2_R1_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "APPROVED_NOT_STARTED" if phase == "V2-R1" else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R1_DELIVERY_STATE = {
    **V2_R1_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION"
    ),
}
V2_R1_VALIDATED_STATE = {
    **V2_R1_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
}
V2_R1_DELIVERY_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "IMPLEMENTED_PENDING_VALIDATION"
            if phase == "V2-R1"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R1_VALIDATED_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "VALIDATED_PENDING_MERGE" if phase == "V2-R1" else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R1_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R1-FACTOR-CONTRACT-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R2",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R1_FINAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": "COMPLETED" if phase == "V2-R1" else ROADMAP_STATUS,
    }
    for phase in ROADMAP_PHASES
]
V2_R2_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R2-HISTORICAL-FACTOR-BASELINE-APP-1"
    ),
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R2",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R1-FACTOR-CONTRACT-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R2",
    "next_product_phase_approval": "APPROVED",
}
V2_R2_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase == "V2-R1"
            else "APPROVED_NOT_STARTED"
            if phase == "V2-R2"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R2_DELIVERY_STATE = {
    **V2_R2_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION"
    ),
}
V2_R2_DELIVERY_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase == "V2-R1"
            else "IMPLEMENTED_PENDING_VALIDATION"
            if phase == "V2-R2"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R2_VALIDATED_STATE = {
    **V2_R2_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
}
V2_R2_VALIDATED_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase == "V2-R1"
            else "VALIDATED_PENDING_MERGE"
            if phase == "V2-R2"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R2_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R2-HISTORICAL-FACTOR-BASELINE-APP-1"
    ),
    "next_product_implementation_phase": "V2-R3",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R2_FINAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED" if phase in ("V2-R1", "V2-R2") else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R3_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R3-LOCAL-EVENT-INGRESS-FOUNDATION-APP-1"
    ),
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R3",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R2-HISTORICAL-FACTOR-BASELINE-APP-1"
    ),
    "next_product_implementation_phase": "V2-R3",
    "next_product_phase_approval": "APPROVED",
}
V2_R3_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2")
            else "APPROVED_NOT_STARTED"
            if phase == "V2-R3"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R3_DELIVERY_STATE = {
    **V2_R3_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION"
    ),
}
V2_R3_DELIVERY_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2")
            else "IMPLEMENTED_PENDING_VALIDATION"
            if phase == "V2-R3"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R3_VALIDATED_STATE = {
    **V2_R3_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
}
V2_R3_VALIDATED_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2")
            else "VALIDATED_PENDING_MERGE"
            if phase == "V2-R3"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R3_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R3-LOCAL-EVENT-INGRESS-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R4",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R3_FINAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3")
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R4_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R4-LOCAL-ANOMALY-RADAR-FOUNDATION-APP-1"
    ),
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R4",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R3-LOCAL-EVENT-INGRESS-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R4",
    "next_product_phase_approval": "APPROVED",
}
V2_R4_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3")
            else "APPROVED_NOT_STARTED"
            if phase == "V2-R4"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R4_DELIVERY_STATE = {
    **V2_R4_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION"
    ),
}
V2_R4_DELIVERY_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3")
            else "IMPLEMENTED_PENDING_VALIDATION"
            if phase == "V2-R4"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R4_VALIDATED_STATE = {
    **V2_R4_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
}
V2_R4_VALIDATED_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3")
            else "VALIDATED_PENDING_MERGE"
            if phase == "V2-R4"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R4_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R4-LOCAL-ANOMALY-RADAR-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R5",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R4_FINAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3", "V2-R4")
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R5_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R5-LOCAL-COGNITIVE-SHIELD-FOUNDATION-APP-1"
    ),
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R5",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R4-LOCAL-ANOMALY-RADAR-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R5",
    "next_product_phase_approval": "APPROVED",
}
V2_R5_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3", "V2-R4")
            else "APPROVED_NOT_STARTED"
            if phase == "V2-R5"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R5_DELIVERY_STATE = {
    **V2_R5_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION"
    ),
}
V2_R5_DELIVERY_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3", "V2-R4")
            else "IMPLEMENTED_PENDING_VALIDATION"
            if phase == "V2-R5"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R5_VALIDATED_STATE = {
    **V2_R5_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
}
V2_R5_VALIDATED_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3", "V2-R4")
            else "VALIDATED_PENDING_MERGE"
            if phase == "V2-R5"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R5_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R5-LOCAL-COGNITIVE-SHIELD-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R6",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R5_FINAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED" if phase in ("V2-R1", "V2-R2", "V2-R3", "V2-R4", "V2-R5")
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R6_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R6-LOCAL-PAPER-SCENARIO-RESEARCH-FOUNDATION-APP-1"
    ),
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R6",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R5-LOCAL-COGNITIVE-SHIELD-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R6",
    "next_product_phase_approval": "APPROVED",
}
V2_R6_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3", "V2-R4", "V2-R5")
            else "APPROVED_NOT_STARTED"
            if phase == "V2-R6"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R6_DELIVERY_STATE = {
    **V2_R6_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION"
    ),
}
V2_R6_DELIVERY_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3", "V2-R4", "V2-R5")
            else "IMPLEMENTED_PENDING_VALIDATION"
            if phase == "V2-R6"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R6_VALIDATED_STATE = {
    **V2_R6_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
}
V2_R6_VALIDATED_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "COMPLETED"
            if phase in ("V2-R1", "V2-R2", "V2-R3", "V2-R4", "V2-R5")
            else "VALIDATED_PENDING_MERGE"
            if phase == "V2-R6"
            else ROADMAP_STATUS
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R6_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R6-LOCAL-PAPER-SCENARIO-RESEARCH-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R6_FINAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": "COMPLETED" if phase != "V2-R7" else ROADMAP_STATUS,
    }
    for phase in ROADMAP_PHASES
]
V2_R7_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R7-LOCAL-MARKET-SESSION-REGISTRY-FOUNDATION-APP-1"
    ),
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R7",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R6-LOCAL-PAPER-SCENARIO-RESEARCH-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R7",
    "next_product_phase_approval": "APPROVED",
}
V2_R7_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "APPROVED_NOT_STARTED" if phase == "V2-R7" else "COMPLETED"
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R7_DELIVERY_STATE = {
    **V2_R7_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION"
    ),
}
V2_R7_DELIVERY_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R7" else "COMPLETED"
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R7_VALIDATED_STATE = {
    **V2_R7_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
}
V2_R7_VALIDATED_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "VALIDATED_PENDING_MERGE" if phase == "V2-R7" else "COMPLETED"
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R7_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R7-LOCAL-MARKET-SESSION-REGISTRY-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R7_FINAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": "COMPLETED" if phase != "V2-R8" else ROADMAP_STATUS,
    }
    for phase in ROADMAP_PHASES
]
V2_R8_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R8-LOCAL-SAME-TIME-BASELINE-FOUNDATION-APP-1"
    ),
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R8",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R7-LOCAL-MARKET-SESSION-REGISTRY-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R8",
    "next_product_phase_approval": "APPROVED",
}
V2_R8_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": "APPROVED_NOT_STARTED" if phase == "V2-R8" else "COMPLETED",
    }
    for phase in ROADMAP_PHASES
]
V2_R8_DELIVERY_STATE = {
    **V2_R8_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION"
    ),
}
V2_R8_DELIVERY_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R8" else "COMPLETED"
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R8_VALIDATED_STATE = {
    **V2_R8_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
}
V2_R8_VALIDATED_ROADMAP = [
    {
        "phase_id": phase,
        "status": "VALIDATED_PENDING_MERGE" if phase == "V2-R8" else "COMPLETED",
    }
    for phase in ROADMAP_PHASES
]
V2_R8_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R8-LOCAL-SAME-TIME-BASELINE-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R8_FINAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": "COMPLETED" if phase != "V2-R9" else ROADMAP_STATUS,
    }
    for phase in ROADMAP_PHASES
]
V2_R9_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R9-LOCAL-VOLUME-RATIO-RESEARCH-FOUNDATION-APP-1"
    ),
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R9",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R8-LOCAL-SAME-TIME-BASELINE-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R9",
    "next_product_phase_approval": "APPROVED",
}
V2_R9_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": "APPROVED_NOT_STARTED" if phase == "V2-R9" else "COMPLETED",
    }
    for phase in ROADMAP_PHASES
]
V2_R9_DELIVERY_STATE = {
    **V2_R9_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION"
    ),
}
V2_R9_DELIVERY_ROADMAP = [
    {
        "phase_id": phase,
        "status": (
            "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R9" else "COMPLETED"
        ),
    }
    for phase in ROADMAP_PHASES
]
V2_R9_VALIDATED_STATE = {
    **V2_R9_APPROVAL_STATE,
    "current_governance_phase_status": (
        "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE"
    ),
}
V2_R9_VALIDATED_ROADMAP = [
    {
        "phase_id": phase,
        "status": "VALIDATED_PENDING_MERGE" if phase == "V2-R9" else "COMPLETED",
    }
    for phase in ROADMAP_PHASES
]
V2_R9_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R9-LOCAL-VOLUME-RATIO-RESEARCH-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R9_FINAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": "COMPLETED" if phase != "V2-R10" else ROADMAP_STATUS,
    }
    for phase in ROADMAP_PHASES
]
V2_R10_APPROVAL_STATE = {
    "current_governance_phase_id": (
        "V2-R10-LOCAL-TURNOVER-DEFINITION-RESEARCH-FOUNDATION-APP-1"
    ),
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R10",
    "latest_completed_governance_delivery": (
        "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1"
    ),
    "latest_completed_product_phase": (
        "V2-R9-LOCAL-VOLUME-RATIO-RESEARCH-FOUNDATION-APP-1"
    ),
    "next_product_implementation_phase": "V2-R10",
    "next_product_phase_approval": "APPROVED",
}
V2_R10_APPROVAL_ROADMAP = [
    {
        "phase_id": phase,
        "status": "APPROVED_NOT_STARTED" if phase == "V2-R10" else "COMPLETED",
    }
    for phase in ROADMAP_PHASES
]
V2_R10_DELIVERY_STATE = {
    **V2_R10_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
}
V2_R10_DELIVERY_ROADMAP = [
    {"phase_id": phase, "status": "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R10" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R10_VALIDATED_STATE = {
    **V2_R10_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE",
}
V2_R10_VALIDATED_ROADMAP = [
    {"phase_id": phase, "status": "VALIDATED_PENDING_MERGE" if phase == "V2-R10" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R10_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R10-LOCAL-TURNOVER-DEFINITION-RESEARCH-FOUNDATION-APP-1",
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R10_FINAL_ROADMAP = [{"phase_id": phase, "status": "COMPLETED"} for phase in ROADMAP_PHASES]
V2_R11_APPROVAL_STATE = {
    "current_governance_phase_id": "V2-R11-LOCAL-FACTOR-REGISTRY-FOUNDATION-APP-1",
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R11",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R10-LOCAL-TURNOVER-DEFINITION-RESEARCH-FOUNDATION-APP-1",
    "next_product_implementation_phase": "V2-R11",
    "next_product_phase_approval": "APPROVED",
}
V2_R11_APPROVAL_ROADMAP = [
    {"phase_id": phase, "status": "APPROVED_NOT_STARTED" if phase == "V2-R11" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R11_DELIVERY_STATE = {
    **V2_R11_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
}
V2_R11_DELIVERY_ROADMAP = [
    {"phase_id": phase, "status": "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R11" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R11_VALIDATED_STATE = {
    **V2_R11_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE",
}
V2_R11_VALIDATED_ROADMAP = [
    {"phase_id": phase, "status": "VALIDATED_PENDING_MERGE" if phase == "V2-R11" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R11_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R11-LOCAL-FACTOR-REGISTRY-FOUNDATION-APP-1",
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R11_FINAL_ROADMAP = [{"phase_id": phase, "status": "COMPLETED"} for phase in ROADMAP_PHASES]
V2_R12_APPROVAL_STATE = {
    "current_governance_phase_id": "V2-R12-LOCAL-TECHNICAL-INDICATOR-FOUNDATION-APP-1",
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R12",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R11-LOCAL-FACTOR-REGISTRY-FOUNDATION-APP-1",
    "next_product_implementation_phase": "V2-R12",
    "next_product_phase_approval": "APPROVED",
}
V2_R12_APPROVAL_ROADMAP = [
    {"phase_id": phase, "status": "APPROVED_NOT_STARTED" if phase == "V2-R12" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R12_DELIVERY_STATE = {
    **V2_R12_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
}
V2_R12_DELIVERY_ROADMAP = [
    {"phase_id": phase, "status": "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R12" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R12_VALIDATED_STATE = {
    **V2_R12_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE",
}
V2_R12_VALIDATED_ROADMAP = [
    {"phase_id": phase, "status": "VALIDATED_PENDING_MERGE" if phase == "V2-R12" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R12_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R12-LOCAL-TECHNICAL-INDICATOR-FOUNDATION-APP-1",
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R12_FINAL_ROADMAP = [{"phase_id": phase, "status": "COMPLETED"} for phase in ROADMAP_PHASES]
V2_R13_APPROVAL_STATE = {
    "current_governance_phase_id": "V2-R13-LOCAL-MOMENTUM-INDICATOR-FOUNDATION-APP-1",
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R13",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R12-LOCAL-TECHNICAL-INDICATOR-FOUNDATION-APP-1",
    "next_product_implementation_phase": "V2-R13",
    "next_product_phase_approval": "APPROVED",
}
V2_R13_APPROVAL_ROADMAP = [
    {"phase_id": phase, "status": "APPROVED_NOT_STARTED" if phase == "V2-R13" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R13_DELIVERY_STATE = {
    **V2_R13_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
}
V2_R13_DELIVERY_ROADMAP = [
    {"phase_id": phase, "status": "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R13" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R13_VALIDATED_STATE = {
    **V2_R13_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE",
}
V2_R13_VALIDATED_ROADMAP = [
    {"phase_id": phase, "status": "VALIDATED_PENDING_MERGE" if phase == "V2-R13" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R13_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R13-LOCAL-MOMENTUM-INDICATOR-FOUNDATION-APP-1",
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R13_FINAL_ROADMAP = [{"phase_id": phase, "status": "COMPLETED"} for phase in ROADMAP_PHASES]
V2_R14_APPROVAL_STATE = {
    "current_governance_phase_id": "V2-R14-LOCAL-TREND-INDICATOR-FOUNDATION-APP-1",
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R14",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R13-LOCAL-MOMENTUM-INDICATOR-FOUNDATION-APP-1",
    "next_product_implementation_phase": "V2-R14",
    "next_product_phase_approval": "APPROVED",
}
V2_R14_APPROVAL_ROADMAP = [
    {"phase_id": phase, "status": "APPROVED_NOT_STARTED" if phase == "V2-R14" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R14_DELIVERY_STATE = {
    **V2_R14_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
}
V2_R14_DELIVERY_ROADMAP = [
    {"phase_id": phase, "status": "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R14" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R14_VALIDATED_STATE = {
    **V2_R14_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE",
}
V2_R14_VALIDATED_ROADMAP = [
    {"phase_id": phase, "status": "VALIDATED_PENDING_MERGE" if phase == "V2-R14" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R14_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R14-LOCAL-TREND-INDICATOR-FOUNDATION-APP-1",
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R14_FINAL_ROADMAP = [{"phase_id": phase, "status": "COMPLETED"} for phase in ROADMAP_PHASES]
V2_R15_APPROVAL_STATE = {
    "current_governance_phase_id": "V2-R15-LOCAL-VOLATILITY-INDICATOR-FOUNDATION-APP-1",
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R15",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R14-LOCAL-TREND-INDICATOR-FOUNDATION-APP-1",
    "next_product_implementation_phase": "V2-R15",
    "next_product_phase_approval": "APPROVED",
}
V2_R15_APPROVAL_ROADMAP = [
    {"phase_id": phase, "status": "APPROVED_NOT_STARTED" if phase == "V2-R15" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R15_DELIVERY_STATE = {
    **V2_R15_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
}
V2_R15_DELIVERY_ROADMAP = [
    {"phase_id": phase, "status": "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R15" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R15_VALIDATED_STATE = {
    **V2_R15_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE",
}
V2_R15_VALIDATED_ROADMAP = [
    {"phase_id": phase, "status": "VALIDATED_PENDING_MERGE" if phase == "V2-R15" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R15_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R15-LOCAL-VOLATILITY-INDICATOR-FOUNDATION-APP-1",
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R15_FINAL_ROADMAP = [{"phase_id": phase, "status": "COMPLETED"} for phase in ROADMAP_PHASES]
V2_R16_APPROVAL_STATE = {
    "current_governance_phase_id": "V2-R16-LOCAL-RANGE-CHANNEL-INDICATOR-FOUNDATION-APP-1",
    "current_governance_phase_status": "PRODUCT_PHASE_APPROVED_NOT_STARTED",
    "current_product_implementation_phase": "V2-R16",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R15-LOCAL-VOLATILITY-INDICATOR-FOUNDATION-APP-1",
    "next_product_implementation_phase": "V2-R16",
    "next_product_phase_approval": "APPROVED",
}
V2_R16_APPROVAL_ROADMAP = [
    {"phase_id": phase, "status": "APPROVED_NOT_STARTED" if phase == "V2-R16" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R16_DELIVERY_STATE = {
    **V2_R16_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
}
V2_R16_DELIVERY_ROADMAP = [
    {"phase_id": phase, "status": "IMPLEMENTED_PENDING_VALIDATION" if phase == "V2-R16" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R16_VALIDATED_STATE = {
    **V2_R16_APPROVAL_STATE,
    "current_governance_phase_status": "PRODUCT_DELIVERY_VALIDATED_PENDING_MERGE",
}
V2_R16_VALIDATED_ROADMAP = [
    {"phase_id": phase, "status": "VALIDATED_PENDING_MERGE" if phase == "V2-R16" else "COMPLETED"}
    for phase in ROADMAP_PHASES
]
V2_R16_FINAL_STATE = {
    "current_governance_phase_id": "NONE",
    "current_governance_phase_status": "NONE",
    "current_product_implementation_phase": "NONE",
    "latest_completed_governance_delivery": "FCF-V2-MARKET-SESSION-RESEARCH-ARCHITECTURE-SYNC-APP-1",
    "latest_completed_product_phase": "V2-R16-LOCAL-RANGE-CHANNEL-INDICATOR-FOUNDATION-APP-1",
    "next_product_implementation_phase": "NOT_SELECTED",
    "next_product_phase_approval": "NOT_APPROVED",
}
V2_R16_FINAL_ROADMAP = [{"phase_id": phase, "status": "COMPLETED"} for phase in ROADMAP_PHASES]
EXPECTED_SAFETY = {
    "ai_advisory_only": True,
    "broker_path_allowed": False,
    "credential_path_allowed": False,
    "deterministic_engine_calculation_authority": True,
    "exchange_path_allowed": False,
    "local_only": True,
    "loopback_only": True,
    "operator_review_mandatory": True,
    "order_or_execution_path_allowed": False,
    "p1_p47_frozen": True,
    "p48_allowed": False,
    "paper_only": True,
    "read_only_product_presentation": True,
    "registered_artifact_only": True,
    "registered_evidence_authority": True,
    "sidecar_only": True,
}


def _read_ascii(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="ascii")


def load_manifest(root: Path = ROOT) -> dict[str, object]:
    return json.loads(_read_ascii(root, MANIFEST_PATH))


def extract_single_block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    start_index = text.index(start)
    end_index = text.index(end)
    if end_index <= start_index:
        return None
    return text[start_index : end_index + len(end)]


def blocks_are_exact(texts: tuple[str, ...], start: str, end: str) -> bool:
    blocks = tuple(extract_single_block(text, start, end) for text in texts)
    if any(block is None for block in blocks):
        return False
    digests = {
        hashlib.sha256(block.encode("ascii")).hexdigest()
        for block in blocks
        if block is not None
    }
    return len(digests) == 1


def extract_gap_rows(text: str) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
    pattern = re.compile(
        r"^\| (V2-FR-GAP-[0-9]{3}) \| [^|]+ \| ([A-Z_]+) \|$"
    )
    for line in text.splitlines():
        match = pattern.fullmatch(line)
        if match:
            rows.append((match.group(1), match.group(2)))
    return tuple(rows)


def gap_statuses_are_valid(text: str) -> bool:
    rows = extract_gap_rows(text)
    return (
        tuple(row[0] for row in rows) == GAP_IDS
        and all(row[1] in FUTURE_STATUSES for row in rows)
        and dict(rows).get("V2-FR-GAP-041")
        == "OUTSIDE_CURRENT_AUTHORIZATION"
        and dict(rows).get("V2-FR-GAP-065")
        == "OUTSIDE_CURRENT_AUTHORIZATION"
    )


def build_project_memory_guard_report(
    root: Path = ROOT,
) -> dict[str, object]:
    required_paths = tuple(Path(path) for path in EXPECTED_FILE_ROLES.values())
    try:
        manifest = load_manifest(root)
        protocol = _read_ascii(root, PROTOCOL_PATH)
        architecture = _read_ascii(root, ARCHITECTURE_PATH)
        gap = _read_ascii(root, GAP_PATH)
        authority_texts = tuple(
            _read_ascii(root, path) for path in AUTHORITY_PATHS
        )
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        manifest = {}
        protocol = ""
        architecture = ""
        gap = ""
        authority_texts = ()
        ascii_only = False

    roadmap = manifest.get("roadmap")
    expected_roadmap = [
        {"phase_id": phase, "status": ROADMAP_STATUS}
        for phase in ROADMAP_PHASES
    ]
    current_truth = manifest.get("current_truth")
    current_truth_safe = current_truth in (
        DELIVERY_STATE,
        FINAL_STATE,
        V2_R1_APPROVAL_STATE,
        V2_R1_DELIVERY_STATE,
        V2_R1_VALIDATED_STATE,
        V2_R1_FINAL_STATE,
        V2_R2_APPROVAL_STATE,
        V2_R2_DELIVERY_STATE,
        V2_R2_VALIDATED_STATE,
        V2_R2_FINAL_STATE,
        V2_R3_APPROVAL_STATE,
        V2_R3_DELIVERY_STATE,
        V2_R3_VALIDATED_STATE,
        V2_R3_FINAL_STATE,
        V2_R4_APPROVAL_STATE,
        V2_R4_DELIVERY_STATE,
        V2_R4_VALIDATED_STATE,
        V2_R4_FINAL_STATE,
        V2_R5_APPROVAL_STATE,
        V2_R5_DELIVERY_STATE,
        V2_R5_VALIDATED_STATE,
        V2_R5_FINAL_STATE,
        V2_R6_APPROVAL_STATE,
        V2_R6_DELIVERY_STATE,
        V2_R6_VALIDATED_STATE,
        V2_R6_FINAL_STATE,
        V2_R7_APPROVAL_STATE,
        V2_R7_DELIVERY_STATE,
        V2_R7_VALIDATED_STATE,
        V2_R7_FINAL_STATE,
        V2_R8_APPROVAL_STATE,
        V2_R8_DELIVERY_STATE,
        V2_R8_VALIDATED_STATE,
        V2_R8_FINAL_STATE,
        V2_R9_APPROVAL_STATE,
        V2_R9_DELIVERY_STATE,
        V2_R9_VALIDATED_STATE,
        V2_R9_FINAL_STATE,
        V2_R10_APPROVAL_STATE,
        V2_R10_DELIVERY_STATE,
        V2_R10_VALIDATED_STATE,
        V2_R10_FINAL_STATE,
        V2_R11_APPROVAL_STATE,
        V2_R11_DELIVERY_STATE,
        V2_R11_VALIDATED_STATE,
        V2_R11_FINAL_STATE,
        V2_R12_APPROVAL_STATE,
        V2_R12_DELIVERY_STATE,
        V2_R12_VALIDATED_STATE,
        V2_R12_FINAL_STATE,
        V2_R13_APPROVAL_STATE,
        V2_R13_DELIVERY_STATE,
        V2_R13_VALIDATED_STATE,
        V2_R13_FINAL_STATE,
        V2_R14_APPROVAL_STATE,
        V2_R14_DELIVERY_STATE,
        V2_R14_VALIDATED_STATE,
        V2_R14_FINAL_STATE,
        V2_R15_APPROVAL_STATE,
        V2_R15_DELIVERY_STATE,
        V2_R15_VALIDATED_STATE,
        V2_R15_FINAL_STATE,
        V2_R16_APPROVAL_STATE,
        V2_R16_DELIVERY_STATE,
        V2_R16_VALIDATED_STATE,
        V2_R16_FINAL_STATE,
    )
    memory_final_blocks = tuple(
        extract_single_block(text, MEMORY_FINAL_START, MEMORY_FINAL_END)
        for text in authority_texts
    )
    session_final_blocks = tuple(
        extract_single_block(text, SESSION_FINAL_START, SESSION_FINAL_END)
        for text in authority_texts
    )
    v2_r1_final_blocks = tuple(
        extract_single_block(text, V2_R1_FINAL_START, V2_R1_FINAL_END)
        for text in authority_texts
    )
    v2_r2_final_blocks = tuple(
        extract_single_block(text, V2_R2_FINAL_START, V2_R2_FINAL_END)
        for text in authority_texts
    )
    v2_r3_final_blocks = tuple(
        extract_single_block(text, V2_R3_FINAL_START, V2_R3_FINAL_END)
        for text in authority_texts
    )
    v2_r4_final_blocks = tuple(
        extract_single_block(text, V2_R4_FINAL_START, V2_R4_FINAL_END)
        for text in authority_texts
    )
    v2_r5_final_blocks = tuple(
        extract_single_block(text, V2_R5_FINAL_START, V2_R5_FINAL_END)
        for text in authority_texts
    )
    v2_r6_final_blocks = tuple(
        extract_single_block(text, V2_R6_FINAL_START, V2_R6_FINAL_END)
        for text in authority_texts
    )
    v2_r7_final_blocks = tuple(
        extract_single_block(text, V2_R7_FINAL_START, V2_R7_FINAL_END)
        for text in authority_texts
    )
    v2_r8_final_blocks = tuple(
        extract_single_block(text, V2_R8_FINAL_START, V2_R8_FINAL_END)
        for text in authority_texts
    )
    v2_r9_final_blocks = tuple(
        extract_single_block(text, V2_R9_FINAL_START, V2_R9_FINAL_END)
        for text in authority_texts
    )
    v2_r10_final_blocks = tuple(
        extract_single_block(text, V2_R10_FINAL_START, V2_R10_FINAL_END)
        for text in authority_texts
    )
    v2_r11_final_blocks = tuple(
        extract_single_block(text, V2_R11_FINAL_START, V2_R11_FINAL_END)
        for text in authority_texts
    )
    v2_r12_final_blocks = tuple(
        extract_single_block(text, V2_R12_FINAL_START, V2_R12_FINAL_END)
        for text in authority_texts
    )
    v2_r13_final_blocks = tuple(
        extract_single_block(text, V2_R13_FINAL_START, V2_R13_FINAL_END)
        for text in authority_texts
    )
    v2_r14_final_blocks = tuple(
        extract_single_block(text, V2_R14_FINAL_START, V2_R14_FINAL_END)
        for text in authority_texts
    )
    v2_r15_final_blocks = tuple(
        extract_single_block(text, V2_R15_FINAL_START, V2_R15_FINAL_END)
        for text in authority_texts
    )
    v2_r16_final_blocks = tuple(
        extract_single_block(text, V2_R16_FINAL_START, V2_R16_FINAL_END)
        for text in authority_texts
    )
    file_roles = manifest.get("canonical_file_roles")
    statuses = manifest.get("future_capability_statuses")
    historical = manifest.get("historical_registry")
    checks = {
        "required_files_exist": all((root / path).is_file() for path in required_paths),
        "governance_files_ascii": ascii_only,
        "manifest_identity_exact": manifest.get("schema_version") == 1
        and manifest.get("project_id") == "FCF"
        and manifest.get("project_name") == "Financial Cognitive Framework"
        and manifest.get("repository") == "wangshaoyuhaha/fcf-spec",
        "canonical_file_roles_exact": file_roles == EXPECTED_FILE_ROLES,
        "accepted_future_architecture_exact": manifest.get(
            "accepted_future_architecture"
        )
        == EXPECTED_FUTURE_ARCHITECTURE,
        "active_authority_registry_exact": manifest.get(
            "active_authority_sources"
        ) == [path.as_posix() for path in AUTHORITY_PATHS],
        "current_truth_safe": current_truth_safe,
        "roadmap_exact": roadmap
        == (
            V2_R1_APPROVAL_ROADMAP
            if current_truth == V2_R1_APPROVAL_STATE
            else V2_R1_DELIVERY_ROADMAP
            if current_truth == V2_R1_DELIVERY_STATE
            else V2_R1_VALIDATED_ROADMAP
            if current_truth == V2_R1_VALIDATED_STATE
            else V2_R1_FINAL_ROADMAP
            if current_truth == V2_R1_FINAL_STATE
            else V2_R2_APPROVAL_ROADMAP
            if current_truth == V2_R2_APPROVAL_STATE
            else V2_R2_DELIVERY_ROADMAP
            if current_truth == V2_R2_DELIVERY_STATE
            else V2_R2_VALIDATED_ROADMAP
            if current_truth == V2_R2_VALIDATED_STATE
            else V2_R2_FINAL_ROADMAP
            if current_truth == V2_R2_FINAL_STATE
            else V2_R3_APPROVAL_ROADMAP
            if current_truth == V2_R3_APPROVAL_STATE
            else V2_R3_DELIVERY_ROADMAP
            if current_truth == V2_R3_DELIVERY_STATE
            else V2_R3_VALIDATED_ROADMAP
            if current_truth == V2_R3_VALIDATED_STATE
            else V2_R3_FINAL_ROADMAP
            if current_truth == V2_R3_FINAL_STATE
            else V2_R4_APPROVAL_ROADMAP
            if current_truth == V2_R4_APPROVAL_STATE
            else V2_R4_DELIVERY_ROADMAP
            if current_truth == V2_R4_DELIVERY_STATE
            else V2_R4_VALIDATED_ROADMAP
            if current_truth == V2_R4_VALIDATED_STATE
            else V2_R4_FINAL_ROADMAP
            if current_truth == V2_R4_FINAL_STATE
            else V2_R5_APPROVAL_ROADMAP
            if current_truth == V2_R5_APPROVAL_STATE
            else V2_R5_DELIVERY_ROADMAP
            if current_truth == V2_R5_DELIVERY_STATE
            else V2_R5_VALIDATED_ROADMAP
            if current_truth == V2_R5_VALIDATED_STATE
            else V2_R5_FINAL_ROADMAP
            if current_truth == V2_R5_FINAL_STATE
            else V2_R6_APPROVAL_ROADMAP
            if current_truth == V2_R6_APPROVAL_STATE
            else V2_R6_DELIVERY_ROADMAP
            if current_truth == V2_R6_DELIVERY_STATE
            else V2_R6_VALIDATED_ROADMAP
            if current_truth == V2_R6_VALIDATED_STATE
            else V2_R6_FINAL_ROADMAP
            if current_truth == V2_R6_FINAL_STATE
            else V2_R7_APPROVAL_ROADMAP
            if current_truth == V2_R7_APPROVAL_STATE
            else V2_R7_DELIVERY_ROADMAP
            if current_truth == V2_R7_DELIVERY_STATE
            else V2_R7_VALIDATED_ROADMAP
            if current_truth == V2_R7_VALIDATED_STATE
            else V2_R7_FINAL_ROADMAP
            if current_truth == V2_R7_FINAL_STATE
            else V2_R8_APPROVAL_ROADMAP
            if current_truth == V2_R8_APPROVAL_STATE
            else V2_R8_DELIVERY_ROADMAP
            if current_truth == V2_R8_DELIVERY_STATE
            else V2_R8_VALIDATED_ROADMAP
            if current_truth == V2_R8_VALIDATED_STATE
            else V2_R8_FINAL_ROADMAP
            if current_truth == V2_R8_FINAL_STATE
            else V2_R9_APPROVAL_ROADMAP
            if current_truth == V2_R9_APPROVAL_STATE
            else V2_R9_DELIVERY_ROADMAP
            if current_truth == V2_R9_DELIVERY_STATE
            else V2_R9_VALIDATED_ROADMAP
            if current_truth == V2_R9_VALIDATED_STATE
            else V2_R9_FINAL_ROADMAP
            if current_truth == V2_R9_FINAL_STATE
            else V2_R10_APPROVAL_ROADMAP
            if current_truth == V2_R10_APPROVAL_STATE
            else V2_R10_DELIVERY_ROADMAP
            if current_truth == V2_R10_DELIVERY_STATE
            else V2_R10_VALIDATED_ROADMAP
            if current_truth == V2_R10_VALIDATED_STATE
            else V2_R10_FINAL_ROADMAP
            if current_truth == V2_R10_FINAL_STATE
            else V2_R11_APPROVAL_ROADMAP
            if current_truth == V2_R11_APPROVAL_STATE
            else V2_R11_DELIVERY_ROADMAP
            if current_truth == V2_R11_DELIVERY_STATE
            else V2_R11_VALIDATED_ROADMAP
            if current_truth == V2_R11_VALIDATED_STATE
            else V2_R11_FINAL_ROADMAP
            if current_truth == V2_R11_FINAL_STATE
            else V2_R12_APPROVAL_ROADMAP
            if current_truth == V2_R12_APPROVAL_STATE
            else V2_R12_DELIVERY_ROADMAP
            if current_truth == V2_R12_DELIVERY_STATE
            else V2_R12_VALIDATED_ROADMAP
            if current_truth == V2_R12_VALIDATED_STATE
            else V2_R12_FINAL_ROADMAP
            if current_truth == V2_R12_FINAL_STATE
            else V2_R13_APPROVAL_ROADMAP
            if current_truth == V2_R13_APPROVAL_STATE
            else V2_R13_DELIVERY_ROADMAP
            if current_truth == V2_R13_DELIVERY_STATE
            else V2_R13_VALIDATED_ROADMAP
            if current_truth == V2_R13_VALIDATED_STATE
            else V2_R13_FINAL_ROADMAP
            if current_truth == V2_R13_FINAL_STATE
            else V2_R14_APPROVAL_ROADMAP
            if current_truth == V2_R14_APPROVAL_STATE
            else V2_R14_DELIVERY_ROADMAP
            if current_truth == V2_R14_DELIVERY_STATE
            else V2_R14_VALIDATED_ROADMAP
            if current_truth == V2_R14_VALIDATED_STATE
            else V2_R14_FINAL_ROADMAP
            if current_truth == V2_R14_FINAL_STATE
            else V2_R15_APPROVAL_ROADMAP
            if current_truth == V2_R15_APPROVAL_STATE
            else V2_R15_DELIVERY_ROADMAP
            if current_truth == V2_R15_DELIVERY_STATE
            else V2_R15_VALIDATED_ROADMAP
            if current_truth == V2_R15_VALIDATED_STATE
            else V2_R15_FINAL_ROADMAP
            if current_truth == V2_R15_FINAL_STATE
            else V2_R16_APPROVAL_ROADMAP
            if current_truth == V2_R16_APPROVAL_STATE
            else V2_R16_DELIVERY_ROADMAP
            if current_truth == V2_R16_DELIVERY_STATE
            else V2_R16_VALIDATED_ROADMAP
            if current_truth == V2_R16_VALIDATED_STATE
            else V2_R16_FINAL_ROADMAP
            if current_truth == V2_R16_FINAL_STATE
            else expected_roadmap
        ),
        "future_status_vocabulary_exact": statuses == list(FUTURE_STATUSES),
        "gap_statuses_closed": gap_statuses_are_valid(gap),
        "gap_roadmap_matches_final_manifest": (
            current_truth == V2_R6_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_FINAL_LINES)
        )
        or (
            current_truth == V2_R7_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R7_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R7_DELIVERY_STATE, V2_R7_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R7_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R7_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R7_FINAL_LINES)
        )
        or (
            current_truth == V2_R8_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R8_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R8_DELIVERY_STATE, V2_R8_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R8_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R8_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R8_FINAL_LINES)
        )
        or (
            current_truth == V2_R9_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R9_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R9_DELIVERY_STATE, V2_R9_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R9_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R9_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R9_FINAL_LINES)
        )
        or (
            current_truth == V2_R10_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R10_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R10_DELIVERY_STATE, V2_R10_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R10_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R10_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R10_FINAL_LINES)
        )
        or (
            current_truth == V2_R11_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R11_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R11_DELIVERY_STATE, V2_R11_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R11_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R11_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R11_FINAL_LINES)
        )
        or (
            current_truth == V2_R12_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R12_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R12_DELIVERY_STATE, V2_R12_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R12_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R12_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R12_FINAL_LINES)
        )
        or (
            current_truth == V2_R13_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R13_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R13_DELIVERY_STATE, V2_R13_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R13_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R13_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R13_FINAL_LINES)
        )
        or (
            current_truth == V2_R14_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R14_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R14_DELIVERY_STATE, V2_R14_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R14_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R14_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R14_FINAL_LINES)
        )
        or (
            current_truth == V2_R15_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R15_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R15_DELIVERY_STATE, V2_R15_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R15_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R15_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R15_FINAL_LINES)
        )
        or (
            current_truth == V2_R16_APPROVAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R16_APPROVAL_LINES)
        )
        or (
            current_truth in (V2_R16_DELIVERY_STATE, V2_R16_VALIDATED_STATE)
            and all(line in gap for line in GAP_ROADMAP_R16_DELIVERY_LINES)
        )
        or (
            current_truth == V2_R16_FINAL_STATE
            and all(line in gap for line in GAP_ROADMAP_R16_FINAL_LINES)
        )
        or current_truth
        not in (
            V2_R6_FINAL_STATE,
            V2_R7_APPROVAL_STATE,
            V2_R7_DELIVERY_STATE,
            V2_R7_VALIDATED_STATE,
            V2_R7_FINAL_STATE,
            V2_R8_APPROVAL_STATE,
            V2_R8_DELIVERY_STATE,
            V2_R8_VALIDATED_STATE,
            V2_R8_FINAL_STATE,
            V2_R9_APPROVAL_STATE,
            V2_R9_DELIVERY_STATE,
            V2_R9_VALIDATED_STATE,
            V2_R9_FINAL_STATE,
            V2_R10_APPROVAL_STATE,
            V2_R10_DELIVERY_STATE,
            V2_R10_VALIDATED_STATE,
            V2_R10_FINAL_STATE,
            V2_R11_APPROVAL_STATE,
            V2_R11_DELIVERY_STATE,
            V2_R11_VALIDATED_STATE,
            V2_R11_FINAL_STATE,
            V2_R12_APPROVAL_STATE,
            V2_R12_DELIVERY_STATE,
            V2_R12_VALIDATED_STATE,
            V2_R13_APPROVAL_STATE,
            V2_R13_DELIVERY_STATE,
            V2_R13_VALIDATED_STATE,
            V2_R14_APPROVAL_STATE,
            V2_R14_DELIVERY_STATE,
            V2_R14_VALIDATED_STATE,
            V2_R15_APPROVAL_STATE,
            V2_R15_DELIVERY_STATE,
            V2_R15_VALIDATED_STATE,
            V2_R16_APPROVAL_STATE,
            V2_R16_DELIVERY_STATE,
            V2_R16_VALIDATED_STATE,
        ),
        "status_definitions_synchronized": all(
            f"`{status}`" in architecture
            and f"`{status}`" in gap
            and f"`{status}`" in protocol
            for status in FUTURE_STATUSES
        ),
        "historical_registry_not_current_authority": historical
        == {
            "path": "scripts/v2_implementation_order_registry.py",
            "status": (
                "HISTORICAL_COMPLETED_SEQUENCE_"
                "NOT_CURRENT_NEXT_PHASE_AUTHORITY"
            ),
        },
        "safety_boundaries_exact": manifest.get("safety_boundaries")
        == EXPECTED_SAFETY,
        "memory_lock_exact_across_authorities": len(authority_texts)
        == len(AUTHORITY_PATHS)
        and blocks_are_exact(
            authority_texts, MEMORY_LOCK_START, MEMORY_LOCK_END
        ),
        "memory_final_sync_exact_across_authorities": current_truth
        == DELIVERY_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, MEMORY_FINAL_START, MEMORY_FINAL_END
            )
        ),
        "memory_final_evidence_commits_exact": current_truth == DELIVERY_STATE
        or (
            len(memory_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in memory_final_blocks)
            and all(
                all(commit in block for commit in FINAL_EVIDENCE_COMMITS)
                for block in memory_final_blocks
                if block is not None
            )
        ),
        "session_approval_exact_across_authorities": len(authority_texts)
        == len(AUTHORITY_PATHS)
        and blocks_are_exact(
            authority_texts, SESSION_APPROVAL_START, SESSION_APPROVAL_END
        ),
        "session_lock_exact_across_authorities": len(authority_texts)
        == len(AUTHORITY_PATHS)
        and blocks_are_exact(
            authority_texts, SESSION_LOCK_START, SESSION_LOCK_END
        ),
        "v2_r1_approval_exact_across_authorities": len(authority_texts)
        == len(AUTHORITY_PATHS)
        and blocks_are_exact(
            authority_texts, V2_R1_APPROVAL_START, V2_R1_APPROVAL_END
        ),
        "v2_r1_lock_exact_across_authorities": len(authority_texts)
        == len(AUTHORITY_PATHS)
        and blocks_are_exact(
            authority_texts, V2_R1_LOCK_START, V2_R1_LOCK_END
        ),
        "v2_r1_final_exact_across_authorities": current_truth
        != V2_R1_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R1_FINAL_START, V2_R1_FINAL_END
            )
        ),
        "v2_r1_final_evidence_commits_exact": current_truth
        != V2_R1_FINAL_STATE
        or (
            len(v2_r1_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r1_final_blocks)
            and all(
                all(commit in block for commit in V2_R1_FINAL_EVIDENCE_COMMITS)
                for block in v2_r1_final_blocks
                if block is not None
            )
        ),
        "v2_r2_approval_exact_across_authorities": current_truth
        not in (
            V2_R2_APPROVAL_STATE,
            V2_R2_DELIVERY_STATE,
            V2_R2_VALIDATED_STATE,
            V2_R2_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R2_APPROVAL_START, V2_R2_APPROVAL_END
            )
        ),
        "v2_r2_lock_exact_across_authorities": current_truth
        not in (
            V2_R2_DELIVERY_STATE,
            V2_R2_VALIDATED_STATE,
            V2_R2_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R2_LOCK_START, V2_R2_LOCK_END
            )
        ),
        "v2_r2_final_exact_across_authorities": current_truth
        != V2_R2_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R2_FINAL_START, V2_R2_FINAL_END
            )
        ),
        "v2_r2_final_evidence_commits_exact": current_truth
        != V2_R2_FINAL_STATE
        or (
            len(v2_r2_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r2_final_blocks)
            and all(
                all(commit in block for commit in V2_R2_FINAL_EVIDENCE_COMMITS)
                for block in v2_r2_final_blocks
                if block is not None
            )
        ),
        "v2_r3_approval_exact_across_authorities": current_truth
        not in (
            V2_R3_APPROVAL_STATE,
            V2_R3_DELIVERY_STATE,
            V2_R3_VALIDATED_STATE,
            V2_R3_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R3_APPROVAL_START, V2_R3_APPROVAL_END
            )
        ),
        "v2_r3_lock_exact_across_authorities": current_truth
        not in (
            V2_R3_DELIVERY_STATE,
            V2_R3_VALIDATED_STATE,
            V2_R3_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R3_LOCK_START, V2_R3_LOCK_END
            )
        ),
        "v2_r3_final_exact_across_authorities": current_truth
        != V2_R3_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R3_FINAL_START, V2_R3_FINAL_END
            )
        ),
        "v2_r3_final_evidence_commits_exact": current_truth
        != V2_R3_FINAL_STATE
        or (
            len(v2_r3_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r3_final_blocks)
            and all(
                all(commit in block for commit in V2_R3_FINAL_EVIDENCE_COMMITS)
                for block in v2_r3_final_blocks
                if block is not None
            )
        ),
        "v2_r4_approval_exact_across_authorities": current_truth
        not in (
            V2_R4_APPROVAL_STATE,
            V2_R4_DELIVERY_STATE,
            V2_R4_VALIDATED_STATE,
            V2_R4_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R4_APPROVAL_START, V2_R4_APPROVAL_END
            )
        ),
        "v2_r4_lock_exact_across_authorities": current_truth
        not in (
            V2_R4_DELIVERY_STATE,
            V2_R4_VALIDATED_STATE,
            V2_R4_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R4_LOCK_START, V2_R4_LOCK_END
            )
        ),
        "v2_r4_final_exact_across_authorities": current_truth
        != V2_R4_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R4_FINAL_START, V2_R4_FINAL_END
            )
        ),
        "v2_r4_final_evidence_commits_exact": current_truth
        != V2_R4_FINAL_STATE
        or (
            len(v2_r4_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r4_final_blocks)
            and all(
                all(commit in block for commit in V2_R4_FINAL_EVIDENCE_COMMITS)
                for block in v2_r4_final_blocks
                if block is not None
            )
        ),
        "v2_r5_approval_exact_across_authorities": current_truth
        not in (
            V2_R5_APPROVAL_STATE,
            V2_R5_DELIVERY_STATE,
            V2_R5_VALIDATED_STATE,
            V2_R5_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R5_APPROVAL_START, V2_R5_APPROVAL_END
            )
        ),
        "v2_r5_lock_exact_across_authorities": current_truth
        not in (V2_R5_DELIVERY_STATE, V2_R5_VALIDATED_STATE, V2_R5_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R5_LOCK_START, V2_R5_LOCK_END
            )
        ),
        "v2_r5_final_exact_across_authorities": current_truth
        != V2_R5_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R5_FINAL_START, V2_R5_FINAL_END
            )
        ),
        "v2_r5_final_evidence_commits_exact": current_truth
        != V2_R5_FINAL_STATE
        or (
            len(v2_r5_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r5_final_blocks)
            and all(
                all(commit in block for commit in V2_R5_FINAL_EVIDENCE_COMMITS)
                for block in v2_r5_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r4_complete": (
            "- V2-R4: Intraday Anomaly Radar; COMPLETED /" in architecture
        ),
        "canonical_roadmap_records_v2_r5_approval": current_truth
        not in (
            V2_R5_APPROVAL_STATE,
            V2_R5_DELIVERY_STATE,
            V2_R5_VALIDATED_STATE,
        )
        or (
            "- V2-R5: Realtime Cognitive Shield; APPROVED / NOT_STARTED /"
            in architecture
        ),
        "canonical_roadmap_records_v2_r5_complete": current_truth
        != V2_R5_FINAL_STATE
        or (
            "- V2-R5: Realtime Cognitive Shield; COMPLETED /" in architecture
        ),
        "v2_r6_approval_exact_across_authorities": current_truth
        not in (
            V2_R6_APPROVAL_STATE,
            V2_R6_DELIVERY_STATE,
            V2_R6_VALIDATED_STATE,
            V2_R6_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R6_APPROVAL_START, V2_R6_APPROVAL_END
            )
        ),
        "v2_r6_lock_exact_across_authorities": current_truth
        not in (V2_R6_DELIVERY_STATE, V2_R6_VALIDATED_STATE, V2_R6_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R6_LOCK_START, V2_R6_LOCK_END
            )
        ),
        "v2_r6_final_exact_across_authorities": current_truth
        != V2_R6_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R6_FINAL_START, V2_R6_FINAL_END
            )
        ),
        "v2_r6_final_evidence_commits_exact": current_truth
        != V2_R6_FINAL_STATE
        or (
            len(v2_r6_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r6_final_blocks)
            and all(
                all(commit in block for commit in V2_R6_FINAL_EVIDENCE_COMMITS)
                for block in v2_r6_final_blocks
                if block is not None
            )
        ),
        "v2_r7_approval_exact_across_authorities": current_truth
        not in (
            V2_R7_APPROVAL_STATE,
            V2_R7_DELIVERY_STATE,
            V2_R7_VALIDATED_STATE,
            V2_R7_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R7_APPROVAL_START, V2_R7_APPROVAL_END
            )
        ),
        "v2_r7_lock_exact_across_authorities": current_truth
        not in (V2_R7_DELIVERY_STATE, V2_R7_VALIDATED_STATE, V2_R7_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R7_LOCK_START, V2_R7_LOCK_END
            )
        ),
        "v2_r7_final_exact_across_authorities": current_truth
        != V2_R7_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R7_FINAL_START, V2_R7_FINAL_END
            )
        ),
        "v2_r7_final_evidence_commits_exact": current_truth
        != V2_R7_FINAL_STATE
        or (
            len(v2_r7_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r7_final_blocks)
            and all(
                all(commit in block for commit in V2_R7_FINAL_EVIDENCE_COMMITS)
                for block in v2_r7_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r7_complete": current_truth
        != V2_R7_FINAL_STATE
        or (
            "- V2-R7: Local Market Session Registry Foundation; COMPLETED /"
            in architecture
        ),
        "v2_r8_approval_exact_across_authorities": current_truth
        not in (
            V2_R8_APPROVAL_STATE,
            V2_R8_DELIVERY_STATE,
            V2_R8_VALIDATED_STATE,
            V2_R8_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R8_APPROVAL_START, V2_R8_APPROVAL_END
            )
        ),
        "v2_r8_lock_exact_across_authorities": current_truth
        not in (V2_R8_DELIVERY_STATE, V2_R8_VALIDATED_STATE, V2_R8_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R8_LOCK_START, V2_R8_LOCK_END
            )
        ),
        "v2_r8_final_exact_across_authorities": current_truth
        != V2_R8_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R8_FINAL_START, V2_R8_FINAL_END
            )
        ),
        "v2_r8_final_evidence_commits_exact": current_truth
        != V2_R8_FINAL_STATE
        or (
            len(v2_r8_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r8_final_blocks)
            and all(
                all(commit in block for commit in V2_R8_FINAL_EVIDENCE_COMMITS)
                for block in v2_r8_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r8_complete": current_truth
        != V2_R8_FINAL_STATE
        or (
            "- V2-R8: Local Same-Time Baseline Foundation; COMPLETED /"
            in architecture
        ),
        "v2_r9_approval_exact_across_authorities": current_truth
        not in (
            V2_R9_APPROVAL_STATE,
            V2_R9_DELIVERY_STATE,
            V2_R9_VALIDATED_STATE,
            V2_R9_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R9_APPROVAL_START, V2_R9_APPROVAL_END
            )
        ),
        "v2_r9_lock_exact_across_authorities": current_truth
        not in (V2_R9_DELIVERY_STATE, V2_R9_VALIDATED_STATE, V2_R9_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R9_LOCK_START, V2_R9_LOCK_END
            )
        ),
        "v2_r9_final_exact_across_authorities": current_truth
        != V2_R9_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R9_FINAL_START, V2_R9_FINAL_END
            )
        ),
        "v2_r9_final_evidence_commits_exact": current_truth
        != V2_R9_FINAL_STATE
        or (
            len(v2_r9_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r9_final_blocks)
            and all(
                all(commit in block for commit in V2_R9_FINAL_EVIDENCE_COMMITS)
                for block in v2_r9_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r9_complete": current_truth
        != V2_R9_FINAL_STATE
        or (
            "- V2-R9: Local Volume-Ratio Research Foundation; COMPLETED /"
            in architecture
        ),
        "v2_r10_approval_exact_across_authorities": current_truth
        not in (V2_R10_APPROVAL_STATE, V2_R10_DELIVERY_STATE, V2_R10_VALIDATED_STATE, V2_R10_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R10_APPROVAL_START, V2_R10_APPROVAL_END
            )
        ),
        "v2_r10_lock_exact_across_authorities": current_truth
        not in (V2_R10_DELIVERY_STATE, V2_R10_VALIDATED_STATE, V2_R10_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(authority_texts, V2_R10_LOCK_START, V2_R10_LOCK_END)
        ),
        "v2_r10_final_exact_across_authorities": current_truth
        != V2_R10_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R10_FINAL_START, V2_R10_FINAL_END
            )
        ),
        "v2_r10_final_evidence_commits_exact": current_truth
        != V2_R10_FINAL_STATE
        or (
            len(v2_r10_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r10_final_blocks)
            and all(
                all(commit in block for commit in V2_R10_FINAL_EVIDENCE_COMMITS)
                for block in v2_r10_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r10_complete": current_truth
        != V2_R10_FINAL_STATE
        or (
            "- V2-R10: Local Turnover-Definition Research Foundation; COMPLETED /"
            in architecture
        ),
        "v2_r11_approval_exact_across_authorities": current_truth
        not in (V2_R11_APPROVAL_STATE, V2_R11_DELIVERY_STATE, V2_R11_VALIDATED_STATE, V2_R11_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R11_APPROVAL_START, V2_R11_APPROVAL_END
            )
        ),
        "v2_r11_lock_exact_across_authorities": current_truth
        not in (V2_R11_DELIVERY_STATE, V2_R11_VALIDATED_STATE, V2_R11_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(authority_texts, V2_R11_LOCK_START, V2_R11_LOCK_END)
        ),
        "v2_r11_final_exact_across_authorities": current_truth
        != V2_R11_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R11_FINAL_START, V2_R11_FINAL_END
            )
        ),
        "v2_r11_final_evidence_commits_exact": current_truth
        != V2_R11_FINAL_STATE
        or (
            len(v2_r11_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r11_final_blocks)
            and all(
                all(commit in block for commit in V2_R11_FINAL_EVIDENCE_COMMITS)
                for block in v2_r11_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r11_complete": current_truth
        != V2_R11_FINAL_STATE
        or (
            "- V2-R11: Local Factor Registry Foundation; COMPLETED /"
            in architecture
        ),
        "v2_r12_approval_exact_across_authorities": current_truth
        not in (V2_R12_APPROVAL_STATE, V2_R12_DELIVERY_STATE, V2_R12_VALIDATED_STATE, V2_R12_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R12_APPROVAL_START, V2_R12_APPROVAL_END
            )
        ),
        "v2_r12_lock_exact_across_authorities": current_truth
        not in (V2_R12_DELIVERY_STATE, V2_R12_VALIDATED_STATE, V2_R12_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(authority_texts, V2_R12_LOCK_START, V2_R12_LOCK_END)
        ),
        "v2_r12_final_exact_across_authorities": current_truth
        != V2_R12_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R12_FINAL_START, V2_R12_FINAL_END
            )
        ),
        "v2_r12_final_evidence_commits_exact": current_truth
        != V2_R12_FINAL_STATE
        or (
            bool(V2_R12_FINAL_EVIDENCE_COMMITS)
            and len(v2_r12_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r12_final_blocks)
            and all(
                all(
                    commit in block
                    for commit in V2_R12_FINAL_EVIDENCE_COMMITS
                )
                for block in v2_r12_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r12_complete": current_truth
        != V2_R12_FINAL_STATE
        or (
            "- V2-R12: Local Technical Indicator Foundation; COMPLETED /"
            in architecture
        ),
        "v2_r13_approval_exact_across_authorities": current_truth
        not in (
            V2_R13_APPROVAL_STATE,
            V2_R13_DELIVERY_STATE,
            V2_R13_VALIDATED_STATE,
            V2_R13_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R13_APPROVAL_START, V2_R13_APPROVAL_END
            )
        ),
        "v2_r13_lock_exact_across_authorities": current_truth
        not in (V2_R13_DELIVERY_STATE, V2_R13_VALIDATED_STATE, V2_R13_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(authority_texts, V2_R13_LOCK_START, V2_R13_LOCK_END)
        ),
        "v2_r13_final_exact_across_authorities": current_truth
        != V2_R13_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R13_FINAL_START, V2_R13_FINAL_END
            )
        ),
        "v2_r13_final_evidence_commits_exact": current_truth
        != V2_R13_FINAL_STATE
        or (
            bool(V2_R13_FINAL_EVIDENCE_COMMITS)
            and len(v2_r13_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r13_final_blocks)
            and all(
                all(
                    commit in block
                    for commit in V2_R13_FINAL_EVIDENCE_COMMITS
                )
                for block in v2_r13_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r13_complete": current_truth
        != V2_R13_FINAL_STATE
        or (
            "- V2-R13: Local Momentum Indicator Foundation; COMPLETED /"
            in architecture
        ),
        "v2_r14_approval_exact_across_authorities": current_truth
        not in (
            V2_R14_APPROVAL_STATE,
            V2_R14_DELIVERY_STATE,
            V2_R14_VALIDATED_STATE,
            V2_R14_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R14_APPROVAL_START, V2_R14_APPROVAL_END
            )
        ),
        "v2_r14_lock_exact_across_authorities": current_truth
        not in (V2_R14_DELIVERY_STATE, V2_R14_VALIDATED_STATE, V2_R14_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(authority_texts, V2_R14_LOCK_START, V2_R14_LOCK_END)
        ),
        "v2_r14_final_exact_across_authorities": current_truth
        != V2_R14_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R14_FINAL_START, V2_R14_FINAL_END
            )
        ),
        "v2_r14_final_evidence_commits_exact": current_truth
        != V2_R14_FINAL_STATE
        or (
            bool(V2_R14_FINAL_EVIDENCE_COMMITS)
            and len(v2_r14_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r14_final_blocks)
            and all(
                all(commit in block for commit in V2_R14_FINAL_EVIDENCE_COMMITS)
                for block in v2_r14_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r14_complete": current_truth
        != V2_R14_FINAL_STATE
        or (
            "- V2-R14: Local Trend Indicator Foundation; COMPLETED /"
            in architecture
        ),
        "v2_r15_approval_exact_across_authorities": current_truth
        not in (
            V2_R15_APPROVAL_STATE,
            V2_R15_DELIVERY_STATE,
            V2_R15_VALIDATED_STATE,
            V2_R15_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R15_APPROVAL_START, V2_R15_APPROVAL_END
            )
        ),
        "v2_r15_lock_exact_across_authorities": current_truth
        not in (V2_R15_DELIVERY_STATE, V2_R15_VALIDATED_STATE, V2_R15_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(authority_texts, V2_R15_LOCK_START, V2_R15_LOCK_END)
        ),
        "v2_r15_final_exact_across_authorities": current_truth
        != V2_R15_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R15_FINAL_START, V2_R15_FINAL_END
            )
        ),
        "v2_r15_final_evidence_commits_exact": current_truth
        != V2_R15_FINAL_STATE
        or (
            bool(V2_R15_FINAL_EVIDENCE_COMMITS)
            and len(v2_r15_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r15_final_blocks)
            and all(
                all(commit in block for commit in V2_R15_FINAL_EVIDENCE_COMMITS)
                for block in v2_r15_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r15_complete": current_truth
        != V2_R15_FINAL_STATE
        or (
            "- V2-R15: Local Volatility Indicator Foundation; COMPLETED /"
            in architecture
        ),
        "v2_r16_approval_exact_across_authorities": current_truth
        not in (
            V2_R16_APPROVAL_STATE,
            V2_R16_DELIVERY_STATE,
            V2_R16_VALIDATED_STATE,
            V2_R16_FINAL_STATE,
        )
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R16_APPROVAL_START, V2_R16_APPROVAL_END
            )
        ),
        "v2_r16_lock_exact_across_authorities": current_truth
        not in (V2_R16_DELIVERY_STATE, V2_R16_VALIDATED_STATE, V2_R16_FINAL_STATE)
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(authority_texts, V2_R16_LOCK_START, V2_R16_LOCK_END)
        ),
        "v2_r16_final_exact_across_authorities": current_truth
        != V2_R16_FINAL_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, V2_R16_FINAL_START, V2_R16_FINAL_END
            )
        ),
        "v2_r16_final_evidence_commits_exact": current_truth
        != V2_R16_FINAL_STATE
        or (
            bool(V2_R16_FINAL_EVIDENCE_COMMITS)
            and len(v2_r16_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in v2_r16_final_blocks)
            and all(
                all(commit in block for commit in V2_R16_FINAL_EVIDENCE_COMMITS)
                for block in v2_r16_final_blocks
                if block is not None
            )
        ),
        "canonical_roadmap_records_v2_r16_complete": current_truth
        != V2_R16_FINAL_STATE
        or (
            "- V2-R16: Local Range Channel Indicator Foundation; COMPLETED /"
            in architecture
        ),
        "canonical_roadmap_records_v2_r6_approval": current_truth
        not in (
            V2_R6_APPROVAL_STATE,
            V2_R6_DELIVERY_STATE,
            V2_R6_VALIDATED_STATE,
        )
        or (
            "- V2-R6: Paper Simulation Research; APPROVED / NOT_STARTED /"
            in architecture
        ),
        "canonical_roadmap_records_v2_r6_complete": current_truth
        != V2_R6_FINAL_STATE
        or (
            "- V2-R6: Paper Simulation Research; COMPLETED /" in architecture
        ),
        "session_final_sync_exact_across_authorities": current_truth
        == DELIVERY_STATE
        or (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and blocks_are_exact(
                authority_texts, SESSION_FINAL_START, SESSION_FINAL_END
            )
        ),
        "session_final_evidence_commits_exact": current_truth
        == DELIVERY_STATE
        or (
            bool(SESSION_FINAL_EVIDENCE_COMMITS)
            and len(session_final_blocks) == len(AUTHORITY_PATHS)
            and all(block is not None for block in session_final_blocks)
            and all(
                all(
                    commit in block
                    for commit in SESSION_FINAL_EVIDENCE_COMMITS
                )
                for block in session_final_blocks
                if block is not None
            )
        ),
        "v2_blocks_exact_across_authorities": len(authority_texts)
        == len(AUTHORITY_PATHS)
        and all(
            blocks_are_exact(authority_texts, start, end)
            for start, end in V2_BLOCKS
        ),
        "protocol_requires_repository_rehydration": (
            "No implementation may start from chat recollection alone."
            in protocol
            and "Only the manifest plus explicit Operator approval"
            in protocol
            and "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json" in protocol
        ),
        "no_v2_phase_overclaim": all(
            f"{phase}: COMPLETED" not in architecture
            for phase in ROADMAP_PHASES
            if phase not in ("V2-R1", "V2-R2")
            or current_truth
            not in (
                V2_R1_FINAL_STATE,
                V2_R2_APPROVAL_STATE,
                V2_R2_DELIVERY_STATE,
                V2_R2_VALIDATED_STATE,
                V2_R2_FINAL_STATE,
                V2_R3_APPROVAL_STATE,
                V2_R3_DELIVERY_STATE,
                V2_R3_VALIDATED_STATE,
                V2_R3_FINAL_STATE,
                V2_R4_APPROVAL_STATE,
                V2_R4_DELIVERY_STATE,
                V2_R4_VALIDATED_STATE,
                V2_R4_FINAL_STATE,
                V2_R5_APPROVAL_STATE,
                V2_R5_DELIVERY_STATE,
                V2_R5_VALIDATED_STATE,
                V2_R5_FINAL_STATE,
                V2_R6_APPROVAL_STATE,
                V2_R6_DELIVERY_STATE,
                V2_R6_VALIDATED_STATE,
                V2_R6_FINAL_STATE,
            )
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_project_memory_guard_report()
    if report["ok"] is not True:
        raise SystemExit("project memory continuity guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
