from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0094_btc_coin_metrics_reference_rate_operator_review_packet_app_1 import (  # noqa: E402
    PHASE_ID,
    build_operator_review_packet,
    build_registered_sample_validation_result,
    render_operator_review_packet_json,
)


AUTHORITY_PATHS = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
MARKER = (
    "FCP 0094 BTC COIN METRICS REFERENCE RATE OPERATOR REVIEW PACKET APP 1"
)
CONTRACT_PATH = Path(
    "apps/fcp_0094_btc_coin_metrics_reference_rate_operator_review_packet_"
    "app_1/contracts.py"
)
BUILDER_PATH = Path(
    "apps/fcp_0094_btc_coin_metrics_reference_rate_operator_review_packet_"
    "app_1/builder.py"
)
APPROVED_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0094_BTC_COIN_METRICS_REFERENCE_RATE_OPERATOR_"
    "REVIEW_PACKET_APP_1_APPROVED.md"
)
DELIVERED_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0094_BTC_COIN_METRICS_REFERENCE_RATE_OPERATOR_"
    "REVIEW_PACKET_APP_1_DELIVERED.md"
)
D1_D6 = Path(
    "docs/FCF_FCP_0094_BTC_COIN_METRICS_REFERENCE_RATE_OPERATOR_REVIEW_"
    "PACKET_APP_1_D1_D6.md"
)
CONTRACT_SHA = "b640757e8441a46532ac408db10d609e5b59522bdd905c14f8eadffbb44751c7"
BUILDER_SHA = "6597f76fbd49dc0fd16f06d508d3dd45ba50a66ba5011548ba504edf85b5f5e9"
VALIDATION_HASH = "689317437eec53117d195c39803d1f759102682aaf416aa4aae2afbbfb3f0e27"
PACKET_HASH = "9c4263ddd8e9102e4b32607bf1da659f4101a196fe03aa4ad4945586c52352f1"
OUTPUT_SHA = "d315473e75341ca6d96da813c710e8277510308f70f1fe83f26d0e5ec48298ca"


def _block(text: str, kind: str) -> str:
    start = f"<!-- {MARKER} {kind} START -->"
    end = f"<!-- {MARKER} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return start + text.split(start, 1)[1].split(end, 1)[0] + end


def build_fcp_0094_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        authority_texts = tuple(
            (root / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS
        )
        architecture = (
            root / "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"
        ).read_text(encoding="ascii")
        adr = (
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md"
        ).read_text(encoding="ascii")
        gap = (
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
        ).read_text(encoding="ascii")
        protocol = (
            root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md"
        ).read_text(encoding="ascii")
        memory = (
            root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md"
        ).read_text(encoding="ascii")
        approved = (root / APPROVED_STATE).read_text(encoding="ascii")
        delivered = (root / DELIVERED_STATE).read_text(encoding="ascii")
        d1_d6 = (root / D1_D6).read_text(encoding="ascii")
        contracts = (root / CONTRACT_PATH).read_bytes()
        builder = (root / BUILDER_PATH).read_bytes()
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        register = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        packet = build_operator_review_packet(
            build_registered_sample_validation_result(),
            packet_id="coin-metrics-btc-reference-review-packet-v1",
            packet_created_at_utc="2026-07-23T04:11:00Z",
        )
        output = render_operator_review_packet_json(packet).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        authority_texts = ()
        architecture = adr = gap = protocol = memory = ""
        approved = delivered = d1_d6 = run_all = ""
        contracts = builder = output = b""
        register = manifest = {}
        packet = None
        readable = False
    approvals = tuple(_block(text, "APPROVAL") for text in authority_texts)
    locks = tuple(_block(text, "LOCK") for text in authority_texts)
    proposal = next(
        (
            item
            for item in register.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0094"
        ),
        {},
    )
    truth = manifest.get("current_truth", {})
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(approvals) == 5
        and all(approvals)
        and len(set(approvals)) == 1,
        "lock_exact": len(locks) == 5 and all(locks) and len(set(locks)) == 1,
        "architecture_registered": (
            "FCF-V2-BTC-COIN-METRICS-REFERENCE-RATE-OPERATOR-REVIEW-PACKET"
            in architecture
        ),
        "adr_registered": "FCF-V2-ADR-094" in adr,
        "gap_registered": "## FCP-0094 Review Boundary" in gap,
        "protocol_registered": "Proposal `FCF-FCP-0094`" in protocol,
        "memory_registered": "FCP-0094 preserves the exact typed FCP-0093" in memory,
        "proposal_active_exact": proposal.get("status") == "APPROVED_FOR_PHASE"
        and proposal.get("operator_decision") == "APPROVED"
        and proposal.get("phase_id") == PHASE_ID
        and register.get("next_proposal_sequence") == 95,
        "manifest_active_exact": (
            truth.get("current_governance_phase_id") == PHASE_ID
            and truth.get("current_governance_phase_status")
            == "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"
        ),
        "state_evidence_registered": (
            "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approved
            and "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE" in delivered
            and VALIDATION_HASH in delivered
            and PACKET_HASH in delivered
            and OUTPUT_SHA in delivered
        ),
        "d1_d6_registered": all(
            f"## D{number} " in d1_d6 for number in range(1, 7)
        ),
        "contract_hash_exact": hashlib.sha256(contracts).hexdigest()
        == CONTRACT_SHA,
        "builder_hash_exact": hashlib.sha256(builder).hexdigest() == BUILDER_SHA,
        "reference_packet_exact": packet is not None
        and packet.validation_result_hash == VALIDATION_HASH
        and packet.packet_hash == PACKET_HASH,
        "reference_output_exact": hashlib.sha256(output).hexdigest() == OUTPUT_SHA,
        "reference_non_authorizing": packet is not None
        and packet.review_state == "OPERATOR_REVIEW_REQUIRED"
        and packet.acceptance_gate == "BLOCKED_PENDING_OPERATOR_DISPOSITION"
        and packet.disposition_assigned is False
        and packet.data_promotion_allowed is False
        and packet.execution_allowed is False,
        "run_all_wired": (
            "control_center_fcp_0094_btc_coin_metrics_reference_rate_operator_"
            "review_packet_guard.py" in run_all
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0094_guard_report(ROOT)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
