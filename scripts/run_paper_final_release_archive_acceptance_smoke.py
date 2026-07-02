import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_release_archive_acceptance import build_paper_final_release_archive_acceptance_gate
from btc_finance_platform.paper_final_release_archive_acceptance import summarize_paper_final_release_archive_acceptance


def archive_summary():
    return {
        "paper_final_release_archive_ready": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
    }


def checklist():
    return {
        "archive_manifest_reviewed": True,
        "archive_items_verified": True,
        "validation_record_verified": True,
        "paper_only_boundary_verified": True,
        "operator_review_record_verified": True,
        "final_archive_location_recorded": True,
    }


def operator_record():
    return {
        "operator_reviewed": True,
        "operator_accepted": True,
    }


if __name__ == "__main__":
    gate = build_paper_final_release_archive_acceptance_gate(archive_summary(), checklist(), operator_record())
    summary = summarize_paper_final_release_archive_acceptance(gate)
    if summary["paper_archive_acceptance_accepted"] is not True:
        raise SystemExit("paper archive acceptance should pass")
    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(summary, indent=2, sort_keys=True))
