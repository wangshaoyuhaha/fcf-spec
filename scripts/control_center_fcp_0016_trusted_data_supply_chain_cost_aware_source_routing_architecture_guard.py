from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ID = "FCF-FCP-0016-TRUSTED-DATA-SUPPLY-CHAIN-COST-AWARE-SOURCE-ROUTING-ARCHITECTURE-APP-1"
ARCHITECTURE_ID = "FCF-V2-TRUSTED-DATA-SUPPLY-CHAIN-COST-AWARE-ROUTING"
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
APPROVAL_START = "<!-- FCP 0016 TRUSTED DATA SUPPLY CHAIN COST AWARE SOURCE ROUTING ARCHITECTURE APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0016 TRUSTED DATA SUPPLY CHAIN COST AWARE SOURCE ROUTING ARCHITECTURE APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0016 TRUSTED DATA SUPPLY CHAIN COST AWARE SOURCE ROUTING ARCHITECTURE APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0016 TRUSTED DATA SUPPLY CHAIN COST AWARE SOURCE ROUTING ARCHITECTURE APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0016 TRUSTED DATA SUPPLY CHAIN COST AWARE SOURCE ROUTING ARCHITECTURE APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0016 TRUSTED DATA SUPPLY CHAIN COST AWARE SOURCE ROUTING ARCHITECTURE APP 1 FINAL END -->"


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0016_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        manifest = json.loads((root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii"))
        intake = json.loads((root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(encoding="ascii"))
        architecture = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md").read_text(encoding="ascii")
        adr = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md").read_text(encoding="ascii")
        gap = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md").read_text(encoding="ascii")
        protocol = (root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md").read_text(encoding="ascii")
        change = (root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md").read_text(encoding="ascii")
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, manifest, intake = (), {}, {}
        architecture = adr = gap = protocol = change = ""
        readable = False
    truth = manifest.get("current_truth", {})
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID
    closed = truth.get("current_governance_phase_id") == "NONE" and truth.get(
        "latest_completed_governance_delivery"
    ) == DELIVERY_ID
    successor = (
        truth.get("current_governance_phase_id") == DELIVERY_ID.replace(
            "0016-TRUSTED-DATA-SUPPLY-CHAIN-COST-AWARE-SOURCE-ROUTING-ARCHITECTURE",
            "0017-A-SHARE-TRUSTED-DAILY-DATA-SUBSTRATE-LOCAL-CALIBRATION",
        )
        and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    ) or (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery")
        == DELIVERY_ID.replace(
            "0016-TRUSTED-DATA-SUPPLY-CHAIN-COST-AWARE-SOURCE-ROUTING-ARCHITECTURE",
            "0017-A-SHARE-TRUSTED-DAILY-DATA-SUBSTRATE-LOCAL-CALIBRATION",
        )
    )
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    proposal = next(
        (item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0016"),
        {},
    )
    architectures = {
        item.get("architecture_id") for item in manifest.get("accepted_future_architecture", [])
    }
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_validated": status != "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"
        or (len(texts) == 5 and all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed
        or (len(texts) == 5 and all(finals) and len(set(finals)) == 1),
        "manifest_state_safe": active or closed or successor,
        "architecture_registered": ARCHITECTURE_ID in architectures,
        "proposal_registered": proposal.get("status") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE",
        "proposal_sequence": isinstance(intake.get("next_proposal_sequence"), int)
        and intake.get("next_proposal_sequence") >= 17,
        "architecture_complete": all(
            term in architecture
            for term in (
                "## 59. Trusted Data Supply Chain Architecture",
                "## 60. Point-in-Time Availability and Revision Law",
                "## 61. Corporate Action, Price Adjustment, and Trading Status",
                "## 62. Immutable Layered Local Storage",
                "## 63. Reconciliation, Quarantine, and Deterministic Routing",
                "## 64. Candidate Provider Role Boundaries",
                "## 65. A-Share and BTC Source Semantics",
                "## 66. Data Cost and Incremental Value Gate",
                "## 67. Commercial Research and Profitability Boundary",
                "SPLIT_FAULT",
                "xttrade",
            )
        ),
        "adr_sequence": all(f"FCF-V2-ADR-{index:03d}" in adr for index in range(31, 34)),
        "gap_sequence": all(f"V2-FR-GAP-{index:03d}" in gap for index in range(87, 96)),
        "protocols_updated": "FCF-FCP-0016" in change
        and "provider-neutral typed observations" in protocol,
        "delivery_files_exist": all(
            (root / path).is_file()
            for path in (
                "FCF_CURRENT_STATE_FCP_0016_TRUSTED_DATA_SUPPLY_CHAIN_COST_AWARE_SOURCE_ROUTING_ARCHITECTURE_APP_1_APPROVED.md",
                "FCF_CURRENT_STATE_FCP_0016_TRUSTED_DATA_SUPPLY_CHAIN_COST_AWARE_SOURCE_ROUTING_ARCHITECTURE_APP_1_DELIVERED.md",
                "docs/FCF_FCP_0016_TRUSTED_DATA_SUPPLY_CHAIN_COST_AWARE_SOURCE_ROUTING_ARCHITECTURE_APP_1_D1_D6.md",
            )
        ),
        "run_all_wired": "control_center_fcp_0016_trusted_data_supply_chain_cost_aware_source_routing_architecture_guard.py"
        in (root / "scripts/run_all_checks.py").read_text(encoding="ascii"),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0016_guard_report()
    if not report["ok"]:
        failed = sorted(name for name, value in report["checks"].items() if not value)
        raise SystemExit("FCP-0016 guard failed: " + ",".join(failed))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
