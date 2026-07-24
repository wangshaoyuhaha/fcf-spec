import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0103_registered_technical_indicator_catalog_runtime_app_1 import (  # noqa: E402
    ACCEPTED_CANDIDATE_KINDS,
    FOUNDATION_KIND_SOURCES,
    build_reference_artifact_bytes,
    build_reference_catalog_snapshot,
    render_catalog_snapshot_json,
)


PHASE_ID = (
    "FCF-FCP-0103-REGISTERED-TECHNICAL-INDICATOR-CATALOG-RUNTIME-APP-1"
)
FINAL = (
    "FCF_CURRENT_STATE_FCP_0103_REGISTERED_TECHNICAL_INDICATOR_"
    "CATALOG_RUNTIME_APP_1_FINAL.md"
)
AUTHORITIES = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
SOURCE_HASHES = {
    "builder.py": "7345e63a463bb967f9ba2b0fa49f2558771503f1b903d2412bec78d7e76f896c",
    "contracts.py": "d09608ad1c150ef0fdef81e22a10cb5811bf6387d0bb0050f3f0572cecd79cd1",
    "runtime.py": "6d6281ee204f2fd557df48a5502ffaec5d0e2813bdcef7282de911b5115a88f9",
}
ARTIFACT_SHA = "cd0a89fe335adc3253f67b0d5d70531b852730b007a833505481a4346f4c975e"
SNAPSHOT_SHA = "0b4bd7ea4906af1ab32bf0a9c606d976796caf27ca6c689efb4e406c6fa79d39"
OUTPUT_SHA = "e6e925114ff02aef52cca86ff25cf99fca24e5660be85ef52afc34f16915c7cb"


def _block(text: str, kind: str) -> str:
    prefix = "FCP 0103 REGISTERED TECHNICAL INDICATOR CATALOG RUNTIME APP 1"
    start = f"<!-- {prefix} {kind} START -->"
    end = f"<!-- {prefix} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0103_guard_report(root: Path = ROOT) -> dict[str, object]:
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
            / "apps/fcp_0103_registered_technical_indicator_catalog_runtime_app_1"
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
        snapshot = build_reference_catalog_snapshot()
        output = render_catalog_snapshot_json(snapshot).encode("ascii")
        final_path = root / FINAL
        final = (
            final_path.read_text(encoding="ascii") if final_path.is_file() else ""
        )
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
            if item.get("proposal_id") == "FCF-FCP-0103"
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
        "adr_registered": "FCF-V2-ADR-103" in governance.get("adr", ""),
        "gap_registered": (
            "## FCP-0103 Registered Technical Indicator Catalog Runtime Boundary"
            in governance.get("gap", "")
        ),
        "protocol_registered": "Proposal `FCF-FCP-0103`"
        in governance.get("protocol", ""),
        "memory_registered": "FCP-0103 composes the completed V2-R12"
        in governance.get("memory", ""),
        "proposal_state_exact": proposal.get("operator_decision")
        == ("ACCEPTED_ARCHITECTURE" if complete else "APPROVED")
        and proposal.get("phase_id") == ("NONE" if complete else PHASE_ID)
        and register.get("next_proposal_sequence") in (104, 105, 106),
        "manifest_state_exact": (
            truth.get("latest_completed_governance_delivery")
            in (
                PHASE_ID,
                "FCF-FCP-0104-REGISTERED-VOLUME-FLOW-INDICATOR-RUNTIME-APP-1",
                "FCF-FCP-0105-REGISTERED-PRICE-SHAPE-INDICATOR-RUNTIME-APP-1",
            )
            and truth.get("current_governance_phase_id")
            in (
                "NONE",
                "FCF-FCP-0104-REGISTERED-VOLUME-FLOW-INDICATOR-RUNTIME-APP-1",
                "FCF-FCP-0105-REGISTERED-PRICE-SHAPE-INDICATOR-RUNTIME-APP-1",
            )
            if complete
            else truth.get("latest_completed_governance_delivery")
            == "FCF-FCP-0102-REGISTERED-FACTOR-NORMALIZATION-MISSING-STATE-RUNTIME-APP-1"
            and truth.get("current_governance_phase_id") == PHASE_ID
        ),
        "source_hashes_exact": source_hashes == SOURCE_HASHES,
        "reference_artifact_exact": hashlib.sha256(artifact).hexdigest()
        == ARTIFACT_SHA,
        "reference_snapshot_exact": snapshot is not None
        and snapshot.snapshot_hash == SNAPSHOT_SHA,
        "reference_output_exact": hashlib.sha256(output).hexdigest() == OUTPUT_SHA,
        "coverage_exact": snapshot is not None
        and snapshot.state == "CATALOG_PARTIAL"
        and dict(snapshot.supported_kind_sources)
        == dict(sorted(FOUNDATION_KIND_SOURCES.items()))
        and snapshot.missing_candidate_kinds
        == tuple(
            sorted(set(ACCEPTED_CANDIDATE_KINDS) - set(FOUNDATION_KIND_SOURCES))
        ),
        "reference_non_authorizing": snapshot is not None
        and snapshot.operator_review_required
        and snapshot.read_only
        and not any(
            (
                snapshot.calculation_activation_allowed,
                snapshot.scoring_allowed,
                snapshot.ranking_allowed,
                snapshot.recommendation_allowed,
                snapshot.account_authority,
                snapshot.execution_authority,
            )
        ),
        "state_evidence_registered": (
            "COMPLETED_MERGED_VALIDATED" in final if complete else True
        ),
        "run_all_wired": (
            "control_center_fcp_0103_registered_technical_indicator_catalog_runtime_guard.py"
            in governance.get("run_all", "")
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0103_guard_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
