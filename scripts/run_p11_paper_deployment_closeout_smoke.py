import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_closeout import evaluate_p11_paper_deployment_closeout
from btc_finance_platform.paper_deployment_closeout import summarize_p11_paper_deployment_closeout


def report(extra=None):
    data = {
        "paper_deployment_handoff_ready": True,
        "paper_preflight_passed": True,
        "paper_dry_run_ready": True,
        "paper_dry_run_report_accepted": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }
    if extra:
        data.update(extra)
    return data


if __name__ == "__main__":
    days = [f"P11-D{i}" for i in range(1, 16)]
    closeout = evaluate_p11_paper_deployment_closeout(report(), report(), report(), report(), days)
    summary = summarize_p11_paper_deployment_closeout(closeout)
    if summary["p11_completed"] is not True:
        raise SystemExit("P11 closeout should be completed")
    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(summary, indent=2, sort_keys=True))
