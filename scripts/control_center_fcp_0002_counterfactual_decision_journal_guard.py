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
APPROVAL_START = "<!-- FCP 0002 COUNTERFACTUAL RESEARCH DECISION JOURNAL FOUNDATION APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0002 COUNTERFACTUAL RESEARCH DECISION JOURNAL FOUNDATION APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0002 COUNTERFACTUAL RESEARCH DECISION JOURNAL FOUNDATION APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0002 COUNTERFACTUAL RESEARCH DECISION JOURNAL FOUNDATION APP 1 LOCK END -->"
REQUIRED = (
    Path("apps/fcp_0002_counterfactual_research_decision_journal_foundation_app_1/boundary.py"),
    Path("apps/fcp_0002_counterfactual_research_decision_journal_foundation_app_1/contracts.py"),
    Path("apps/fcp_0002_counterfactual_research_decision_journal_foundation_app_1/journal.py"),
    Path("apps/fcp_0002_counterfactual_research_decision_journal_foundation_app_1/presentation.py"),
    Path("docs/FCF_FCP_0002_COUNTERFACTUAL_RESEARCH_DECISION_JOURNAL_FOUNDATION_APP_1_D1_D6.md"),
)


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0002_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        approval = (root / "FCF_CURRENT_STATE_FCP_0002_COUNTERFACTUAL_RESEARCH_DECISION_JOURNAL_FOUNDATION_APP_1_APPROVED.md").read_text(encoding="ascii")
        intake = json.loads((root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(encoding="ascii"))
        manifest = json.loads((root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii"))
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, approval, intake, manifest, readable = (), "", {}, {}, False
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    proposal = next((item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0002"), {})
    truth = manifest.get("current_truth", {})
    safety = manifest.get("safety_boundaries", {})
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "approval_document_safe": "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approval and "FCF-FCP-0002 remains NEEDS_RESEARCH" in " ".join(approval.split()),
        "lock_exact": len(texts) == 5 and all(locks) and len(set(locks)) == 1,
        "delivery_files_exist": all((root / path).is_file() for path in REQUIRED),
        "proposal_research_only": proposal.get("status") == "NEEDS_RESEARCH" and proposal.get("operator_decision") == "PENDING" and proposal.get("phase_id") == "NONE",
        "no_active_phase": truth.get("current_governance_phase_id") == "NONE" and truth.get("current_product_implementation_phase") == "NONE" and truth.get("next_product_implementation_phase") == "NOT_SELECTED",
        "p48_forbidden": safety.get("p48_allowed") is False,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0002_guard_report()
    if not report["ok"]:
        raise SystemExit("FCP-0002 counterfactual journal guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
