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
ROADMAP_PHASES = tuple(f"V2-R{index}" for index in range(1, 7))
ROADMAP_STATUS = "PLANNED_NOT_APPROVED_NOT_STARTED"
GAP_IDS = tuple(f"V2-FR-GAP-{index:03d}" for index in range(1, 71))
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
            else expected_roadmap
        ),
        "future_status_vocabulary_exact": statuses == list(FUTURE_STATUSES),
        "gap_statuses_closed": gap_statuses_are_valid(gap),
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
