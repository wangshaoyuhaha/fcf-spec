from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0085_btc_registered_local_export_validation_runner_app_1.runner import (  # noqa: E402
    build_reference_result,
)
from apps.fcp_0086_btc_registered_local_export_operator_review_packet_app_1 import (  # noqa: E402
    build_operator_review_packet,
    render_operator_review_packet_json,
)


AUTHORITY_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    "docs/HANDOFF_PROMPT.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
)
DELIVERY_ID = "FCF-FCP-0086-BTC-REGISTERED-LOCAL-EXPORT-OPERATOR-REVIEW-PACKET-APP-1"
MARKER = "FCP 0086 BTC REGISTERED LOCAL EXPORT OPERATOR REVIEW PACKET APP 1"
CONTRACT_PATH = "apps/fcp_0086_btc_registered_local_export_operator_review_packet_app_1/contracts.py"
BUILDER_PATH = "apps/fcp_0086_btc_registered_local_export_operator_review_packet_app_1/builder.py"
CONTRACT_SHA = "c49b67a2cebc349c55a3851bde6517e80173883ec13428b0777427d116a8c5b4"
BUILDER_SHA = "cb7524dae8e4b45c5befa8d3d2a5f31fe7ec08385dc4a64246b1cd00f4f44f62"
REFERENCE_PACKET_HASH = "6ca693557d360cebeef516c9ecbc17f11ce003d6ba874696e82eee106b97e88d"
REFERENCE_OUTPUT_SHA = "3ec201a878ccd2091eb678eceee2d866b111e39ea1038ed3582aab76940ab7a7"


def _block(text: str, kind: str) -> str:
    start = f"<!-- {MARKER} {kind} START -->"
    end = f"<!-- {MARKER} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    begin = text.index(start)
    finish = text.index(end, begin) + len(end)
    return text[begin:finish]


def _read_ascii(path: Path) -> str:
    return path.read_text(encoding="ascii")


def build_fcp_0086_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple(_read_ascii(root / path) for path in AUTHORITY_PATHS)
        manifest = json.loads(_read_ascii(root / "FCF_CURRENT_STATE_MANIFEST.json"))
        intake = json.loads(_read_ascii(root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json"))
        architecture = _read_ascii(
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
        )
        adr = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md")
        gaps = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md")
        protocol = _read_ascii(root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md")
        memory = _read_ascii(root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md")
        run_all = _read_ascii(root / "scripts/run_all_checks.py")
        contract_bytes = (root / CONTRACT_PATH).read_bytes()
        builder_bytes = (root / BUILDER_PATH).read_bytes()
        builder_text = builder_bytes.decode("ascii")
        reference = build_operator_review_packet(
            build_reference_result(),
            packet_id="btc-local-export-review-packet-v1",
            packet_created_at_utc="2026-07-21T00:00:21Z",
        )
        reference_output = render_operator_review_packet_json(reference).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        texts, manifest, intake = (), {}, {}
        architecture = adr = gaps = protocol = memory = run_all = builder_text = ""
        contract_bytes = builder_bytes = reference_output = b""
        reference = None
        readable = False
    truth = manifest.get("current_truth", {})
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID and status in {
        "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
    }
    closed = (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    )
    approvals = tuple(_block(text, "APPROVAL") for text in texts)
    locks = tuple(_block(text, "LOCK") for text in texts)
    finals = tuple(_block(text, "FINAL") for text in texts)
    proposal = next(
        (item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0086"),
        {},
    )
    expected = {
        "FCF_CURRENT_STATE_FCP_0086_BTC_REGISTERED_LOCAL_EXPORT_OPERATOR_REVIEW_PACKET_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0086_BTC_REGISTERED_LOCAL_EXPORT_OPERATOR_REVIEW_PACKET_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0086_BTC_REGISTERED_LOCAL_EXPORT_OPERATOR_REVIEW_PACKET_APP_1_FINAL.md",
        "docs/FCF_FCP_0086_BTC_REGISTERED_LOCAL_EXPORT_OPERATOR_REVIEW_PACKET_APP_1_D1_D6.md",
    }
    gap_row = next((line for line in gaps.splitlines() if "| V2-FR-GAP-095 |" in line), "")
    prohibited = (
        "import requests",
        "import socket",
        "import urllib",
        "import websocket",
        "import ccxt",
        "from ccxt",
        "import binance",
        "from binance",
    )
    delivered = next(path for path in expected if "DELIVERED" in path)
    final = next(path for path in expected if "FINAL" in path)
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_implemented": status not in {
            "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
            "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
        } or (all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed or (all(finals) and len(set(finals)) == 1),
        "final_evidence_when_closed": not closed
        or ((root / final).is_file() and all(finals) and "ALL CHECKS PASSED" in finals[0]),
        "manifest_state_safe": active or closed or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status")
        == proposal.get("operator_decision")
        == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and expected.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": all(
            term in architecture
            for term in (
                "## 119. BTC Registered Local Export Operator Review Packet",
                "closed checklist",
                "cannot decide, approve, reject",
            )
        ),
        "adr_registered": all(
            term in adr
            for term in (
                "FCF-V2-ADR-086",
                "Require An Undecided BTC Local Export Review Packet",
                "exact typed FCP-0085 validation result",
            )
        ),
        "gap_preserved": "| RESEARCH_REQUIRED |" in gap_row,
        "gap_observation_registered": "FCP-0086 is approved" in gaps and "GAP-095" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0086`" in protocol and "FCP-0085" in protocol,
        "memory_registered": "FCP-0086 preserves one FCP-0085 result" in memory,
        "run_all_wired": (
            "control_center_fcp_0086_btc_registered_local_export_operator_review_packet_guard.py"
            in run_all
        ),
        "contract_hash_exact": hashlib.sha256(contract_bytes).hexdigest() == CONTRACT_SHA,
        "builder_hash_exact": hashlib.sha256(builder_bytes).hexdigest() == BUILDER_SHA,
        "reference_packet_hash_exact": reference is not None
        and reference.packet_hash == REFERENCE_PACKET_HASH,
        "reference_output_hash_exact": hashlib.sha256(reference_output).hexdigest()
        == REFERENCE_OUTPUT_SHA,
        "reference_non_authorizing": reference is not None
        and reference.operator_review_required is True
        and reference.disposition_assigned is False
        and reference.evidence_promotion_allowed is False
        and reference.replay_activation_allowed is False
        and reference.gap_closed is False
        and reference.execution_allowed is False,
        "builder_reuses_frozen_authority": (
            "BTCLocalExportValidationResult" in builder_text
            and "fcp_0085_btc_registered_local_export" in builder_text
            and not any(term in builder_text for term in prohibited)
        ),
        "delivery_files_exist": all(
            (root / path).is_file()
            for path in expected
            if "DELIVERED" not in path and "FINAL" not in path
        )
        and ((root / delivered).is_file() if status != "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" or closed else True)
        and ((root / final).is_file() if closed else True),
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0086_guard_report()
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
