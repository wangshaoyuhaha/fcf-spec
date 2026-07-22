from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
DELIVERY_ID = "FCF-FCP-0050-GUOJIN-QMT-REGISTERED-DUAL-EXPORT-QUALITY-EVIDENCE-APP-1"
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
MARKER = "FCP 0050 GUOJIN QMT REGISTERED DUAL EXPORT QUALITY EVIDENCE APP 1"
APPROVAL_START = f"<!-- {MARKER} APPROVAL START -->"
APPROVAL_END = f"<!-- {MARKER} APPROVAL END -->"
LOCK_START = f"<!-- {MARKER} LOCK START -->"
LOCK_END = f"<!-- {MARKER} LOCK END -->"
FINAL_START = f"<!-- {MARKER} FINAL START -->"
FINAL_END = f"<!-- {MARKER} FINAL END -->"
EVIDENCE_PATH = Path(
    "FCF_REGISTERED_EVIDENCE_FCP_0050_GUOJIN_QMT_DUAL_EXPORT_QUALITY.json"
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


def _record_is_safe(record: dict[str, object]) -> bool:
    try:
        record_copy = dict(record)
        record_sha256 = record_copy.pop("record_sha256")
        artifact_pair = record["artifact_pair"]
        observation = record["observation"]
        quality = record["quality"]
        lineage = record["lineage"]
        text = json.dumps(record, ensure_ascii=True, sort_keys=True)
        keys = set()

        def collect(value: object) -> None:
            if isinstance(value, dict):
                keys.update(value)
                for nested in value.values():
                    collect(nested)
            elif isinstance(value, list):
                for nested in value:
                    collect(nested)

        collect(record)
        return all(
            (
                record_sha256 == _canonical_sha256(record_copy),
                record.get("schema_version") == 1,
                record.get("operator_review_required") is True,
                artifact_pair["raw"]["artifact_sha256"]
                == "4c61b151c7dda4d321d1bbf6143d9cde2dec7db593f90d14a47fa79ac15e8da6",
                artifact_pair["front"]["artifact_sha256"]
                == "ca509e505f9df82812ee822de72726149a9df878b0ca6e47504a5818d4686c6c",
                artifact_pair["raw"]["byte_length"] == 26711,
                artifact_pair["front"]["byte_length"] == 26711,
                artifact_pair["raw_provider_bytes_committed"] is False,
                artifact_pair["local_paths_committed"] is False,
                observation["instrument_id"] == "600028.XSHG",
                observation["actual_start_date"] == "2024-06-28",
                observation["actual_end_date"] == "2026-07-21",
                observation["row_count"] == 500,
                observation["row_cap_state"] == "AT_REGISTERED_CAP",
                observation["volume_lot_size"] == 100,
                sum(item["row_count"] for item in observation["offset_distribution"])
                == 500,
                len(observation["boundary_dates"]) == 5,
                quality["quality_state"] == "BLOCKED_PENDING_SUPPLEMENTS",
                quality["adjustment_factor_authority"] is False,
                quality["historical_completeness_claimed"] is False,
                quality["provider_selected"] is False,
                quality["gap_closed"] is False,
                quality["sdk_used"] is False,
                quality["network_used"] is False,
                len(lineage["row_ledger_sha256"]) == 64,
                not {"timetag", "open", "high", "low", "close", "volumn", "amount"}
                & keys,
                "C:\\" not in text,
                "price_600028.txt" not in text,
            )
        )
    except (KeyError, TypeError, ValueError):
        return False


def build_fcp_0050_guard_report(root: Path = ROOT) -> dict[str, object]:
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
        architecture = (
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
        ).read_text(encoding="ascii")
        adr = (
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md"
        ).read_text(encoding="ascii")
        gaps = (
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
        ).read_text(encoding="ascii")
        protocol = (root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md").read_text(
            encoding="ascii"
        )
        memory = (root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md").read_text(
            encoding="ascii"
        )
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        texts, manifest, intake, evidence = (), {}, {}, {}
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
            if item.get("proposal_id") == "FCF-FCP-0050"
        ),
        {},
    )
    expected_evidence = {
        "FCF_CURRENT_STATE_FCP_0050_GUOJIN_QMT_REGISTERED_DUAL_EXPORT_QUALITY_EVIDENCE_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0050_GUOJIN_QMT_REGISTERED_DUAL_EXPORT_QUALITY_EVIDENCE_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0050_GUOJIN_QMT_REGISTERED_DUAL_EXPORT_QUALITY_EVIDENCE_APP_1_FINAL.md",
        "FCF_REGISTERED_EVIDENCE_FCP_0050_GUOJIN_QMT_DUAL_EXPORT_QUALITY.json",
        "docs/FCF_FCP_0050_GUOJIN_QMT_REGISTERED_DUAL_EXPORT_QUALITY_EVIDENCE_APP_1_D1_D6.md",
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
                / "FCF_CURRENT_STATE_FCP_0050_GUOJIN_QMT_REGISTERED_DUAL_EXPORT_QUALITY_EVIDENCE_APP_1_FINAL.md"
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
                "## 83. Guojin QMT Registered Dual Export Quality Evidence",
                "100-share-lot consistency check",
                "does not close GAP-104 through",
            )
        ),
        "adr_registered": all(
            term in adr
            for term in (
                "FCF-V2-ADR-050",
                "Preserve QMT Dual-Export Facts Without Inventing Adjustment Authority",
                "infer an official factor from additive deltas",
            )
        ),
        "gaps_preserved": all(
            f"V2-FR-GAP-{index:03d}" in gaps and "RESEARCH_REQUIRED" in gaps
            for index in range(104, 110)
        ),
        "protocol_registered": "Proposal `FCF-FCP-0050`" in protocol,
        "memory_registered": all(
            term in memory
            for term in (
                "registered Guojin QMT dual-export quality evidence",
                "100-share-lot consistency",
                "no completeness or factor-authority claim",
            )
        ),
        "registered_evidence_safe": _record_is_safe(evidence),
        "delivery_files_exist": all(
            (root / path).is_file()
            for path in (
                "FCF_CURRENT_STATE_FCP_0050_GUOJIN_QMT_REGISTERED_DUAL_EXPORT_QUALITY_EVIDENCE_APP_1_APPROVED.md",
                "FCF_CURRENT_STATE_FCP_0050_GUOJIN_QMT_REGISTERED_DUAL_EXPORT_QUALITY_EVIDENCE_APP_1_DELIVERED.md",
                EVIDENCE_PATH.as_posix(),
                "docs/FCF_FCP_0050_GUOJIN_QMT_REGISTERED_DUAL_EXPORT_QUALITY_EVIDENCE_APP_1_D1_D6.md",
                "apps/fcp_0050_guojin_qmt_registered_dual_export_quality_evidence_app_1/evidence.py",
                "tests/fcp_0050_guojin_qmt_registered_dual_export_quality_evidence_app_1/test_d1_d6.py",
            )
        ),
        "run_all_wired": "control_center_fcp_0050_guojin_qmt_registered_dual_export_quality_evidence_guard.py"
        in run_all,
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE"
        and truth.get("next_product_implementation_phase") == "NOT_SELECTED"
        and truth.get("next_product_phase_approval") == "NOT_APPROVED",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0050_guard_report()
    if report["ok"] is not True:
        failed = sorted(key for key, value in report["checks"].items() if not value)
        raise SystemExit("FCP-0050 guard failed: " + ",".join(failed))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
