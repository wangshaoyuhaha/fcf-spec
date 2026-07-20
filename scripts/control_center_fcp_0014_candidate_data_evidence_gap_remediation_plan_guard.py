from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ID = "FCF-FCP-0014-CANDIDATE-DATA-EVIDENCE-GAP-REMEDIATION-PLAN-APP-1"
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
APPROVAL_START = "<!-- FCP 0014 CANDIDATE DATA EVIDENCE GAP REMEDIATION PLAN APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0014 CANDIDATE DATA EVIDENCE GAP REMEDIATION PLAN APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0014 CANDIDATE DATA EVIDENCE GAP REMEDIATION PLAN APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0014 CANDIDATE DATA EVIDENCE GAP REMEDIATION PLAN APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0014 CANDIDATE DATA EVIDENCE GAP REMEDIATION PLAN APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0014 CANDIDATE DATA EVIDENCE GAP REMEDIATION PLAN APP 1 FINAL END -->"
APP_ROOT = Path("apps/fcp_0014_candidate_data_evidence_gap_remediation_plan_app_1")
APP_FILES = (
    "__init__.py",
    "application.py",
    "boundary.py",
    "contracts.py",
    "fixtures.py",
    "launcher.py",
    "planner.py",
)
CORE_FILES = (
    Path("FCF_CURRENT_STATE_FCP_0014_CANDIDATE_DATA_EVIDENCE_GAP_REMEDIATION_PLAN_APP_1_APPROVED.md"),
    Path("FCF_CURRENT_STATE_FCP_0014_CANDIDATE_DATA_EVIDENCE_GAP_REMEDIATION_PLAN_APP_1_DELIVERED.md"),
    Path("docs/FCF_FCP_0014_CANDIDATE_DATA_EVIDENCE_GAP_REMEDIATION_PLAN_APP_1_D1_D6.md"),
    Path("scripts/run_fcp_0014_candidate_evidence_gap_remediation.py"),
)
FINAL_FILE = Path("FCF_CURRENT_STATE_FCP_0014_CANDIDATE_DATA_EVIDENCE_GAP_REMEDIATION_PLAN_APP_1_FINAL.md")
EXPECTED_FINAL_REFS = (
    FINAL_FILE.as_posix(),
    "FCF_REGISTERED_EVIDENCE_FCP_0013_RQDATA_CANDIDATE_BUNDLE.json",
    "docs/FCF_FCP_0014_CANDIDATE_DATA_EVIDENCE_GAP_REMEDIATION_PLAN_APP_1_D1_D6.md",
)
EXPECTED_EVIDENCE_COMMITS = (
    "6e04b4ac9d26fac0246174461a966cee6622059e",
    "ae4f513259ed148ffd18ff9f705f3df26ddafd46",
    "bd89ef664cf69fc2572afebaee890df37f27f71a",
)


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0014_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        app_text = "\n".join((root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES)
        d1_d6 = (root / CORE_FILES[2]).read_text(encoding="ascii")
        script_text = (root / CORE_FILES[3]).read_text(encoding="ascii")
        manifest = json.loads((root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii"))
        intake = json.loads((root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(encoding="ascii"))
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, app_text, d1_d6, script_text, manifest, intake = (), "", "", "", {}, {}
        readable = False
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    truth = manifest.get("current_truth", {})
    safety = manifest.get("safety_boundaries", {})
    proposal = next(
        (item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0014"),
        {},
    )
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID
    closed = (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    )
    source_terms = (app_text + "\n" + script_text).lower()
    final_text = (root / FINAL_FILE).read_text(encoding="ascii") if (root / FINAL_FILE).is_file() else ""
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_validated": status != "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"
        or (len(texts) == 5 and all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed
        or (len(texts) == 5 and all(finals) and len(set(finals)) == 1),
        "app_surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py")) == sorted(APP_FILES),
        "core_files_exist": all((root / path).is_file() for path in CORE_FILES),
        "manifest_state_safe": active or closed,
        "proposal_architecture_only": proposal.get("status") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE",
        "proposal_evidence_transition_safe": proposal.get("evidence_refs") in ([], list(EXPECTED_FINAL_REFS))
        and (not closed or proposal.get("evidence_refs") == list(EXPECTED_FINAL_REFS)),
        "permanent_safety_preserved": safety.get("p48_allowed") is False
        and safety.get("paper_only") is True
        and safety.get("local_only") is True
        and safety.get("loopback_only") is True
        and safety.get("registered_artifact_only") is True
        and safety.get("operator_review_mandatory") is True
        and safety.get("order_or_execution_path_allowed") is False,
        "closed_plan_explicit": all(
            term in d1_d6
            for term in (
                "FCP-0013 reconciliation packet",
                "All requirements remain OPEN",
                "GET and HEAD",
                "No form, button, script",
                "cannot close V2-FR-GAP-022",
            )
        ),
        "no_prohibited_runtime": all(
            term not in source_terms
            for term in (
                "import requests",
                "import socket",
                "import subprocess",
                "urllib.request",
                "websocket",
                "import rqdatac",
                "import rqsdk",
                "api_key",
                "access_token",
            )
        ),
        "run_all_wired": "control_center_fcp_0014_candidate_data_evidence_gap_remediation_plan_guard.py"
        in (root / "scripts/run_all_checks.py").read_text(encoding="ascii"),
        "final_file_exists_when_closed": not closed or bool(final_text),
        "final_evidence_commits_when_closed": not closed
        or all(commit in (finals[0] or "") and commit in final_text for commit in EXPECTED_EVIDENCE_COMMITS),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0014_guard_report()
    if not report["ok"]:
        failed = sorted(name for name, value in report["checks"].items() if not value)
        raise SystemExit("FCP-0014 guard failed: " + ",".join(failed))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
