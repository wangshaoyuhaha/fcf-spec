from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_PATH = Path(
    "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
)
ADR_PATH = Path("docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md")
GAP_PATH = Path("docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md")
MANIFEST_PATH = Path("FCF_CURRENT_STATE_MANIFEST.json")
AUTHORITY_PATHS = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
LOCK_MARKER = "FCF V2 FACTOR REALTIME COGNITIVE ARCHITECTURE LOCK"
ADR_IDS = tuple(f"FCF-V2-ADR-{index:03d}" for index in range(1, 21))
GAP_IDS = tuple(f"V2-FR-GAP-{index:03d}" for index in range(1, 71))
ROADMAP_PHASES = tuple(f"V2-R{index}" for index in range(1, 17))
REQUIRED_ARCHITECTURE_TERMS = (
    "Deterministic Factor Registry",
    "Forecast Target and Outcome Label Contract",
    "State-Sync Lock",
    "Macro-to-Micro Transmission Contract",
    "Research-Horizon Isolation",
    "Bollinger",
    "MA5",
    "VWAP",
    "Capital-Flow Research Contract",
    "CVD",
    "Order-Book and Microstructure Research Contract",
    "Realtime Event Semantics",
    "Uncertainty, Calibration, and Abstention",
    "Implementation Readiness Gate",
    "Single-Market MVP Gate",
    "MVP Success and Stop Rules",
    "Market Session Registry and Exchange Calendar",
    "Same-Time-of-Day and Regime Baselines",
    "A-Share Call-Auction Research Contract",
    "Late-Session and Closing Research Contract",
    "Entrusted Order, Volume Ratio, Turnover, and Flow Semantics",
    "Sector, Theme, and Cross-Market Transmission Graph",
    "Controlled Research Candidate Lifecycle",
    "Read-Only Operator Research Control Plane",
    "Controlled Offline Adaptation and Learning Boundary",
    "Session-Aware Evaluation and Failure Law",
)


def _read_ascii(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="ascii")


def build_architecture_guard_report(root: Path = ROOT) -> dict[str, object]:
    canonical_paths = (ARCHITECTURE_PATH, ADR_PATH, GAP_PATH)
    canonical_exists = all((root / path).is_file() for path in canonical_paths)
    try:
        architecture = _read_ascii(root, ARCHITECTURE_PATH)
        adr_register = _read_ascii(root, ADR_PATH)
        gap_register = _read_ascii(root, GAP_PATH)
        manifest = json.loads(_read_ascii(root, MANIFEST_PATH))
        authority_texts = {
            path.as_posix(): _read_ascii(root, path) for path in AUTHORITY_PATHS
        }
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        architecture = ""
        adr_register = ""
        gap_register = ""
        authority_texts = {}
        manifest = {}
        ascii_only = False

    found_gap_ids = set(re.findall(r"V2-FR-GAP-[0-9]{3}", gap_register))
    manifest_roadmap = {
        item.get("phase_id"): item.get("status")
        for item in manifest.get("roadmap", [])
        if isinstance(item, dict)
    }
    checks = {
        "canonical_documents_exist": canonical_exists,
        "canonical_documents_ascii": ascii_only,
        "architecture_status_safe": (
            "Status: ACCEPTED_ARCHITECTURE" in architecture
            and "Implementation status: NOT_IMPLEMENTED" in architecture
        ),
        "required_architecture_terms_present": all(
            term in architecture for term in REQUIRED_ARCHITECTURE_TERMS
        ),
        "adr_register_exact": all(
            adr_register.count(adr_id) == 1 for adr_id in ADR_IDS
        ),
        "gap_register_exact": found_gap_ids == set(GAP_IDS),
        "roadmap_complete": all(
            phase in architecture and phase in gap_register
            for phase in ROADMAP_PHASES
        ),
        "future_status_not_overclaimed": all(
            (
                manifest_roadmap.get(phase) == "COMPLETED"
            )
            == bool(
                re.search(
                    rf"- {re.escape(phase)}:[^\n]*; COMPLETED",
                    architecture,
                )
            )
            == bool(
                re.search(
                    rf"\| {re.escape(phase)} \|[^\n]*COMPLETED",
                    gap_register,
                )
            )
            for phase in ROADMAP_PHASES
        )
        and "Implementation status: NOT_IMPLEMENTED" in architecture,
        "readiness_gate_present": (
            "No future product Sidecar branch may start" in architecture
        ),
        "real_execution_excluded": (
            "Real Execution Mode: OUTSIDE FCF AND PROHIBITED" in architecture
            and "No entry authorizes" in gap_register
        ),
        "authority_sources_synchronized": len(authority_texts)
        == len(AUTHORITY_PATHS)
        and all(
            LOCK_MARKER in text
            and ARCHITECTURE_PATH.as_posix() in text
            and ADR_PATH.as_posix() in text
            and GAP_PATH.as_posix() in text
            and "V2-R1 through V2-R6: PLANNED / NOT_APPROVED / NOT_STARTED"
            in text
            for text in authority_texts.values()
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_architecture_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2 factor realtime architecture guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
