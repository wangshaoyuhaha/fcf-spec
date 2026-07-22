from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ID = "FCF-FCP-0051-GUOJIN-QMT-HISTORICAL-COVERAGE-COMPLETENESS-GATE-APP-1"
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
MARKER = "FCP 0051 GUOJIN QMT HISTORICAL COVERAGE COMPLETENESS GATE APP 1"
APPROVAL_START = f"<!-- {MARKER} APPROVAL START -->"
APPROVAL_END = f"<!-- {MARKER} APPROVAL END -->"
LOCK_START = f"<!-- {MARKER} LOCK START -->"
LOCK_END = f"<!-- {MARKER} LOCK END -->"
FINAL_START = f"<!-- {MARKER} FINAL START -->"
FINAL_END = f"<!-- {MARKER} FINAL END -->"
EVIDENCE_PATH = Path(
    "FCF_REGISTERED_EVIDENCE_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE.json"
)
SOURCE_PATH = Path(
    "FCF_REGISTERED_EVIDENCE_FCP_0050_GUOJIN_QMT_DUAL_EXPORT_QUALITY.json"
)
REQUIREMENT_IDS = (
    "EXPECTED_TRADING_DATE_ARTIFACT_REGISTERED",
    "FCP_0050_QUALITY_RECORD_VALID",
    "MULTI_BATCH_COVERAGE_RECONCILED",
    "PAGINATION_BEHAVIOR_REGISTERED",
    "POINT_IN_TIME_SUPPLEMENTS_REGISTERED",
    "RECONCILED_DATE_SET_EXACT",
    "REQUESTED_END_BOUNDARY_COVERED",
    "REQUESTED_START_BOUNDARY_COVERED",
    "ROW_CAP_AMBIGUITY_RESOLVED",
)


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _block(text: str, start: str, end: str) -> str | None:
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def _record_is_safe(record: dict[str, object], source: dict[str, object]) -> bool:
    try:
        record_copy = dict(record)
        record_sha256 = record_copy.pop("record_sha256")
        coverage = record["coverage"]
        gate = record["gate"]
        lineage = record["lineage"]
        requirements = record["requirements"]
        text = json.dumps(record, ensure_ascii=True, sort_keys=True)
        states = {
            item["requirement_id"]: item["state"] for item in requirements
        }
        return all(
            (
                record_sha256 == _canonical_sha256(record_copy),
                record.get("schema_version") == 1,
                record.get("instrument_id") == "600028.XSHG",
                coverage["requested_start_date"] == "2021-01-01",
                coverage["requested_end_date"] == "2026-07-21",
                coverage["observed_start_date"] == "2024-06-28",
                coverage["observed_end_date"] == "2026-07-21",
                coverage["row_count"] == 500,
                coverage["row_cap_state"] == "AT_REGISTERED_CAP",
                coverage["unresolved_intervals"]
                == [
                    {
                        "end_exclusive": "2024-06-28",
                        "kind": "LEADING",
                        "start_inclusive": "2021-01-01",
                    }
                ],
                gate["gate_state"] == "BLOCKED_INCOMPLETE_REQUESTED_RANGE",
                gate["historical_completeness_proven"] is False,
                gate["operator_review_required"] is True,
                gate["provider_selected"] is False,
                gate["gap_closed"] is False,
                gate["sdk_used"] is False,
                gate["network_used"] is False,
                lineage["source_record_sha256"] == source["record_sha256"],
                lineage["source_evidence_id"] == source["evidence_id"],
                lineage["source_quality_state"]
                == "BLOCKED_PENDING_SUPPLEMENTS",
                tuple(item["requirement_id"] for item in requirements)
                == REQUIREMENT_IDS,
                states["FCP_0050_QUALITY_RECORD_VALID"] == "SATISFIED",
                states["REQUESTED_END_BOUNDARY_COVERED"] == "SATISFIED",
                states["REQUESTED_START_BOUNDARY_COVERED"] == "UNSATISFIED",
                states["RECONCILED_DATE_SET_EXACT"] == "UNRESOLVED",
                all(len(item["requirement_hash"]) == 64 for item in requirements),
                "C:\\" not in text,
                "price_600028.txt" not in text,
                "timetag" not in text,
            )
        )
    except (KeyError, TypeError, ValueError):
        return False


def build_fcp_0051_guard_report(root: Path = ROOT) -> dict[str, object]:
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
        evidence = json.loads((root / EVIDENCE_PATH).read_text(encoding="ascii"))
        source = json.loads((root / SOURCE_PATH).read_text(encoding="ascii"))
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
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, manifest, intake, evidence, source = (), {}, {}, {}, {}
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
    approvals = tuple(_block(text, APPROVAL_START, APPROVAL_END) for text in texts)
    locks = tuple(_block(text, LOCK_START, LOCK_END) for text in texts)
    finals = tuple(_block(text, FINAL_START, FINAL_END) for text in texts)
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0051"
        ),
        {},
    )
    expected_evidence = {
        "FCF_CURRENT_STATE_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE_APP_1_FINAL.md",
        EVIDENCE_PATH.as_posix(),
        "docs/FCF_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE_APP_1_D1_D6.md",
    }
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
            (
                root
                / "FCF_CURRENT_STATE_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE_APP_1_FINAL.md"
            ).is_file()
            and all(finals)
            and "ALL CHECKS PASSED" in finals[0]
        ),
        "manifest_state_safe": active
        or closed
        or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and expected_evidence.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": all(
            term in architecture
            for term in (
                "## 84. Guojin QMT Historical Coverage Completeness Gate",
                "closed conditions",
                "never proves completeness",
            )
        ),
        "adr_registered": all(
            term in adr
            for term in (
                "FCF-V2-ADR-051",
                "Positive Registered Proof",
                "infer sessions from weekdays",
            )
        ),
        "gaps_preserved": all(
            f"V2-FR-GAP-{index:03d}" in gaps and "RESEARCH_REQUIRED" in gaps
            for index in (105, 107, 108)
        ),
        "protocol_registered": "Proposal `FCF-FCP-0051`" in protocol,
        "memory_registered": all(
            term in memory
            for term in (
                "QMT historical coverage completeness gates",
                "closed positive-proof",
                "no inferred trading sessions",
            )
        ),
        "registered_evidence_safe": _record_is_safe(evidence, source),
        "delivery_files_exist": all(
            (root / path).is_file()
            for path in (
                "FCF_CURRENT_STATE_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE_APP_1_APPROVED.md",
                "FCF_CURRENT_STATE_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE_APP_1_DELIVERED.md",
                EVIDENCE_PATH.as_posix(),
                "docs/FCF_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE_APP_1_D1_D6.md",
                "apps/fcp_0051_guojin_qmt_historical_coverage_completeness_gate_app_1/evidence.py",
                "tests/fcp_0051_guojin_qmt_historical_coverage_completeness_gate_app_1/test_d1_d6.py",
            )
        ),
        "run_all_wired": (
            "control_center_fcp_0051_guojin_qmt_historical_coverage_completeness_gate_guard.py"
            in run_all
        ),
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE"
        and truth.get("next_product_implementation_phase") == "NOT_SELECTED"
        and truth.get("next_product_phase_approval") == "NOT_APPROVED",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0051_guard_report()
    if report["ok"] is not True:
        failed = sorted(key for key, value in report["checks"].items() if not value)
        raise SystemExit("FCP-0051 guard failed: " + ",".join(failed))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
