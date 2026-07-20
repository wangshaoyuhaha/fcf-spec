from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ID = (
    "FCF-FCP-0010-SIMPLIFIED-CHINESE-CONSOLE-LOCALIZATION-CONSISTENCY-APP-1"
)
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
APPROVAL_START = "<!-- FCP 0010 SIMPLIFIED CHINESE CONSOLE LOCALIZATION CONSISTENCY APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0010 SIMPLIFIED CHINESE CONSOLE LOCALIZATION CONSISTENCY APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0010 SIMPLIFIED CHINESE CONSOLE LOCALIZATION CONSISTENCY APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0010 SIMPLIFIED CHINESE CONSOLE LOCALIZATION CONSISTENCY APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0010 SIMPLIFIED CHINESE CONSOLE LOCALIZATION CONSISTENCY APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0010 SIMPLIFIED CHINESE CONSOLE LOCALIZATION CONSISTENCY APP 1 FINAL END -->"
APP_ROOT = Path(
    "apps/fcp_0010_simplified_chinese_console_localization_consistency_app_1"
)
APP_FILES = (
    "__init__.py",
    "application.py",
    "boundary.py",
    "catalog.py",
    "coverage.py",
    "launcher.py",
    "localization.py",
)
CORE_FILES = (
    Path("FCF_CURRENT_STATE_FCP_0010_SIMPLIFIED_CHINESE_CONSOLE_LOCALIZATION_CONSISTENCY_APP_1_APPROVED.md"),
    Path("FCF_CURRENT_STATE_FCP_0010_SIMPLIFIED_CHINESE_CONSOLE_LOCALIZATION_CONSISTENCY_APP_1_DELIVERED.md"),
    Path("docs/FCF_FCP_0010_SIMPLIFIED_CHINESE_CONSOLE_LOCALIZATION_CONSISTENCY_APP_1_D1_D6.md"),
    Path("scripts/run_fcp_0010_simplified_chinese_console.py"),
)
FINAL_FILE = Path(
    "FCF_CURRENT_STATE_FCP_0010_SIMPLIFIED_CHINESE_CONSOLE_LOCALIZATION_CONSISTENCY_APP_1_FINAL.md"
)
EXPECTED_FINAL_REFS = (
    FINAL_FILE.as_posix(),
    "docs/FCF_FCP_0010_SIMPLIFIED_CHINESE_CONSOLE_LOCALIZATION_CONSISTENCY_APP_1_D1_D6.md",
)
EXPECTED_EVIDENCE_COMMITS = (
    "8376a3ec74b80dfa4aa6bc5e46902d6b45d28b12",
    "c01b0a90df4b279c1bff9cd4beeda57e8e7e4015",
    "beb9cb4426c82aa3511e3bf07a472cab2e98dff1",
)


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0010_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        app_text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii")
            for name in APP_FILES
        )
        d1_d6 = (root / CORE_FILES[2]).read_text(encoding="ascii")
        script_text = (root / CORE_FILES[3]).read_text(encoding="ascii")
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        intake = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, app_text, d1_d6, script_text, manifest, intake = (), "", "", "", {}, {}
        readable = False

    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    truth = manifest.get("current_truth", {})
    fcp_0016_successor = truth.get("current_governance_phase_id") == "FCF-FCP-0016-TRUSTED-DATA-SUPPLY-CHAIN-COST-AWARE-SOURCE-ROUTING-ARCHITECTURE-APP-1" and truth.get("latest_completed_governance_delivery") == "FCF-FCP-0015-CANDIDATE-EVIDENCE-CONSOLE-LAUNCH-ROUTING-HARDENING-APP-1" or truth.get("current_governance_phase_id") == "NONE" and truth.get("latest_completed_governance_delivery") == "FCF-FCP-0016-TRUSTED-DATA-SUPPLY-CHAIN-COST-AWARE-SOURCE-ROUTING-ARCHITECTURE-APP-1" or truth.get("current_governance_phase_id") == "FCF-FCP-0017-A-SHARE-TRUSTED-DAILY-DATA-SUBSTRATE-LOCAL-CALIBRATION-APP-1" and truth.get("latest_completed_governance_delivery") == "FCF-FCP-0016-TRUSTED-DATA-SUPPLY-CHAIN-COST-AWARE-SOURCE-ROUTING-ARCHITECTURE-APP-1" or truth.get("current_governance_phase_id") == "NONE" and truth.get("latest_completed_governance_delivery") == "FCF-FCP-0017-A-SHARE-TRUSTED-DAILY-DATA-SUBSTRATE-LOCAL-CALIBRATION-APP-1"
    safety = manifest.get("safety_boundaries", {})
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0010"
        ),
        {},
    )
    active = truth.get("current_governance_phase_id") == DELIVERY_ID
    final = (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    )
    successor = (
        truth.get("current_governance_phase_id")
        == "FCF-FCP-0011-CANDIDATE-DATA-SOURCE-ONBOARDING-EVIDENCE-REVIEW-APP-1"
        and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    ) or (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0011-CANDIDATE-DATA-SOURCE-ONBOARDING-EVIDENCE-REVIEW-APP-1"
    ) or (
        truth.get("current_governance_phase_id")
        == "FCF-FCP-0012-SANITIZED-CANDIDATE-DATA-SESSION-EVIDENCE-INTAKE-APP-1"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0011-CANDIDATE-DATA-SOURCE-ONBOARDING-EVIDENCE-REVIEW-APP-1"
    ) or (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0012-SANITIZED-CANDIDATE-DATA-SESSION-EVIDENCE-INTAKE-APP-1"
    ) or (
        truth.get("current_governance_phase_id")
        == "FCF-FCP-0013-CANDIDATE-DATA-EVIDENCE-BUNDLE-RECONCILIATION-APP-1"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0012-SANITIZED-CANDIDATE-DATA-SESSION-EVIDENCE-INTAKE-APP-1"
    ) or (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0013-CANDIDATE-DATA-EVIDENCE-BUNDLE-RECONCILIATION-APP-1"
    ) or (
        truth.get("current_governance_phase_id")
        == "FCF-FCP-0014-CANDIDATE-DATA-EVIDENCE-GAP-REMEDIATION-PLAN-APP-1"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0013-CANDIDATE-DATA-EVIDENCE-BUNDLE-RECONCILIATION-APP-1"
    ) or (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0014-CANDIDATE-DATA-EVIDENCE-GAP-REMEDIATION-PLAN-APP-1"
    ) or (
        truth.get("current_governance_phase_id")
        == "FCF-FCP-0015-CANDIDATE-EVIDENCE-CONSOLE-LAUNCH-ROUTING-HARDENING-APP-1"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0014-CANDIDATE-DATA-EVIDENCE-GAP-REMEDIATION-PLAN-APP-1"
    ) or (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0015-CANDIDATE-EVIDENCE-CONSOLE-LAUNCH-ROUTING-HARDENING-APP-1"
    )
    source_terms = (app_text + "\n" + script_text).lower()
    final_text = ""
    if (root / FINAL_FILE).is_file():
        final_text = (root / FINAL_FILE).read_text(encoding="ascii")

    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact": len(texts) == 5 and all(locks) and len(set(locks)) == 1,
        "final_exact_when_closed": not final
        or (len(texts) == 5 and all(finals) and len(set(finals)) == 1),
        "app_surface_exact": sorted(
            path.name for path in (root / APP_ROOT).glob("*.py")
        )
        == sorted(APP_FILES),
        "core_files_exist": all((root / path).is_file() for path in CORE_FILES),
        "final_file_exists_when_closed": not final or bool(final_text),
        "manifest_state_safe": active or final or successor or fcp_0016_successor,
        "proposal_architecture_only": (
            proposal.get("status") == "ACCEPTED_ARCHITECTURE"
            and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
            and proposal.get("phase_id") == "NONE"
        ),
        "proposal_evidence_transition_safe": (
            proposal.get("evidence_refs") in ([], list(EXPECTED_FINAL_REFS))
            and (not final or proposal.get("evidence_refs") == list(EXPECTED_FINAL_REFS))
        ),
        "permanent_safety_preserved": (
            safety.get("p48_allowed") is False
            and safety.get("paper_only") is True
            and safety.get("local_only") is True
            and safety.get("loopback_only") is True
            and safety.get("registered_artifact_only") is True
            and safety.get("operator_review_mandatory") is True
            and safety.get("order_or_execution_path_allowed") is False
        ),
        "localization_boundary_explicit": all(
            term in d1_d6
            for term in (
                "all registered read-only HTML routes",
                "td and code",
                "Default Simplified Chinese",
                "explicit English",
                "GET and HEAD",
                "No form, button, script, upload",
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
                "api_key",
                "access_token",
            )
        ),
        "run_all_wired": (
            "control_center_fcp_0010_simplified_chinese_console_localization_consistency_guard.py"
            in (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        ),
        "final_evidence_labels_when_closed": not final
        or all(
            label in (finals[0] or "") and label in final_text
            for label in (
                "governance approval:",
                "sidecar delivery:",
                "main merge:",
            )
        ),
        "final_evidence_commits_when_closed": not final
        or all(
            commit in (finals[0] or "") and commit in final_text
            for commit in EXPECTED_EVIDENCE_COMMITS
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0010_guard_report()
    if not report["ok"]:
        failed = sorted(name for name, value in report["checks"].items() if not value)
        raise SystemExit("FCP-0010 guard failed: " + ",".join(failed))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
