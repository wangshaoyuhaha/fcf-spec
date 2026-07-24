import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0104_registered_volume_flow_indicator_runtime_app_1 import (  # noqa: E402
    INDICATOR_KINDS,
    build_reference_artifact_bytes,
    build_reference_volume_flow_snapshot,
    render_volume_flow_snapshot_json,
)


PHASE_ID = "FCF-FCP-0104-REGISTERED-VOLUME-FLOW-INDICATOR-RUNTIME-APP-1"
FINAL = "FCF_CURRENT_STATE_FCP_0104_REGISTERED_VOLUME_FLOW_INDICATOR_RUNTIME_APP_1_FINAL.md"
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
SOURCE_HASHES = {
    "builder.py": "f1b4558e686c6ec7bc7bdf0c53a804cd9be99fdda0bb036e1a666faf3a34d01d",
    "contracts.py": "07e21c6b93c03b8078579ab6f79026eafbfb062c2d2c87ab642630f5c2518d2b",
    "runtime.py": "147dcf7ca69bfed482e81f1160d7078f69a42ec1c0720777700d6dd7f5b3db92",
}
ARTIFACT_SHA = "77a7eaa1bcceea4ad6e2522bb592831bc82598fc861f520cce6259e7bad9aa24"
SNAPSHOT_SHA = "98f89c359415b97e38629a4d774a36d5b004eb9d2b3d168648fee5136b8959f4"
OUTPUT_SHA = "99b8bcf75df1f7073704d673ce64643c94859f78effb74f059753cea06da655f"


def _block(text: str, kind: str) -> str:
    prefix = "FCP 0104 REGISTERED VOLUME FLOW INDICATOR RUNTIME APP 1"
    start = f"<!-- {prefix} {kind} START -->"
    end = f"<!-- {prefix} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0104_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        authorities = tuple(
            (root / path).read_text(encoding="ascii") for path in AUTHORITIES
        )
        register = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        source = (
            root / "apps/fcp_0104_registered_volume_flow_indicator_runtime_app_1"
        )
        source_hashes = {
            name: hashlib.sha256(
                (source / name)
                .read_text(encoding="ascii")
                .replace("\r\n", "\n")
                .encode("ascii")
            ).hexdigest()
            for name in SOURCE_HASHES
        }
        artifact = build_reference_artifact_bytes()
        snapshot = build_reference_volume_flow_snapshot()
        output = render_volume_flow_snapshot_json(snapshot).encode("ascii")
        final_path = root / FINAL
        final = final_path.read_text(encoding="ascii") if final_path.is_file() else ""
        governance = {
            "adr": (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md").read_text(encoding="ascii"),
            "gap": (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md").read_text(encoding="ascii"),
            "protocol": (root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md").read_text(encoding="ascii"),
            "memory": (root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md").read_text(encoding="ascii"),
            "run_all": (root / "scripts/run_all_checks.py").read_text(encoding="ascii"),
        }
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        authorities = ()
        register = manifest = governance = {}
        source_hashes = {}
        artifact = output = b""
        snapshot = None
        final = ""
        readable = False
    proposal = next(
        (
            item
            for item in register.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0104"
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
        "adr_registered": "FCF-V2-ADR-104" in governance.get("adr", ""),
        "gap_registered": "## FCP-0104 Registered Volume Flow Indicator Runtime Boundary"
        in governance.get("gap", ""),
        "protocol_registered": "Proposal `FCF-FCP-0104`"
        in governance.get("protocol", ""),
        "memory_registered": "FCP-0104 adds deterministic rolling OBV"
        in governance.get("memory", ""),
        "proposal_state_exact": proposal.get("operator_decision")
        == ("ACCEPTED_ARCHITECTURE" if complete else "APPROVED")
        and proposal.get("phase_id") == ("NONE" if complete else PHASE_ID)
        and register.get("next_proposal_sequence") in (105, 106),
        "manifest_state_exact": (
            truth.get("latest_completed_governance_delivery")
            in (
                PHASE_ID,
                "FCF-FCP-0105-REGISTERED-PRICE-SHAPE-INDICATOR-RUNTIME-APP-1",
            )
            and truth.get("current_governance_phase_id")
            in (
                "NONE",
                "FCF-FCP-0105-REGISTERED-PRICE-SHAPE-INDICATOR-RUNTIME-APP-1",
            )
            if complete
            else truth.get("latest_completed_governance_delivery")
            == "FCF-FCP-0103-REGISTERED-TECHNICAL-INDICATOR-CATALOG-RUNTIME-APP-1"
            and truth.get("current_governance_phase_id") == PHASE_ID
        ),
        "source_hashes_exact": source_hashes == SOURCE_HASHES,
        "reference_artifact_exact": hashlib.sha256(artifact).hexdigest()
        == ARTIFACT_SHA,
        "reference_snapshot_exact": snapshot is not None
        and snapshot.snapshot_hash == SNAPSHOT_SHA,
        "reference_output_exact": hashlib.sha256(output).hexdigest() == OUTPUT_SHA,
        "volume_flow_pack_exact": snapshot is not None
        and set(snapshot.result_values)
        == {
            "registered-mfi-3",
            "registered-obv-3",
            "registered-volume-price-trend-3",
        }
        and len(snapshot.supported_kind_sources) == 17
        and len(snapshot.missing_candidate_kinds) == 36
        and set(INDICATOR_KINDS).isdisjoint(snapshot.missing_candidate_kinds),
        "reference_non_authorizing": snapshot is not None
        and snapshot.operator_review_required
        and snapshot.read_only
        and snapshot.deterministic_engine_authority
        and not any(
            (
                snapshot.scoring_authority,
                snapshot.ranking_authority,
                snapshot.recommendation_authority,
                snapshot.account_authority,
                snapshot.execution_authority,
            )
        ),
        "state_evidence_registered": (
            "COMPLETED_MERGED_VALIDATED" in final if complete else True
        ),
        "run_all_wired": (
            "control_center_fcp_0104_registered_volume_flow_indicator_runtime_guard.py"
            in governance.get("run_all", "")
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0104_guard_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
