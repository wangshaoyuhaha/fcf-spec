from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0093_btc_coin_metrics_reference_rate_local_csv_validation_app_1 import (
    PHASE_ID,
    build_reference_result,
    render_validation_json,
)


AUTHORITY_PATHS = (
    Path("docs/FCF_PROJECT_CONTROL_CENTER.md"),
    Path("docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md"),
    Path("docs/HANDOFF_PROMPT.md"),
    Path("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md"),
    Path("FCF_NEW_WINDOW_CHAT_PROMPT.md"),
)
APPROVAL_START = (
    "<!-- FCP 0093 BTC COIN METRICS REFERENCE RATE LOCAL CSV VALIDATION "
    "APP 1 APPROVAL START -->"
)
APPROVAL_END = (
    "<!-- FCP 0093 BTC COIN METRICS REFERENCE RATE LOCAL CSV VALIDATION "
    "APP 1 APPROVAL END -->"
)
LOCK_START = (
    "<!-- FCP 0093 BTC COIN METRICS REFERENCE RATE LOCAL CSV VALIDATION "
    "APP 1 LOCK START -->"
)
LOCK_END = (
    "<!-- FCP 0093 BTC COIN METRICS REFERENCE RATE LOCAL CSV VALIDATION "
    "APP 1 LOCK END -->"
)
FINAL_START = (
    "<!-- FCP 0093 BTC COIN METRICS REFERENCE RATE LOCAL CSV VALIDATION "
    "APP 1 FINAL START -->"
)
FINAL_END = (
    "<!-- FCP 0093 BTC COIN METRICS REFERENCE RATE LOCAL CSV VALIDATION "
    "APP 1 FINAL END -->"
)
APPROVED_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0093_BTC_COIN_METRICS_REFERENCE_RATE_LOCAL_CSV_"
    "VALIDATION_APP_1_APPROVED.md"
)
DELIVERED_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0093_BTC_COIN_METRICS_REFERENCE_RATE_LOCAL_CSV_"
    "VALIDATION_APP_1_DELIVERED.md"
)
FINAL_STATE = Path(
    "FCF_CURRENT_STATE_FCP_0093_BTC_COIN_METRICS_REFERENCE_RATE_LOCAL_CSV_"
    "VALIDATION_APP_1_FINAL.md"
)
D1_D6 = Path(
    "docs/FCF_FCP_0093_BTC_COIN_METRICS_REFERENCE_RATE_LOCAL_CSV_"
    "VALIDATION_APP_1_D1_D6.md"
)
REFERENCE_RESULT_HASH = (
    "b6c156f9c02fc5da76cee9f0ca9e18869fa495f3b1bc7db6e9da69af8318cff1"
)
REFERENCE_OUTPUT_HASH = (
    "ee5a117747a66613ddc8113bc3877ae5cd89d1effc4b3725ea1b4da2b8f0b027"
)


def _single_block(text: str, start: str, end: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def _phase_sequence(value: object) -> int:
    if not isinstance(value, str):
        return -1
    for part in value.split("-"):
        if part.isdigit():
            return int(part)
    return -1


def build_fcp_0093_guard_report(root: Path = ROOT) -> dict[str, object]:
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
        final = (root / FINAL_STATE).read_text(encoding="ascii")
        d1_d6 = (root / D1_D6).read_text(encoding="ascii")
        contracts = (
            root
            / "apps/fcp_0093_btc_coin_metrics_reference_rate_local_csv_"
            "validation_app_1/contracts.py"
        ).read_text(encoding="ascii")
        validator = (
            root
            / "apps/fcp_0093_btc_coin_metrics_reference_rate_local_csv_"
            "validation_app_1/validator.py"
        ).read_text(encoding="ascii")
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        register = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        files_ascii = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        authority_texts = ()
        architecture = adr = gap = protocol = memory = ""
        approved = delivered = final = d1_d6 = contracts = validator = run_all = ""
        register = manifest = {}
        files_ascii = False

    approval_blocks = tuple(
        _single_block(text, APPROVAL_START, APPROVAL_END)
        for text in authority_texts
    )
    lock_blocks = tuple(
        _single_block(text, LOCK_START, LOCK_END) for text in authority_texts
    )
    final_blocks = tuple(
        _single_block(text, FINAL_START, FINAL_END) for text in authority_texts
    )
    proposals = {
        item.get("proposal_id"): item
        for item in register.get("proposals", [])
        if isinstance(item, dict)
    }
    proposal = proposals.get("FCF-FCP-0093", {})
    current_truth = manifest.get("current_truth", {})
    reference = build_reference_result()
    rendered = render_validation_json(reference)
    checks = {
        "files_ascii": files_ascii,
        "authority_approval_exact": len(approval_blocks) == len(AUTHORITY_PATHS)
        and bool(approval_blocks[0])
        and len(set(approval_blocks)) == 1,
        "authority_lock_exact": len(lock_blocks) == len(AUTHORITY_PATHS)
        and bool(lock_blocks[0])
        and len(set(lock_blocks)) == 1,
        "authority_final_exact": len(final_blocks) == len(AUTHORITY_PATHS)
        and bool(final_blocks[0])
        and len(set(final_blocks)) == 1,
        "architecture_registered": (
            "FCF-V2-BTC-COIN-METRICS-REFERENCE-RATE-LOCAL-CSV-VALIDATION"
            in architecture
        ),
        "adr_registered": "FCF-V2-ADR-093" in adr,
        "gap_boundary_registered": "## FCP-0093 Evidence Boundary" in gap
        and "GAP-095 remains" in gap,
        "protocol_registered": "Proposal `FCF-FCP-0093`" in protocol,
        "memory_registered": (
            "FCP-0093 validates one exact registered local" in memory
        ),
        "proposal_final_exact": proposal.get("status") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and str(FINAL_STATE) in proposal.get("evidence_refs", [])
        and int(register.get("next_proposal_sequence", -1)) >= 94,
        "manifest_final_exact": (
            _phase_sequence(
                current_truth.get("latest_completed_governance_delivery")
            )
            >= 93
            and (
                current_truth.get("current_governance_phase_id") == "NONE"
                or _phase_sequence(
                    current_truth.get("current_governance_phase_id")
                )
                > 93
            )
        ),
        "state_evidence_registered": (
            "APPROVED_GOVERNANCE_ONLY_NOT_STARTED" in approved
            and "COMPLETED_MERGED_VALIDATED" in delivered
            and "COMPLETED_MERGED_VALIDATED" in final
            and "50cc52664679f88209aba3d7f9989ec5a0957002a1d23003f59088736fd3d19a"
            in delivered
            and "689317437eec53117d195c39803d1f759102682aaf416aa4aae2afbbfb3f0e27"
            in delivered
            and "865ceb4338e339e703294a51d2dd81f7affc3d70" in final
            and "9efe550fc93cf2de7fce20f5ca2f369ba0e78bdb" in final
        ),
        "d1_d6_registered": all(
            f"## D{number} " in d1_d6 for number in range(1, 7)
        ),
        "contracts_keep_authority_false": all(
            token in contracts
            for token in (
                'observation_kind: str = "NEUTRAL_REFERENCE_RATE_USD"',
                'quality_state: str = "READY_FOR_OPERATOR_REVIEW"',
                'gap_095_status: str = "RESEARCH_REQUIRED"',
                "operator_review_required: bool = True",
                "network_used: bool = False",
                "source_values_retained: bool = False",
                "execution_authority: bool = False",
            )
        ),
        "validator_local_only": (
            "Path(file_path)" in validator
            and ".read_bytes()" in validator
            and "requests" not in validator
            and "urllib" not in validator
            and "rqdatac" not in validator
            and "xtquant" not in validator
        ),
        "reference_result_hash_exact": reference.result_hash
        == REFERENCE_RESULT_HASH,
        "reference_output_hash_exact": hashlib.sha256(rendered.encode("ascii")).hexdigest()
        == REFERENCE_OUTPUT_HASH,
        "run_all_wired": (
            "control_center_fcp_0093_btc_coin_metrics_reference_rate_local_csv_"
            "validation_guard.py" in run_all
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0093_guard_report(ROOT)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
