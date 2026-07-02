import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_dry_run_report import build_paper_deployment_dry_run_report
from btc_finance_platform.paper_deployment_dry_run_report import summarize_paper_deployment_dry_run_report


def plan():
    return {
        "paper_dry_run_ready": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def observations():
    return {
        "handoff_pack_loaded": True,
        "preflight_gate_verified": True,
        "config_render_simulated": True,
        "operator_checkpoint_simulated": True,
        "rollback_checkpoint_simulated": True,
    }


def review():
    return {
        "operator_reviewed": True,
        "operator_approved": True,
    }


if __name__ == "__main__":
    report = build_paper_deployment_dry_run_report(plan(), observations(), review())
    summary = summarize_paper_deployment_dry_run_report(report)
    if summary["paper_dry_run_report_accepted"] is not True:
        raise SystemExit("paper dry run report should be accepted")
    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(summary, indent=2, sort_keys=True))
