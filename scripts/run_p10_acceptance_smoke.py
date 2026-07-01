import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from scripts.run_p9_global_regression_summary import run_smoke as run_p9_global_regression_summary


RUNNER_NAME = "p10_acceptance_smoke"
RUNNER_VERSION = "0.1.0"

ACCEPTED_DAYS = [
    "P10-D1",
    "P10-D2",
    "P10-D3",
    "P10-D4",
    "P10-D5",
    "P10-D6",
    "P10-D7",
]

P10_DOCS = [
    "docs/90_p10_dify_safe_paper_operations_plan.md",
    "docs/91_p10_global_regression_dify_adapter_contract.md",
    "docs/92_p10_operator_review_response_templates.md",
    "docs/93_p10_paper_only_operator_runbook.md",
    "docs/94_p10_failure_triage_guide.md",
    "docs/95_p10_dify_workflow_node_contract.md",
    "docs/96_p10_acceptance_smoke.md",
]


def _request() -> Dict[str, Any]:
    return {
        "request_id": "p10-d7-acceptance",
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
        for doc in P10_DOCS
    }
    return {
        "docs": docs,
        "all_docs_present": all(docs.values()),
        "doc_count": len(docs),
    }


def run_smoke() -> Dict[str, Any]:
    p9_summary = run_p9_global_regression_summary()
    dify_response = handle_dify_global_regression_request(_request())
    operator_response = render_operator_review_response(dify_response)
    docs_readiness = _docs_readiness()

    dify_data = dify_response.get("data") or {}
    safe_boundary = dify_data.get("safe_boundary") or {}

    acceptance_summary = {
        "phase": "P10",
        "phase_name": "Dify-safe paper operations packaging and operator review readiness",
        "accepted_days": ACCEPTED_DAYS,
        "p9_global_regression_completed": p9_summary.get("status") == "completed",
        "ready_for_phase10_planning": (
            p9_summary.get("global_summary") or {}
        ).get("ready_for_phase10_planning") is True,
        "dify_global_regression_ok": dify_response.get("ok") is True,
        "operator_response_type": operator_response.get("response_type"),
        "operator_response_passed": operator_response.get("response_type") == "global_regression_passed",
        "operator_review_required": dify_data.get("operator_review_required") is True,
        "ready_for_operator_review": dify_data.get("ready_for_operator_review") is True,
        "p10_docs_ready": docs_readiness["all_docs_present"] is True,
        "safe_boundary_ok": (
            safe_boundary.get("paper_only") is True
            and safe_boundary.get("real_execution") is False
            and safe_boundary.get("real_exchange_api") is False
            and safe_boundary.get("real_money_impact") is False
            and safe_boundary.get("operator_review_required") is True
            and safe_boundary.get("bypass_operator_review") is False
            and safe_boundary.get("bypass_policy_risk_safe_boundary") is False
        ),
    }
    acceptance_summary["ready_for_p10_d8_closeout"] = all(
        [
            acceptance_summary["p9_global_regression_completed"],
            acceptance_summary["ready_for_phase10_planning"],
            acceptance_summary["dify_global_regression_ok"],
            acceptance_summary["operator_response_passed"],
            acceptance_summary["operator_review_required"],
            acceptance_summary["ready_for_operator_review"],
            acceptance_summary["p10_docs_ready"],
            acceptance_summary["safe_boundary_ok"],
        ]
    )

    return {
        "status": "completed" if acceptance_summary["ready_for_p10_d8_closeout"] else "failed",
        "runner": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "acceptance_summary": acceptance_summary,
        "components": {
            "p9_global_regression_summary": {
                "status": p9_summary.get("status"),
                "ready_for_phase10_planning": (
                    p9_summary.get("global_summary") or {}
                ).get("ready_for_phase10_planning"),
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
            "p10_docs_readiness": docs_readiness,
        },
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
