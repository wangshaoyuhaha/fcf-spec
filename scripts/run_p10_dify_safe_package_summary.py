import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from scripts.run_p10_acceptance_smoke import run_smoke as run_p10_acceptance_smoke


RUNNER_NAME = "p10_dify_safe_package_summary"
RUNNER_VERSION = "0.1.0"

DELIVERABLE_PATHS = {
    "p10_plan": "docs/90_p10_dify_safe_paper_operations_plan.md",
    "dify_adapter_contract": "docs/91_p10_global_regression_dify_adapter_contract.md",
    "operator_response_templates_doc": "docs/92_p10_operator_review_response_templates.md",
    "paper_only_operator_runbook": "docs/93_p10_paper_only_operator_runbook.md",
    "failure_triage_guide": "docs/94_p10_failure_triage_guide.md",
    "dify_workflow_node_contract": "docs/95_p10_dify_workflow_node_contract.md",
    "p10_acceptance_smoke_doc": "docs/96_p10_acceptance_smoke.md",
    "p10_closeout_doc": "docs/97_p10_closeout_project_state.md",
    "dify_global_regression_api": "fcf/api/dify_global_regression_api.py",
    "operator_review_response_templates": "fcf/api/operator_review_response_templates.py",
    "p10_acceptance_smoke_script": "scripts/run_p10_acceptance_smoke.py",
}


def _request() -> Dict[str, Any]:
    return {
        "request_id": "p10-d9-package-summary",
        "operator_id": "operator-paper-review",
        "review_mode": "operator_review",
        "requested_checks": [
            "all_smokes",
            "global_report",
            "safe_boundary",
            "project_state_consistency",
        ],
        "output_format": "json",
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
    acceptance = run_p10_acceptance_smoke()
    dify_response = handle_dify_global_regression_request(_request())
    operator_response = render_operator_review_response(dify_response)
    deliverables = _deliverables()

    dify_data = dify_response.get("data") or {}
    safe_boundary = dify_data.get("safe_boundary") or {}

    package_summary = {
        "phase": "P10",
        "phase_name": "Dify-safe paper operations packaging and operator review readiness",
        "post_closeout_package_summary": True,
        "p10_acceptance_completed": acceptance.get("status") == "completed",
        "ready_for_p10_d8_closeout": (
            acceptance.get("acceptance_summary") or {}
        ).get("ready_for_p10_d8_closeout") is True,
        "dify_global_regression_ok": dify_response.get("ok") is True,
        "operator_response_type": operator_response.get("response_type"),
        "operator_response_passed": operator_response.get("response_type") == "global_regression_passed",
        "operator_review_required": dify_data.get("operator_review_required") is True,
        "ready_for_operator_review": dify_data.get("ready_for_operator_review") is True,
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

    package_summary["ready_for_p10_d10_bridge_plan"] = all(
        [
            package_summary["p10_acceptance_completed"],
            package_summary["ready_for_p10_d8_closeout"],
            package_summary["dify_global_regression_ok"],
            package_summary["operator_response_passed"],
            package_summary["operator_review_required"],
            package_summary["ready_for_operator_review"],
            package_summary["deliverables_all_present"],
            package_summary["safe_boundary_ok"],
        ]
    )

    return {
        "status": "completed" if package_summary["ready_for_p10_d10_bridge_plan"] else "failed",
        "runner": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "package_summary": package_summary,
        "deliverables": deliverables,
        "components": {
            "p10_acceptance_smoke": {
                "status": acceptance.get("status"),
                "ready_for_p10_d8_closeout": (
                    acceptance.get("acceptance_summary") or {}
                ).get("ready_for_p10_d8_closeout"),
            },
            "dify_global_regression_adapter": {
                "ok": dify_response.get("ok"),
                "api": dify_response.get("api"),
                "api_version": dify_response.get("api_version"),
                "ready_for_operator_review": dify_data.get("ready_for_operator_review"),
                "operator_review_required": dify_data.get("operator_review_required"),
            },
            "operator_review_response": {
                "response_type": operator_response.get("response_type"),
                "template": operator_response.get("template"),
                "template_version": operator_response.get("template_version"),
                "title": operator_response.get("title"),
            },
        },
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
