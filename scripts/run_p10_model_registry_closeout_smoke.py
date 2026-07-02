import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p10_model_registry_closeout import build_p10_model_registry_closeout_summary
from btc_finance_platform.p10_model_registry_closeout import evaluate_p10_model_registry_closeout


def safe_report():
    return {
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_api_key_required": False,
        "wallet_private_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "bypass_operator_review": False,
        "bypass_policy_risk_safe_boundary": False,
    }


if __name__ == "__main__":
    completed_days = [f"P10-D{i}" for i in range(1, 16)]
    closeout = evaluate_p10_model_registry_closeout(safe_report(), safe_report(), completed_days)
    summary = build_p10_model_registry_closeout_summary(closeout)

    if closeout["closeout_status"] != "completed":
        raise SystemExit("P10 closeout should be completed")
    if closeout["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    if summary["next_stage_allowed"] is not True:
        raise SystemExit("P11 should be allowed only after P10 closeout")

    print(json.dumps({
        "closeout": closeout,
        "summary": summary,
    }, indent=2, sort_keys=True))
