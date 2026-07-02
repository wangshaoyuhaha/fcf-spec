import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_release_acceptance import build_paper_final_release_acceptance_gate
from btc_finance_platform.paper_final_release_acceptance import summarize_paper_final_release_acceptance


def release_summary():
    return {
        "paper_final_release_ready": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
    }


def checklist():
    return {
        "release_package_reviewed": True,
        "validation_summary_reviewed": True,
        "paper_only_boundary_reviewed": True,
        "operator_review_recorded": True,
        "rollback_notes_reviewed": True,
        "next_stage_handoff_reviewed": True,
    }


def operator_record():
    return {
        "operator_reviewed": True,
        "operator_accepted": True,
    }


if __name__ == "__main__":
    gate = build_paper_final_release_acceptance_gate(release_summary(), checklist(), operator_record())
    summary = summarize_paper_final_release_acceptance(gate)
    if summary["paper_final_release_accepted"] is not True:
        raise SystemExit("paper final release acceptance should pass")
    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(summary, indent=2, sort_keys=True))
