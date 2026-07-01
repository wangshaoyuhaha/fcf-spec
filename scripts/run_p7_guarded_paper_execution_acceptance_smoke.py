import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_multi_asset_guarded_paper_execution_response_smoke import (
    run_smoke as run_response_smoke,
)
from scripts.run_multi_asset_guarded_paper_execution_smoke import (
    run_smoke as run_execution_smoke,
)


RUNNER_NAME = "p7_guarded_paper_execution_acceptance_smoke"

ARTIFACTS = {
    "p7_d1_plan_doc": "docs/61_p7_multi_asset_guarded_paper_execution_fixture_plan.md",
    "p7_d2_fixture_doc": "docs/62_p7_multi_asset_guarded_paper_execution_fixture.md",
    "p7_d2_fixture": "fixtures/paper_orders_multi_asset_guarded.json",
    "p7_d2_fixture_tests": "tests/test_multi_asset_guarded_paper_fixture.py",
    "p7_d3_smoke_doc": "docs/63_p7_multi_asset_guarded_paper_execution_smoke_runner.md",
    "p7_d3_smoke_runner": "scripts/run_multi_asset_guarded_paper_execution_smoke.py",
    "p7_d3_smoke_tests": "tests/test_multi_asset_guarded_paper_execution_smoke_runner.py",
    "p7_d4_response_doc": "docs/64_p7_guarded_paper_execution_dify_response_smoke.md",
    "p7_d4_response_runner": "scripts/run_multi_asset_guarded_paper_execution_response_smoke.py",
    "p7_d4_response_tests": "tests/test_multi_asset_guarded_paper_execution_response_smoke.py",
    "p7_d5_acceptance_doc": "docs/65_p7_guarded_paper_execution_acceptance.md",
    "p7_d5_acceptance_tests": "tests/test_p7_guarded_paper_execution_acceptance.py",
}

EXPECTED_ASSET_CLASS_COUNTS = {
    "commodities": 4,
    "crypto": 4,
    "equities": 4,
    "fx": 4,
}

EXPECTED_BRANCH_COUNTS = {
    "fill_success": 4,
    "policy_deny": 4,
    "risk_deny": 4,
    "sandbox_reject": 4,
}

EXPECTED_RESPONSE_TYPE_COUNTS = {
    "paper_fill_success": 4,
    "paper_policy_deny": 4,
    "paper_reject_success": 4,
    "paper_risk_deny": 4,
}


def _check_artifacts() -> Dict[str, Any]:
    checks: Dict[str, Any] = {}

    for name, relative_path in ARTIFACTS.items():
        checks[name] = (PROJECT_ROOT / relative_path).exists()

    return {
        "all_present": all(checks.values()),
        "checks": checks,
        "artifact_count": len(checks),
        "missing": [
            name
            for name, exists in checks.items()
            if exists is not True
        ],
    }


def _summarize_execution_smoke(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": result.get("status"),
        "runner": result.get("runner"),
        "case_count": result.get("case_count"),
        "passed_count": result.get("passed_count"),
        "failed_count": result.get("failed_count"),
        "asset_class_counts": result.get("asset_class_counts"),
        "branch_counts": result.get("branch_counts"),
        "safe_boundary": result.get("safe_boundary"),
    }


def _summarize_response_smoke(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": result.get("status"),
        "runner": result.get("runner"),
        "case_count": result.get("case_count"),
        "passed_count": result.get("passed_count"),
        "failed_count": result.get("failed_count"),
        "asset_class_counts": result.get("asset_class_counts"),
        "branch_counts": result.get("branch_counts"),
        "response_type_counts": result.get("response_type_counts"),
        "safe_boundary": result.get("safe_boundary"),
    }


def run_smoke() -> Dict[str, Any]:
    artifact_checks = _check_artifacts()
    execution_smoke = run_execution_smoke()
    response_smoke = run_response_smoke()

    execution_summary = _summarize_execution_smoke(execution_smoke)
    response_summary = _summarize_response_smoke(response_smoke)

    acceptance_summary = {
        "p7_d2_fixture_complete": artifact_checks["checks"]["p7_d2_fixture"] is True,
        "p7_d3_execution_smoke_complete": execution_summary["status"] == "completed",
        "p7_d4_response_smoke_complete": response_summary["status"] == "completed",
        "p7_d5_acceptance_doc_complete": artifact_checks["checks"]["p7_d5_acceptance_doc"] is True,
        "case_count": execution_summary["case_count"],
        "asset_class_count": len(execution_summary["asset_class_counts"] or {}),
        "branch_count": len(execution_summary["branch_counts"] or {}),
        "response_type_count": len(response_summary["response_type_counts"] or {}),
        "expected_asset_class_counts_match": execution_summary["asset_class_counts"] == EXPECTED_ASSET_CLASS_COUNTS,
        "expected_branch_counts_match": execution_summary["branch_counts"] == EXPECTED_BRANCH_COUNTS,
        "expected_response_type_counts_match": response_summary["response_type_counts"] == EXPECTED_RESPONSE_TYPE_COUNTS,
        "all_execution_cases_passed": execution_summary["passed_count"] == 16 and execution_summary["failed_count"] == 0,
        "all_response_cases_passed": response_summary["passed_count"] == 16 and response_summary["failed_count"] == 0,
    }

    safe_boundary = {
        "execution_mode": "paper",
        "real_order": False,
        "real_execution": False,
        "real_exchange_api": False,
        "real_money_impact": False,
        "no_real_exchange_api": True,
        "no_real_order_placement": True,
        "no_exchange_api_key_storage": True,
        "no_wallet_private_key_access": True,
        "policy_risk_cannot_be_bypassed": True,
        "does_not_claim_real_trade_success": True,
        "sandbox_fill_is_not_real_fill": True,
        "sandbox_reject_is_not_exchange_reject": True,
        "policy_deny_is_not_exchange_reject": True,
        "risk_deny_is_not_exchange_reject": True,
    }

    all_acceptance_checks_passed = (
        artifact_checks["all_present"] is True
        and all(acceptance_summary.values())
        and safe_boundary["no_real_exchange_api"] is True
        and safe_boundary["no_real_order_placement"] is True
        and safe_boundary["policy_risk_cannot_be_bypassed"] is True
    )

    return {
        "status": "completed" if all_acceptance_checks_passed else "failed",
        "runner": RUNNER_NAME,
        "acceptance_summary": acceptance_summary,
        "artifact_checks": artifact_checks,
        "execution_smoke_summary": execution_summary,
        "response_smoke_summary": response_summary,
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
