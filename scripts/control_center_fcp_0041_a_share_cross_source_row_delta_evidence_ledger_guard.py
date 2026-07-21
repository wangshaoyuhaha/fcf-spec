from __future__ import annotations

import json
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ID = "FCF-FCP-0041-A-SHARE-CROSS-SOURCE-ROW-DELTA-EVIDENCE-LEDGER-APP-1"
AUTHORITIES = tuple(
    Path(value)
    for value in (
        "docs/FCF_PROJECT_CONTROL_CENTER.md",
        "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
        "docs/HANDOFF_PROMPT.md",
        "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
        "FCF_NEW_WINDOW_CHAT_PROMPT.md",
    )
)
MARKER = "FCP 0041 A SHARE CROSS SOURCE ROW DELTA EVIDENCE LEDGER APP 1"
APPROVAL_START, APPROVAL_END = (
    f"<!-- {MARKER} APPROVAL START -->",
    f"<!-- {MARKER} APPROVAL END -->",
)
LOCK_START, LOCK_END = (
    f"<!-- {MARKER} LOCK START -->",
    f"<!-- {MARKER} LOCK END -->",
)
FINAL_START, FINAL_END = (
    f"<!-- {MARKER} FINAL START -->",
    f"<!-- {MARKER} FINAL END -->",
)


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0041_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        intake = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        architecture = (
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
        ).read_text(encoding="ascii")
        adr = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md").read_text(
            encoding="ascii"
        )
        gaps = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md").read_text(
            encoding="ascii"
        )
        protocol = (root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md").read_text(
            encoding="ascii"
        )
        memory = (root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md").read_text(
            encoding="ascii"
        )
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, manifest, intake = (), {}, {}
        architecture = adr = gaps = protocol = memory = run_all = ""
        readable = False
    truth = manifest.get("current_truth", {})
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID and status in {
        "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
    }
    closed = (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    )
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0041"
        ),
        {},
    )
    expected_evidence = {
        "FCF_CURRENT_STATE_FCP_0041_A_SHARE_CROSS_SOURCE_ROW_DELTA_EVIDENCE_LEDGER_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0041_A_SHARE_CROSS_SOURCE_ROW_DELTA_EVIDENCE_LEDGER_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0041_A_SHARE_CROSS_SOURCE_ROW_DELTA_EVIDENCE_LEDGER_APP_1_FINAL.md",
        "docs/FCF_FCP_0041_A_SHARE_CROSS_SOURCE_ROW_DELTA_EVIDENCE_LEDGER_APP_1_D1_D6.md",
    }
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_implemented": status
        not in {
            "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
            "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
        }
        or (all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed
        or (all(finals) and len(set(finals)) == 1),
        "final_evidence_when_closed": not closed
        or (
            (
                root
                / "FCF_CURRENT_STATE_FCP_0041_A_SHARE_CROSS_SOURCE_ROW_DELTA_EVIDENCE_LEDGER_APP_1_FINAL.md"
            ).is_file()
            and all(finals)
            and "ALL CHECKS PASSED" in finals[0]
        ),
        "manifest_state_safe": active
        or closed
        or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and expected_evidence.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": all(
            term in architecture
            for term in (
                "## 74. A-Share Cross-Source Row-Delta Evidence Ledger",
                "exact-match, delta-present, or pair-incomplete",
                "Synthetic fixtures do not close GAP-109",
            )
        ),
        "adr_registered": all(
            term in adr
            for term in (
                "FCF-V2-ADR-041",
                "Bind Aggregate Diagnostics to Exact Row Evidence",
                "retain only mismatches",
            )
        ),
        "gap_preserved": "V2-FR-GAP-109" in gaps and "RESEARCH_REQUIRED" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0041`" in protocol,
        "memory_registered": all(
            term in memory
            for term in (
                "cross-source row-delta evidence ledgers",
                "stable instrument, date, and closed-field order",
                "artifact-independence",
            )
        ),
        "delivery_files_exist": all(
            (root / path).is_file()
            for path in (
                "FCF_CURRENT_STATE_FCP_0041_A_SHARE_CROSS_SOURCE_ROW_DELTA_EVIDENCE_LEDGER_APP_1_APPROVED.md",
                "FCF_CURRENT_STATE_FCP_0041_A_SHARE_CROSS_SOURCE_ROW_DELTA_EVIDENCE_LEDGER_APP_1_DELIVERED.md",
                "docs/FCF_FCP_0041_A_SHARE_CROSS_SOURCE_ROW_DELTA_EVIDENCE_LEDGER_APP_1_D1_D6.md",
                "apps/fcp_0041_a_share_cross_source_row_delta_evidence_ledger_app_1/ledger.py",
                "tests/fcp_0041_a_share_cross_source_row_delta_evidence_ledger_app_1/test_d1_d6.py",
            )
        ),
        "run_all_wired": (
            "control_center_fcp_0041_a_share_cross_source_row_delta_evidence_ledger_guard.py"
            in run_all
        ),
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE"
        and truth.get("next_product_implementation_phase") == "NOT_SELECTED"
        and truth.get("next_product_phase_approval") == "NOT_APPROVED",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0041_guard_report()
    if report["ok"] is not True:
        failed = sorted(key for key, value in report["checks"].items() if not value)
        raise SystemExit("FCP-0041 guard failed: " + ",".join(failed))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
