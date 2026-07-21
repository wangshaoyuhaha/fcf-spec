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
INSTITUTIONAL_REGISTRATION_START = (
    "<!-- FCF INSTITUTIONAL CALENDAR CAUSAL MARKET INTELLIGENCE "
    "REGISTRATION START -->"
)
INSTITUTIONAL_REGISTRATION_END = (
    "<!-- FCF INSTITUTIONAL CALENDAR CAUSAL MARKET INTELLIGENCE "
    "REGISTRATION END -->"
)
ADR_IDS = tuple(f"FCF-V2-ADR-{index:03d}" for index in range(1, 46))
GAP_IDS = tuple(f"V2-FR-GAP-{index:03d}" for index in range(1, 110))
ROADMAP_PHASES = tuple(f"V2-R{index}" for index in range(1, 23))
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
    "Institutional Calendar and Causal Market Intelligence Architecture",
    "Five-Clock Regime Context",
    "Three Causal Transmission Chains",
    "Official Event Calendar and Point-in-Time Registry",
    "Multi-Clock Regime Orchestrator and Event State Stack",
    "Expectation Gap and Event Reaction Quality",
    "Earnings Lifecycle and Accounting Quality",
    "Index-Futures Expiry and Derivatives Context",
    "Equity Supply and Forced-Sale Pressure",
    "Policy Windows and Local Institutional Cycles",
    "Rates, FX, and Cross-Market Transmission",
    "Federal Reserve and FOMC decisions",
    "nonfarm payrolls",
    "Institutional Crowding, Rebalance, and Holiday Liquidity",
    "Spring Festival",
    "National Day",
    "June and December",
    "Institutional Factor Lifecycle and Validation Order",
    "Named Institutional Factor Research Candidates",
    "EARNINGS_SURPRISE",
    "EVENT_REACTION_QUALITY",
    "EXPIRY_BASIS_ROLL_STRESS",
    "EQUITY_SUPPLY_PRESSURE",
    "FX_TRANSMISSION_SENSITIVITY",
    "INSTITUTIONAL_CROWDING",
    "WINDOW_DRESSING_PRESSURE",
    "HOLIDAY_LIQUIDITY_STRESS",
    "POLICY_NOVELTY_ALIGNMENT",
    "CAPITAL_TRANSMISSION_PRESSURE",
    "Module Ownership and Research Order",
    "Trusted Data Supply Chain Architecture",
    "Point-in-Time Availability and Revision Law",
    "Corporate Action, Price Adjustment, and Trading Status",
    "Immutable Layered Local Storage",
    "Reconciliation, Quarantine, and Deterministic Routing",
    "Candidate Provider Role Boundaries",
    "A-Share and BTC Source Semantics",
    "Data Cost and Incremental Value Gate",
    "Commercial Research and Profitability Boundary",
    "BTC Perpetual Leverage Paper Research Architecture",
    "partial liquidation, liquidation fee, insurance-fund, ADL",
    "isolated or cross margin and one-way or hedge position-mode semantics",
    "Guojin QMT Registered Local Daily Export Profile",
    "Integral `volumn` lots are multiplied by exactly 100",
    "front-adjusted reference exports may be compared only as additive price",
    "offset evidence. They cannot become the multiplicative adjustment-factor",
    "Guojin QMT Registered Batch Coverage Reconciliation",
    "exact registered trading-date",
    "overlaps are removed from the merged output",
)


def _read_ascii(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="ascii")


def _extract_single_block(text: str, start: str, end: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len(end)
    return text[start_index:end_index]


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
    institutional_blocks = tuple(
        _extract_single_block(
            text,
            INSTITUTIONAL_REGISTRATION_START,
            INSTITUTIONAL_REGISTRATION_END,
        )
        for text in authority_texts.values()
    )
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
        "institutional_registration_synchronized": (
            len(institutional_blocks) == len(AUTHORITY_PATHS)
            and all(institutional_blocks)
            and len(set(institutional_blocks)) == 1
            and "FCF-FCP-0004" in institutional_blocks[0]
            and "FCF-V2-INSTITUTIONAL-CALENDAR-CAUSAL-MARKET-INTELLIGENCE"
            in institutional_blocks[0]
            and "Named research candidates, all NOT_ACTIVATED:"
            in institutional_blocks[0]
            and "Next product phase remains NOT_SELECTED / NOT_APPROVED."
            in institutional_blocks[0]
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
