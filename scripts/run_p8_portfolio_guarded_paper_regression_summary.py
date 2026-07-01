import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_p7_guarded_paper_execution_regression_summary import (
    run_smoke as run_p7_regression,
)
from scripts.run_portfolio_guarded_paper_execution_smoke import (
    run_smoke as run_p8_portfolio_smoke,
)


RUNNER_NAME = "p8_portfolio_guarded_paper_regression_summary"


def run_smoke() -> Dict[str, Any]:
    p7_result = run_p7_regression()
    p8_result = run_p8_portfolio_smoke()

    p8_response_type_count = len(p8_result.get("response_type_counts") or {})
    p8_branch_count = len(p8_result.get("portfolio_branch_counts") or {})

    regression_summary = {
        "phase": "P8",
        "phase_name": "portfolio guarded paper execution",
        "post_closeout_regression": True,
        "p7_regression_completed": p7_result.get("status") == "completed",
        "p8_portfolio_smoke_completed": p8_result.get("status") == "completed",
        "p8_portfolio_case_count": p8_result.get("portfolio_case_count"),
        "p8_portfolio_passed_count": p8_result.get("passed_count"),
        "p8_portfolio_failed_count": p8_result.get("failed_count"),
        "p8_portfolio_branch_count": p8_branch_count,
        "p8_response_type_count": p8_response_type_count,
        "ready_for_phase9_planning": (
            p7_result.get("status") == "completed"
            and p8_result.get("status") == "completed"
            and p8_result.get("portfolio_case_count") == 4
            and p8_result.get("passed_count") == 4
            and p8_result.get("failed_count") == 0
            and p8_branch_count == 4
            and p8_response_type_count == 4
        ),
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
        "no_real_account_balance_read": True,
        "no_real_position_read": True,
        "does_not_claim_real_trade_success": True,
    }

    return {
        "status": "completed" if regression_summary["ready_for_phase9_planning"] else "failed",
        "runner": RUNNER_NAME,
        "regression_summary": regression_summary,
        "p7_regression_summary": p7_result.get("regression_summary"),
        "p8_portfolio_summary": {
            "status": p8_result.get("status"),
            "portfolio_case_count": p8_result.get("portfolio_case_count"),
            "passed_count": p8_result.get("passed_count"),
            "failed_count": p8_result.get("failed_count"),
            "portfolio_branch_counts": p8_result.get("portfolio_branch_counts"),
            "response_type_counts": p8_result.get("response_type_counts"),
        },
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
