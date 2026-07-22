from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_app_1 import (  # noqa: E402
    build_reference_evidence,
    render_evidence_json,
)


AUTHORITY_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    "docs/HANDOFF_PROMPT.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
)
DELIVERY_ID = "FCF-FCP-0084-A-SHARE-GUOJIN-QMT-LOCAL-EXPORT-BATCH-COVERAGE-EVIDENCE-APP-1"
MARKER = "FCP 0084 A SHARE GUOJIN QMT LOCAL EXPORT BATCH COVERAGE EVIDENCE APP 1"
CONTRACT_PATH = "apps/fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_app_1/contracts.py"
RUNNER_PATH = "apps/fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_app_1/runner.py"
CONTRACT_SHA = "3c5ba7da999a2d256373bee73ddee26b0132f2321dbe140a28df1165ef354ff5"
RUNNER_SHA = "af2c6c9ccbc4c619a4cb87824cb8e991c46a08f83ac3fb33602d95fa67325dae"
REFERENCE_EVIDENCE_HASH = "a4d0f5164c98db1d03c6fdc6d87bb8b3c9ccae8f8ef5b3a8c854370629abbf8a"
REFERENCE_OUTPUT_SHA = "35e30a784912f65189544882f4062fb9dcbc0522e31c8657ad985536f2cd6c72"


def _block(text: str, kind: str) -> str:
    start = f"<!-- {MARKER} {kind} START -->"
    end = f"<!-- {MARKER} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    begin = text.index(start)
    finish = text.index(end, begin) + len(end)
    return text[begin:finish]


def _read_ascii(path: Path) -> str:
    return path.read_text(encoding="ascii")


def build_fcp_0084_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple(_read_ascii(root / path) for path in AUTHORITY_PATHS)
        manifest = json.loads(_read_ascii(root / "FCF_CURRENT_STATE_MANIFEST.json"))
        intake = json.loads(
            _read_ascii(root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json")
        )
        architecture = _read_ascii(
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
        )
        adr = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md")
        gaps = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md")
        protocol = _read_ascii(root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md")
        memory = _read_ascii(root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md")
        run_all = _read_ascii(root / "scripts/run_all_checks.py")
        contract_bytes = (root / CONTRACT_PATH).read_bytes()
        runner_bytes = (root / RUNNER_PATH).read_bytes()
        runner_text = runner_bytes.decode("ascii")
        reference = build_reference_evidence()
        reference_output = render_evidence_json(reference).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        texts, manifest, intake = (), {}, {}
        architecture = adr = gaps = protocol = memory = run_all = runner_text = ""
        contract_bytes = runner_bytes = reference_output = b""
        reference = None
        readable = False
    truth = manifest.get("current_truth", {})
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID and status in {
        "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
    }
    closed = (
        truth.get("current_governance_phase_id") == "NONE"
        and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    )
    approvals = tuple(_block(text, "APPROVAL") for text in texts)
    locks = tuple(_block(text, "LOCK") for text in texts)
    finals = tuple(_block(text, "FINAL") for text in texts)
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0084"
        ),
        {},
    )
    expected = {
        "FCF_CURRENT_STATE_FCP_0084_A_SHARE_GUOJIN_QMT_LOCAL_EXPORT_BATCH_COVERAGE_EVIDENCE_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0084_A_SHARE_GUOJIN_QMT_LOCAL_EXPORT_BATCH_COVERAGE_EVIDENCE_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0084_A_SHARE_GUOJIN_QMT_LOCAL_EXPORT_BATCH_COVERAGE_EVIDENCE_APP_1_FINAL.md",
        "docs/FCF_FCP_0084_A_SHARE_GUOJIN_QMT_LOCAL_EXPORT_BATCH_COVERAGE_EVIDENCE_APP_1_D1_D6.md",
    }
    gap_row = next(
        (line for line in gaps.splitlines() if "| V2-FR-GAP-105 |" in line), ""
    )
    prohibited = (
        "import csv",
        "import xtquant",
        "from xtquant",
        "import requests",
        "import socket",
        "import urllib",
    )
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_implemented": status not in {
            "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
            "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
        }
        or (all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed or (all(finals) and len(set(finals)) == 1),
        "final_evidence_when_closed": not closed
        or (
            (root / next(path for path in expected if "FINAL" in path)).is_file()
            and all(finals)
            and "ALL CHECKS PASSED" in finals[0]
        ),
        "manifest_state_safe": active
        or closed
        or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status")
        == proposal.get("operator_decision")
        == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and expected.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": all(
            term in architecture
            for term in (
                "## 117. Guojin QMT Local Export Batch Coverage Evidence",
                "delegates all registered-byte parsing and normalization",
                "FCP-0036 remains the only batch reconciliation authority",
            )
        ),
        "adr_registered": all(
            term in adr
            for term in (
                "FCF-V2-ADR-084",
                "Preserve QMT Export Coverage As Observed Evidence",
                "FCP-0035 remains the QMT parsing and",
            )
        ),
        "gap_preserved": "| RESEARCH_REQUIRED |" in gap_row,
        "gap_observation_registered": "FCP-0084 is approved" in gaps
        and "GAP-105" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0084`" in protocol
        and "FCP-0035" in protocol
        and "FCP-0036" in protocol,
        "memory_registered": "FCP-0084 preserves Guojin QMT" in memory,
        "run_all_wired": (
            "control_center_fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_guard.py"
            in run_all
        ),
        "contract_hash_exact": hashlib.sha256(contract_bytes).hexdigest()
        == CONTRACT_SHA,
        "runner_hash_exact": hashlib.sha256(runner_bytes).hexdigest() == RUNNER_SHA,
        "reference_evidence_hash_exact": reference is not None
        and reference.evidence_hash == REFERENCE_EVIDENCE_HASH,
        "reference_output_hash_exact": hashlib.sha256(reference_output).hexdigest()
        == REFERENCE_OUTPUT_SHA,
        "reference_non_authorizing": reference is not None
        and reference.registered_evidence_promotion_allowed is False
        and reference.provider_selection_allowed is False
        and reference.product_authority_allowed is False,
        "runner_reuses_frozen_authority": (
            "normalize_registered_qmt_daily_export" in runner_text
            and "fcp_0035_guojin_qmt" in runner_text
            and not any(term in runner_text for term in prohibited)
        ),
        "raw_samples_absent": not any(
            (root / value).exists()
            for value in ("SH", "SH_front", "price_600028.txt")
        ),
        "delivery_files_exist": all(
            (root / path).is_file() for path in expected if "FINAL" not in path
        )
        and (
            (root / next(path for path in expected if "FINAL" in path)).is_file()
            if closed
            else True
        ),
        "no_product_phase": truth.get("current_product_implementation_phase")
        == "NONE",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0084_guard_report()
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
