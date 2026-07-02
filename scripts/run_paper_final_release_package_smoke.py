import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_release_package import build_paper_final_release_package
from btc_finance_platform.paper_final_release_package import summarize_paper_final_release_package


def p10():
    return {"p10_completed": True, "paper_only": True, "operator_review_required": True}


def p11():
    return {"p11_completed": True, "paper_only": True, "operator_review_required": True}


def validation():
    return {"all_checks_passed": True, "pytest_passed": True, "paper_only": True, "operator_review_required": True}


def sections():
    return [
        "project_state_summary",
        "p10_model_registry_closeout",
        "p11_paper_deployment_closeout",
        "validation_summary",
        "paper_only_safety_boundary",
        "operator_review_record",
    ]


if __name__ == "__main__":
    package = build_paper_final_release_package(p10(), p11(), validation(), sections())
    summary = summarize_paper_final_release_package(package)
    if summary["paper_final_release_ready"] is not True:
        raise SystemExit("paper final release package should be ready")
    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(summary, indent=2, sort_keys=True))
