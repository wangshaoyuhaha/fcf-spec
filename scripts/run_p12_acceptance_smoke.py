import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_p11_release_readiness_package_summary import run_smoke as run_p11_package_summary


RUNNER_NAME = "p12_acceptance_smoke"
RUNNER_VERSION = "0.1.0"

P12_DELIVERABLES = {
    "documentation_hardening_plan": "docs/110_p12_documentation_hardening_plan.md",
    "final_non_production_delivery_package": "docs/111_p12_final_non_production_delivery_package.md",
    "archive_readiness_checklist": "docs/112_p12_archive_readiness_checklist.md",
    "final_command_index": "docs/113_p12_final_command_index.md",
    "final_artifact_manifest": "docs/114_p12_final_artifact_manifest.md",
    "final_safety_boundary_declaration": "docs/115_p12_final_safety_boundary_declaration.md",
    "final_operator_delivery_note": "docs/116_p12_final_operator_delivery_note.md",
    "phase12_acceptance_smoke_doc": "docs/117_p12_acceptance_smoke.md",
    "phase12_acceptance_smoke_script": "scripts/run_p12_acceptance_smoke.py",
}


def _deliverables() -> Dict[str, Any]:
    items = {
        name: {
            "path": path,
            "exists": (PROJECT_ROOT / path).exists(),
        }
        for name, path in P12_DELIVERABLES.items()
    }

    return {
        "items": items,
        "deliverable_count": len(items),
        "present_count": sum(1 for item in items.values() if item["exists"]),
        "all_present": all(item["exists"] for item in items.values()),
    }


def _safe_boundary_ok(boundary: Dict[str, Any]) -> bool:
    return all(
        [
            boundary.get("paper_only") is True,
            boundary.get("execution_mode") == "paper",
            boundary.get("real_order") is False,
            boundary.get("real_execution") is False,
            boundary.get("real_exchange_api") is False,
            boundary.get("real_money_impact") is False,
            boundary.get("no_real_exchange_api") is True,
            boundary.get("no_real_order_placement") is True,
            boundary.get("no_exchange_api_key_storage") is True,
            boundary.get("no_wallet_private_key_access") is True,
            boundary.get("no_real_account_balance_read") is True,
            boundary.get("no_real_position_read") is True,
            boundary.get("does_not_claim_real_trade_success") is True,
            boundary.get("operator_review_required") is True,
            boundary.get("auto_live_trading") is False,
            boundary.get("bypass_operator_review") is False,
            boundary.get("bypass_policy_risk_safe_boundary") is False,
        ]
    )


def run_smoke() -> Dict[str, Any]:
    p11_summary = run_p11_package_summary()
    deliverables = _deliverables()
    boundary = p11_summary.get("safe_boundary") or {}

    p11_package_summary = p11_summary.get("package_summary") or {}

    acceptance_summary = {
        "phase": "P12",
        "phase_name": "Documentation hardening, archive readiness, and final non-production delivery package",
        "accepted_days": ["P12-D1", "P12-D2", "P12-D3", "P12-D4", "P12-D5", "P12-D6", "P12-D7"],
        "p11_release_readiness_summary_completed": p11_summary.get("status") == "completed",
        "ready_for_p11_d10_bridge_plan": p11_package_summary.get("ready_for_p11_d10_bridge_plan") is True,
        "p12_docs_all_present": deliverables["all_present"] is True,
        "final_non_production_delivery_package_present": deliverables["items"]["final_non_production_delivery_package"]["exists"] is True,
        "archive_readiness_checklist_present": deliverables["items"]["archive_readiness_checklist"]["exists"] is True,
        "final_command_index_present": deliverables["items"]["final_command_index"]["exists"] is True,
        "final_artifact_manifest_present": deliverables["items"]["final_artifact_manifest"]["exists"] is True,
        "final_safety_boundary_declaration_present": deliverables["items"]["final_safety_boundary_declaration"]["exists"] is True,
        "final_operator_delivery_note_present": deliverables["items"]["final_operator_delivery_note"]["exists"] is True,
        "safe_boundary_ok": _safe_boundary_ok(boundary),
    }

    acceptance_summary["ready_for_p12_d8_closeout"] = all(
        [
            acceptance_summary["p11_release_readiness_summary_completed"],
            acceptance_summary["ready_for_p11_d10_bridge_plan"],
            acceptance_summary["p12_docs_all_present"],
            acceptance_summary["final_non_production_delivery_package_present"],
            acceptance_summary["archive_readiness_checklist_present"],
            acceptance_summary["final_command_index_present"],
            acceptance_summary["final_artifact_manifest_present"],
            acceptance_summary["final_safety_boundary_declaration_present"],
            acceptance_summary["final_operator_delivery_note_present"],
            acceptance_summary["safe_boundary_ok"],
        ]
    )

    return {
        "status": "completed" if acceptance_summary["ready_for_p12_d8_closeout"] else "failed",
        "runner": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "acceptance_summary": acceptance_summary,
        "deliverables": deliverables,
        "components": {
            "p11_release_readiness_package_summary": {
                "status": p11_summary.get("status"),
                "ready_for_p11_d10_bridge_plan": p11_package_summary.get("ready_for_p11_d10_bridge_plan"),
                "safe_boundary_ok": p11_package_summary.get("safe_boundary_ok"),
            },
            "p12_final_delivery_package": {
                "path": P12_DELIVERABLES["final_non_production_delivery_package"],
                "exists": deliverables["items"]["final_non_production_delivery_package"]["exists"],
            },
            "p12_final_safety_boundary_declaration": {
                "path": P12_DELIVERABLES["final_safety_boundary_declaration"],
                "exists": deliverables["items"]["final_safety_boundary_declaration"]["exists"],
            },
        },
        "safe_boundary": boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
