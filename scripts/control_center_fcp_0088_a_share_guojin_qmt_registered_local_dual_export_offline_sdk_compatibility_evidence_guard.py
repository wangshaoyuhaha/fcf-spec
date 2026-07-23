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

from apps.fcp_0088_a_share_guojin_qmt_registered_local_dual_export_offline_sdk_compatibility_evidence_app_1 import (  # noqa: E402
    build_reference_evidence,
    render_compatibility_evidence_json,
)


AUTHORITY_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    "docs/HANDOFF_PROMPT.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
)
DELIVERY_ID = (
    "FCF-FCP-0088-A-SHARE-GUOJIN-QMT-REGISTERED-LOCAL-DUAL-EXPORT-"
    "OFFLINE-SDK-COMPATIBILITY-EVIDENCE-APP-1"
)
MARKER = (
    "FCP 0088 A SHARE GUOJIN QMT REGISTERED LOCAL DUAL EXPORT OFFLINE SDK "
    "COMPATIBILITY EVIDENCE APP 1"
)
CONTRACT_PATH = (
    "apps/fcp_0088_a_share_guojin_qmt_registered_local_dual_export_offline_"
    "sdk_compatibility_evidence_app_1/contracts.py"
)
CONTRACT_SHA = "bb15419efd3b45ee37fc05b9e5ee8507f363670fe78b5db451bf79a1d895b1f1"
REFERENCE_EVIDENCE_HASH = (
    "fd0760c7f04012d0ba3db0b2af43233579b111fafdd04be14fe2e9b4e8ee8509"
)
REFERENCE_OUTPUT_SHA = (
    "2f86c7b4b7c63f538ee6cebdf5ff463e05600792911a27517dfa378875abda64"
)
OBSERVED_EVIDENCE_HASH = (
    "4d6f4924326be8ffa9e72d055196a242488ab46e6b239030becea4cd17f0ada5"
)


def _block(text: str, kind: str) -> str:
    start = f"<!-- {MARKER} {kind} START -->"
    end = f"<!-- {MARKER} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    begin = text.index(start)
    return text[begin : text.index(end, begin) + len(end)]


def _read_ascii(path: Path) -> str:
    return path.read_text(encoding="ascii")


def build_fcp_0088_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple(_read_ascii(root / path) for path in AUTHORITY_PATHS)
        manifest = json.loads(_read_ascii(root / "FCF_CURRENT_STATE_MANIFEST.json"))
        intake = json.loads(
            _read_ascii(root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json")
        )
        architecture = _read_ascii(
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
        )
        adr = _read_ascii(
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md"
        )
        gaps = _read_ascii(
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
        )
        protocol = _read_ascii(root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md")
        memory = _read_ascii(
            root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md"
        )
        run_all = _read_ascii(root / "scripts/run_all_checks.py")
        contract_bytes = (root / CONTRACT_PATH).read_bytes()
        contract_text = contract_bytes.decode("ascii")
        delivered_text = _read_ascii(
            root
            / "FCF_CURRENT_STATE_FCP_0088_A_SHARE_GUOJIN_QMT_REGISTERED_LOCAL_DUAL_EXPORT_OFFLINE_SDK_COMPATIBILITY_EVIDENCE_APP_1_DELIVERED.md"
        )
        reference = build_reference_evidence()
        reference_output = render_compatibility_evidence_json(reference).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        texts, manifest, intake = (), {}, {}
        architecture = adr = gaps = protocol = memory = run_all = ""
        contract_text = delivered_text = ""
        contract_bytes = reference_output = b""
        reference = None
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
    approvals = tuple(_block(text, "APPROVAL") for text in texts)
    locks = tuple(_block(text, "LOCK") for text in texts)
    finals = tuple(_block(text, "FINAL") for text in texts)
    proposal = next(
        (item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0088"),
        {},
    )
    expected = {
        "FCF_CURRENT_STATE_FCP_0088_A_SHARE_GUOJIN_QMT_REGISTERED_LOCAL_DUAL_EXPORT_OFFLINE_SDK_COMPATIBILITY_EVIDENCE_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0088_A_SHARE_GUOJIN_QMT_REGISTERED_LOCAL_DUAL_EXPORT_OFFLINE_SDK_COMPATIBILITY_EVIDENCE_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0088_A_SHARE_GUOJIN_QMT_REGISTERED_LOCAL_DUAL_EXPORT_OFFLINE_SDK_COMPATIBILITY_EVIDENCE_APP_1_FINAL.md",
        "docs/FCF_FCP_0088_A_SHARE_GUOJIN_QMT_REGISTERED_LOCAL_DUAL_EXPORT_OFFLINE_SDK_COMPATIBILITY_EVIDENCE_APP_1_D1_D6.md",
    }
    final = next(path for path in expected if "FINAL" in path)
    gap_rows = tuple(
        next(
            (line for line in gaps.splitlines() if f"| V2-FR-GAP-{number} |" in line),
            "",
        )
        for number in ("104", "105", "106")
    )
    prohibited = (
        "import requests",
        "import socket",
        "import urllib",
        "import websocket",
        "connect(",
        "subscribe_quote",
        "get_market_data",
        "xttrader",
    )
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5
        and all(approvals)
        and len(set(approvals)) == 1,
        "lock_exact_when_implemented": status
        not in {
            "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
            "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
        }
        or (all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed
        or (all(finals) and len(set(finals)) == 1),
        "final_evidence_when_closed": not closed
        or ((root / final).is_file() and "ALL CHECKS PASSED" in finals[0]),
        "manifest_state_safe": active
        or closed
        or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status")
        == proposal.get("operator_decision")
        == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and expected.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": (
            "## 121. Guojin QMT Dual Export And Offline SDK Compatibility Evidence"
            in architecture
        ),
        "adr_registered": "FCF-V2-ADR-088" in adr
        and "Preserve Dual Export And Offline SDK Compatibility As Evidence" in adr,
        "gaps_preserved": all("| RESEARCH_REQUIRED |" in row for row in gap_rows)
        and "## FCP-0088 Evidence Boundary" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0088`" in protocol
        and "FCP-0035" in protocol
        and "FCP-0084" in protocol,
        "memory_registered": "FCP-0088 preserves exact Guojin QMT" in memory,
        "run_all_wired": (
            "control_center_fcp_0088_a_share_guojin_qmt_registered_local_dual_export_offline_sdk_compatibility_evidence_guard.py"
            in run_all
        ),
        "contract_hash_exact": hashlib.sha256(contract_bytes).hexdigest()
        == CONTRACT_SHA,
        "reference_evidence_hash_exact": reference is not None
        and reference.evidence_hash == REFERENCE_EVIDENCE_HASH,
        "reference_output_hash_exact": hashlib.sha256(reference_output).hexdigest()
        == REFERENCE_OUTPUT_SHA,
        "reference_non_authorizing": reference is not None
        and reference.sdk_observation.connection_attempted is False
        and reference.sdk_observation.network_used is False
        and reference.entitlement_proven is False
        and reference.provider_selected is False
        and reference.realtime_activation_allowed is False
        and reference.registered_evidence_promotion_allowed is False
        and reference.gap_closed is False
        and reference.execution_allowed is False,
        "contract_reuses_frozen_authorities": (
            "QmtFrontAdjustmentReference" in contract_text
            and "QmtLocalExportCoverageEvidence" in contract_text
            and not any(term in contract_text for term in prohibited)
        ),
        "observed_evidence_registered": OBSERVED_EVIDENCE_HASH in delivered_text
        and "rows: 500" in delivered_text
        and "connection attempted and network used: false" in delivered_text,
        "delivery_files_exist": all(
            (root / path).is_file()
            for path in expected
            if "FINAL" not in path
        )
        and ((root / final).is_file() if closed else True),
        "no_product_phase": truth.get("current_product_implementation_phase")
        == "NONE",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0088_guard_report()
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
