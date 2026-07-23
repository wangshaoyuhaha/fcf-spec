from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0101_registered_technical_indicator_core_runtime_app_1 import (  # noqa: E402
    INDICATOR_KINDS,
    PHASE_ID,
    build_reference_artifact_bytes,
    build_reference_indicator_snapshot,
    render_indicator_snapshot_json,
)


AUTHORITY_PATHS = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
MARKER = "FCP 0101 REGISTERED TECHNICAL INDICATOR CORE RUNTIME APP 1"
APPROVED = Path(
    "FCF_CURRENT_STATE_FCP_0101_REGISTERED_TECHNICAL_INDICATOR_CORE_RUNTIME_APP_1_APPROVED.md"
)
DELIVERED = Path(
    "FCF_CURRENT_STATE_FCP_0101_REGISTERED_TECHNICAL_INDICATOR_CORE_RUNTIME_APP_1_DELIVERED.md"
)
FINAL = Path(
    "FCF_CURRENT_STATE_FCP_0101_REGISTERED_TECHNICAL_INDICATOR_CORE_RUNTIME_APP_1_FINAL.md"
)
D1_D6 = Path(
    "docs/FCF_FCP_0101_REGISTERED_TECHNICAL_INDICATOR_CORE_RUNTIME_APP_1_D1_D6.md"
)
SOURCE_HASHES = {
    "contracts.py": "97cbf786b1b4a98bdf83e0ec3e3fb2467602af90fef357edf68ed16973d7cdbb",
    "runtime.py": "7eb50e0454ca35c9b3660d51796614e586a46deff2cbb7ccac35ce64eed418e9",
    "builder.py": "905031f9cdc317ce9c25396eff00dc8077f52aa975241e2f5be252352494b86f",
}
ARTIFACT_SHA = "4c537b0e80db53fe2f7e4faf38355f3f5f36e63871b8087514a8b3fc0e48d852"
SNAPSHOT_HASH = "261a2044b12634905e8b94fd54bacaa2aaf4cce2134c246c439418960dfab6dc"
OUTPUT_SHA = "8834b0b8d1bac8dfbd2bbbd1f264f8932c85a3c55e5daaa7112e4a348aea3c26"


def _block(text: str, kind: str) -> str:
    start = f"<!-- {MARKER} {kind} START -->"
    end = f"<!-- {MARKER} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return start + text.split(start, 1)[1].split(end, 1)[0] + end


def build_fcp_0101_guard_report(root: Path = ROOT) -> dict[str, object]:
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
        source = (
            root / "apps/fcp_0101_registered_technical_indicator_core_runtime_app_1"
        )
        source_hashes = {
            name: hashlib.sha256(
                (source / name).read_text(encoding="ascii").encode("ascii")
            ).hexdigest()
            for name in SOURCE_HASHES
        }
        artifact = build_reference_artifact_bytes()
        snapshot = build_reference_indicator_snapshot()
        output = render_indicator_snapshot_json(snapshot).encode("ascii")
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
            if item.get("proposal_id") == "FCF-FCP-0101"
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
            "FCF-V2-REGISTERED-TECHNICAL-INDICATOR-CORE-RUNTIME"
            in texts.get("architecture", "")
        ),
        "adr_registered": "FCF-V2-ADR-101" in texts.get("adr", ""),
        "gap_registered": (
            "## FCP-0101 Technical Indicator Core Runtime Boundary"
            in texts.get("gap", "")
        ),
        "protocol_registered": "Proposal `FCF-FCP-0101`"
        in texts.get("protocol", ""),
        "memory_registered": "FCP-0101 adds the first registered deterministic"
        in texts.get("memory", ""),
        "proposal_state_exact": proposal.get("operator_decision")
        == ("ACCEPTED_ARCHITECTURE" if complete else "APPROVED")
        and proposal.get("phase_id") == ("NONE" if complete else PHASE_ID)
        and register.get("next_proposal_sequence") == 102,
        "manifest_state_exact": truth.get("latest_completed_governance_delivery")
        == (
            PHASE_ID
            if complete
            else "FCF-FCP-0100-REGISTERED-MULTI-HORIZON-CONFLICT-RESOLVER-RUNTIME-APP-1"
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
        "core_indicators_exact": snapshot is not None
        and len(snapshot.result_values) == len(INDICATOR_KINDS)
        and snapshot.result_values["request.sma"]["value"] == "15"
        and snapshot.result_values["request.atr"]["value"] == "3",
        "reference_non_authorizing": snapshot is not None
        and snapshot.operator_review_required
        and snapshot.read_only
        and snapshot.deterministic_engine_authority
        and not any(
            (
                snapshot.scoring_authority,
                snapshot.recommendation_authority,
                snapshot.account_authority,
                snapshot.execution_authority,
            )
        ),
        "run_all_wired": (
            "control_center_fcp_0101_registered_technical_indicator_core_runtime_guard.py"
            in texts.get("run_all", "")
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0101_guard_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
