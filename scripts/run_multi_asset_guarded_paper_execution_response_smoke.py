import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.dify_paper_execution_adapter import (
    ROUTE_EXECUTE,
    route_dify_paper_execution_request,
)
from fcf.api.paper_execution_response_templates import (
    render_paper_execution_user_response,
)


FIXTURE_PATH = PROJECT_ROOT / "fixtures" / "paper_orders_multi_asset_guarded.json"

RUNNER_NAME = "multi_asset_guarded_paper_execution_response_smoke"

EXPECTED_RESPONSE_TYPE_BY_BRANCH = {
    "fill_success": "paper_fill_success",
    "sandbox_reject": "paper_reject_success",
    "policy_deny": "paper_policy_deny",
    "risk_deny": "paper_risk_deny",
}


def _load_cases() -> List[Dict[str, Any]]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _call_dify_execute(case: Dict[str, Any], output_path: Path) -> Dict[str, Any]:
    request = case["request"]

    body: Dict[str, Any] = {
        "raw_order": request["raw_order"],
        "simulation_mode": request.get("simulation_mode", "simulated_fill"),
        "fill_price": request.get("fill_price"),
        "filled_quantity": request.get("filled_quantity"),
        "reject_reason": request.get("reject_reason"),
        "output_path": str(output_path),
        "risk_context": request.get("risk_context"),
    }

    policy_context = request.get("policy_context")
    if isinstance(policy_context, dict):
        body.update(policy_context)

    return route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        body,
    )


def _summarize_case(case: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    expected = case["expected"]
    expected_response_type = EXPECTED_RESPONSE_TYPE_BY_BRANCH[case["branch"]]

    output_path = output_dir / f"{case['case_id']}.jsonl"

    adapter_response = _call_dify_execute(case=case, output_path=output_path)
    user_response = render_paper_execution_user_response(adapter_response)

    body = adapter_response.get("body") or {}
    data = body.get("data") or {}
    error = body.get("error") or {}
    fields = user_response.get("fields") or {}
    safety_notice = user_response.get("safety_notice", "")

    checks = {
        "adapter_ok_matches": body.get("ok") is expected.get("ok"),
        "http_status_matches": (
            adapter_response.get("http_status") == 200
            if expected.get("ok") is True
            else adapter_response.get("http_status") == 422
        ),
        "error_type_matches": error.get("type") == expected.get("error_type"),
        "execution_status_matches": data.get("execution_status") == expected.get("execution_status"),
        "response_type_matches": user_response.get("response_type") == expected_response_type,
        "safety_notice_present": "没有真实下单" in safety_notice,
        "does_not_claim_real_execution": (
            fields.get("real_execution") is not True
            and fields.get("real_order") is not True
            and fields.get("real_exchange_api") is not True
            and fields.get("real_money_impact") is not True
        ),
        "sandbox_event_expectation_matches": output_path.exists() is expected.get(
            "sandbox_event_expected"
        ),
    }

    if case["branch"] == "policy_deny":
        checks["policy_denied_flag_matches"] = fields.get("policy_denied") is True
        checks["not_exchange_reject_matches"] = fields.get("not_exchange_reject") is True

    if case["branch"] == "risk_deny":
        checks["risk_denied_flag_matches"] = fields.get("risk_denied") is True
        checks["not_exchange_reject_matches"] = fields.get("not_exchange_reject") is True

    if case["branch"] == "sandbox_reject":
        checks["sandbox_reject_message_safe"] = "真实拒单" in user_response.get("message", "")

    checks["passed"] = all(checks.values())

    return {
        "case_id": case["case_id"],
        "asset_class": case["asset_class"],
        "branch": case["branch"],
        "passed": checks["passed"],
        "checks": checks,
        "adapter_http_status": adapter_response.get("http_status"),
        "adapter_ok": body.get("ok"),
        "adapter_error_type": error.get("type"),
        "adapter_execution_status": data.get("execution_status"),
        "user_response_type": user_response.get("response_type"),
        "user_title": user_response.get("title"),
        "expected_response_type": expected_response_type,
        "sandbox_event_written": output_path.exists(),
        "sandbox_event_expected": expected.get("sandbox_event_expected"),
    }


def run_smoke() -> Dict[str, Any]:
    cases = _load_cases()

    with tempfile.TemporaryDirectory(prefix="fcf_p7_d4_guarded_response_") as tmp_dir:
        output_dir = Path(tmp_dir)
        case_results = [
            _summarize_case(case=case, output_dir=output_dir)
            for case in cases
        ]

    asset_class_counts = Counter(case["asset_class"] for case in case_results)
    branch_counts = Counter(case["branch"] for case in case_results)
    response_type_counts = Counter(case["user_response_type"] for case in case_results)

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
        "response_type_counts": dict(sorted(response_type_counts.items())),
        "cases": case_results,
        "safe_boundary": {
            "execution_mode": "paper",
            "real_order": False,
            "real_execution": False,
            "real_exchange_api": False,
            "real_money_impact": False,
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_exchange_api_key_storage": True,
            "no_wallet_private_key_access": True,
            "only_calls_dify_paper_execution_adapter": True,
            "only_renders_paper_user_responses": True,
            "does_not_claim_real_trade_success": True,
            "does_not_claim_sandbox_reject_as_exchange_reject": True,
            "does_not_claim_policy_deny_as_exchange_reject": True,
            "does_not_claim_risk_deny_as_exchange_reject": True,
        },
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
