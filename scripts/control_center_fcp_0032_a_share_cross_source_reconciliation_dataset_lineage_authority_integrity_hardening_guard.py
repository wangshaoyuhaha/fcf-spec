from __future__ import annotations

import json
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ID = "FCF-FCP-0032-A-SHARE-CROSS-SOURCE-RECONCILIATION-DATASET-LINEAGE-AUTHORITY-INTEGRITY-HARDENING-APP-1"
AUTHORITIES = tuple(Path(item) for item in (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    "docs/HANDOFF_PROMPT.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
))
APPROVAL_START = "<!-- FCP 0032 A SHARE CROSS SOURCE RECONCILIATION DATASET LINEAGE AUTHORITY INTEGRITY HARDENING APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0032 A SHARE CROSS SOURCE RECONCILIATION DATASET LINEAGE AUTHORITY INTEGRITY HARDENING APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0032 A SHARE CROSS SOURCE RECONCILIATION DATASET LINEAGE AUTHORITY INTEGRITY HARDENING APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0032 A SHARE CROSS SOURCE RECONCILIATION DATASET LINEAGE AUTHORITY INTEGRITY HARDENING APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0032 A SHARE CROSS SOURCE RECONCILIATION DATASET LINEAGE AUTHORITY INTEGRITY HARDENING APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0032 A SHARE CROSS SOURCE RECONCILIATION DATASET LINEAGE AUTHORITY INTEGRITY HARDENING APP 1 FINAL END -->"


def _block(text, start, end):
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start):text.index(end) + len(end)]


def build_fcp_0032_guard_report(root=ROOT):
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        manifest = json.loads((root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii"))
        intake = json.loads((root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(encoding="ascii"))
        contracts = (root / "apps/fcp_0021_a_share_cross_source_quality_reconciliation_app_1/contracts.py").read_text(encoding="ascii")
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, manifest, intake, contracts, run_all, readable = (), {}, {}, "", "", False
    truth = manifest.get("current_truth", {})
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID and status in {
        "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
    }
    closed = truth.get("current_governance_phase_id") == "NONE" and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    proposal = next((item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0032"), {})
    markers = (
        "result requires ordered dataset identity and digest pairs",
        "result finding dataset lineage is not registered",
        "reconciliation authority identities are immutable",
        "zip(dataset_ids, dataset_hashes, strict=True)",
    )
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_validated": status != "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE" or (all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed or (all(finals) and len(set(finals)) == 1),
        "final_evidence_when_closed": not closed or (
            (root / "FCF_CURRENT_STATE_FCP_0032_A_SHARE_CROSS_SOURCE_RECONCILIATION_DATASET_LINEAGE_AUTHORITY_INTEGRITY_HARDENING_APP_1_FINAL.md").is_file()
            and all(finals)
            and all(term in finals[0] for term in (
                "93f3aef26958b1c0b23753dba52e373735c783ad",
                "bb025bcd81e6766d46e5a0d89bf6e28c13f6fe0f",
                "5997 passed",
                "ALL CHECKS PASSED",
            ))
        ),
        "manifest_state_safe": active or closed or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status") == "ACCEPTED_ARCHITECTURE" and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE" and proposal.get("phase_id") == "NONE",
        "result_integrity": all(marker in contracts for marker in markers),
        "delivery_files_exist": all((root / path).is_file() for path in (
            "FCF_CURRENT_STATE_FCP_0032_A_SHARE_CROSS_SOURCE_RECONCILIATION_DATASET_LINEAGE_AUTHORITY_INTEGRITY_HARDENING_APP_1_APPROVED.md",
            "FCF_CURRENT_STATE_FCP_0032_A_SHARE_CROSS_SOURCE_RECONCILIATION_DATASET_LINEAGE_AUTHORITY_INTEGRITY_HARDENING_APP_1_DELIVERED.md",
            "docs/FCF_FCP_0032_A_SHARE_CROSS_SOURCE_RECONCILIATION_DATASET_LINEAGE_AUTHORITY_INTEGRITY_HARDENING_APP_1_D1_D6.md",
            "tests/fcp_0032_a_share_cross_source_reconciliation_dataset_lineage_authority_integrity_hardening_app_1/test_d1_d6.py",
        )),
        "run_all_wired": "control_center_fcp_0032_a_share_cross_source_reconciliation_dataset_lineage_authority_integrity_hardening_guard.py" in run_all,
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE" and truth.get("next_product_implementation_phase") == "NOT_SELECTED" and truth.get("next_product_phase_approval") == "NOT_APPROVED",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main():
    report = build_fcp_0032_guard_report()
    if report["ok"] is not True:
        raise SystemExit("FCP-0032 guard failed: " + ",".join(sorted(k for k, v in report["checks"].items() if not v)))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
