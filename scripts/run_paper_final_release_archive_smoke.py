import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_release_archive import build_paper_final_release_archive_manifest
from btc_finance_platform.paper_final_release_archive import summarize_paper_final_release_archive_manifest


def acceptance_summary():
    return {
        "paper_final_release_accepted": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
    }


def archive_items():
    return [
        "project_state",
        "release_package_summary",
        "acceptance_summary",
        "validation_log",
        "safety_boundary_record",
        "operator_review_record",
    ]


def validation_record():
    return {
        "all_checks_passed": True,
        "pytest_passed": True,
        "paper_only": True,
        "operator_review_required": True,
    }


if __name__ == "__main__":
    manifest = build_paper_final_release_archive_manifest(acceptance_summary(), archive_items(), validation_record())
    summary = summarize_paper_final_release_archive_manifest(manifest)
    if summary["paper_final_release_archive_ready"] is not True:
        raise SystemExit("paper final release archive should be ready")
    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(summary, indent=2, sort_keys=True))
