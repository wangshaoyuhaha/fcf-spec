from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ID = "FCF-FCP-0009-PROVIDER-NEUTRAL-MARKET-DATA-ADAPTER-READINESS-APP-1"
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
APPROVAL_START = "<!-- FCP 0009 PROVIDER NEUTRAL MARKET DATA ADAPTER READINESS APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0009 PROVIDER NEUTRAL MARKET DATA ADAPTER READINESS APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0009 PROVIDER NEUTRAL MARKET DATA ADAPTER READINESS APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0009 PROVIDER NEUTRAL MARKET DATA ADAPTER READINESS APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0009 PROVIDER NEUTRAL MARKET DATA ADAPTER READINESS APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0009 PROVIDER NEUTRAL MARKET DATA ADAPTER READINESS APP 1 FINAL END -->"
EXPECTED_EVIDENCE_COMMITS = (
    "ea31f0292268316959a9f37fea1345b907476d8f",
    "fa7fae723fb9c8ceefe82a62f03d77ffce088217",
    "1f31f392c771155551d938041d1a67ccc6810264",
    "9ec9345c12f9c1be26debe2ff1b19d98e7c431bb",
    "39aa1ce39415b6ef219310534a878704bf32661e",
    "6006d66c1ec7b30fa49a97e557d1de2c665da53a",
    "02daa5e68b4ed485eca2850506831709c76a81de",
    "a0e363b48b916e86f42c4ee177d270af3d9cea8c",
    "871e1bb9a4a5acb9707bdae7071ac708b9f6f362",
)
APP_ROOT = Path("apps/fcp_0009_provider_neutral_market_data_adapter_readiness_app_1")
APP_FILES = (
    "__init__.py",
    "adapter.py",
    "application.py",
    "boundary.py",
    "contracts.py",
    "fixtures.py",
    "launcher.py",
    "readiness.py",
)
CORE_FILES = (
    Path("FCF_CURRENT_STATE_FCP_0009_PROVIDER_NEUTRAL_MARKET_DATA_ADAPTER_READINESS_APP_1_APPROVED.md"),
    Path("FCF_CURRENT_STATE_FCP_0009_PROVIDER_NEUTRAL_MARKET_DATA_ADAPTER_READINESS_APP_1_DELIVERED.md"),
    Path("docs/FCF_FCP_0009_PROVIDER_NEUTRAL_MARKET_DATA_ADAPTER_READINESS_APP_1_D1_D6.md"),
    Path("scripts/run_fcp_0009_market_data_adapter_readiness.py"),
    Path("scripts/run_fcp_0009_market_data_diagnostics_console.py"),
)


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0009_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        app_text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES
        )
        script_text = "\n".join(
            (root / path).read_text(encoding="ascii") for path in CORE_FILES[3:]
        )
        d1_d6 = (root / CORE_FILES[2]).read_text(encoding="ascii")
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
        texts, app_text, script_text, d1_d6, manifest, intake = (), "", "", "", {}, {}
        readable = False
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    truth = manifest.get("current_truth", {})
    safety = manifest.get("safety_boundaries", {})
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0009"
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
        == "FCF-FCP-0010-SIMPLIFIED-CHINESE-CONSOLE-LOCALIZATION-CONSISTENCY-APP-1"
        and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    ) or (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0010-SIMPLIFIED-CHINESE-CONSOLE-LOCALIZATION-CONSISTENCY-APP-1"
    ) or (
        truth.get("current_governance_phase_id")
        == "FCF-FCP-0011-CANDIDATE-DATA-SOURCE-ONBOARDING-EVIDENCE-REVIEW-APP-1"
        and truth.get("latest_completed_governance_delivery")
        == "FCF-FCP-0010-SIMPLIFIED-CHINESE-CONSOLE-LOCALIZATION-CONSISTENCY-APP-1"
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
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact": len(texts) == 5 and all(locks) and len(set(locks)) == 1,
        "final_exact_when_closed": not final
        or (len(texts) == 5 and all(finals) and len(set(finals)) == 1),
        "final_evidence_commits_exact_when_closed": not final
        or (
            all(
                commit in (finals[0] or "")
                for commit in EXPECTED_EVIDENCE_COMMITS
            )
            and all(
                commit
                in (
                    root
                    / "FCF_CURRENT_STATE_FCP_0009_PROVIDER_NEUTRAL_MARKET_DATA_ADAPTER_READINESS_APP_1_FINAL.md"
                ).read_text(encoding="ascii")
                for commit in EXPECTED_EVIDENCE_COMMITS
            )
        ),
        "app_surface_exact": sorted(
            path.name for path in (root / APP_ROOT).glob("*.py")
        )
        == sorted(APP_FILES),
        "core_files_exist": all((root / path).is_file() for path in CORE_FILES),
        "final_file_exists_when_closed": not final
        or (root / "FCF_CURRENT_STATE_FCP_0009_PROVIDER_NEUTRAL_MARKET_DATA_ADAPTER_READINESS_APP_1_FINAL.md").is_file(),
        "manifest_state_safe": active or final or successor,
        "proposal_architecture_only": (
            proposal.get("status") == "ACCEPTED_ARCHITECTURE"
            and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
            and proposal.get("phase_id") == "NONE"
        ),
        "permanent_safety_preserved": (
            safety.get("p48_allowed") is False
            and safety.get("paper_only") is True
            and safety.get("local_only") is True
            and safety.get("loopback_only") is True
            and safety.get("operator_review_mandatory") is True
            and safety.get("order_or_execution_path_allowed") is False
        ),
        "closed_activation_explicit": all(
            term in d1_d6
            for term in (
                "provider selection",
                "credentials absent",
                "network disabled",
                "external activation blocked",
                "GET and HEAD",
                "explicit registered",
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
            "control_center_fcp_0009_provider_neutral_market_data_adapter_readiness_guard.py"
            in (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0009_guard_report()
    if not report["ok"]:
        failed = sorted(name for name, value in report["checks"].items() if not value)
        raise SystemExit("FCP-0009 guard failed: " + ",".join(failed))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
