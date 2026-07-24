from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0105_registered_price_shape_indicator_runtime_app_1 import (
    INDICATOR_KINDS,
    build_reference_artifact_bytes,
    build_reference_price_shape_snapshot,
    render_price_shape_snapshot_json,
)

PHASE_ID = "FCF-FCP-0105-REGISTERED-PRICE-SHAPE-INDICATOR-RUNTIME-APP-1"
APPROVED = ROOT / (
    "FCF_CURRENT_STATE_FCP_0105_REGISTERED_PRICE_SHAPE_"
    "INDICATOR_RUNTIME_APP_1_APPROVED.md"
)
DELIVERED = ROOT / (
    "FCF_CURRENT_STATE_FCP_0105_REGISTERED_PRICE_SHAPE_"
    "INDICATOR_RUNTIME_APP_1_DELIVERED.md"
)
FINAL = ROOT / (
    "FCF_CURRENT_STATE_FCP_0105_REGISTERED_PRICE_SHAPE_"
    "INDICATOR_RUNTIME_APP_1_FINAL.md"
)
AUTHORITY = (
    ROOT / "docs/FCF_PROJECT_CONTROL_CENTER.md",
    ROOT / "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    ROOT / "docs/HANDOFF_PROMPT.md",
    ROOT / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    ROOT / "FCF_NEW_WINDOW_CHAT_PROMPT.md",
)
SOURCE_HASHES = {
    "builder.py": "09fc25a870fe33a752e9fa5a0ed58a2f559b4e1f01b5da32a3f770cfb7dc27cd",
    "contracts.py": "fd8636c242b616521e546989c1df0c99ba0f58060fa98cfdc8a3b2344f7f660a",
    "runtime.py": "7b23863f91e5bd4f67664aa4f2c795ebd405ed8281d7fee572ef80a2ab9a2868",
}
ARTIFACT_SHA = "802e8d8a3416727144617aecbfd5b4d1d361bacf815586ab3139eca6c3f344dd"
SNAPSHOT_SHA = "4b58c8342b5068c554be074a24153c3c2745b3f5c1bd17c650b47c76ec4d706f"
OUTPUT_SHA = "27efe200d219ebe43a8875c48da3c1698b2effe9fb0f13eb5b31d36a34ceac83"


def _block(text: str, kind: str) -> str:
    prefix = "FCP 0105 REGISTERED PRICE SHAPE INDICATOR RUNTIME APP 1"
    start = f"<!-- {prefix} {kind} START -->"
    end = f"<!-- {prefix} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def build_fcp_0105_guard_report(root: Path = ROOT) -> dict[str, object]:
    readable = True
    texts: dict[str, str] = {}
    paths = {
        "approved": APPROVED,
        "delivered": DELIVERED,
        "d1_d6": root
        / "docs/FCF_FCP_0105_REGISTERED_PRICE_SHAPE_INDICATOR_RUNTIME_APP_1_D1_D6.md",
        "adr": root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md",
        "gap": root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md",
        "protocol": root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md",
        "memory": root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md",
        "run_all": root / "scripts/run_all_checks.py",
    }
    try:
        for name, path in paths.items():
            texts[name] = path.read_text(encoding="ascii")
        authority_texts = tuple(path.read_text(encoding="ascii") for path in AUTHORITY)
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        register = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
    except (OSError, UnicodeError, json.JSONDecodeError):
        readable = False
        authority_texts = ()
        manifest = {}
        register = {}
    approvals = tuple(_block(text, "APPROVAL") for text in authority_texts)
    locks = tuple(_block(text, "LOCK") for text in authority_texts)
    finals = tuple(_block(text, "FINAL") for text in authority_texts)
    complete = FINAL.exists()
    proposal = next(
        (
            item
            for item in register.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0105"
        ),
        {},
    )
    truth = manifest.get("current_truth", {})
    source_dir = root / "apps/fcp_0105_registered_price_shape_indicator_runtime_app_1"
    source_hashes = {
        name: hashlib.sha256(
            (source_dir / name).read_text(encoding="ascii").encode("ascii")
        ).hexdigest()
        for name in SOURCE_HASHES
    }
    artifact = build_reference_artifact_bytes()
    snapshot = build_reference_price_shape_snapshot()
    output = render_price_shape_snapshot_json(snapshot).encode("ascii")
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(approvals) == 5
        and all(approvals)
        and len(set(approvals)) == 1,
        "lock_exact": len(locks) == 5 and all(locks) and len(set(locks)) == 1,
        "final_exact_when_complete": (
            not complete
            or len(finals) == 5
            and all(finals)
            and len(set(finals)) == 1
        ),
        "architecture_registered": (
            "FCF-V2-REGISTERED-PRICE-SHAPE-INDICATOR-RUNTIME"
            in texts.get("memory", "")
            or "FCP-0105 composes the completed FCP-0104"
            in texts.get("memory", "")
        ),
        "adr_registered": "FCF-V2-ADR-105" in texts.get("adr", ""),
        "gap_registered": (
            "## FCP-0105 Registered Price Shape Indicator Runtime Boundary"
            in texts.get("gap", "")
        ),
        "protocol_registered": "Proposal `FCF-FCP-0105`"
        in texts.get("protocol", ""),
        "memory_registered": "FCP-0105 composes the completed FCP-0104"
        in texts.get("memory", ""),
        "proposal_state_exact": proposal.get("operator_decision")
        == ("ACCEPTED_ARCHITECTURE" if complete else "APPROVED")
        and proposal.get("phase_id") == ("NONE" if complete else PHASE_ID)
        and register.get("next_proposal_sequence") == 106,
        "manifest_state_exact": truth.get("latest_completed_governance_delivery")
        == (
            PHASE_ID
            if complete
            else "FCF-FCP-0104-REGISTERED-VOLUME-FLOW-INDICATOR-RUNTIME-APP-1"
        )
        and truth.get("current_governance_phase_id")
        == ("NONE" if complete else PHASE_ID),
        "source_hashes_exact": source_hashes == SOURCE_HASHES,
        "reference_artifact_exact": hashlib.sha256(artifact).hexdigest()
        == ARTIFACT_SHA,
        "reference_snapshot_exact": snapshot.snapshot_hash == SNAPSHOT_SHA,
        "reference_output_exact": hashlib.sha256(output).hexdigest() == OUTPUT_SHA,
        "coverage_exact": len(snapshot.supported_kind_sources) == 25
        and len(snapshot.missing_candidate_kinds) == 28
        and not set(INDICATOR_KINDS).intersection(snapshot.missing_candidate_kinds),
        "reference_non_authorizing": snapshot.operator_review_required
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
            "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"
            in texts.get("delivered", "")
            or "COMPLETED_MERGED_VALIDATED" in texts.get("delivered", "")
        )
        and (not complete or "COMPLETED_MERGED_VALIDATED" in FINAL.read_text("ascii")),
        "d1_d6_registered": all(
            f"## D{number} " in texts.get("d1_d6", "") for number in range(1, 7)
        ),
        "run_all_wired": (
            "control_center_fcp_0105_registered_price_shape_indicator_runtime_guard.py"
            in texts.get("run_all", "")
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0105_guard_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
