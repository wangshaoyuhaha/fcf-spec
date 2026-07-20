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
APPROVAL_START = "<!-- FCP 0005 MVP PRODUCT READINESS DECISION GATE APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0005 MVP PRODUCT READINESS DECISION GATE APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0005 MVP PRODUCT READINESS DECISION GATE APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0005 MVP PRODUCT READINESS DECISION GATE APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0005 MVP PRODUCT READINESS DECISION GATE APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0005 MVP PRODUCT READINESS DECISION GATE APP 1 FINAL END -->"
APP_ROOT = Path("apps/fcp_0005_mvp_product_readiness_decision_gate_app_1")
APP_FILES = ("__init__.py", "boundary.py", "contracts.py", "decision.py", "presentation.py")
EXPECTED_GAPS = [f"V2-FR-GAP-{number:03d}" for number in range(42, 48)]
EXPECTED_EVIDENCE_REFS = [
    "FCF_CURRENT_STATE_FCP_0005_MVP_PRODUCT_READINESS_DECISION_GATE_APP_1_FINAL.md",
    "docs/FCF_FCP_0005_MVP_PRODUCT_READINESS_DECISION_GATE_APP_1_D1_D6.md",
]
APPROVAL_FILE = Path("FCF_CURRENT_STATE_FCP_0005_MVP_PRODUCT_READINESS_DECISION_GATE_APP_1_APPROVED.md")
D1_D6_FILE = Path("docs/FCF_FCP_0005_MVP_PRODUCT_READINESS_DECISION_GATE_APP_1_D1_D6.md")
DELIVERED_FILE = Path("FCF_CURRENT_STATE_FCP_0005_MVP_PRODUCT_READINESS_DECISION_GATE_APP_1_DELIVERED.md")
FINAL_FILE = Path("FCF_CURRENT_STATE_FCP_0005_MVP_PRODUCT_READINESS_DECISION_GATE_APP_1_FINAL.md")
FINAL_DELIVERY_ID = "FCF-FCP-0005-MVP-PRODUCT-READINESS-DECISION-GATE-APP-1"
ACTIVE_DELIVERY_ID = FINAL_DELIVERY_ID


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0005_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        approval = (root / APPROVAL_FILE).read_text(encoding="ascii")
        d1_d6 = (root / D1_D6_FILE).read_text(encoding="ascii")
        intake = json.loads((root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(encoding="ascii"))
        manifest = json.loads((root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii"))
        app_text = "\n".join((root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES)
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, approval, d1_d6, intake, manifest, app_text, readable = (), "", "", {}, {}, "", False

    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0005"
        ),
        {},
    )
    truth = manifest.get("current_truth", {})
    safety = manifest.get("safety_boundaries", {})
    active = truth.get("current_governance_phase_id") == ACTIVE_DELIVERY_ID
    final = (
        truth.get("current_governance_phase_id")
        in {
            "NONE",
            "FCF-FCP-0006-A-SHARE-MVP-TARGET-DATA-ACCEPTANCE-BASELINE-APP-1",
            "FCF-FCP-0007-A-SHARE-RQDATA-DEMO-ARTIFACT-INTAKE-REPLAY-ACCEPTANCE-APP-1",
            "FCF-FCP-0008-CHINESE-BROWSER-CONSOLE-LOCAL-DATA-INTAKE-PREVIEW-APP-1",
            "FCF-FCP-0009-PROVIDER-NEUTRAL-MARKET-DATA-ADAPTER-READINESS-APP-1",
            "FCF-FCP-0010-SIMPLIFIED-CHINESE-CONSOLE-LOCALIZATION-CONSISTENCY-APP-1",
            "FCF-FCP-0011-CANDIDATE-DATA-SOURCE-ONBOARDING-EVIDENCE-REVIEW-APP-1",
            "FCF-FCP-0012-SANITIZED-CANDIDATE-DATA-SESSION-EVIDENCE-INTAKE-APP-1",
            "FCF-FCP-0013-CANDIDATE-DATA-EVIDENCE-BUNDLE-RECONCILIATION-APP-1",
            "FCF-FCP-0014-CANDIDATE-DATA-EVIDENCE-GAP-REMEDIATION-PLAN-APP-1",
            "FCF-FCP-0015-CANDIDATE-EVIDENCE-CONSOLE-LAUNCH-ROUTING-HARDENING-APP-1",
            "FCF-FCP-0016-TRUSTED-DATA-SUPPLY-CHAIN-COST-AWARE-SOURCE-ROUTING-ARCHITECTURE-APP-1",
        }
        and truth.get("latest_completed_governance_delivery")
        in {
            FINAL_DELIVERY_ID,
            "FCF-FCP-0006-A-SHARE-MVP-TARGET-DATA-ACCEPTANCE-BASELINE-APP-1",
            "FCF-FCP-0007-A-SHARE-RQDATA-DEMO-ARTIFACT-INTAKE-REPLAY-ACCEPTANCE-APP-1",
            "FCF-FCP-0008-CHINESE-BROWSER-CONSOLE-LOCAL-DATA-INTAKE-PREVIEW-APP-1",
            "FCF-FCP-0009-PROVIDER-NEUTRAL-MARKET-DATA-ADAPTER-READINESS-APP-1",
            "FCF-FCP-0010-SIMPLIFIED-CHINESE-CONSOLE-LOCALIZATION-CONSISTENCY-APP-1",
            "FCF-FCP-0011-CANDIDATE-DATA-SOURCE-ONBOARDING-EVIDENCE-REVIEW-APP-1",
            "FCF-FCP-0012-SANITIZED-CANDIDATE-DATA-SESSION-EVIDENCE-INTAKE-APP-1",
            "FCF-FCP-0013-CANDIDATE-DATA-EVIDENCE-BUNDLE-RECONCILIATION-APP-1",
            "FCF-FCP-0014-CANDIDATE-DATA-EVIDENCE-GAP-REMEDIATION-PLAN-APP-1",
            "FCF-FCP-0015-CANDIDATE-EVIDENCE-CONSOLE-LAUNCH-ROUTING-HARDENING-APP-1",
            "FCF-FCP-0016-TRUSTED-DATA-SUPPLY-CHAIN-COST-AWARE-SOURCE-ROUTING-ARCHITECTURE-APP-1",
        }
    )
    evidence_refs = proposal.get("evidence_refs")
    final_text = ""
    if (root / FINAL_FILE).is_file():
        final_text = (root / FINAL_FILE).read_text(encoding="ascii")

    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "approval_document_safe": (
            "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approval
            and "FCF-FCP-0005 remains NEEDS_RESEARCH" in " ".join(approval.split())
        ),
        "lock_exact": len(texts) == 5 and all(locks) and len(set(locks)) == 1,
        "final_exact_when_closed": not final or (
            len(texts) == 5 and all(finals) and len(set(finals)) == 1
        ),
        "app_surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py"))
        == sorted(APP_FILES),
        "core_files_exist": all(
            (root / path).is_file()
            for path in (
                APPROVAL_FILE,
                D1_D6_FILE,
                *(APP_ROOT / name for name in APP_FILES),
            )
        ),
        "closeout_files_exist_when_final": not final or all(
            (root / path).is_file() for path in (DELIVERED_FILE, FINAL_FILE)
        ),
        "deterministic_gate_present": all(
            term in app_text
            for term in (
                "EVIDENCE_DIMENSIONS",
                "READY_FOR_OPERATOR_DECISION",
                "NEEDS_EVIDENCE",
                "ABSTAIN",
                "selected_market_id",
                "automatic_ranking_applied",
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
        "proposal_research_only": (
            proposal.get("status") == "NEEDS_RESEARCH"
            and proposal.get("operator_decision") == "PENDING"
            and proposal.get("phase_id") == "NONE"
            and proposal.get("gap_refs") == EXPECTED_GAPS
        ),
        "proposal_evidence_transition_safe": evidence_refs in ([], EXPECTED_EVIDENCE_REFS),
        "proposal_evidence_exact_when_final": not final or evidence_refs == EXPECTED_EVIDENCE_REFS,
        "manifest_state_safe": active or final,
        "no_product_phase_selected": (
            truth.get("current_product_implementation_phase") == "NONE"
            and truth.get("next_product_implementation_phase") == "NOT_SELECTED"
            and truth.get("next_product_phase_approval") == "NOT_APPROVED"
        ),
        "permanent_safety_preserved": (
            safety.get("p48_allowed") is False
            and safety.get("paper_only") is True
            and safety.get("local_only") is True
            and safety.get("operator_review_mandatory") is True
            and safety.get("order_or_execution_path_allowed") is False
        ),
        "d1_d6_boundary_explicit": (
            "cannot select a market" in d1_d6
            and "V2-R48" in d1_d6
            and "NEEDS_RESEARCH" in d1_d6
        ),
        "final_document_complete_when_closed": not final or (
            "COMPLETED_MERGED_VALIDATED" in final_text
            and re.search(r"- main merge: `[0-9a-f]{40}`", final_text) is not None
            and "No P48 was created" in final_text
        ),
        "run_all_wired": "control_center_fcp_0005_mvp_product_readiness_decision_gate_guard.py"
        in (root / "scripts/run_all_checks.py").read_text(encoding="ascii"),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0005_guard_report()
    if not report["ok"]:
        failed = sorted(name for name, value in report["checks"].items() if not value)
        raise SystemExit("FCP-0005 product readiness decision gate guard failed: " + ",".join(failed))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
