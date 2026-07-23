from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0092_a_share_guojin_qmt_local_cache_probe_operator_review_packet_app_1 import (  # noqa: E402
    DEFAULT_EVIDENCE_REFERENCE,
    build_operator_review_packet,
    render_operator_review_packet_json,
)
from scripts.run_all_checks import COMMANDS  # noqa: E402


AUTHORITY_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    "docs/HANDOFF_PROMPT.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
)
DELIVERY_ID = (
    "FCF-FCP-0092-A-SHARE-GUOJIN-QMT-LOCAL-CACHE-PROBE-OPERATOR-"
    "REVIEW-PACKET-APP-1"
)
PREFIX = (
    "FCP 0092 A SHARE GUOJIN QMT LOCAL CACHE PROBE OPERATOR REVIEW PACKET APP 1"
)
GUARD_PATH = (
    "scripts/control_center_fcp_0092_a_share_guojin_qmt_local_cache_probe_"
    "operator_review_packet_guard.py"
)


def _read_ascii(path: Path) -> str:
    return path.read_text(encoding="ascii")


def _block(text: str, kind: str) -> str | None:
    start = f"<!-- {PREFIX} {kind} START -->"
    end = f"<!-- {PREFIX} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    first = text.index(start)
    last = text.index(end)
    return text[first : last + len(end)] if first < last else None


def build_fcp_0092_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple(_read_ascii(root / path) for path in AUTHORITY_PATHS)
        manifest = json.loads(_read_ascii(root / "FCF_CURRENT_STATE_MANIFEST.json"))
        intake = json.loads(
            _read_ascii(root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json")
        )
        architecture = _read_ascii(
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
        )
        adr = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md")
        gaps = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md")
        protocol = _read_ascii(root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md")
        memory = _read_ascii(root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md")
        builder = _read_ascii(
            root
            / "apps/fcp_0092_a_share_guojin_qmt_local_cache_probe_operator_review_packet_app_1/builder.py"
        )
        delivered = _read_ascii(
            root
            / "FCF_CURRENT_STATE_FCP_0092_A_SHARE_GUOJIN_QMT_LOCAL_CACHE_PROBE_OPERATOR_REVIEW_PACKET_APP_1_DELIVERED.md"
        )
        packet = build_operator_review_packet()
        output = render_operator_review_packet_json(packet).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        texts, manifest, intake = (), {}, {}
        architecture = adr = gaps = protocol = memory = builder = delivered = ""
        packet = None
        output = b""
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
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0092"
        ),
        {},
    )
    required = {
        "FCF_CURRENT_STATE_FCP_0092_A_SHARE_GUOJIN_QMT_LOCAL_CACHE_PROBE_OPERATOR_REVIEW_PACKET_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0092_A_SHARE_GUOJIN_QMT_LOCAL_CACHE_PROBE_OPERATOR_REVIEW_PACKET_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0092_A_SHARE_GUOJIN_QMT_LOCAL_CACHE_PROBE_OPERATOR_REVIEW_PACKET_APP_1_FINAL.md",
        "docs/FCF_FCP_0092_A_SHARE_GUOJIN_QMT_LOCAL_CACHE_PROBE_OPERATOR_REVIEW_PACKET_APP_1_D1_D6.md",
    }
    final_path = next(path for path in required if "FINAL" in path)
    forbidden_builder = (
        "subprocess",
        "socket",
        "requests",
        "xtquant",
        "get_local_data",
        "account_id",
        "credential",
        "price",
        "volume",
        "amount",
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
        or ((root / final_path).is_file() and "ALL CHECKS PASSED" in finals[0]),
        "manifest_state_safe": active
        or closed
        or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status")
        == proposal.get("operator_decision")
        == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and required.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": (
            "## 125. Guojin QMT Local-Cache Probe Operator Review Packet"
            in architecture
        ),
        "adr_registered": "FCF-V2-ADR-092" in adr,
        "gap_preserved": "## FCP-0092 Review Boundary" in gaps
        and "| V2-FR-GAP-104 |" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0092`" in protocol,
        "memory_registered": "FCP-0092 preserves the exact FCP-0091" in memory,
        "builder_is_pure": all(term not in builder for term in forbidden_builder),
        "run_all_wired": ["python", GUARD_PATH] in COMMANDS,
        "reference_hash_exact": DEFAULT_EVIDENCE_REFERENCE.reference_hash
        == "3c866b54a9aec1b00c203430ba76e74271106d6642be4b7c8eb2646e7c1df1dc",
        "packet_hash_exact": packet is not None
        and packet.packet_hash
        == "5dd514d530d33c8256f160141ca3c0e6ee81a0b0f253f65917b7bdfd8f9225a0",
        "output_hash_exact": hashlib.sha256(output).hexdigest()
        == "3cd0f9d2006774e02011698543d47dddbe45a707e54e0339b3695e4794b6196e",
        "delivered_boundary_exact": "acceptance gate: BLOCKED_PENDING_REGISTERED_TERMINAL_PROBE"
        in delivered
        and "GAP-104 remains RESEARCH_REQUIRED" in delivered,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0092_guard_report()
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
