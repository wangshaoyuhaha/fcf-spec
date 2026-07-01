import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_p12_final_delivery_package_summary import run_smoke as run_p12_final_summary


RUNNER_NAME = "final_archive_acceptance_smoke"
RUNNER_VERSION = "0.1.0"

ARCHIVE_DELIVERABLES = {
    "archive_d1_final_archive_plan": "docs/121_archive_d1_final_archive_plan.md",
    "archive_d2_immutable_delivery_snapshot_checklist": "docs/122_archive_d2_immutable_delivery_snapshot_checklist.md",
    "archive_d3_final_release_note": "docs/123_archive_d3_final_release_note.md",
    "archive_d4_final_archive_manifest": "docs/124_archive_d4_final_archive_manifest.md",
    "archive_d5_final_operator_archive_handoff": "docs/125_archive_d5_final_operator_archive_handoff.md",
    "archive_d6_final_archive_acceptance_smoke_doc": "docs/126_archive_d6_final_archive_acceptance_smoke.md",
    "archive_d6_final_archive_acceptance_smoke_script": "scripts/run_final_archive_acceptance_smoke.py",
    "archive_d6_final_archive_acceptance_smoke_test": "tests/test_archive_d6_final_archive_acceptance_smoke.py",
}


def _deliverables() -> Dict[str, Any]:
    items = {
        name: {
            "path": path,
            "exists": (PROJECT_ROOT / path).exists(),
        }
        for name, path in ARCHIVE_DELIVERABLES.items()
    }
    return {
        "items": items,
        "deliverable_count": len(items),
        "present_count": sum(1 for item in items.values() if item["exists"]),
        "all_present": all(item["exists"] for item in items.values()),
    }


def _safe_boundary_ok(boundary: Dict[str, Any]) -> bool:
    return all(
        [
            boundary.get("paper_only") is True,
            boundary.get("execution_mode") == "paper",
            boundary.get("real_order") is False,
            boundary.get("real_execution") is False,
            boundary.get("real_exchange_api") is False,
            boundary.get("real_money_impact") is False,
            boundary.get("operator_review_required") is True,
            boundary.get("auto_live_trading") is False,
            boundary.get("bypass_operator_review") is False,
            boundary.get("bypass_policy_risk_safe_boundary") is False,
        ]
    )


def run_smoke() -> Dict[str, Any]:
    p12_summary = run_p12_final_summary()
    package_summary = p12_summary.get("package_summary") or {}
    deliverables = _deliverables()
    safe_boundary = p12_summary.get("safe_boundary") or {}

    acceptance_summary = {
        "phase": "Final Archive",
        "accepted_days": [
            "Archive-D1",
            "Archive-D2",
            "Archive-D3",
            "Archive-D4",
            "Archive-D5",
            "Archive-D6",
        ],
        "p12_final_delivery_package_summary_completed": p12_summary.get("status") == "completed",
        "ready_for_p12_d10_archive_bridge_plan": package_summary.get("ready_for_p12_d10_archive_bridge_plan") is True,
        "archive_docs_all_present": deliverables["all_present"] is True,
        "final_archive_plan_present": deliverables["items"]["archive_d1_final_archive_plan"]["exists"] is True,
        "immutable_delivery_snapshot_checklist_present": deliverables["items"]["archive_d2_immutable_delivery_snapshot_checklist"]["exists"] is True,
        "final_release_note_present": deliverables["items"]["archive_d3_final_release_note"]["exists"] is True,
        "final_archive_manifest_present": deliverables["items"]["archive_d4_final_archive_manifest"]["exists"] is True,
        "final_operator_archive_handoff_present": deliverables["items"]["archive_d5_final_operator_archive_handoff"]["exists"] is True,
        "final_archive_acceptance_smoke_present": deliverables["items"]["archive_d6_final_archive_acceptance_smoke_doc"]["exists"] is True,
        "safe_boundary_ok": _safe_boundary_ok(safe_boundary),
    }

    acceptance_summary["ready_for_archive_d7_closeout"] = all(
        [
            acceptance_summary["p12_final_delivery_package_summary_completed"],
            acceptance_summary["ready_for_p12_d10_archive_bridge_plan"],
            acceptance_summary["archive_docs_all_present"],
            acceptance_summary["final_archive_plan_present"],
            acceptance_summary["immutable_delivery_snapshot_checklist_present"],
            acceptance_summary["final_release_note_present"],
            acceptance_summary["final_archive_manifest_present"],
            acceptance_summary["final_operator_archive_handoff_present"],
            acceptance_summary["final_archive_acceptance_smoke_present"],
            acceptance_summary["safe_boundary_ok"],
        ]
    )

    return {
        "status": "completed" if acceptance_summary["ready_for_archive_d7_closeout"] else "failed",
        "runner": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "acceptance_summary": acceptance_summary,
        "deliverables": deliverables,
        "components": {
            "p12_final_delivery_package_summary": {
                "status": p12_summary.get("status"),
                "ready_for_p12_d10_archive_bridge_plan": package_summary.get("ready_for_p12_d10_archive_bridge_plan"),
                "safe_boundary_ok": package_summary.get("safe_boundary_ok"),
            }
        },
        "safe_boundary": safe_boundary,
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
