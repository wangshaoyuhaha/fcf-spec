import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.regression.global_regression_report_schema import build_global_regression_report
from fcf.regression.global_safe_boundary_checker import check_global_safe_boundary
from fcf.regression.project_state_consistency_checker import check_project_state_consistency
from scripts.run_all_smokes import run_all_smokes
from scripts.run_p9_acceptance_smoke import run_smoke as run_p9_acceptance_smoke


RUNNER_NAME = "p9_global_regression_summary"
RUNNER_VERSION = "0.1.0"
CLOSEOUT_DOC = PROJECT_ROOT / "docs" / "87_p9_closeout_project_state.md"


def run_smoke() -> Dict[str, Any]:
    all_smokes = run_all_smokes()
    acceptance = run_p9_acceptance_smoke()
    report = build_global_regression_report(all_smokes)
    safe_boundary_check = check_global_safe_boundary(report)
    project_state_check = check_project_state_consistency()

    closeout_doc_exists = CLOSEOUT_DOC.exists()

    global_summary = {
        "phase": "P9",
        "phase_name": "Global paper-only regression suite and CI-safe operational readiness",
        "post_closeout_global_regression": True,
        "run_all_smokes_completed": all_smokes.get("status") == "completed",
        "p9_acceptance_completed": acceptance.get("status") == "completed",
        "global_report_completed": report.get("status") == "completed",
        "global_safe_boundary_ok": safe_boundary_check.get("ok") is True,
        "project_state_consistency_ok": project_state_check.get("ok") is True,
        "closeout_doc_exists": closeout_doc_exists,
        "ready_for_phase10_planning": (
            all_smokes.get("status") == "completed"
            and acceptance.get("status") == "completed"
            and report.get("status") == "completed"
            and safe_boundary_check.get("ok") is True
            and project_state_check.get("ok") is True
            and closeout_doc_exists
        ),
    }

    return {
        "status": "completed" if global_summary["ready_for_phase10_planning"] else "failed",
        "runner": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "global_summary": global_summary,
        "components": {
            "run_all_smokes": {
                "status": all_smokes.get("status"),
                "counts": all_smokes.get("counts"),
                "readiness": all_smokes.get("readiness"),
            },
            "p9_acceptance_smoke": {
                "status": acceptance.get("status"),
                "ready_for_p9_d8_closeout": (
                    acceptance.get("acceptance_summary") or {}
                ).get("ready_for_p9_d8_closeout"),
            },
            "global_regression_report": {
                "status": report.get("status"),
                "report_version": report.get("report_version"),
                "generated_by": report.get("generated_by"),
                "next_action": report.get("next_action"),
            },
            "global_safe_boundary_checker": {
                "status": safe_boundary_check.get("status"),
                "ok": safe_boundary_check.get("ok"),
                "violation_count": len(safe_boundary_check.get("violations") or []),
            },
            "project_state_consistency_checker": {
                "status": project_state_check.get("status"),
                "ok": project_state_check.get("ok"),
                "violation_count": len(project_state_check.get("violations") or []),
            },
            "p9_closeout_doc": {
                "path": CLOSEOUT_DOC.relative_to(PROJECT_ROOT).as_posix(),
                "exists": closeout_doc_exists,
            },
        },
        "safe_boundary": report.get("safe_boundary"),
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
