from __future__ import annotations

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

from apps.fcp_0078_a_share_publication_availability_clock_contract_app_1 import (  # noqa: E402
    build_augmented_coverage_matrix,
)


DELIVERY_ID = (
    "FCF-FCP-0078-A-SHARE-PUBLICATION-AVAILABILITY-CLOCK-CONTRACT-APP-1"
)
MARKER = "FCP 0078 A SHARE PUBLICATION AVAILABILITY CLOCK CONTRACT APP 1"
MATRIX_HASH = "345ab6bc9d01293226ade1c4b50b647ed85cd133f295d9620a983339379e3397"
AUTHORITIES = tuple(
    Path(value)
    for value in (
        "docs/FCF_PROJECT_CONTROL_CENTER.md",
        "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
        "docs/HANDOFF_PROMPT.md",
        "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
        "FCF_NEW_WINDOW_CHAT_PROMPT.md",
    )
)


def _block(text: str, label: str) -> str | None:
    start = f"<!-- {MARKER} {label} START -->"
    end = f"<!-- {MARKER} {label} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0078_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        intake = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
        architecture = (
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
        ).read_text(encoding="ascii")
        adr = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md").read_text(
            encoding="ascii"
        )
        gaps = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md").read_text(
            encoding="ascii"
        )
        protocol = (root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md").read_text(
            encoding="ascii"
        )
        memory = (root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md").read_text(
            encoding="ascii"
        )
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        matrix = build_augmented_coverage_matrix(
            root,
            evaluated_at_utc="2026-07-22T18:30:00Z",
        )
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
        texts, manifest, intake, matrix = (), {}, {}, None
        architecture = adr = gaps = protocol = memory = run_all = ""
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
            if item.get("proposal_id") == "FCF-FCP-0078"
        ),
        {},
    )
    expected = {
        "FCF_CURRENT_STATE_FCP_0078_A_SHARE_PUBLICATION_AVAILABILITY_CLOCK_CONTRACT_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0078_A_SHARE_PUBLICATION_AVAILABILITY_CLOCK_CONTRACT_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0078_A_SHARE_PUBLICATION_AVAILABILITY_CLOCK_CONTRACT_APP_1_FINAL.md",
        "docs/FCF_FCP_0078_A_SHARE_PUBLICATION_AVAILABILITY_CLOCK_CONTRACT_APP_1_D1_D6.md",
    }
    row = (
        next(
            item
            for item in matrix.rows
            if item.requirement.gap_id == "V2-FR-GAP-088"
        )
        if matrix is not None
        else None
    )
    gap_row = next(
        (line for line in gaps.splitlines() if "| V2-FR-GAP-088 |" in line),
        "",
    )
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_implemented": status
        not in {
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
                "## 111. A-Share Publication And Availability Clock Contract",
                "Date-only or unknown publication evidence is explicit",
                "may be substituted for source publication evidence",
            )
        ),
        "adr_registered": all(
            term in adr
            for term in (
                "FCF-V2-ADR-078",
                "Preserve Exact Publication Time Without Inference",
                "infer publication time from trade date",
            )
        ),
        "gap_preserved": "| NOT_IMPLEMENTED |" in gap_row,
        "gap_observation_registered": "FCP-0078 is approved" in gaps
        and "publication-clock gap" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0078`" in protocol,
        "memory_registered": "publication and availability clock contracts" in memory,
        "run_all_wired": "control_center_fcp_0078_a_share_publication_availability_clock_contract_guard.py"
        in run_all,
        "matrix_hash_exact": matrix is not None and matrix.matrix_hash == MATRIX_HASH,
        "publication_foundation_covered": row is not None
        and row.missing_capabilities == ()
        and row.coverage_state == "FOUNDATION_COVERED_GAP_OPEN",
        "matrix_non_authorizing": matrix is not None
        and matrix.changes_gap_status is False
        and matrix.promotes_candidate_data is False
        and matrix.provider_selected is False
        and all(item.gap_open is True for item in matrix.rows)
        and all(item.authority_established is False for item in matrix.rows),
        "delivery_files_exist": all(
            (root / path).is_file() for path in expected if "FINAL" not in path
        )
        and (
            (root / next(path for path in expected if "FINAL" in path)).is_file()
            if closed
            else True
        ),
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0078_guard_report()
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
