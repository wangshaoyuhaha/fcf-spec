from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
APPROVAL_START = "<!-- FCP 0003 CORRELATED EVIDENCE CONFIDENCE BUDGET FOUNDATION APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0003 CORRELATED EVIDENCE CONFIDENCE BUDGET FOUNDATION APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0003 CORRELATED EVIDENCE CONFIDENCE BUDGET FOUNDATION APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0003 CORRELATED EVIDENCE CONFIDENCE BUDGET FOUNDATION APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0003 CORRELATED EVIDENCE CONFIDENCE BUDGET FOUNDATION APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0003 CORRELATED EVIDENCE CONFIDENCE BUDGET FOUNDATION APP 1 FINAL END -->"
APP_ROOT = Path("apps/fcp_0003_correlated_evidence_confidence_budget_foundation_app_1")
APP_FILES = ("__init__.py", "boundary.py", "budget.py", "contracts.py", "presentation.py")
REQUIRED = (
    *(APP_ROOT / name for name in APP_FILES),
    Path("docs/FCF_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_D1_D6.md"),
    Path("FCF_CURRENT_STATE_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_APPROVED.md"),
    Path("FCF_CURRENT_STATE_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_DELIVERED.md"),
    Path("FCF_CURRENT_STATE_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_FINAL.md"),
)
FINAL_EVIDENCE_COMMITS = (
    "516538824e91dce6b1b61ba9e126d0ddad435e39",
    "7381b37b18f31c47c6d3071c31e56ea0c9655ec7",
    "1256506a6dba74bdc016fcb3831d4e862a9cf7eb",
)
EXPECTED_EVIDENCE_REFS = [
    "FCF_CURRENT_STATE_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_FINAL.md",
    "docs/FCF_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_D1_D6.md",
]


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0003_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        approval = (root / "FCF_CURRENT_STATE_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_APPROVED.md").read_text(encoding="ascii")
        final_document = (root / "FCF_CURRENT_STATE_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_FINAL.md").read_text(encoding="ascii")
        intake = json.loads((root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(encoding="ascii"))
        manifest = json.loads((root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii"))
        app_text = "\n".join((root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES)
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, approval, final_document, intake, manifest, app_text, readable = (), "", "", {}, {}, "", False
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    proposal = next((item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0003"), {})
    truth = manifest.get("current_truth", {})
    safety = manifest.get("safety_boundaries", {})
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "approval_document_safe": "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approval and "FCF-FCP-0003 remains NEEDS_RESEARCH" in " ".join(approval.split()),
        "lock_exact": len(texts) == 5 and all(locks) and len(set(locks)) == 1,
        "final_exact": len(texts) == 5 and all(finals) and len(set(finals)) == 1,
        "final_document_complete": "COMPLETED_MERGED_VALIDATED" in final_document and all(commit in final_document for commit in FINAL_EVIDENCE_COMMITS),
        "delivery_files_exist": all((root / path).is_file() for path in REQUIRED),
        "app_surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py")) == sorted(APP_FILES),
        "deterministic_budget_present": all(term in app_text for term in ("_allocate_largest_remainder", "group_cap_bps", "global_cap_bps", "ABSTAIN", "future-available evidence")),
        "no_prohibited_runtime": all(term not in app_text.lower() for term in ("import requests", "import socket", "import subprocess", "urllib.request", "websocket")),
        "proposal_research_only": proposal.get("status") == "NEEDS_RESEARCH" and proposal.get("operator_decision") == "PENDING" and proposal.get("phase_id") == "NONE",
        "proposal_evidence_exact": proposal.get("evidence_refs") == EXPECTED_EVIDENCE_REFS,
        "no_active_phase": truth.get("current_governance_phase_id") in {
            "NONE",
            "FCF-FCP-0005-MVP-PRODUCT-READINESS-DECISION-GATE-APP-1",
            "FCF-FCP-0006-A-SHARE-MVP-TARGET-DATA-ACCEPTANCE-BASELINE-APP-1",
            "FCF-FCP-0007-A-SHARE-RQDATA-DEMO-ARTIFACT-INTAKE-REPLAY-ACCEPTANCE-APP-1",
            "FCF-FCP-0008-CHINESE-BROWSER-CONSOLE-LOCAL-DATA-INTAKE-PREVIEW-APP-1",
            "FCF-FCP-0009-PROVIDER-NEUTRAL-MARKET-DATA-ADAPTER-READINESS-APP-1",
        } and truth.get("current_product_implementation_phase") == "NONE" and truth.get("next_product_implementation_phase") == "NOT_SELECTED",
        "p48_forbidden": safety.get("p48_allowed") is False,
        "manifest_records_latest_delivery": truth.get("latest_completed_governance_delivery") in {
            "FCF-FCP-0003-CORRELATED-EVIDENCE-CONFIDENCE-BUDGET-FOUNDATION-APP-1",
            "FCF-FCP-0004-INSTITUTIONAL-CALENDAR-CAUSAL-INTELLIGENCE-RECONCILIATION-APP-1",
            "FCF-FCP-0005-MVP-PRODUCT-READINESS-DECISION-GATE-APP-1",
            "FCF-FCP-0006-A-SHARE-MVP-TARGET-DATA-ACCEPTANCE-BASELINE-APP-1",
            "FCF-FCP-0007-A-SHARE-RQDATA-DEMO-ARTIFACT-INTAKE-REPLAY-ACCEPTANCE-APP-1",
            "FCF-FCP-0008-CHINESE-BROWSER-CONSOLE-LOCAL-DATA-INTAKE-PREVIEW-APP-1",
            "FCF-FCP-0009-PROVIDER-NEUTRAL-MARKET-DATA-ADAPTER-READINESS-APP-1",
        },
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0003_guard_report()
    if not report["ok"]:
        raise SystemExit("FCP-0003 confidence budget guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
