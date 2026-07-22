from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0075_a_share_external_candidate_daily_corpus_quality_quarantine_evidence_app_1 import (  # noqa: E402
    CandidateDailyCorpusQualityEvidence,
)
from apps.fcp_0076_a_share_candidate_daily_promotion_readiness_gate_app_1 import (  # noqa: E402
    evaluate_candidate_daily_promotion_readiness,
)


DELIVERY_ID = "FCF-FCP-0076-A-SHARE-CANDIDATE-DAILY-PROMOTION-READINESS-GATE-APP-1"
MARKER = "FCP 0076 A SHARE CANDIDATE DAILY PROMOTION READINESS GATE APP 1"
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
QUALITY_PATH = Path(
    "FCF_REGISTERED_EVIDENCE_FCP_0075_A_SHARE_EXTERNAL_CANDIDATE_DAILY_"
    "CORPUS_QUALITY_QUARANTINE.json"
)
GATE_PATH = Path(
    "FCF_REGISTERED_EVIDENCE_FCP_0076_A_SHARE_CANDIDATE_DAILY_PROMOTION_"
    "READINESS_GATE.json"
)


def _block(text: str, label: str) -> str | None:
    start = f"<!-- {MARKER} {label} START -->"
    end = f"<!-- {MARKER} {label} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    return text[text.index(start) : text.index(end) + len(end)]


def build_fcp_0076_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        manifest = json.loads((root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii"))
        intake = json.loads((root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(encoding="ascii"))
        quality_payload = json.loads((root / QUALITY_PATH).read_text(encoding="ascii"))
        quality_payload.pop("evidence_hash")
        quality = CandidateDailyCorpusQualityEvidence(**quality_payload)
        gate_payload = json.loads((root / GATE_PATH).read_text(encoding="ascii"))
        replay = evaluate_candidate_daily_promotion_readiness(
            quality,
            (),
            evaluated_at_utc=gate_payload["evaluated_at_utc"],
            gate_id=gate_payload["gate_id"],
        )
        architecture = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md").read_text(encoding="ascii")
        adr = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md").read_text(encoding="ascii")
        gaps = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md").read_text(encoding="ascii")
        protocol = (root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md").read_text(encoding="ascii")
        memory = (root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md").read_text(encoding="ascii")
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError, KeyError):
        texts, manifest, intake, gate_payload, replay = (), {}, {}, {}, None
        architecture = adr = gaps = protocol = memory = run_all = ""
        readable = False
    truth = manifest.get("current_truth", {})
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID and status in {
        "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
    }
    closed = truth.get("current_governance_phase_id") == "NONE" and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    approvals = tuple(_block(text, "APPROVAL") for text in texts)
    locks = tuple(_block(text, "LOCK") for text in texts)
    finals = tuple(_block(text, "FINAL") for text in texts)
    proposal = next((item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0076"), {})
    expected = {
        "FCF_CURRENT_STATE_FCP_0076_A_SHARE_CANDIDATE_DAILY_PROMOTION_READINESS_GATE_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0076_A_SHARE_CANDIDATE_DAILY_PROMOTION_READINESS_GATE_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0076_A_SHARE_CANDIDATE_DAILY_PROMOTION_READINESS_GATE_APP_1_FINAL.md",
        "docs/FCF_FCP_0076_A_SHARE_CANDIDATE_DAILY_PROMOTION_READINESS_GATE_APP_1_D1_D6.md",
    }
    required_gaps = (
        "V2-FR-GAP-023",
        "V2-FR-GAP-087",
        "V2-FR-GAP-088",
        "V2-FR-GAP-089",
        "V2-FR-GAP-090",
        "V2-FR-GAP-091",
        "V2-FR-GAP-092",
        "V2-FR-GAP-093",
    )
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_implemented": status not in {"GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION", "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"} or (all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed or (all(finals) and len(set(finals)) == 1),
        "final_evidence_when_closed": not closed or ((root / next(path for path in expected if "FINAL" in path)).is_file() and all(finals) and "ALL CHECKS PASSED" in finals[0]),
        "manifest_state_safe": active or closed or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status") == proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE" and proposal.get("phase_id") == "NONE" and expected.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": all(term in architecture for term in ("## 109. A-Share Candidate Daily Promotion Readiness Gate", "ready for mandatory Operator review only", "current downloaded corpus must fail closed")),
        "adr_registered": all(term in adr for term in ("FCF-V2-ADR-076", "Fail Closed Before Candidate Daily Promotion", "let the gate", "promote data itself")),
        "gaps_preserved": all(any(gap in line and any(f"| {state} |" in line for state in ("NOT_IMPLEMENTED", "RESEARCH_REQUIRED")) for line in gaps.splitlines()) for gap in required_gaps),
        "protocol_registered": "Proposal `FCF-FCP-0076`" in protocol,
        "memory_registered": "candidate daily promotion-readiness gates" in memory,
        "run_all_wired": "control_center_fcp_0076_a_share_candidate_daily_promotion_readiness_gate_guard.py" in run_all,
        "gate_replays": replay is not None and json.loads(json.dumps(asdict(replay), sort_keys=True)) == gate_payload,
        "gate_fail_closed": gate_payload.get("status") == "BLOCKED_NOT_READY_FOR_OPERATOR_REVIEW" and len(gate_payload.get("blocker_codes", [])) == 11 and gate_payload.get("candidate_promotion_allowed") is False and gate_payload.get("factor_calculation_allowed") is False and gate_payload.get("training_label_allowed") is False and gate_payload.get("provider_selection_allowed") is False and gate_payload.get("operator_review_mandatory") is True,
        "delivery_files_exist": all((root / path).is_file() for path in expected if "FINAL" not in path) and ((root / next(path for path in expected if "FINAL" in path)).is_file() if closed else True) and (root / GATE_PATH).is_file(),
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0076_guard_report()
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
