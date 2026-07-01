import json
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_p7_guarded_paper_execution_regression_summary import (
    run_smoke as run_p7_regression,
)
from scripts.run_p8_portfolio_guarded_paper_regression_summary import (
    run_smoke as run_p8_regression,
)


RUNNER_NAME = "run_all_smokes"
RUNNER_VERSION = "0.1.0"


def _safe_boundary() -> Dict[str, Any]:
    return {
        "paper_only": True,
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
        "ci_secret_required": False,
        "production_deployment": False,
    }


def _suite(
    *,
    name: str,
    phase: str,
    result: Dict[str, Any],
    readiness_key: str,
) -> Dict[str, Any]:
    summary = result.get("regression_summary") or {}
    completed = result.get("status") == "completed"
    ready = summary.get(readiness_key) is True

    return {
        "name": name,
        "phase": phase,
        "status": result.get("status"),
        "completed": completed,
        "readiness_key": readiness_key,
        "ready": ready,
        "runner": result.get("runner"),
    }


def run_all_smokes() -> Dict[str, Any]:
    p7_result = run_p7_regression()
    p8_result = run_p8_regression()

    suites: List[Dict[str, Any]] = [
        _suite(
            name="p7_guarded_paper_execution_regression",
            phase="P7",
            result=p7_result,
            readiness_key="ready_for_phase8_planning",
        ),
        _suite(
            name="p8_portfolio_guarded_paper_regression",
            phase="P8",
            result=p8_result,
            readiness_key="ready_for_phase9_planning",
        ),
    ]

    total_count = len(suites)
    completed_count = sum(1 for suite in suites if suite["completed"])
    failed_count = total_count - completed_count
    ready_count = sum(1 for suite in suites if suite["ready"])

    readiness = {
        "phase": "P9",
        "global_regression_suite_ready": (
            total_count == 2
            and completed_count == 2
            and failed_count == 0
            and ready_count == 2
        ),
        "ready_for_p9_d3_report_schema": (
            total_count == 2
            and completed_count == 2
            and failed_count == 0
            and ready_count == 2
        ),
    }

    counts = {
        "total_smoke_count": total_count,
        "completed_count": completed_count,
        "failed_count": failed_count,
        "ready_count": ready_count,
    }

    return {
        "status": "completed" if readiness["global_regression_suite_ready"] else "failed",
        "runner": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "suites": suites,
        "counts": counts,
        "readiness": readiness,
        "safe_boundary": _safe_boundary(),
    }


def main() -> None:
    print(json.dumps(run_all_smokes(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
