from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0095_a_share_qmt_local_export_continuity_routing_app_1 import (  # noqa: E402
    PHASE_ID,
    build_continuity_route,
    build_registered_runtime_evidence,
    render_continuity_route_json,
)


AUTHORITY_PATHS = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
MARKER = "FCP 0095 A SHARE QMT LOCAL EXPORT CONTINUITY ROUTING APP 1"
CONTRACT_PATH = Path(
    "apps/fcp_0095_a_share_qmt_local_export_continuity_routing_app_1/"
    "contracts.py"
)
BUILDER_PATH = Path(
    "apps/fcp_0095_a_share_qmt_local_export_continuity_routing_app_1/"
    "builder.py"
)
APPROVED_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0095_A_SHARE_QMT_LOCAL_EXPORT_CONTINUITY_"
    "ROUTING_APP_1_APPROVED.md"
)
DELIVERED_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0095_A_SHARE_QMT_LOCAL_EXPORT_CONTINUITY_"
    "ROUTING_APP_1_DELIVERED.md"
)
FINAL_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0095_A_SHARE_QMT_LOCAL_EXPORT_CONTINUITY_"
    "ROUTING_APP_1_FINAL.md"
)
D1_D6 = Path(
    "docs/FCF_FCP_0095_A_SHARE_QMT_LOCAL_EXPORT_CONTINUITY_ROUTING_"
    "APP_1_D1_D6.md"
)
CONTRACT_SHA = "ca494a3798962bcdb67a8b8231138fe411c5185df30b4540f83e720fdb02cf45"
BUILDER_SHA = "0ecbb81ce34cc8e4a8546b751a44b41938dbb5bee8a6950b6a935b9a2b78cfe7"
EVIDENCE_HASH = "b185df88a3c293c5b32629227c25faac78a897a4f0248c84fdea28f41935a3cc"
ROUTE_HASH = "6e36886f8c953252fffa0f0dd20b1d6ae12fee8ddf817681a2f3e3eba5a3a6f4"
OUTPUT_SHA = "f3d2d4e57f570ed3a0cced83101fc6c99233e5358ed46fce745e9724d458de74"


def _block(text: str, kind: str) -> str:
    start = f"<!-- {MARKER} {kind} START -->"
    end = f"<!-- {MARKER} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return start + text.split(start, 1)[1].split(end, 1)[0] + end


def build_fcp_0095_guard_report(root: Path = ROOT) -> dict[str, object]:
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
        contracts = (root / CONTRACT_PATH).read_text(encoding="ascii").encode("ascii")
        builder = (root / BUILDER_PATH).read_text(encoding="ascii").encode("ascii")
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        register = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        final = (
            (root / FINAL_STATE).read_text(encoding="ascii")
            if (root / FINAL_STATE).is_file()
            else ""
        )
        evidence = build_registered_runtime_evidence()
        route = build_continuity_route()
        output = render_continuity_route_json(route).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        authority_texts = ()
        architecture = adr = gap = protocol = memory = ""
        approved = delivered = final = d1_d6 = run_all = ""
        contracts = builder = output = b""
        register = manifest = {}
        evidence = route = None
        readable = False

    approvals = tuple(_block(text, "APPROVAL") for text in authority_texts)
    locks = tuple(_block(text, "LOCK") for text in authority_texts)
    finals = tuple(_block(text, "FINAL") for text in authority_texts)
    proposal = next(
        (
            item
            for item in register.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0095"
        ),
        {},
    )
    truth = manifest.get("current_truth", {})
    phase_complete = proposal.get("status") == "ACCEPTED_ARCHITECTURE"
    expected_proposal = (
        proposal.get("operator_decision")
        == ("ACCEPTED_ARCHITECTURE" if phase_complete else "APPROVED")
        and proposal.get("phase_id") == ("NONE" if phase_complete else PHASE_ID)
        and register.get("next_proposal_sequence") == 96
    )
    expected_manifest = (
        truth.get("latest_completed_governance_delivery") == PHASE_ID
        and truth.get("current_governance_phase_id") == "NONE"
        and truth.get("current_governance_phase_status") == "NONE"
        if phase_complete
        else truth.get("current_governance_phase_id") == PHASE_ID
        and truth.get("current_governance_phase_status")
        == "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"
    )
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(approvals) == 5
        and all(approvals)
        and len(set(approvals)) == 1,
        "lock_exact": len(locks) == 5 and all(locks) and len(set(locks)) == 1,
        "final_exact_when_complete": (
            not phase_complete
            or len(finals) == 5
            and all(finals)
            and len(set(finals)) == 1
        ),
        "architecture_registered": (
            "FCF-V2-A-SHARE-QMT-LOCAL-EXPORT-CONTINUITY-ROUTING"
            in architecture
        ),
        "adr_registered": "FCF-V2-ADR-095" in adr,
        "gap_registered": "## FCP-0095 Continuity Boundary" in gap,
        "protocol_registered": "Proposal `FCF-FCP-0095`" in protocol,
        "memory_registered": "FCP-0095 preserves exact QMT terminal-observed" in memory,
        "proposal_state_exact": expected_proposal,
        "manifest_state_exact": expected_manifest,
        "state_evidence_registered": (
            "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approved
            and (
                "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE" in delivered
                or "COMPLETED_MERGED_VALIDATED" in delivered
            )
            and EVIDENCE_HASH in delivered
            and ROUTE_HASH in delivered
            and OUTPUT_SHA in delivered
            and (
                not phase_complete
                or "COMPLETED_MERGED_VALIDATED" in final
                and str(FINAL_STATE) in proposal.get("evidence_refs", [])
            )
        ),
        "d1_d6_registered": all(
            f"## D{number} " in d1_d6 for number in range(1, 7)
        ),
        "contract_hash_exact": hashlib.sha256(contracts).hexdigest()
        == CONTRACT_SHA,
        "builder_hash_exact": hashlib.sha256(builder).hexdigest() == BUILDER_SHA,
        "reference_evidence_exact": evidence is not None
        and evidence.evidence_hash == EVIDENCE_HASH,
        "reference_route_exact": route is not None
        and route.route_hash == ROUTE_HASH
        and route.miniqmt_route_state == "DEFERRED_NON_BLOCKING"
        and route.active_research_route == "REGISTERED_QMT_LOCAL_EXPORT",
        "reference_output_exact": hashlib.sha256(output).hexdigest() == OUTPUT_SHA,
        "reference_non_authorizing": route is not None
        and not any(
            (
                route.provider_selection_authority,
                route.data_promotion_authority,
                route.realtime_activation_authority,
                route.product_authority,
                route.account_authority,
                route.execution_authority,
            )
        ),
        "run_all_wired": (
            "control_center_fcp_0095_a_share_qmt_local_export_continuity_"
            "routing_guard.py" in run_all
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0095_guard_report(ROOT)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
