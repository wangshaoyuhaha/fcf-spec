import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_p11_release_readiness_package_summary import run_smoke as run_p11_summary
from scripts.run_p12_acceptance_smoke import run_smoke as run_p12_acceptance


RUNNER_NAME = "p12_final_delivery_package_summary"
RUNNER_VERSION = "0.1.0"

DELIVERABLE_PATHS = {
    "p12_documentation_hardening_plan": "docs/110_p12_documentation_hardening_plan.md",
    "final_non_production_delivery_package": "docs/111_p12_final_non_production_delivery_package.md",
    "archive_readiness_checklist": "docs/112_p12_archive_readiness_checklist.md",
    "final_command_index": "docs/113_p12_final_command_index.md",
    "final_artifact_manifest": "docs/114_p12_final_artifact_manifest.md",
    "final_safety_boundary_declaration": "docs/115_p12_final_safety_boundary_declaration.md",
    "final_operator_delivery_note": "docs/116_p12_final_operator_delivery_note.md",
    "p12_acceptance_smoke_doc": "docs/117_p12_acceptance_smoke.md",
    "p12_closeout_project_state": "docs/118_p12_closeout_project_state.md",
    "post_closeout_final_delivery_package_summary": "docs/119_p12_post_closeout_final_delivery_package_summary.md",
    "p12_acceptance_smoke_script": "scripts/run_p12_acceptance_smoke.py",
    "p12_final_delivery_package_summary_script": "scripts/run_p12_final_delivery_package_summary.py",
}


def _deliverables() -> Dict[str, Any]:
    items = {
        name: {
            "path": path,
            "exists": (PROJECT_ROOT / path).exists(),
        }
        for name, path in DELIVERABLE_PATHS.items()
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
            boundary.get("operator_review_required") is True,
            boundary.get("auto_live_trading") is False,
            boundary.get("bypass_operator_review") is False,
            boundary.get("bypass_policy_risk_safe_boundary") is False,
        ]
    )


def run_smoke() -> Dict[str, Any]:
    p11_summary = run_p11_summary()
    p12_acceptance = run_p12_acceptance()
    deliverables = _deliverables()

    p11_package_summary = p11_summary.get("package_summary") or {}
    p12_acceptance_summary = p12_acceptance.get("acceptance_summary") or {}
    safe_boundary = p12_acceptance.get("safe_boundary") or p11_summary.get("safe_boundary") or {}

    package_summary = {
        "phase": "P12",
        "phase_name": "Documentation hardening, archive readiness, and final non-production delivery package",
        "post_closeout_final_delivery_package_summary": True,
        "p12_acceptance_completed": p12_acceptance.get("status") == "completed",
        "ready_for_p12_d8_closeout": p12_acceptance_summary.get("ready_for_p12_d8_closeout") is True,
        "p11_release_readiness_summary_completed": p11_summary.get("status") == "completed",
        "ready_for_p11_d10_bridge_plan": p11_package_summary.get("ready_for_p11_d10_bridge_plan") is True,
        "deliverables_all_present": deliverables["all_present"] is True,
        "safe_boundary_ok": _safe_boundary_ok(safe_boundary),
    }

    package_summary["ready_for_p12_d10_archive_bridge_plan"] = all(
        [
            package_summary["p12_acceptance_completed"],
            package_summary["ready_for_p12_d8_closeout"],
            package_summary["p11_release_readiness_summary_completed"],
            package_summary["ready_for_p11_d10_bridge_plan"],
            package_summary["deliverables_all_present"],
            package_summary["safe_boundary_ok"],
        ]
    )

    return {
        "status": "completed" if package_summary["ready_for_p12_d10_archive_bridge_plan"] else "failed",
        "runner": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "package_summary": package_summary,
        "deliverables": deliverables,
        "components": {
            "p12_acceptance_smoke": {
                "status": p12_acceptance.get("status"),
                "ready_for_p12_d8_closeout": p12_acceptance_summary.get("ready_for_p12_d8_closeout"),
            },
            "p11_release_readiness_package_summary": {
                "status": p11_summary.get("status"),
                "ready_for_p11_d10_bridge_plan": p11_package_summary.get("ready_for_p11_d10_bridge_plan"),
                "safe_boundary_ok": p11_package_summary.get("safe_boundary_ok"),
            },
            "final_non_production_delivery_package": {
                "path": DELIVERABLE_PATHS["final_non_production_delivery_package"],
                "exists": deliverables["items"]["final_non_production_delivery_package"]["exists"],
            },
            "p12_closeout_project_state": {
                "path": DELIVERABLE_PATHS["p12_closeout_project_state"],
                "exists": deliverables["items"]["p12_closeout_project_state"]["exists"],
            },
        },
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
