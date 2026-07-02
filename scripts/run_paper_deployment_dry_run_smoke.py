import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_dry_run import build_paper_deployment_dry_run_plan
from btc_finance_platform.paper_deployment_dry_run import summarize_paper_deployment_dry_run


def preflight():
    return {
        "paper_preflight_passed": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def steps():
    return [
        "load_paper_handoff_pack",
        "verify_paper_preflight_gate",
        "simulate_config_render",
        "simulate_operator_review_checkpoint",
        "simulate_rollback_checkpoint",
    ]


if __name__ == "__main__":
    plan = build_paper_deployment_dry_run_plan(preflight(), steps(), {"paper_only": True})
    summary = summarize_paper_deployment_dry_run(plan)
    if summary["paper_dry_run_ready"] is not True:
        raise SystemExit("paper dry run should be ready")
    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(summary, indent=2, sort_keys=True))
