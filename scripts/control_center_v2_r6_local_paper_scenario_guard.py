from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r6_local_paper_scenario_research_foundation_app_1 import (  # noqa: E402
    V2_R6_LOCAL_PAPER_SCENARIO_BOUNDARY,
)


APP_ROOT = Path("apps/v2_r6_local_paper_scenario_research_foundation_app_1")
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "boundary.py",
    "contracts.py",
    "evaluator.py",
    "ledger.py",
    "presentation.py",
)
DOCS = tuple(
    Path(f"docs/V2_R6_LOCAL_PAPER_SCENARIO_RESEARCH_FOUNDATION_APP_1_D{index}.md")
    for index in range(1, 7)
)
PROHIBITED = (
    "import requests",
    "import socket",
    "from urllib",
    "import subprocess",
    "import asyncio",
    "websocket",
    "place_order",
)


def build_v2_r6_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        app_text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii")
            for name in APP_FILES
        )
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        app_text = ""
        docs = ()
        ascii_only = False
    lower_app = app_text.lower()
    boundary = V2_R6_LOCAL_PAPER_SCENARIO_BOUNDARY
    checks = {
        "surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py"))
        == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6
        and all("P1-P47 frozen" in text and "no P48" in text for text in docs),
        "deterministic_metrics_present": all(
            term in app_text
            for term in (
                "raw_path_return",
                "aligned_research_return",
                "cost_adjusted_return",
                "maximum_favorable_movement",
                "maximum_adverse_movement",
                "REGISTERED_PATH_RETURN",
            )
        ),
        "leakage_and_blocking_present": all(
            term in lower_app for term in ("future evidence", "contiguous", "blocked")
        ),
        "no_prohibited_runtime": all(token not in lower_app for token in PROHIBITED),
        "boundary_closed": (
            boundary.local_only
            and boundary.registered_artifact_only
            and boundary.operator_review_required
            and not boundary.network_access_allowed
            and not boundary.virtual_account_allowed
            and not boundary.paper_order_allowed
            and not boundary.portfolio_allowed
            and not boundary.position_allowed
            and not boundary.leverage_allowed
            and not boundary.margin_allowed
            and not boundary.liquidation_allowed
            and not boundary.model_invocation_allowed
            and not boundary.real_execution_allowed
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r6_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R6 local Paper scenario guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
