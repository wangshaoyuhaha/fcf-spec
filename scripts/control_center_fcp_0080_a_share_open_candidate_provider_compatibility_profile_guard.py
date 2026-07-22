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

from apps.fcp_0080_a_share_open_candidate_provider_compatibility_profile_app_1 import (  # noqa: E402
    BLOCKERS,
    PROVIDERS,
    build_augmented_coverage_matrix,
    candidate_provider_profiles,
    provider_profile_set_hash,
)


DELIVERY_ID = "FCF-FCP-0080-A-SHARE-OPEN-CANDIDATE-PROVIDER-COMPATIBILITY-PROFILE-APP-1"
MARKER = "FCP 0080 A SHARE OPEN CANDIDATE PROVIDER COMPATIBILITY PROFILE APP 1"
PROFILE_SET_HASH = "b384a3172929e36c26a88658cae2287b233c42a691bd52d72d75389d6040978a"
MATRIX_HASH = "2f9853264ef7bcaa34e34867976e59bd5161e84403ef69a559ac3ee67b20abcf"
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


def build_fcp_0080_guard_report(root: Path = ROOT) -> dict[str, object]:
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
        profiles = candidate_provider_profiles()
        profile_hash = provider_profile_set_hash(profiles)
        matrix = build_augmented_coverage_matrix(root, evaluated_at_utc="2026-07-23T05:00:00Z")
        readable = True
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
        texts, manifest, intake, profiles, matrix = (), {}, {}, (), None
        architecture = adr = gaps = protocol = memory = run_all = ""
        profile_hash = ""
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
    proposal = next((item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0080"), {})
    expected = {
        "FCF_CURRENT_STATE_FCP_0080_A_SHARE_OPEN_CANDIDATE_PROVIDER_COMPATIBILITY_PROFILE_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0080_A_SHARE_OPEN_CANDIDATE_PROVIDER_COMPATIBILITY_PROFILE_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0080_A_SHARE_OPEN_CANDIDATE_PROVIDER_COMPATIBILITY_PROFILE_APP_1_FINAL.md",
        "docs/FCF_FCP_0080_A_SHARE_OPEN_CANDIDATE_PROVIDER_COMPATIBILITY_PROFILE_APP_1_D1_D6.md",
    }
    row = next((item for item in matrix.rows if item.requirement.gap_id == "V2-FR-GAP-093"), None) if matrix else None
    gap_row = next((line for line in gaps.splitlines() if "| V2-FR-GAP-093 |" in line), "")
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
                "## 113. A-Share Open Candidate Provider Compatibility Profiles",
                "Tushare, AkShare, and BaoStock",
                "cannot select a provider",
            )
        ),
        "adr_registered": all(
            term in adr
            for term in (
                "FCF-V2-ADR-080",
                "Profile Open Candidates Without Provider Selection",
                "provider selection",
            )
        ),
        "gap_preserved": "| RESEARCH_REQUIRED |" in gap_row,
        "gap_observation_registered": "FCP-0080 is approved" in gaps and "provider-compatibility gap" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0080`" in protocol,
        "memory_registered": "Tushare, AkShare, and BaoStock" in memory,
        "run_all_wired": "control_center_fcp_0080_a_share_open_candidate_provider_compatibility_profile_guard.py" in run_all,
        "provider_order_exact": tuple(item.provider for item in profiles) == PROVIDERS,
        "provider_profile_hash_exact": profile_hash == PROFILE_SET_HASH,
        "profile_blockers_exact": bool(profiles) and all(item.blockers == BLOCKERS for item in profiles),
        "profiles_non_authorizing": bool(profiles)
        and all(
            item.local_artifact_only is True
            and item.sdk_invocation_allowed is False
            and item.network_access_allowed is False
            and item.credentials_allowed is False
            and item.provider_selected is False
            and item.fallback_allowed is False
            and item.promotion_ready is False
            and item.promotes_candidate_data is False
            and item.claims_data_authority is False
            and item.operator_review_required is True
            for item in profiles
        ),
        "matrix_hash_exact": matrix is not None and matrix.matrix_hash == MATRIX_HASH,
        "provider_profile_foundation_covered": row is not None
        and row.missing_capabilities == ()
        and row.coverage_state == "FOUNDATION_COVERED_GAP_OPEN",
        "matrix_non_authorizing": matrix is not None
        and matrix.changes_gap_status is False
        and matrix.promotes_candidate_data is False
        and matrix.provider_selected is False
        and all(item.gap_open is True for item in matrix.rows)
        and all(item.authority_established is False for item in matrix.rows),
        "delivery_files_exist": all((root / path).is_file() for path in expected if "FINAL" not in path)
        and ((root / next(path for path in expected if "FINAL" in path)).is_file() if closed else True),
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0080_guard_report()
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
