import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RUNNER_NAME = "p7_guarded_paper_execution_regression_summary"

SMOKE_SCRIPTS = [
    "scripts/run_dify_http_adapter_smoke.py",
    "scripts/run_dify_integration_smoke.py",
    "scripts/run_multi_asset_dify_smoke.py",
    "scripts/run_multi_asset_error_dify_smoke.py",
    "scripts/run_dify_paper_execution_smoke.py",
    "scripts/run_dify_paper_execution_response_smoke.py",
    "scripts/run_multi_asset_guarded_paper_execution_smoke.py",
    "scripts/run_multi_asset_guarded_paper_execution_response_smoke.py",
    "scripts/run_p7_guarded_paper_execution_acceptance_smoke.py",
]


def _run_script(script_path: str) -> Dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, script_path],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()

    parsed: Dict[str, Any] = {}
    parse_error = None

    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as error:
        parse_error = str(error)

    return {
        "script": script_path,
        "returncode": completed.returncode,
        "stdout_json_parse_ok": parse_error is None,
        "parse_error": parse_error,
        "status": parsed.get("status"),
        "runner": parsed.get("runner"),
        "case_count": parsed.get("case_count"),
        "passed_count": parsed.get("passed_count"),
        "failed_count": parsed.get("failed_count"),
        "asset_class_counts": parsed.get("asset_class_counts"),
        "branch_counts": parsed.get("branch_counts"),
        "response_type_counts": parsed.get("response_type_counts"),
        "acceptance_summary": parsed.get("acceptance_summary"),
        "safe_boundary": parsed.get("safe_boundary"),
        "stderr": stderr,
    }


def _guarded_summary(smoke_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_script = {
        result["script"]: result
        for result in smoke_results
    }

    execution = by_script["scripts/run_multi_asset_guarded_paper_execution_smoke.py"]
    response = by_script["scripts/run_multi_asset_guarded_paper_execution_response_smoke.py"]
    acceptance = by_script["scripts/run_p7_guarded_paper_execution_acceptance_smoke.py"]

    return {
        "execution_case_count": execution.get("case_count"),
        "execution_passed_count": execution.get("passed_count"),
        "execution_failed_count": execution.get("failed_count"),
        "execution_asset_class_counts": execution.get("asset_class_counts"),
        "execution_branch_counts": execution.get("branch_counts"),
        "response_case_count": response.get("case_count"),
        "response_passed_count": response.get("passed_count"),
        "response_failed_count": response.get("failed_count"),
        "response_type_counts": response.get("response_type_counts"),
        "acceptance_summary": acceptance.get("acceptance_summary"),
    }


def run_smoke() -> Dict[str, Any]:
    smoke_results = [
        _run_script(script_path)
        for script_path in SMOKE_SCRIPTS
    ]

    completed_count = sum(
        1
        for result in smoke_results
        if result["returncode"] == 0
        and result["stdout_json_parse_ok"] is True
        and result["status"] == "completed"
    )
    failed_count = len(smoke_results) - completed_count

    guarded_summary = _guarded_summary(smoke_results)

    regression_summary = {
        "phase": "P7",
        "phase_name": "guarded paper execution",
        "post_closeout_regression": True,
        "smoke_count": len(smoke_results),
        "completed_count": completed_count,
        "failed_count": failed_count,
        "all_smokes_completed": failed_count == 0,
        "guarded_execution_cases": guarded_summary["execution_case_count"],
        "guarded_response_cases": guarded_summary["response_case_count"],
        "asset_class_count": len(guarded_summary["execution_asset_class_counts"] or {}),
        "branch_count": len(guarded_summary["execution_branch_counts"] or {}),
        "response_type_count": len(guarded_summary["response_type_counts"] or {}),
        "ready_for_phase8_planning": failed_count == 0,
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

    return {
        "status": "completed" if failed_count == 0 else "failed",
        "runner": RUNNER_NAME,
        "smoke_count": len(smoke_results),
        "completed_count": completed_count,
        "failed_count": failed_count,
        "smoke_results": smoke_results,
        "guarded_summary": guarded_summary,
        "regression_summary": regression_summary,
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
