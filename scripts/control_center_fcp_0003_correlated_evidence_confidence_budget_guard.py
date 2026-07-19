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
APP_ROOT = Path("apps/fcp_0003_correlated_evidence_confidence_budget_foundation_app_1")
APP_FILES = ("__init__.py", "boundary.py", "budget.py", "contracts.py", "presentation.py")
REQUIRED = (
    *(APP_ROOT / name for name in APP_FILES),
    Path("docs/FCF_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_D1_D6.md"),
    Path("FCF_CURRENT_STATE_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_APPROVED.md"),
)


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0003_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        approval = (root / "FCF_CURRENT_STATE_FCP_0003_CORRELATED_EVIDENCE_CONFIDENCE_BUDGET_FOUNDATION_APP_1_APPROVED.md").read_text(encoding="ascii")
        intake = json.loads((root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(encoding="ascii"))
        manifest = json.loads((root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii"))
        app_text = "\n".join((root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES)
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, approval, intake, manifest, app_text, readable = (), "", {}, {}, "", False
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    proposal = next((item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0003"), {})
    truth = manifest.get("current_truth", {})
    safety = manifest.get("safety_boundaries", {})
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "approval_document_safe": "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approval and "FCF-FCP-0003 remains NEEDS_RESEARCH" in " ".join(approval.split()),
        "lock_exact": len(texts) == 5 and all(locks) and len(set(locks)) == 1,
        "delivery_files_exist": all((root / path).is_file() for path in REQUIRED),
        "app_surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py")) == sorted(APP_FILES),
        "deterministic_budget_present": all(term in app_text for term in ("_allocate_largest_remainder", "group_cap_bps", "global_cap_bps", "ABSTAIN", "future-available evidence")),
        "no_prohibited_runtime": all(term not in app_text.lower() for term in ("import requests", "import socket", "import subprocess", "urllib.request", "websocket")),
        "proposal_research_only": proposal.get("status") == "NEEDS_RESEARCH" and proposal.get("operator_decision") == "PENDING" and proposal.get("phase_id") == "NONE",
        "no_active_phase": truth.get("current_governance_phase_id") == "NONE" and truth.get("current_product_implementation_phase") == "NONE" and truth.get("next_product_implementation_phase") == "NOT_SELECTED",
        "p48_forbidden": safety.get("p48_allowed") is False,
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
