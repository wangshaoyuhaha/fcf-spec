from pathlib import Path
from typing import Any, Dict, Iterable, List


CHECKER_NAME = "project_state_consistency_checker"
CHECKER_VERSION = "0.1.0"

REQUIRED_PHASE_MARKERS = [
    "P9-D1",
    "P9-D2",
    "P9-D3",
    "P9-D4",
    "P9-D5",
]

REQUIRED_SAFETY_MARKERS = [
    "不接真实交易所 API",
    "不保存真实 API key",
    "不读取钱包私钥",
    "不真实下单",
    "不读取真实账户余额",
    "不读取真实仓位",
    "不声明真实成交",
    "不声明真实资金影响",
]

REQUIRED_NEXT_MARKERS = [
    "P9-D6",
    "CI-safe regression command document",
]


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _marker_checks(
    *,
    file_label: str,
    text: str,
    markers: Iterable[str],
    check_group: str,
) -> List[Dict[str, Any]]:
    checks = []
    for marker in markers:
        checks.append(
            {
                "name": f"{file_label}:{check_group}:{marker}",
                "file": file_label,
                "group": check_group,
                "marker": marker,
                "passed": marker in text,
            }
        )
    return checks


def _file_exists_check(file_label: str, path: Path) -> Dict[str, Any]:
    return {
        "name": f"{file_label}:exists",
        "file": file_label,
        "group": "exists",
        "marker": str(path),
        "passed": path.exists(),
    }


def _violations(checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "name": check["name"],
            "file": check["file"],
            "group": check["group"],
            "marker": check["marker"],
        }
        for check in checks
        if check["passed"] is not True
    ]


def check_project_state_consistency(
    *,
    readme_path: str = "README.md",
    project_state_path: str = "PROJECT_STATE.md",
) -> Dict[str, Any]:
    readme = Path(readme_path)
    project_state = Path(project_state_path)

    readme_text = _read_text(readme)
    project_state_text = _read_text(project_state)

    checks: List[Dict[str, Any]] = [
        _file_exists_check("README.md", readme),
        _file_exists_check("PROJECT_STATE.md", project_state),
    ]

    checks.extend(
        _marker_checks(
            file_label="README.md",
            text=readme_text,
            markers=REQUIRED_PHASE_MARKERS,
            check_group="phase_markers",
        )
    )
    checks.extend(
        _marker_checks(
            file_label="PROJECT_STATE.md",
            text=project_state_text,
            markers=REQUIRED_PHASE_MARKERS,
            check_group="phase_markers",
        )
    )
    checks.extend(
        _marker_checks(
            file_label="README.md",
            text=readme_text,
            markers=REQUIRED_SAFETY_MARKERS,
            check_group="safety_markers",
        )
    )
    checks.extend(
        _marker_checks(
            file_label="PROJECT_STATE.md",
            text=project_state_text,
            markers=REQUIRED_SAFETY_MARKERS,
            check_group="safety_markers",
        )
    )
    checks.extend(
        _marker_checks(
            file_label="README.md",
            text=readme_text,
            markers=REQUIRED_NEXT_MARKERS,
            check_group="next_markers",
        )
    )
    checks.extend(
        _marker_checks(
            file_label="PROJECT_STATE.md",
            text=project_state_text,
            markers=REQUIRED_NEXT_MARKERS,
            check_group="next_markers",
        )
    )

    violations = _violations(checks)
    ok = len(violations) == 0

    return {
        "status": "completed" if ok else "failed",
        "checker": CHECKER_NAME,
        "checker_version": CHECKER_VERSION,
        "ok": ok,
        "checks": checks,
        "violations": violations,
        "files": {
            "readme_path": str(readme),
            "project_state_path": str(project_state),
        },
        "ready_for_p9_d6_ci_safe_command_doc": ok,
    }
