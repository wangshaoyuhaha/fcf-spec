from __future__ import annotations

import hashlib
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
APPROVAL_START = "<!-- FCP 0007 A SHARE RQDATA DEMO ARTIFACT INTAKE REPLAY ACCEPTANCE APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0007 A SHARE RQDATA DEMO ARTIFACT INTAKE REPLAY ACCEPTANCE APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0007 A SHARE RQDATA DEMO ARTIFACT INTAKE REPLAY ACCEPTANCE APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0007 A SHARE RQDATA DEMO ARTIFACT INTAKE REPLAY ACCEPTANCE APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0007 A SHARE RQDATA DEMO ARTIFACT INTAKE REPLAY ACCEPTANCE APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0007 A SHARE RQDATA DEMO ARTIFACT INTAKE REPLAY ACCEPTANCE APP 1 FINAL END -->"
APP_ROOT = Path(
    "apps/fcp_0007_a_share_rqdata_demo_artifact_intake_replay_acceptance_app_1"
)
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "boundary.py",
    "contracts.py",
    "loader.py",
    "presentation.py",
)
APPROVAL_FILE = Path(
    "FCF_CURRENT_STATE_FCP_0007_A_SHARE_RQDATA_DEMO_ARTIFACT_INTAKE_REPLAY_ACCEPTANCE_APP_1_APPROVED.md"
)
D1_D6_FILE = Path(
    "docs/FCF_FCP_0007_A_SHARE_RQDATA_DEMO_ARTIFACT_INTAKE_REPLAY_ACCEPTANCE_APP_1_D1_D6.md"
)
DELIVERED_FILE = Path(
    "FCF_CURRENT_STATE_FCP_0007_A_SHARE_RQDATA_DEMO_ARTIFACT_INTAKE_REPLAY_ACCEPTANCE_APP_1_DELIVERED.md"
)
FINAL_FILE = Path(
    "FCF_CURRENT_STATE_FCP_0007_A_SHARE_RQDATA_DEMO_ARTIFACT_INTAKE_REPLAY_ACCEPTANCE_APP_1_FINAL.md"
)
EVIDENCE_FILE = Path(
    "FCF_REGISTERED_EVIDENCE_FCP_0007_RQDATA_A_SHARE_DAILY_DEMO.json"
)
CLI_FILE = Path("scripts/run_fcp_0007_rqdata_demo_acceptance.py")
FINAL_DELIVERY_ID = (
    "FCF-FCP-0007-A-SHARE-RQDATA-DEMO-ARTIFACT-INTAKE-REPLAY-ACCEPTANCE-APP-1"
)
SOURCE_SHA256 = "f229fdf9f86b92562828290159ad2a3d2bcb69a6b57f5e935ce4853a8f280c1e"
EXPECTED_GAPS = [
    "V2-FR-GAP-012",
    "V2-FR-GAP-023",
    "V2-FR-GAP-038",
    "V2-FR-GAP-043",
    "V2-FR-GAP-044",
]
EXPECTED_EVIDENCE_REFS = [
    "FCF_CURRENT_STATE_FCP_0007_A_SHARE_RQDATA_DEMO_ARTIFACT_INTAKE_REPLAY_ACCEPTANCE_APP_1_FINAL.md",
    "FCF_REGISTERED_EVIDENCE_FCP_0007_RQDATA_A_SHARE_DAILY_DEMO.json",
    "docs/FCF_FCP_0007_A_SHARE_RQDATA_DEMO_ARTIFACT_INTAKE_REPLAY_ACCEPTANCE_APP_1_D1_D6.md",
]


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def _raw_demo_absent(root: Path) -> bool:
    for path in root.rglob("*.csv"):
        if ".git" in path.parts or not path.is_file():
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() == SOURCE_SHA256:
            return False
    return True


def build_fcp_0007_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        approval = (root / APPROVAL_FILE).read_text(encoding="ascii")
        d1_d6 = (root / D1_D6_FILE).read_text(encoding="ascii")
        app_text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES
        )
        cli_text = (root / CLI_FILE).read_text(encoding="ascii")
        evidence = json.loads((root / EVIDENCE_FILE).read_text(encoding="ascii"))
        intake = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, approval, d1_d6, app_text, cli_text, evidence, intake, manifest = (
            (),
            "",
            "",
            "",
            "",
            {},
            {},
            {},
        )
        readable = False

    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0007"
        ),
        {},
    )
    truth = manifest.get("current_truth", {})
    safety = manifest.get("safety_boundaries", {})
    active = truth.get("current_governance_phase_id") == FINAL_DELIVERY_ID
    final = (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery") == FINAL_DELIVERY_ID
    )
    successor = (
        truth.get("current_governance_phase_id")
        == "FCF-FCP-0008-CHINESE-BROWSER-CONSOLE-LOCAL-DATA-INTAKE-PREVIEW-APP-1"
        and truth.get("latest_completed_governance_delivery") == FINAL_DELIVERY_ID
    ) or (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0008-CHINESE-BROWSER-CONSOLE-LOCAL-DATA-INTAKE-PREVIEW-APP-1"
    ) or (
        truth.get("current_governance_phase_id")
        == "FCF-FCP-0009-PROVIDER-NEUTRAL-MARKET-DATA-ADAPTER-READINESS-APP-1"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0008-CHINESE-BROWSER-CONSOLE-LOCAL-DATA-INTAKE-PREVIEW-APP-1"
    ) or (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0009-PROVIDER-NEUTRAL-MARKET-DATA-ADAPTER-READINESS-APP-1"
    )
    final_text = ""
    if (root / FINAL_FILE).is_file():
        final_text = (root / FINAL_FILE).read_text(encoding="ascii")
    artifact = evidence.get("artifact", {})
    acceptance = evidence.get("acceptance", {})
    evidence_refs = proposal.get("evidence_refs")
    source_terms = (app_text + "\n" + cli_text).lower()

    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "approval_document_safe": (
            "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approval
            and "does not select RQData" in approval
            and "provider sample must not be committed or redistributed" in approval
        ),
        "lock_exact": len(texts) == 5 and all(locks) and len(set(locks)) == 1,
        "final_exact_when_closed": not final
        or (len(texts) == 5 and all(finals) and len(set(finals)) == 1),
        "app_surface_exact": sorted(
            path.name for path in (root / APP_ROOT).glob("*.py")
        )
        == sorted(APP_FILES),
        "core_files_exist": all(
            (root / path).is_file()
            for path in (
                APPROVAL_FILE,
                D1_D6_FILE,
                EVIDENCE_FILE,
                CLI_FILE,
                *(APP_ROOT / name for name in APP_FILES),
            )
        ),
        "closeout_files_exist_when_final": not final
        or all((root / path).is_file() for path in (DELIVERED_FILE, FINAL_FILE)),
        "registered_artifact_exact": (
            artifact.get("artifact_sha256") == SOURCE_SHA256
            and artifact.get("byte_length") == 1897
            and artifact.get("entitlement_state") == "UNRESOLVED"
            and artifact.get("retention_state") == "UNRESOLVED"
            and artifact.get("provider_selected") is False
            and artifact.get("raw_repository_storage_allowed") is False
            and artifact.get("redistribution_allowed") is False
            and evidence.get("raw_provider_bytes_committed") is False
        ),
        "registered_acceptance_exact": (
            acceptance.get("row_count") == 19
            and acceptance.get("repeated_bom_count") == 20
            and acceptance.get("date_min") == "2022-01-04"
            and acceptance.get("date_max") == "2022-01-28"
            and acceptance.get("instrument_ids") == ["000001.XSHE"]
            and acceptance.get("schema_state") == "READY_FOR_LOCAL_SCHEMA_REPLAY"
            and acceptance.get("product_evidence_state") == "BLOCKED"
            and acceptance.get("result_sha256")
            == "172d1a8337e986405a7ba99fc4c528c78fe49507bafde8ba576d2a2b496e2bb1"
        ),
        "raw_provider_csv_absent": _raw_demo_absent(root),
        "no_prohibited_runtime": all(
            term not in source_terms
            for term in (
                "import requests",
                "import socket",
                "import subprocess",
                "urllib.request",
                "websocket",
            )
        ),
        "proposal_architecture_only": (
            proposal.get("status") == "ACCEPTED_ARCHITECTURE"
            and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
            and proposal.get("phase_id") == "NONE"
            and proposal.get("gap_refs") == EXPECTED_GAPS
        ),
        "proposal_evidence_transition_safe": evidence_refs
        in ([], EXPECTED_EVIDENCE_REFS),
        "proposal_evidence_exact_when_final": not final
        or evidence_refs == EXPECTED_EVIDENCE_REFS,
        "manifest_state_safe": active or final or successor,
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
            "raw provider CSV remains outside the repository" in d1_d6
            and "cannot start a" in d1_d6
            and "V2-R48" in d1_d6
        ),
        "final_document_complete_when_closed": not final
        or (
            "COMPLETED_MERGED_VALIDATED" in final_text
            and re.search(r"- main merge: `[0-9a-f]{40}`", final_text) is not None
            and "No P48 was created" in final_text
        ),
        "run_all_wired": (
            "control_center_fcp_0007_a_share_rqdata_demo_artifact_intake_replay_acceptance_guard.py"
            in (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0007_guard_report()
    if not report["ok"]:
        failed = sorted(name for name, value in report["checks"].items() if not value)
        raise SystemExit(
            "FCP-0007 RQData demo acceptance guard failed: " + ",".join(failed)
        )
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
