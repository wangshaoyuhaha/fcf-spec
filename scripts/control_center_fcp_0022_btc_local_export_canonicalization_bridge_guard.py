from __future__ import annotations

import json
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ID = "FCF-FCP-0022-BTC-LOCAL-EXPORT-CANONICALIZATION-BRIDGE-APP-1"
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
APPROVAL_START = "<!-- FCP 0022 BTC LOCAL EXPORT CANONICALIZATION BRIDGE APP 1 APPROVAL START -->"
APPROVAL_END = "<!-- FCP 0022 BTC LOCAL EXPORT CANONICALIZATION BRIDGE APP 1 APPROVAL END -->"
LOCK_START = "<!-- FCP 0022 BTC LOCAL EXPORT CANONICALIZATION BRIDGE APP 1 LOCK START -->"
LOCK_END = "<!-- FCP 0022 BTC LOCAL EXPORT CANONICALIZATION BRIDGE APP 1 LOCK END -->"
FINAL_START = "<!-- FCP 0022 BTC LOCAL EXPORT CANONICALIZATION BRIDGE APP 1 FINAL START -->"
FINAL_END = "<!-- FCP 0022 BTC LOCAL EXPORT CANONICALIZATION BRIDGE APP 1 FINAL END -->"


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0022_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        intake = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        contracts = (
            root
            / "apps/fcp_0022_btc_local_export_canonicalization_bridge_app_1/contracts.py"
        ).read_text(encoding="ascii")
        bridge = (
            root / "apps/fcp_0022_btc_local_export_canonicalization_bridge_app_1/bridge.py"
        ).read_text(encoding="ascii")
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, manifest, intake, contracts, bridge = (), {}, {}, "", ""
        readable = False
    truth = manifest.get("current_truth", {})
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID and status in {
        "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
    }
    closed = truth.get("current_governance_phase_id") == "NONE" and truth.get(
        "latest_completed_governance_delivery"
    ) == DELIVERY_ID
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0022"
        ),
        {},
    )
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_validated": status != "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"
        or (len(texts) == 5 and all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed
        or (len(texts) == 5 and all(finals) and len(set(finals)) == 1),
        "manifest_state_safe": active
        or closed
        or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE",
        "contracts_complete": all(
            term in contracts
            for term in (
                "RegisteredBTCLocalExport",
                "BTCLocalExportProfile",
                "BTCLocalExportBridgeManifest",
                "BTCLocalExportBridgeResult",
                "MappingProxyType",
                "provider-unselected",
            )
        ),
        "bridge_fail_closed": all(
            term in bridge
            for term in (
                "registered local export byte length mismatch",
                "registered local export SHA-256 mismatch",
                "registered local export contains invalid NDJSON",
                "source row lacks required field",
                "duplicate observation_id",
                "future ingestion",
                "BTCBookSnapshot",
                "BTCBookDelta",
                "BTCReferencePriceObservation",
                "BTCFundingObservation",
            )
        ),
        "delivery_files_exist": all(
            (root / path).is_file()
            for path in (
                "FCF_CURRENT_STATE_FCP_0022_BTC_LOCAL_EXPORT_CANONICALIZATION_BRIDGE_APP_1_APPROVED.md",
                "FCF_CURRENT_STATE_FCP_0022_BTC_LOCAL_EXPORT_CANONICALIZATION_BRIDGE_APP_1_DELIVERED.md",
                "docs/FCF_FCP_0022_BTC_LOCAL_EXPORT_CANONICALIZATION_BRIDGE_APP_1_D1_D6.md",
                "tests/fcp_0022_btc_local_export_canonicalization_bridge_app_1/test_d1_d6.py",
            )
        ),
        "run_all_wired": "control_center_fcp_0022_btc_local_export_canonicalization_bridge_guard.py"
        in (root / "scripts/run_all_checks.py").read_text(encoding="ascii"),
        "no_provider_runtime": all(
            term not in (contracts + bridge).lower()
            for term in (
                "import requests",
                "import socket",
                "import websocket",
                "import ccxt",
                "api_key",
                "secret_key",
                "password",
            )
        ),
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE"
        and truth.get("next_product_implementation_phase") == "NOT_SELECTED"
        and truth.get("next_product_phase_approval") == "NOT_APPROVED",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0022_guard_report()
    if not report["ok"]:
        failed = sorted(name for name, value in report["checks"].items() if not value)
        raise SystemExit("FCP-0022 guard failed: " + ",".join(failed))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
