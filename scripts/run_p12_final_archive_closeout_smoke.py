import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_archive_closeout import evaluate_p12_final_archive_closeout
from btc_finance_platform.paper_final_archive_closeout import summarize_p12_final_archive_closeout

def report(extra=None):
    data = {
        "paper_final_release_ready": True,
        "paper_final_release_accepted": True,
        "paper_final_release_archive_ready": True,
        "paper_archive_acceptance_accepted": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
    }
    if extra:
        data.update(extra)
    return data

if __name__ == "__main__":
    days = [f"P12-D{i}" for i in range(1, 16)]
    closeout = evaluate_p12_final_archive_closeout(report(), report(), report(), report(), days)
    summary = summarize_p12_final_archive_closeout(closeout)
    if summary["final_archive_completed"] is not True:
        raise SystemExit("final archive should be completed")
    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(summary, indent=2, sort_keys=True))
