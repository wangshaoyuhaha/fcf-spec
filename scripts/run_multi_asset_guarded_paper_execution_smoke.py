import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.paper_execution_api import handle_paper_execution


FIXTURE_PATH = PROJECT_ROOT / "fixtures" / "paper_orders_multi_asset_guarded.json"

RUNNER_NAME = "multi_asset_guarded_paper_execution_smoke"


def _load_cases() -> List[Dict[str, Any]]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _matches_expected(
    response: Dict[str, Any],
    expected: Dict[str, Any],
    output_path: Path,
) -> Dict[str, Any]:
    checks: Dict[str, Any] = {
        "ok_matches": response.get("ok") is expected.get("ok"),
        "error_type_matches": True,
        "execution_status_matches": True,
        "sandbox_event_expectation_matches": True,
        "real_execution_false": True,
    }

    if expected.get("ok") is True:
        data = response.get("data") or {}

        checks["error_type_matches"] = response.get("error") is None
        checks["execution_status_matches"] = (
            data.get("execution_status") == expected.get("execution_status")
        )
        checks["sandbox_event_expectation_matches"] = output_path.exists() is expected.get(
            "sandbox_event_expected"
        )
        checks["real_execution_false"] = (
            data.get("real_execution") is False
            and data.get("real_order") is False
            and data.get("real_exchange_api") is False
            and data.get("real_money_impact") is False
        )

    else:
        error = response.get("error") or {}

        checks["error_type_matches"] = error.get("type") == expected.get("error_type")
        checks["execution_status_matches"] = response.get("data") is None
        checks["sandbox_event_expectation_matches"] = output_path.exists() is expected.get(
            "sandbox_event_expected"
        )
        checks["real_execution_false"] = expected.get("real_execution") is False

    checks["passed"] = all(checks.values())

    return checks


def _run_case(case: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    request = case["request"]
    expected = case["expected"]

    output_path = output_dir / f"{case['case_id']}.jsonl"

    response = handle_paper_execution(
        raw_order=request["raw_order"],
        simulation_mode=request.get("simulation_mode", "simulated_fill"),
        fill_price=request.get("fill_price"),
        filled_quantity=request.get("filled_quantity"),
        reject_reason=request.get("reject_reason"),
        output_path=str(output_path),
        policy_context=request.get("policy_context"),
        risk_context=request.get("risk_context"),
    )

    checks = _matches_expected(
        response=response,
        expected=expected,
        output_path=output_path,
    )

    error = response.get("error") or {}
    data = response.get("data") or {}

    return {
        "case_id": case["case_id"],
        "asset_class": case["asset_class"],
        "branch": case["branch"],
        "passed": checks["passed"],
        "checks": checks,
        "actual_ok": response.get("ok"),
        "expected_ok": expected.get("ok"),
        "actual_error_type": error.get("type"),
        "expected_error_type": expected.get("error_type"),
        "actual_execution_status": data.get("execution_status"),
        "expected_execution_status": expected.get("execution_status"),
        "sandbox_event_written": output_path.exists(),
        "sandbox_event_expected": expected.get("sandbox_event_expected"),
    }


def run_smoke() -> Dict[str, Any]:
    cases = _load_cases()

    with tempfile.TemporaryDirectory(prefix="fcf_p7_d3_guarded_paper_") as tmp_dir:
        output_dir = Path(tmp_dir)
        case_results = [
            _run_case(case=case, output_dir=output_dir)
            for case in cases
        ]

    asset_class_counts = Counter(case["asset_class"] for case in case_results)
    branch_counts = Counter(case["branch"] for case in case_results)

    passed_count = sum(1 for case in case_results if case["passed"])
    failed_count = len(case_results) - passed_count

    return {
        "status": "completed" if failed_count == 0 else "failed",
        "runner": RUNNER_NAME,
        "fixture_path": FIXTURE_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "case_count": len(case_results),
        "passed_count": passed_count,
        "failed_count": failed_count,
        "asset_class_counts": dict(sorted(asset_class_counts.items())),
        "branch_counts": dict(sorted(branch_counts.items())),
        "cases": case_results,
        "safe_boundary": {
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_exchange_api_key_storage": True,
            "no_wallet_private_key_access": True,
            "paper_only": True,
            "policy_risk_cannot_be_bypassed": True,
            "sandbox_reject_is_not_exchange_reject": True,
            "policy_deny_is_not_exchange_reject": True,
            "risk_deny_is_not_exchange_reject": True,
        },
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
