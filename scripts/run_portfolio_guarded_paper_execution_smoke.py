import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.portfolio_paper_execution_api import handle_portfolio_paper_execution
from fcf.api.portfolio_paper_execution_response_templates import (
    render_portfolio_paper_execution_user_response,
)


FIXTURE_PATH = PROJECT_ROOT / "fixtures" / "paper_order_portfolios_multi_asset.json"
RUNNER_NAME = "portfolio_guarded_paper_execution_smoke"

EXPECTED_RESPONSE_TYPE_BY_CASE = {
    "portfolio_all_fill": "portfolio_paper_success",
    "portfolio_mixed_results": "portfolio_paper_partial_success",
    "portfolio_policy_deny": "portfolio_policy_deny",
    "portfolio_risk_deny": "portfolio_risk_deny",
}


def _load_cases() -> List[Dict[str, Any]]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _run_case(case: Dict[str, Any], output_root: Path) -> Dict[str, Any]:
    api_response = handle_portfolio_paper_execution(
        case["request"],
        output_dir=str(output_root / case["case_id"]),
    )
    user_response = render_portfolio_paper_execution_user_response(api_response)

    expected = case["expected"]
    data = api_response.get("data") or {}
    error = api_response.get("error") or {}
    fields = user_response.get("fields") or {}

    expected_response_type = EXPECTED_RESPONSE_TYPE_BY_CASE[case["case_id"]]

    checks = {
        "api_ok_matches": api_response.get("ok") is expected["ok"],
        "portfolio_status_matches": data.get("portfolio_status") == expected["portfolio_status"],
        "order_count_matches": data.get("order_count") == expected["order_count"],
        "filled_count_matches": data.get("filled_count") == expected["filled_count"],
        "sandbox_rejected_count_matches": data.get("sandbox_rejected_count") == expected["sandbox_rejected_count"],
        "policy_denied_count_matches": data.get("policy_denied_count") == expected["policy_denied_count"],
        "risk_denied_count_matches": data.get("risk_denied_count") == expected["risk_denied_count"],
        "asset_class_counts_match": data.get("asset_class_counts") == expected["asset_class_counts"],
        "branch_counts_match": data.get("branch_counts") == expected["branch_counts"],
        "response_type_matches": user_response.get("response_type") == expected_response_type,
        "no_real_execution_claim": (
            fields.get("real_order") is False
            and fields.get("real_execution") is False
            and fields.get("real_exchange_api") is False
            and fields.get("real_money_impact") is False
        ),
        "safety_notice_present": "没有真实下单" in user_response.get("safety_notice", ""),
    }

    checks["passed"] = all(checks.values())

    return {
        "case_id": case["case_id"],
        "portfolio_id": case["portfolio_id"],
        "branch": case["branch"],
        "passed": checks["passed"],
        "checks": checks,
        "api_ok": api_response.get("ok"),
        "error_type": error.get("type"),
        "portfolio_status": data.get("portfolio_status"),
        "order_count": data.get("order_count"),
        "filled_count": data.get("filled_count"),
        "sandbox_rejected_count": data.get("sandbox_rejected_count"),
        "policy_denied_count": data.get("policy_denied_count"),
        "risk_denied_count": data.get("risk_denied_count"),
        "asset_class_counts": data.get("asset_class_counts"),
        "branch_counts": data.get("branch_counts"),
        "response_type": user_response.get("response_type"),
        "expected_response_type": expected_response_type,
    }


def run_smoke() -> Dict[str, Any]:
    cases = _load_cases()

    with tempfile.TemporaryDirectory(prefix="fcf_p8_portfolio_smoke_") as tmp_dir:
        output_root = Path(tmp_dir)
        case_results = [_run_case(case, output_root) for case in cases]

    portfolio_branch_counts = Counter(case["branch"] for case in case_results)
    response_type_counts = Counter(case["response_type"] for case in case_results)

    passed_count = sum(1 for case in case_results if case["passed"])
    failed_count = len(case_results) - passed_count

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
        "no_real_account_balance_read": True,
        "no_real_position_read": True,
        "does_not_claim_real_trade_success": True,
    }

    return {
        "status": "completed" if failed_count == 0 else "failed",
        "runner": RUNNER_NAME,
        "fixture_path": FIXTURE_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "portfolio_case_count": len(case_results),
        "passed_count": passed_count,
        "failed_count": failed_count,
        "portfolio_branch_counts": dict(sorted(portfolio_branch_counts.items())),
        "response_type_counts": dict(sorted(response_type_counts.items())),
        "cases": case_results,
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
