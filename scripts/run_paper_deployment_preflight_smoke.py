import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_preflight import build_paper_deployment_preflight_gate
from btc_finance_platform.paper_deployment_preflight import summarize_paper_deployment_preflight


def handoff():
    return {
        "paper_deployment_handoff_ready": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def checklist():
    return {
        "paper_handoff_pack_reviewed": True,
        "model_card_reviewed": True,
        "readiness_gate_reviewed": True,
        "risk_policy_boundary_reviewed": True,
        "rollback_plan_reviewed": True,
    }


if __name__ == "__main__":
    preflight = build_paper_deployment_preflight_gate(handoff(), checklist(), {"paper_only": True})
    summary = summarize_paper_deployment_preflight(preflight)
    if summary["paper_preflight_passed"] is not True:
        raise SystemExit("paper preflight should pass")
    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(summary, indent=2, sort_keys=True))
