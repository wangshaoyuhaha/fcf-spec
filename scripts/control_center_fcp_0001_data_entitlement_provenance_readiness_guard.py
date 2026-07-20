from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_PATHS = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
APPROVAL_PATH = Path(
    "FCF_CURRENT_STATE_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_"
    "READINESS_FOUNDATION_APP_1_APPROVED.md"
)
MANIFEST_PATH = Path("FCF_CURRENT_STATE_MANIFEST.json")
INTAKE_PATH = Path("FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json")
APPROVAL_START = (
    "<!-- FCP 0001 DATA ENTITLEMENT PROVENANCE READINESS FOUNDATION "
    "APP 1 APPROVAL START -->"
)
APPROVAL_END = (
    "<!-- FCP 0001 DATA ENTITLEMENT PROVENANCE READINESS FOUNDATION "
    "APP 1 APPROVAL END -->"
)
LOCK_START = (
    "<!-- FCP 0001 DATA ENTITLEMENT PROVENANCE READINESS FOUNDATION "
    "APP 1 LOCK START -->"
)
LOCK_END = (
    "<!-- FCP 0001 DATA ENTITLEMENT PROVENANCE READINESS FOUNDATION "
    "APP 1 LOCK END -->"
)
FINAL_START = (
    "<!-- FCP 0001 DATA ENTITLEMENT PROVENANCE READINESS FOUNDATION "
    "APP 1 FINAL START -->"
)
FINAL_END = (
    "<!-- FCP 0001 DATA ENTITLEMENT PROVENANCE READINESS FOUNDATION "
    "APP 1 FINAL END -->"
)
FINAL_PATH = Path(
    "FCF_CURRENT_STATE_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_"
    "READINESS_FOUNDATION_APP_1_FINAL.md"
)
REQUIRED_DELIVERY_PATHS = (
    Path("apps/fcp_0001_data_entitlement_provenance_readiness_foundation_app_1/boundary.py"),
    Path("apps/fcp_0001_data_entitlement_provenance_readiness_foundation_app_1/contracts.py"),
    Path("apps/fcp_0001_data_entitlement_provenance_readiness_foundation_app_1/registry.py"),
    Path("apps/fcp_0001_data_entitlement_provenance_readiness_foundation_app_1/readiness.py"),
    Path("apps/fcp_0001_data_entitlement_provenance_readiness_foundation_app_1/service.py"),
    Path("apps/fcp_0001_data_entitlement_provenance_readiness_foundation_app_1/presentation.py"),
    Path("apps/fcp_0001_data_entitlement_provenance_readiness_foundation_app_1/acceptance.py"),
    Path("docs/FCF_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_READINESS_FOUNDATION_APP_1_D1.md"),
    Path("docs/FCF_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_READINESS_FOUNDATION_APP_1_D2.md"),
    Path("docs/FCF_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_READINESS_FOUNDATION_APP_1_D3.md"),
    Path("docs/FCF_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_READINESS_FOUNDATION_APP_1_D4.md"),
    Path("docs/FCF_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_READINESS_FOUNDATION_APP_1_D5.md"),
    Path("docs/FCF_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_READINESS_FOUNDATION_APP_1_D6.md"),
)


def _approval_block(text: str) -> str | None:
    if text.count(APPROVAL_START) != 1 or text.count(APPROVAL_END) != 1:
        return None
    start = text.index(APPROVAL_START)
    end = text.index(APPROVAL_END) + len(APPROVAL_END)
    if end <= start:
        return None
    return text[start:end]


def _lock_block(text: str) -> str | None:
    if text.count(LOCK_START) != 1 or text.count(LOCK_END) != 1:
        return None
    start = text.index(LOCK_START)
    end = text.index(LOCK_END) + len(LOCK_END)
    if end <= start:
        return None
    return text[start:end]


def _final_block(text: str) -> str | None:
    if text.count(FINAL_START) != 1 or text.count(FINAL_END) != 1:
        return None
    start = text.index(FINAL_START)
    end = text.index(FINAL_END) + len(FINAL_END)
    if end <= start:
        return None
    return text[start:end]


def validate_fcp_0001_state(
    authority_texts: tuple[str, ...],
    approval_text: str,
    manifest: object,
    intake: object,
    required_paths_exist: bool,
) -> dict[str, bool]:
    blocks = tuple(_approval_block(text) for text in authority_texts)
    lock_blocks = tuple(_lock_block(text) for text in authority_texts)
    normalized_lock = " ".join(lock_blocks[0].split()) if lock_blocks and lock_blocks[0] else ""
    final_blocks = tuple(_final_block(text) for text in authority_texts)
    manifest_data = manifest if isinstance(manifest, dict) else {}
    current_truth = manifest_data.get("current_truth", {})
    safety_boundaries = manifest_data.get("safety_boundaries", {})
    intake_data = intake if isinstance(intake, dict) else {}
    normalized_approval = " ".join(approval_text.split())
    proposals = intake_data.get("proposals", [])
    fcp_0001 = next(
        (
            item
            for item in proposals
            if isinstance(item, dict) and item.get("proposal_id") == "FCF-FCP-0001"
        ),
        {},
    )
    return {
        "approval_blocks_exact_across_authorities": (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and all(block is not None for block in blocks)
            and len(set(blocks)) == 1
        ),
        "approval_document_preserves_boundary": (
            "Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approval_text
            and "FCF-FCP-0001 remains NEEDS_RESEARCH" in normalized_approval
            and "No network," in approval_text
            and "No P48 is created." in approval_text
        ),
        "lock_blocks_exact_across_authorities": (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and all(block is not None for block in lock_blocks)
            and len(set(lock_blocks)) == 1
            and "Status: DELIVERY_IMPLEMENTED_VALIDATION_PENDING" in lock_blocks[0]
            and "FCF-FCP-0001 remains NEEDS_RESEARCH" in normalized_lock
        ),
        "final_blocks_exact_across_authorities": (
            len(authority_texts) == len(AUTHORITY_PATHS)
            and all(block is not None for block in final_blocks)
            and len(set(final_blocks)) == 1
            and "Status: GOVERNANCE_FOUNDATION_COMPLETED_MERGED_VALIDATED"
            in final_blocks[0]
            and "315ca4dba01e53448e39131418c153fa73ad2aa0" in final_blocks[0]
            and "4a0c29cc4b7ab8d2d9b78b0a014be967f7ef485e" in final_blocks[0]
        ),
        "delivery_paths_exist": required_paths_exist,
        "fcp_0001_still_research_only": (
            fcp_0001.get("status") == "NEEDS_RESEARCH"
            and fcp_0001.get("operator_decision") == "PENDING"
            and fcp_0001.get("phase_id") == "NONE"
        ),
        "manifest_has_no_active_phase": (
            isinstance(current_truth, dict)
            and current_truth.get("current_governance_phase_id") in {
                "NONE",
                "FCF-FCP-0005-MVP-PRODUCT-READINESS-DECISION-GATE-APP-1",
                "FCF-FCP-0006-A-SHARE-MVP-TARGET-DATA-ACCEPTANCE-BASELINE-APP-1",
                "FCF-FCP-0007-A-SHARE-RQDATA-DEMO-ARTIFACT-INTAKE-REPLAY-ACCEPTANCE-APP-1",
                "FCF-FCP-0008-CHINESE-BROWSER-CONSOLE-LOCAL-DATA-INTAKE-PREVIEW-APP-1",
                "FCF-FCP-0009-PROVIDER-NEUTRAL-MARKET-DATA-ADAPTER-READINESS-APP-1",
                "FCF-FCP-0010-SIMPLIFIED-CHINESE-CONSOLE-LOCALIZATION-CONSISTENCY-APP-1",
                "FCF-FCP-0011-CANDIDATE-DATA-SOURCE-ONBOARDING-EVIDENCE-REVIEW-APP-1",
            }
            and current_truth.get("current_governance_phase_status") in {
                "NONE",
                "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
                "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
                "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
            }
            and current_truth.get("current_product_implementation_phase") == "NONE"
            and current_truth.get("next_product_implementation_phase")
            == "NOT_SELECTED"
            and current_truth.get("next_product_phase_approval") == "NOT_APPROVED"
        ),
        "manifest_records_latest_governance_delivery": (
            isinstance(current_truth, dict)
            and current_truth.get("latest_completed_governance_delivery")
            in {
                "FCF-FCP-0001-DATA-ENTITLEMENT-PROVENANCE-READINESS-FOUNDATION-APP-1",
                "FCF-FCP-0002-COUNTERFACTUAL-RESEARCH-DECISION-JOURNAL-FOUNDATION-APP-1",
                "FCF-FCP-0003-CORRELATED-EVIDENCE-CONFIDENCE-BUDGET-FOUNDATION-APP-1",
                "FCF-FCP-0004-INSTITUTIONAL-CALENDAR-CAUSAL-INTELLIGENCE-RECONCILIATION-APP-1",
                "FCF-FCP-0005-MVP-PRODUCT-READINESS-DECISION-GATE-APP-1",
                "FCF-FCP-0006-A-SHARE-MVP-TARGET-DATA-ACCEPTANCE-BASELINE-APP-1",
                "FCF-FCP-0007-A-SHARE-RQDATA-DEMO-ARTIFACT-INTAKE-REPLAY-ACCEPTANCE-APP-1",
                "FCF-FCP-0008-CHINESE-BROWSER-CONSOLE-LOCAL-DATA-INTAKE-PREVIEW-APP-1",
                "FCF-FCP-0009-PROVIDER-NEUTRAL-MARKET-DATA-ADAPTER-READINESS-APP-1",
                "FCF-FCP-0010-SIMPLIFIED-CHINESE-CONSOLE-LOCALIZATION-CONSISTENCY-APP-1",
                "FCF-FCP-0011-CANDIDATE-DATA-SOURCE-ONBOARDING-EVIDENCE-REVIEW-APP-1",
            }
        ),
        "p48_remains_forbidden": (
            isinstance(safety_boundaries, dict)
            and safety_boundaries.get("p48_allowed") is False
        ),
    }


def build_fcp_0001_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        authority_texts = tuple(
            (root / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS
        )
        approval_text = (root / APPROVAL_PATH).read_text(encoding="ascii")
        final_text = (root / FINAL_PATH).read_text(encoding="ascii")
        manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="ascii"))
        intake = json.loads((root / INTAKE_PATH).read_text(encoding="ascii"))
        files_ascii_and_json = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        authority_texts = ()
        approval_text = ""
        final_text = ""
        manifest = {}
        intake = {}
        files_ascii_and_json = False
    checks = {
        "files_ascii_and_json": files_ascii_and_json,
        "final_document_complete": (
            "Status: COMPLETED_MERGED_VALIDATED" in final_text
            and "FCF-FCP-0001 remains NEEDS_RESEARCH" in " ".join(final_text.split())
            and "No P48 was created." in final_text
        ),
        **validate_fcp_0001_state(
            authority_texts,
            approval_text,
            manifest,
            intake,
            all((root / path).is_file() for path in REQUIRED_DELIVERY_PATHS),
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0001_guard_report()
    if report["ok"] is not True:
        raise SystemExit("FCP-0001 readiness governance guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
