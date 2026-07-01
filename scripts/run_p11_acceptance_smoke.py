import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from fcf.regression.regression_stability_gate import evaluate_regression_stability_gate
from scripts.run_p10_dify_safe_package_summary import run_smoke as run_p10_package_summary


RUNNER_NAME = "p11_acceptance_smoke"
RUNNER_VERSION = "0.1.0"

ACCEPTED_DAYS = [
    "P11-D1",
    "P11-D2",
    "P11-D3",
    "P11-D4",
    "P11-D5",
    "P11-D6",
    "P11-D7",
]

P11_DOCS = [
    "docs/100_p11_release_readiness_plan.md",
    "docs/101_p11_operator_handoff_package.md",
    "docs/102_p11_versioned_run_commands.md",
    "docs/103_p11_artifact_inventory.md",
    "docs/104_p11_maintenance_checklist.md",
    "docs/105_p11_regression_stability_gate.md",
    "docs/106_p11_acceptance_smoke.md",
]


def _request() -> Dict[str, Any]:
    return {
        "request_id": "p11-d7-acceptance",
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


def _docs_readiness() -> Dict[str, Any]:
    docs = {
        doc: (PROJECT_ROOT / doc).exists()
        for doc in P11_DOCS
    }
    return {
        "docs": docs,
        "doc_count": len(docs),
        "present_count": sum(1 for exists in docs.values() if exists),
        "all_docs_present": all(docs.values()),
    }


def run_smoke() -> Dict[str, Any]:
    package = run_p10_package_summary()
    gate = evaluate_regression_stability_gate(package)
    dify_response = handle_dify_global_regression_request(_request())
    operator_response = render_operator_review_response(dify_response)
    docs_readiness = _docs_readiness()

    dify_data = dify_response.get("data") or {}
    safe_boundary = dify_data.get("safe_boundary") or package.get("safe_boundary") or {}

    acceptance_summary = {
        "phase": "P11",
        "phase_name": "Release readiness, operator handoff package, and long-term maintainability",
        "accepted_days": ACCEPTED_DAYS,
        "p10_package_completed": package.get("status") == "completed",
        "p10_package_ready_for_bridge": (
            package.get("package_summary") or {}
        ).get("ready_for_p10_d10_bridge_plan") is True,
        "regression_stability_gate_completed": gate.get("status") == "completed",
        "regression_stability_gate_ok": gate.get("ok") is True,
        "ready_for_p11_d7_acceptance_smoke": gate.get("ready_for_p11_d7_acceptance_smoke") is True,
        "dify_global_regression_ok": dify_response.get("ok") is True,
        "operator_response_type": operator_response.get("response_type"),
        "operator_response_passed": operator_response.get("response_type") == "global_regression_passed",
        "operator_review_required": dify_data.get("operator_review_required") is True,
        "ready_for_operator_review": dify_data.get("ready_for_operator_review") is True,
        "p11_docs_ready": docs_readiness["all_docs_present"] is True,
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

    acceptance_summary["ready_for_p11_d8_closeout"] = all(
        [
            acceptance_summary["p10_package_completed"],
            acceptance_summary["p10_package_ready_for_bridge"],
            acceptance_summary["regression_stability_gate_completed"],
            acceptance_summary["regression_stability_gate_ok"],
            acceptance_summary["ready_for_p11_d7_acceptance_smoke"],
            acceptance_summary["dify_global_regression_ok"],
            acceptance_summary["operator_response_passed"],
            acceptance_summary["operator_review_required"],
            acceptance_summary["ready_for_operator_review"],
            acceptance_summary["p11_docs_ready"],
            acceptance_summary["safe_boundary_ok"],
        ]
    )

    return {
        "status": "completed" if acceptance_summary["ready_for_p11_d8_closeout"] else "failed",
        "runner": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "acceptance_summary": acceptance_summary,
        "components": {
            "p10_package_summary": {
                "status": package.get("status"),
                "ready_for_p10_d10_bridge_plan": (
                    package.get("package_summary") or {}
                ).get("ready_for_p10_d10_bridge_plan"),
            },
            "regression_stability_gate": {
                "status": gate.get("status"),
                "ok": gate.get("ok"),
                "ready_for_p11_d7_acceptance_smoke": gate.get("ready_for_p11_d7_acceptance_smoke"),
                "violation_count": len(gate.get("violations") or []),
            },
            "dify_global_regression_adapter": {
                "ok": dify_response.get("ok"),
                "api": dify_response.get("api"),
                "api_version": dify_response.get("api_version"),
                "operator_review_required": dify_data.get("operator_review_required"),
                "ready_for_operator_review": dify_data.get("ready_for_operator_review"),
            },
            "operator_review_response": {
                "response_type": operator_response.get("response_type"),
                "template": operator_response.get("template"),
                "template_version": operator_response.get("template_version"),
                "title": operator_response.get("title"),
            },
            "p11_docs_readiness": docs_readiness,
        },
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
