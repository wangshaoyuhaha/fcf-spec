import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0102_registered_factor_normalization_missing_state_runtime_app_1 import (  # noqa: E402
    build_reference_artifact_bytes,
    build_reference_normalization_snapshot,
    render_normalization_snapshot_json,
)


PHASE_ID = (
    "FCF-FCP-0102-REGISTERED-FACTOR-NORMALIZATION-MISSING-STATE-RUNTIME-APP-1"
)
FINAL = (
    "FCF_CURRENT_STATE_FCP_0102_REGISTERED_FACTOR_NORMALIZATION_"
    "MISSING_STATE_RUNTIME_APP_1_FINAL.md"
)
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
SOURCE_HASHES = {
    "builder.py": "aac7585c6dbb7bc9eb7fb15797fb3af1c3844a949c71876990117cd7050652fd",
    "contracts.py": "f827c98d7f7b915253986d0a487806bad37d089f3f6f7df3dada6afd91b62360",
    "runtime.py": "a5f54cc234e97c02be82beeef0610c21e63fe0f2c18b06f8acc15757b8e1e1df",
}
ARTIFACT_SHA = "069ec690d0fcd0d2603f76af13a3579a3f6dc1bc7d8cf24ccdb56c23add9912c"
SNAPSHOT_SHA = "f5e42e9e6673e56f042bde77fd7cd183a8ce8a7644d32eee76b6c631d1970822"
OUTPUT_SHA = "e39e3a15d546dfb92b54886c35c758097e7881e47f6a045a6206724b149d028b"


def _block(text: str, kind: str) -> str:
    prefix = "FCP 0102 REGISTERED FACTOR NORMALIZATION MISSING STATE RUNTIME APP 1"
    start = f"<!-- {prefix} {kind} START -->"
    end = f"<!-- {prefix} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0102_guard_report(root: Path = ROOT) -> dict[str, object]:
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
            root
            / "apps/fcp_0102_registered_factor_normalization_missing_state_runtime_app_1"
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
        snapshot = build_reference_normalization_snapshot()
        output = render_normalization_snapshot_json(snapshot).encode("ascii")
        final = (root / FINAL).read_text(encoding="ascii") if (root / FINAL).is_file() else ""
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
            if item.get("proposal_id") == "FCF-FCP-0102"
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
        "adr_registered": "FCF-V2-ADR-102" in governance.get("adr", ""),
        "gap_registered": "## FCP-0102 Registered Normalization Runtime Boundary"
        in governance.get("gap", ""),
        "protocol_registered": "Proposal `FCF-FCP-0102`"
        in governance.get("protocol", ""),
        "memory_registered": "FCP-0102 composes the completed V2-R21"
        in governance.get("memory", ""),
        "proposal_state_exact": proposal.get("operator_decision")
        == ("ACCEPTED_ARCHITECTURE" if complete else "APPROVED")
        and proposal.get("phase_id") == ("NONE" if complete else PHASE_ID)
        and register.get("next_proposal_sequence") in (103, 104, 105, 106),
        "manifest_state_exact": (
            truth.get("latest_completed_governance_delivery")
            in (
                PHASE_ID,
                "FCF-FCP-0103-REGISTERED-TECHNICAL-INDICATOR-CATALOG-RUNTIME-APP-1",
                "FCF-FCP-0104-REGISTERED-VOLUME-FLOW-INDICATOR-RUNTIME-APP-1",
                "FCF-FCP-0105-REGISTERED-PRICE-SHAPE-INDICATOR-RUNTIME-APP-1",
            )
            and truth.get("current_governance_phase_id")
            in (
                "NONE",
                "FCF-FCP-0103-REGISTERED-TECHNICAL-INDICATOR-CATALOG-RUNTIME-APP-1",
                "FCF-FCP-0104-REGISTERED-VOLUME-FLOW-INDICATOR-RUNTIME-APP-1",
                "FCF-FCP-0105-REGISTERED-PRICE-SHAPE-INDICATOR-RUNTIME-APP-1",
            )
            if complete
            else truth.get("latest_completed_governance_delivery")
            == "FCF-FCP-0101-REGISTERED-TECHNICAL-INDICATOR-CORE-RUNTIME-APP-1"
            and truth.get("current_governance_phase_id") == PHASE_ID
        ),
        "source_hashes_exact": source_hashes == SOURCE_HASHES,
        "reference_artifact_exact": hashlib.sha256(artifact).hexdigest()
        == ARTIFACT_SHA,
        "reference_snapshot_exact": snapshot is not None
        and snapshot.snapshot_hash == SNAPSHOT_SHA,
        "reference_output_exact": hashlib.sha256(output).hexdigest() == OUTPUT_SHA,
        "foundation_composed_exactly": snapshot is not None
        and snapshot.state == "NORMALIZATION_READY"
        and dict(snapshot.metrics)
        == {
            "available_sample_count": "5",
            "mad": "1",
            "median": "3",
            "minimum_samples": "3",
            "robust_z_score": "3",
            "winsorized_value": "6",
        },
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
        "state_evidence_registered": (
            "COMPLETED_MERGED_VALIDATED" in final if complete else True
        ),
        "run_all_wired": (
            "control_center_fcp_0102_registered_factor_normalization_missing_state_runtime_guard.py"
            in governance.get("run_all", "")
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0102_guard_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
