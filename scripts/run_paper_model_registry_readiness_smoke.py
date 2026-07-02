import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_model_registry_readiness import build_paper_model_registry_readiness_report
from btc_finance_platform.paper_model_registry_readiness import evaluate_paper_model_registry_readiness


def approved_card():
    return {
        "model_id": "paper-btc-model-v1",
        "paper_only": True,
        "operator_review_required": True,
        "operator_approved": True,
        "real_world_actions_allowed": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
    }


def blocked_card():
    card = approved_card()
    card["model_id"] = "paper-btc-model-v2"
    card["operator_approved"] = False
    return card


if __name__ == "__main__":
    safe_registry_report = {
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }
    ready = evaluate_paper_model_registry_readiness(approved_card(), registry_report=safe_registry_report)
    blocked = evaluate_paper_model_registry_readiness(blocked_card(), registry_report=safe_registry_report)
    report = build_paper_model_registry_readiness_report([approved_card(), blocked_card()], safe_registry_report)

    if ready["gate_status"] != "ready":
        raise SystemExit("approved paper model should be ready")
    if blocked["gate_status"] != "blocked":
        raise SystemExit("unapproved paper model should be blocked")
    if report["ready_count"] != 1 or report["blocked_count"] != 1:
        raise SystemExit("readiness report counts are wrong")
    if ready["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must stay blocked")

    print(json.dumps({
        "ready": ready,
        "blocked": blocked,
        "report": report,
    }, indent=2, sort_keys=True))
