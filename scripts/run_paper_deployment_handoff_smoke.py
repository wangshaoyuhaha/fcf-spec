import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_handoff import build_paper_deployment_handoff_pack
from btc_finance_platform.paper_deployment_handoff import summarize_paper_deployment_handoff


def closeout():
    return {
        "p10_completed": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def summary():
    return {
        "next_stage_allowed": True,
        "paper_only": True,
        "operator_review_required": True,
        "operator_approved": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


if __name__ == "__main__":
    pack = build_paper_deployment_handoff_pack("paper-btc-model-v1", closeout(), summary())
    result = summarize_paper_deployment_handoff(pack)
    if result["paper_deployment_handoff_ready"] is not True:
        raise SystemExit("handoff should be ready")
    if result["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(result, indent=2, sort_keys=True))
