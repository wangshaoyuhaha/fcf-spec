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

from apps.fcp_0081_a_share_candidate_provider_after_cost_data_value_experiment_contract_app_1 import (  # noqa: E402
    LOWER_IS_BETTER,
    METRIC_IDS,
    AfterCostEvidence,
    ComparableMetricObservation,
    DataValueExperimentSpecification,
    evaluate_data_value_experiment,
)


DELIVERY_ID = "FCF-FCP-0081-A-SHARE-CANDIDATE-PROVIDER-AFTER-COST-DATA-VALUE-EXPERIMENT-CONTRACT-APP-1"
MARKER = "FCP 0081 A SHARE CANDIDATE PROVIDER AFTER COST DATA VALUE EXPERIMENT CONTRACT APP 1"
CONTRACT_PATH = "apps/fcp_0081_a_share_candidate_provider_after_cost_data_value_experiment_contract_app_1/contracts.py"
CONTRACT_SHA = "3c22ac10ccbd3e8d27db97bdf2a9f851679e01f2ec336a2433b0a458f408bd1a"
REFERENCE_PACKET_HASH = "e54b2033f4eca1773d3a3544fe98aba77653cd1ac393f2b6c4e9f2f3e7263baf"
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


def _reference_packet():
    sha_a, sha_b, sha_c, sha_d = (character * 64 for character in "abcd")
    specification = DataValueExperimentSpecification(
        experiment_id="experiment-a-share-provider-v1",
        baseline_candidate_id="miniqmt-local-baseline",
        candidate_id="tushare-local-candidate",
        baseline_profile_hash=sha_a,
        candidate_profile_hash=sha_b,
        baseline_artifact_sha256=sha_c,
        candidate_artifact_sha256=sha_d,
        instrument_ids=("000001.XSHE", "600000.XSHG"),
        start_date="2026-01-01",
        end_date="2026-06-30",
    )
    rows = []
    for metric_id in METRIC_IDS:
        baseline = "0.1" if metric_id == "CONFLICT_RATE" else "10" if metric_id in LOWER_IS_BETTER else "0.8"
        candidate = "0.05" if metric_id == "CONFLICT_RATE" else "5" if metric_id in LOWER_IS_BETTER else "0.9"
        rows.append(
            ComparableMetricObservation(
                specification_hash=specification.specification_hash,
                metric_id=metric_id,
                baseline_value=baseline,
                candidate_value=candidate,
                comparable_window_hash=sha_a,
                evidence_sha256=sha_b,
                observed_at_utc="2026-07-23T06:30:00Z",
            )
        )
    after_cost = AfterCostEvidence(
        specification_hash=specification.specification_hash,
        fixed_cost_cny="0",
        measured_benefit_cny="10",
        cost_evidence_sha256=sha_c,
        benefit_evidence_sha256=sha_d,
        rights_state="REGISTERED_REVIEW_COMPLETE",
        retention_state="REGISTERED_REVIEW_COMPLETE",
        observed_at_utc="2026-07-23T06:31:00Z",
    )
    return specification, evaluate_data_value_experiment(specification, tuple(rows), after_cost)


def build_fcp_0081_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple((root / path).read_text(encoding="ascii") for path in AUTHORITIES)
        manifest = json.loads((root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii"))
        intake = json.loads((root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(encoding="ascii"))
        architecture = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md").read_text(encoding="ascii")
        adr = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md").read_text(encoding="ascii")
        gaps = (root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md").read_text(encoding="ascii")
        protocol = (root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md").read_text(encoding="ascii")
        memory = (root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md").read_text(encoding="ascii")
        run_all = (root / "scripts/run_all_checks.py").read_text(encoding="ascii")
        contract_bytes = (root / CONTRACT_PATH).read_bytes()
        contract_text = contract_bytes.decode("ascii")
        specification, packet = _reference_packet()
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
        texts, manifest, intake = (), {}, {}
        architecture = adr = gaps = protocol = memory = run_all = contract_text = ""
        contract_bytes = b""
        specification = packet = None
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
    proposal = next((item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0081"), {})
    expected = {
        "FCF_CURRENT_STATE_FCP_0081_A_SHARE_CANDIDATE_PROVIDER_AFTER_COST_DATA_VALUE_EXPERIMENT_CONTRACT_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0081_A_SHARE_CANDIDATE_PROVIDER_AFTER_COST_DATA_VALUE_EXPERIMENT_CONTRACT_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0081_A_SHARE_CANDIDATE_PROVIDER_AFTER_COST_DATA_VALUE_EXPERIMENT_CONTRACT_APP_1_FINAL.md",
        "docs/FCF_FCP_0081_A_SHARE_CANDIDATE_PROVIDER_AFTER_COST_DATA_VALUE_EXPERIMENT_CONTRACT_APP_1_D1_D6.md",
    }
    gap_row = next((line for line in gaps.splitlines() if "| V2-FR-GAP-094 |" in line), "")
    prohibited_imports = ("import requests", "import socket", "import urllib", "import rqdatac", "import xtquant")
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_implemented": status not in {
            "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
            "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
        } or (all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed or (all(finals) and len(set(finals)) == 1),
        "final_evidence_when_closed": not closed or (
            (root / next(path for path in expected if "FINAL" in path)).is_file()
            and all(finals)
            and "ALL CHECKS PASSED" in finals[0]
        ),
        "manifest_state_safe": active or closed or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status") == proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and expected.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": all(
            term in architecture
            for term in (
                "## 114. A-Share Incremental After-Cost Data-Value Experiment Contract",
                "mandatory Operator review",
                "cannot select, endorse, purchase, renew, cancel, or activate",
            )
        ),
        "adr_registered": all(
            term in adr
            for term in (
                "FCF-V2-ADR-081",
                "Require Incremental After-Cost Evidence Before Provider Spend",
                "Current authorized spend is zero",
            )
        ),
        "gap_preserved": "| RESEARCH_REQUIRED |" in gap_row,
        "gap_observation_registered": "FCP-0081 is approved" in gaps and "authorized spend remains zero" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0081`" in protocol,
        "memory_registered": "incremental after-cost candidate-provider experiment contracts" in memory,
        "run_all_wired": "control_center_fcp_0081_a_share_candidate_provider_after_cost_data_value_experiment_contract_guard.py" in run_all,
        "contract_hash_exact": hashlib.sha256(contract_bytes).hexdigest() == CONTRACT_SHA,
        "reference_packet_hash_exact": packet is not None and packet.packet_hash == REFERENCE_PACKET_HASH,
        "reference_outcome_review_only": packet is not None
        and packet.decision_state == "OPERATOR_REVIEW_ELIGIBLE"
        and packet.provider_selected is False
        and packet.purchase_authorized is False
        and packet.renewal_authorized is False
        and packet.cancellation_authorized is False
        and packet.claims_profitability is False
        and packet.closes_gap is False,
        "zero_spend_exact": specification is not None and str(specification.authorized_spend_cny) == "0",
        "no_provider_runtime_import": not any(term in contract_text for term in prohibited_imports),
        "delivery_files_exist": all((root / path).is_file() for path in expected if "FINAL" not in path)
        and ((root / next(path for path in expected if "FINAL" in path)).is_file() if closed else True),
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0081_guard_report()
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
