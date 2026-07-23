from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0099_registered_macro_micro_transmission_runtime_app_1 import (  # noqa: E402
    CHAIN_LEVELS,
    PHASE_ID,
    build_reference_artifact_bytes,
    build_reference_transmission_snapshot,
    render_transmission_snapshot_json,
)


AUTHORITY_PATHS = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
MARKER = "FCP 0099 REGISTERED MACRO MICRO TRANSMISSION RUNTIME APP 1"
APPROVED = Path(
    "FCF_CURRENT_STATE_FCP_0099_REGISTERED_MACRO_MICRO_TRANSMISSION_RUNTIME_APP_1_APPROVED.md"
)
DELIVERED = Path(
    "FCF_CURRENT_STATE_FCP_0099_REGISTERED_MACRO_MICRO_TRANSMISSION_RUNTIME_APP_1_DELIVERED.md"
)
FINAL = Path(
    "FCF_CURRENT_STATE_FCP_0099_REGISTERED_MACRO_MICRO_TRANSMISSION_RUNTIME_APP_1_FINAL.md"
)
D1_D6 = Path(
    "docs/FCF_FCP_0099_REGISTERED_MACRO_MICRO_TRANSMISSION_RUNTIME_APP_1_D1_D6.md"
)
SOURCE_HASHES = {
    "contracts.py": "98d66b5b5dc60c11e62b2844f97b8553be17ff06cf1bb9fd90b38c3bca843096",
    "runtime.py": "67289d8f59b153cb684d7340f9df0ccb75ac8fffe428b2a48231262dbd4275dd",
    "builder.py": "89e754cb1a87893c79f19871ce00adb33df2e4909559eacc24320c204d0846eb",
}
ARTIFACT_SHA = "d6443cca9fa39913a6fc5847f5656679faf439e2c2dbb273a01eca8f8c96e4ea"
SNAPSHOT_HASH = "a423220725fc7c2c9874d979b408f3bb5b2b2a2573e9781e3d441e5bb7227c85"
OUTPUT_SHA = "32ec1db88c5db178594c92a3c6665879f5f555f1a0babfec6fe21e8af6903425"


def _block(text: str, kind: str) -> str:
    start = f"<!-- {MARKER} {kind} START -->"
    end = f"<!-- {MARKER} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return start + text.split(start, 1)[1].split(end, 1)[0] + end


def build_fcp_0099_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        authorities = tuple(
            (root / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS
        )
        register = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        texts = {
            "architecture": (
                root / "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"
            ).read_text(encoding="ascii"),
            "adr": (
                root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md"
            ).read_text(encoding="ascii"),
            "gap": (
                root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
            ).read_text(encoding="ascii"),
            "protocol": (
                root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md"
            ).read_text(encoding="ascii"),
            "memory": (
                root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md"
            ).read_text(encoding="ascii"),
            "approved": (root / APPROVED).read_text(encoding="ascii"),
            "delivered": (root / DELIVERED).read_text(encoding="ascii"),
            "d1_d6": (root / D1_D6).read_text(encoding="ascii"),
            "run_all": (root / "scripts/run_all_checks.py").read_text(
                encoding="ascii"
            ),
        }
        final = (
            (root / FINAL).read_text(encoding="ascii")
            if (root / FINAL).is_file()
            else ""
        )
        source = root / "apps/fcp_0099_registered_macro_micro_transmission_runtime_app_1"
        source_hashes = {
            name: hashlib.sha256(
                (source / name).read_text(encoding="ascii").encode("ascii")
            ).hexdigest()
            for name in SOURCE_HASHES
        }
        artifact = build_reference_artifact_bytes()
        snapshot = build_reference_transmission_snapshot()
        output = render_transmission_snapshot_json(snapshot).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        authorities = ()
        register = manifest = {}
        texts = {}
        final = ""
        source_hashes = {}
        artifact = output = b""
        snapshot = None
        readable = False
    proposal = next(
        (
            item
            for item in register.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0099"
        ),
        {},
    )
    complete = proposal.get("status") == "ACCEPTED_ARCHITECTURE"
    truth = manifest.get("current_truth", {})
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len({_block(text, "APPROVAL") for text in authorities})
        == 1
        and all(_block(text, "APPROVAL") for text in authorities),
        "lock_exact": len({_block(text, "LOCK") for text in authorities}) == 1
        and all(_block(text, "LOCK") for text in authorities),
        "final_exact_when_complete": not complete
        or len({_block(text, "FINAL") for text in authorities}) == 1
        and all(_block(text, "FINAL") for text in authorities),
        "architecture_registered": (
            "FCF-V2-REGISTERED-MACRO-MICRO-TRANSMISSION-RUNTIME"
            in texts.get("architecture", "")
        ),
        "adr_registered": "FCF-V2-ADR-099" in texts.get("adr", ""),
        "gap_registered": (
            "## FCP-0099 Macro-to-Micro Transmission Runtime Boundary"
            in texts.get("gap", "")
        ),
        "protocol_registered": "Proposal `FCF-FCP-0099`"
        in texts.get("protocol", ""),
        "memory_registered": "FCP-0099 upgrades the completed V2-R25"
        in texts.get("memory", ""),
        "proposal_state_exact": proposal.get("operator_decision")
        == ("ACCEPTED_ARCHITECTURE" if complete else "APPROVED")
        and proposal.get("phase_id") == ("NONE" if complete else PHASE_ID)
        and register.get("next_proposal_sequence") == 100,
        "manifest_state_exact": truth.get("latest_completed_governance_delivery")
        == (
            PHASE_ID
            if complete
            else "FCF-FCP-0098-REGISTERED-STATE-SYNC-LOCK-RUNTIME-APP-1"
        )
        and truth.get("current_governance_phase_id")
        == ("NONE" if complete else PHASE_ID),
        "state_evidence_registered": (
            "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in texts.get("approved", "")
            and (
                "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"
                in texts.get("delivered", "")
                or "COMPLETED_MERGED_VALIDATED" in texts.get("delivered", "")
            )
            and (
                not complete
                or "COMPLETED_MERGED_VALIDATED" in final
                and str(FINAL) in proposal.get("evidence_refs", [])
            )
        ),
        "d1_d6_registered": all(
            f"## D{number} " in texts.get("d1_d6", "") for number in range(1, 7)
        ),
        "source_hashes_exact": source_hashes == SOURCE_HASHES,
        "reference_artifact_exact": hashlib.sha256(artifact).hexdigest()
        == ARTIFACT_SHA,
        "reference_snapshot_exact": snapshot is not None
        and snapshot.snapshot_hash == SNAPSHOT_HASH,
        "reference_output_exact": hashlib.sha256(output).hexdigest() == OUTPUT_SHA,
        "official_chain_exact": snapshot is not None
        and all(
            len(subjects) == len(CHAIN_LEVELS)
            for subjects in snapshot.chain_subjects.values()
        ),
        "reference_non_authorizing": snapshot is not None
        and snapshot.operator_review_required
        and snapshot.read_only
        and not any(
            (
                snapshot.calculation_allowed,
                snapshot.scoring_allowed,
                snapshot.causal_truth_authority,
                snapshot.account_authority,
                snapshot.execution_authority,
            )
        ),
        "run_all_wired": (
            "control_center_fcp_0099_registered_macro_micro_transmission_runtime_guard.py"
            in texts.get("run_all", "")
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0099_guard_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
