from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0096_registered_factor_registry_runtime_app_1 import (  # noqa: E402
    PHASE_ID,
    build_reference_artifact_bytes,
    build_reference_runtime_snapshot,
    render_runtime_snapshot_json,
)


AUTHORITY_PATHS = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
MARKER = "FCP 0096 REGISTERED FACTOR REGISTRY RUNTIME APP 1"
CONTRACT_PATH = Path(
    "apps/fcp_0096_registered_factor_registry_runtime_app_1/contracts.py"
)
RUNTIME_PATH = Path(
    "apps/fcp_0096_registered_factor_registry_runtime_app_1/runtime.py"
)
BUILDER_PATH = Path(
    "apps/fcp_0096_registered_factor_registry_runtime_app_1/builder.py"
)
APPROVED_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0096_REGISTERED_FACTOR_REGISTRY_RUNTIME_APP_1_APPROVED.md"
)
DELIVERED_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0096_REGISTERED_FACTOR_REGISTRY_RUNTIME_APP_1_DELIVERED.md"
)
FINAL_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0096_REGISTERED_FACTOR_REGISTRY_RUNTIME_APP_1_FINAL.md"
)
D1_D6 = Path(
    "docs/FCF_FCP_0096_REGISTERED_FACTOR_REGISTRY_RUNTIME_APP_1_D1_D6.md"
)
CONTRACT_SHA = "214a006032bb6e8fca1adf6c33a5e33afb6b2333457884fba99abcc4d41cfb07"
RUNTIME_SHA = "436009a6edabec2f0b2ef13c9bb3b4a570df64c80d5e711ed3af624b840cd5da"
BUILDER_SHA = "7eff0f53dbff31fa5f2c7026831ed0bb0fdd96d8f16e4c766a5f24cfa291b031"
ARTIFACT_SHA = "be3e9b4edd3ab38b74459546a73aed8809907f2dfe1c27aee173fd924f8a95f9"
SNAPSHOT_HASH = "c576022a450c15ec3185e6756d2b48998c3ab761eaa95ce657945e0c2be61a40"
OUTPUT_SHA = "574c8467beaf5a70a76b5c27a4d5b7a04a8bdda45b483a6785347ca09eb6cc3d"


def _block(text: str, kind: str) -> str:
    start = f"<!-- {MARKER} {kind} START -->"
    end = f"<!-- {MARKER} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return start + text.split(start, 1)[1].split(end, 1)[0] + end


def build_fcp_0096_guard_report(root: Path = ROOT) -> dict[str, object]:
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
        runtime = (root / RUNTIME_PATH).read_text(encoding="ascii").encode("ascii")
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
        artifact = build_reference_artifact_bytes()
        snapshot = build_reference_runtime_snapshot()
        output = render_runtime_snapshot_json(snapshot).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        authority_texts = ()
        architecture = adr = gap = protocol = memory = ""
        approved = delivered = final = d1_d6 = run_all = ""
        contracts = runtime = builder = artifact = output = b""
        register = manifest = {}
        snapshot = None
        readable = False

    approvals = tuple(_block(text, "APPROVAL") for text in authority_texts)
    locks = tuple(_block(text, "LOCK") for text in authority_texts)
    finals = tuple(_block(text, "FINAL") for text in authority_texts)
    proposal = next(
        (
            item
            for item in register.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0096"
        ),
        {},
    )
    successor = next(
        (
            item
            for item in register.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0097"
        ),
        {},
    )
    truth = manifest.get("current_truth", {})
    phase_complete = proposal.get("status") == "ACCEPTED_ARCHITECTURE"
    expected_proposal = (
        proposal.get("operator_decision")
        == ("ACCEPTED_ARCHITECTURE" if phase_complete else "APPROVED")
        and proposal.get("phase_id") == ("NONE" if phase_complete else PHASE_ID)
        and register.get("next_proposal_sequence") in (99, 100, 101)
        and successor.get("phase_id")
        in (
            "NONE",
            "FCF-FCP-0097-REGISTERED-TARGET-LABEL-REGISTRY-RUNTIME-APP-1",
            "FCF-FCP-0098-REGISTERED-STATE-SYNC-LOCK-RUNTIME-APP-1",
            "FCF-FCP-0099-REGISTERED-MACRO-MICRO-TRANSMISSION-RUNTIME-APP-1",
            "FCF-FCP-0100-REGISTERED-MULTI-HORIZON-CONFLICT-RESOLVER-RUNTIME-APP-1",
        )
    )
    expected_manifest = (
        truth.get("latest_completed_governance_delivery")
        in (
            PHASE_ID,
            "FCF-FCP-0097-REGISTERED-TARGET-LABEL-REGISTRY-RUNTIME-APP-1",
            "FCF-FCP-0098-REGISTERED-STATE-SYNC-LOCK-RUNTIME-APP-1",
            "FCF-FCP-0099-REGISTERED-MACRO-MICRO-TRANSMISSION-RUNTIME-APP-1",
            "FCF-FCP-0100-REGISTERED-MULTI-HORIZON-CONFLICT-RESOLVER-RUNTIME-APP-1",
        )
        and truth.get("current_governance_phase_id")
        in (
            "NONE",
            "FCF-FCP-0097-REGISTERED-TARGET-LABEL-REGISTRY-RUNTIME-APP-1",
            "FCF-FCP-0098-REGISTERED-STATE-SYNC-LOCK-RUNTIME-APP-1",
            "FCF-FCP-0099-REGISTERED-MACRO-MICRO-TRANSMISSION-RUNTIME-APP-1",
            "FCF-FCP-0100-REGISTERED-MULTI-HORIZON-CONFLICT-RESOLVER-RUNTIME-APP-1",
        )
        and truth.get("current_governance_phase_status")
        in ("NONE", "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE")
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
        "architecture_registered": "FCF-V2-REGISTERED-FACTOR-REGISTRY-RUNTIME"
        in architecture,
        "adr_registered": "FCF-V2-ADR-096" in adr,
        "gap_registered": "## FCP-0096 Factor Registry Runtime Boundary" in gap,
        "protocol_registered": "Proposal `FCF-FCP-0096`" in protocol,
        "memory_registered": "FCP-0096 upgrades the completed V2-R11" in memory,
        "proposal_state_exact": expected_proposal,
        "manifest_state_exact": expected_manifest,
        "state_evidence_registered": (
            "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approved
            and (
                "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE" in delivered
                or "COMPLETED_MERGED_VALIDATED" in delivered
            )
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
        "runtime_hash_exact": hashlib.sha256(runtime).hexdigest() == RUNTIME_SHA,
        "builder_hash_exact": hashlib.sha256(builder).hexdigest() == BUILDER_SHA,
        "reference_artifact_exact": hashlib.sha256(artifact).hexdigest()
        == ARTIFACT_SHA,
        "reference_snapshot_exact": snapshot is not None
        and snapshot.snapshot_hash == SNAPSHOT_HASH,
        "reference_output_exact": hashlib.sha256(output).hexdigest() == OUTPUT_SHA,
        "reference_non_authorizing": snapshot is not None
        and snapshot.operator_review_required
        and snapshot.read_only
        and not any(
            (
                snapshot.calculation_activation_allowed,
                snapshot.scoring_allowed,
                snapshot.promotion_allowed,
                snapshot.account_authority,
                snapshot.execution_authority,
            )
        ),
        "run_all_wired": (
            "control_center_fcp_0096_registered_factor_registry_runtime_guard.py"
            in run_all
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0096_guard_report(ROOT)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
