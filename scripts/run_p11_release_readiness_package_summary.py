import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.regression.regression_stability_gate import evaluate_regression_stability_gate
from scripts.run_p10_dify_safe_package_summary import run_smoke as run_p10_package_summary
from scripts.run_p11_acceptance_smoke import run_smoke as run_p11_acceptance_smoke


RUNNER_NAME = "p11_release_readiness_package_summary"
RUNNER_VERSION = "0.1.0"

DELIVERABLE_PATHS = {
    "p11_release_readiness_plan": "docs/100_p11_release_readiness_plan.md",
    "operator_handoff_package": "docs/101_p11_operator_handoff_package.md",
    "versioned_run_commands": "docs/102_p11_versioned_run_commands.md",
    "artifact_inventory": "docs/103_p11_artifact_inventory.md",
    "maintenance_checklist": "docs/104_p11_maintenance_checklist.md",
    "regression_stability_gate_doc": "docs/105_p11_regression_stability_gate.md",
    "p11_acceptance_smoke_doc": "docs/106_p11_acceptance_smoke.md",
    "p11_closeout_doc": "docs/107_p11_closeout_project_state.md",
    "regression_stability_gate_module": "fcf/regression/regression_stability_gate.py",
    "p11_acceptance_smoke_script": "scripts/run_p11_acceptance_smoke.py",
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


def run_smoke() -> Dict[str, Any]:
    p10_package = run_p10_package_summary()
    gate = evaluate_regression_stability_gate(p10_package)
    acceptance = run_p11_acceptance_smoke()
    deliverables = _deliverables()

    safe_boundary = acceptance.get("safe_boundary") or p10_package.get("safe_boundary") or {}

    package_summary = {
        "phase": "P11",
        "phase_name": "Release readiness, operator handoff package, and long-term maintainability",
        "post_closeout_release_readiness_package_summary": True,
        "p11_acceptance_completed": acceptance.get("status") == "completed",
        "ready_for_p11_d8_closeout": (
            acceptance.get("acceptance_summary") or {}
        ).get("ready_for_p11_d8_closeout") is True,
        "regression_stability_gate_completed": gate.get("status") == "completed",
        "regression_stability_gate_ok": gate.get("ok") is True,
        "ready_for_p11_d7_acceptance_smoke": gate.get("ready_for_p11_d7_acceptance_smoke") is True,
        "deliverables_all_present": deliverables["all_present"] is True,
        "safe_boundary_ok": (
            safe_boundary.get("paper_only") is True
            and safe_boundary.get("real_order") is False
            and safe_boundary.get("real_execution") is False
            and safe_boundary.get("real_exchange_api") is False
            and safe_boundary.get("real_money_impact") is False
            and safe_boundary.get("operator_review_required") is True
            and safe_boundary.get("auto_live_trading") is False
            and safe_boundary.get("bypass_operator_review") is False
            and safe_boundary.get("bypass_policy_risk_safe_boundary") is False
        ),
    }

    package_summary["ready_for_p11_d10_bridge_plan"] = all(
        [
            package_summary["p11_acceptance_completed"],
            package_summary["ready_for_p11_d8_closeout"],
            package_summary["regression_stability_gate_completed"],
            package_summary["regression_stability_gate_ok"],
            package_summary["ready_for_p11_d7_acceptance_smoke"],
            package_summary["deliverables_all_present"],
            package_summary["safe_boundary_ok"],
        ]
    )

    return {
        "status": "completed" if package_summary["ready_for_p11_d10_bridge_plan"] else "failed",
        "runner": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "package_summary": package_summary,
        "deliverables": deliverables,
        "components": {
            "p11_acceptance_smoke": {
                "status": acceptance.get("status"),
                "ready_for_p11_d8_closeout": (
                    acceptance.get("acceptance_summary") or {}
                ).get("ready_for_p11_d8_closeout"),
            },
            "regression_stability_gate": {
                "status": gate.get("status"),
                "ok": gate.get("ok"),
                "ready_for_p11_d7_acceptance_smoke": gate.get("ready_for_p11_d7_acceptance_smoke"),
                "violation_count": len(gate.get("violations") or []),
            },
            "p10_package_summary": {
                "status": p10_package.get("status"),
                "ready_for_p10_d10_bridge_plan": (
                    p10_package.get("package_summary") or {}
                ).get("ready_for_p10_d10_bridge_plan"),
            },
        },
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
