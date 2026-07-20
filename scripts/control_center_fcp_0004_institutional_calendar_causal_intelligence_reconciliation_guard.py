from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
APPROVAL_START = "<!-- FCP 0004 INSTITUTIONAL CALENDAR CAUSAL INTELLIGENCE RECONCILIATION APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0004 INSTITUTIONAL CALENDAR CAUSAL INTELLIGENCE RECONCILIATION APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0004 INSTITUTIONAL CALENDAR CAUSAL INTELLIGENCE RECONCILIATION APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0004 INSTITUTIONAL CALENDAR CAUSAL INTELLIGENCE RECONCILIATION APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0004 INSTITUTIONAL CALENDAR CAUSAL INTELLIGENCE RECONCILIATION APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0004 INSTITUTIONAL CALENDAR CAUSAL INTELLIGENCE RECONCILIATION APP 1 FINAL END -->"
APP_ROOT = Path(
    "apps/fcp_0004_institutional_calendar_causal_intelligence_reconciliation_app_1"
)
APP_FILES = (
    "__init__.py",
    "boundary.py",
    "contracts.py",
    "presentation.py",
    "reconciliation.py",
)
REQUIRED = (
    *(APP_ROOT / name for name in APP_FILES),
    Path(
        "docs/FCF_FCP_0004_INSTITUTIONAL_CALENDAR_CAUSAL_INTELLIGENCE_RECONCILIATION_APP_1_D1_D6.md"
    ),
    Path(
        "FCF_CURRENT_STATE_FCP_0004_INSTITUTIONAL_CALENDAR_CAUSAL_INTELLIGENCE_RECONCILIATION_APP_1_APPROVED.md"
    ),
    Path(
        "FCF_CURRENT_STATE_FCP_0004_INSTITUTIONAL_CALENDAR_CAUSAL_INTELLIGENCE_RECONCILIATION_APP_1_DELIVERED.md"
    ),
    Path(
        "FCF_CURRENT_STATE_FCP_0004_INSTITUTIONAL_CALENDAR_CAUSAL_INTELLIGENCE_RECONCILIATION_APP_1_FINAL.md"
    ),
)
FINAL_EVIDENCE_COMMITS = (
    "c57ca9370e235fb1f3453af24ca73b990ea7967b",
    "c483264a52af15417b454733a850e84cec8bd5fa",
    "8ffbaebd607f7ebd6729a8a7daf5244c5c6cd583",
)
EXPECTED_EVIDENCE_REFS = [
    "FCF_CURRENT_STATE_FCP_0004_INSTITUTIONAL_CALENDAR_CAUSAL_INTELLIGENCE_RECONCILIATION_APP_1_FINAL.md",
    "docs/FCF_FCP_0004_INSTITUTIONAL_CALENDAR_CAUSAL_INTELLIGENCE_RECONCILIATION_APP_1_D1_D6.md",
]
STAGE_ROWS = (
    (23, "local_institutional_calendar_evidence", "control_center_v2_r23_local_institutional_calendar_evidence_guard.py"),
    (24, "local_multi_clock_event_state", "control_center_v2_r24_local_multi_clock_event_state_guard.py"),
    (25, "local_causal_transmission_graph", "control_center_v2_r25_local_causal_transmission_graph_guard.py"),
    (26, "local_consensus_expectation_gap", "control_center_v2_r26_local_consensus_expectation_gap_guard.py"),
    (27, "local_event_reaction_quality", "control_center_v2_r27_local_event_reaction_quality_guard.py"),
    (28, "local_a_share_earnings_lifecycle_accounting_quality", "control_center_v2_r28_local_a_share_earnings_accounting_quality_guard.py"),
    (29, "local_index_futures_basis_roll_expiry", "control_center_v2_r29_local_index_futures_basis_roll_expiry_guard.py"),
    (30, "local_equity_supply_pressure", "control_center_v2_r30_local_equity_supply_pressure_guard.py"),
    (31, "local_fx_transmission_sensitivity", "control_center_v2_r31_local_fx_transmission_sensitivity_guard.py"),
    (32, "local_institutional_crowding", "control_center_v2_r32_local_institutional_crowding_guard.py"),
    (33, "local_holiday_liquidity_state", "control_center_v2_r33_local_holiday_liquidity_state_guard.py"),
    (34, "local_policy_window_language_evidence", "control_center_v2_r34_local_policy_window_language_evidence_guard.py"),
    (35, "local_evidence_integrity", "control_center_v2_r35_local_evidence_integrity_guard.py"),
    (36, "local_institutional_factor_lifecycle", "control_center_v2_r36_local_institutional_factor_lifecycle_guard.py"),
    (37, "local_factor_validation_evidence", "control_center_v2_r37_local_factor_validation_evidence_guard.py"),
)
GAP_STATUSES = {
    "V2-FR-GAP-071": "NOT_IMPLEMENTED",
    "V2-FR-GAP-072": "NOT_IMPLEMENTED",
    "V2-FR-GAP-073": "NOT_IMPLEMENTED",
    "V2-FR-GAP-074": "RESEARCH_REQUIRED",
    "V2-FR-GAP-075": "RESEARCH_REQUIRED",
    "V2-FR-GAP-076": "NOT_IMPLEMENTED",
    "V2-FR-GAP-077": "RESEARCH_REQUIRED",
    "V2-FR-GAP-078": "RESEARCH_REQUIRED",
    "V2-FR-GAP-079": "RESEARCH_REQUIRED",
    "V2-FR-GAP-080": "RESEARCH_REQUIRED",
    "V2-FR-GAP-081": "RESEARCH_REQUIRED",
    "V2-FR-GAP-082": "NOT_IMPLEMENTED",
    "V2-FR-GAP-083": "RESEARCH_REQUIRED",
    "V2-FR-GAP-084": "NOT_IMPLEMENTED",
    "V2-FR-GAP-085": "NOT_IMPLEMENTED",
    "V2-FR-GAP-086": "RESEARCH_REQUIRED",
}
CANDIDATE_IDS = (
    "CAPITAL_TRANSMISSION_PRESSURE",
    "EARNINGS_SURPRISE",
    "EQUITY_SUPPLY_PRESSURE",
    "EVENT_REACTION_QUALITY",
    "EXPIRY_BASIS_ROLL_STRESS",
    "FX_TRANSMISSION_SENSITIVITY",
    "HOLIDAY_LIQUIDITY_STRESS",
    "INSTITUTIONAL_CROWDING",
    "POLICY_NOVELTY_ALIGNMENT",
    "WINDOW_DRESSING_PRESSURE",
)


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def _delivery_paths() -> tuple[Path, ...]:
    paths = []
    for stage, name, guard_name in STAGE_ROWS:
        app_id = f"v2_r{stage}_{name}_foundation_app_1"
        paths.extend(
            (
                Path("apps") / app_id,
                Path(
                    f"FCF_CURRENT_STATE_V2_R{stage}_{name.upper()}_FOUNDATION_APP_1_FINAL.md"
                ),
                Path("scripts") / guard_name,
                Path("tests") / app_id / f"test_v2_r{stage}_d1_d6.py",
            )
        )
    return tuple(paths)


def _gap_statuses(backlog: str) -> dict[str, str]:
    return {
        match.group(1): match.group(2)
        for match in re.finditer(
            r"^\| (V2-FR-GAP-(?:07[1-9]|08[0-6])) \|.*\| ([A-Z_]+) \|$",
            backlog,
            re.MULTILINE,
        )
    }


def build_fcp_0004_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        approval = (
            root
            / "FCF_CURRENT_STATE_FCP_0004_INSTITUTIONAL_CALENDAR_CAUSAL_INTELLIGENCE_RECONCILIATION_APP_1_APPROVED.md"
        ).read_text(encoding="ascii")
        delivered = (
            root
            / "FCF_CURRENT_STATE_FCP_0004_INSTITUTIONAL_CALENDAR_CAUSAL_INTELLIGENCE_RECONCILIATION_APP_1_DELIVERED.md"
        ).read_text(encoding="ascii")
        final_document = (
            root
            / "FCF_CURRENT_STATE_FCP_0004_INSTITUTIONAL_CALENDAR_CAUSAL_INTELLIGENCE_RECONCILIATION_APP_1_FINAL.md"
        ).read_text(encoding="ascii")
        intake = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        backlog = (
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
        ).read_text(encoding="ascii")
        adr = (
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md"
        ).read_text(encoding="ascii")
        app_text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES
        )
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, approval, delivered, final_document, intake, manifest = (
            (),
            "",
            "",
            "",
            {},
            {},
        )
        backlog, adr, app_text, run_all, readable = "", "", "", "", False
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0004"
        ),
        {},
    )
    truth = manifest.get("current_truth", {})
    safety = manifest.get("safety_boundaries", {})
    delivery_paths = _delivery_paths()
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5
        and all(approvals)
        and len(set(approvals)) == 1,
        "approval_document_safe": (
            "APPROVED_GOVERNANCE_RECONCILIATION_ONLY_NOT_STARTED" in approval
            and "FCF-FCP-0004 remains ACCEPTED_ARCHITECTURE" in " ".join(approval.split())
        ),
        "delivered_document_complete": (
            "DELIVERY_VALIDATED_READY_FOR_MANUAL_MERGE" in delivered
            and "5421 passed" in delivered
            and "ACCEPTED_ARCHITECTURE" in delivered
        ),
        "lock_exact": len(texts) == 5 and all(locks) and len(set(locks)) == 1,
        "final_exact": len(texts) == 5 and all(finals) and len(set(finals)) == 1,
        "final_document_complete": (
            "COMPLETED_MERGED_VALIDATED" in final_document
            and all(commit in final_document for commit in FINAL_EVIDENCE_COMMITS)
        ),
        "delivery_files_exist": all((root / path).is_file() for path in REQUIRED),
        "historical_delivery_evidence_exists": all(
            (root / path).exists() for path in delivery_paths
        ),
        "historical_stage_surfaces_unique": all(
            len(tuple((root / "apps").glob(f"v2_r{stage}_*"))) == 1
            for stage, _, _ in STAGE_ROWS
        ),
        "app_surface_exact": sorted(
            path.name for path in (root / APP_ROOT).glob("*.py")
        )
        == sorted(APP_FILES),
        "deterministic_reconciliation_present": all(
            term in app_text
            for term in (
                "EXPECTED_OVERLAP_GAP_IDS",
                "DELIVERY_MAPPING_MISMATCH",
                "PRODUCTION_AUTHORITY_OVERCLAIM",
                "READY_FOR_OPERATOR_REVIEW",
            )
        ),
        "no_prohibited_runtime": all(
            term not in app_text.lower()
            for term in (
                "import requests",
                "import socket",
                "import subprocess",
                "urllib.request",
                "websocket",
            )
        ),
        "candidate_inventory_synchronized": all(
            candidate in adr and candidate in app_text for candidate in CANDIDATE_IDS
        ),
        "production_gap_statuses_preserved": _gap_statuses(backlog) == GAP_STATUSES,
        "proposal_accepted_architecture": (
            proposal.get("status") == "ACCEPTED_ARCHITECTURE"
            and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
            and proposal.get("phase_id") == "NONE"
            and proposal.get("gap_refs") == list(GAP_STATUSES)
        ),
        "proposal_evidence_exact": proposal.get("evidence_refs")
        == EXPECTED_EVIDENCE_REFS,
        "no_active_phase": truth.get("current_governance_phase_id") == "NONE"
        and truth.get("current_product_implementation_phase") == "NONE"
        and truth.get("next_product_implementation_phase") == "NOT_SELECTED",
        "p48_forbidden": safety.get("p48_allowed") is False,
        "manifest_records_latest_delivery": truth.get(
            "latest_completed_governance_delivery"
        )
        in {
            "FCF-FCP-0004-INSTITUTIONAL-CALENDAR-CAUSAL-INTELLIGENCE-RECONCILIATION-APP-1",
            "FCF-FCP-0005-MVP-PRODUCT-READINESS-DECISION-GATE-APP-1",
        },
        "guard_wired_into_all_checks": (
            "scripts/control_center_fcp_0004_institutional_calendar_causal_intelligence_reconciliation_guard.py"
            in run_all
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0004_guard_report()
    if not report["ok"]:
        raise SystemExit("FCP-0004 architecture reconciliation guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
