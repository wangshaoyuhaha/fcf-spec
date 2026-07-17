from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r2_historical_factor_baseline_app_1 import (  # noqa: E402
    V2_R2_HISTORICAL_BASELINE_BOUNDARY,
)


APP_ROOT = Path("apps/v2_r2_historical_factor_baseline_app_1")
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "baseline.py",
    "boundary.py",
    "contracts.py",
    "presentation.py",
    "registry.py",
    "replay.py",
)
DOCS = tuple(
    Path(f"docs/V2_R2_HISTORICAL_FACTOR_BASELINE_APP_1_D{index}.md")
    for index in range(1, 7)
)
PROHIBITED = (
    "import requests",
    "import socket",
    "from urllib",
    "import subprocess",
    "websocket",
    "broker",
    "place_order",
)


def build_v2_r2_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        app_text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES
        )
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        app_text = ""
        docs = ()
        ascii_only = False
    boundary = V2_R2_HISTORICAL_BASELINE_BOUNDARY
    checks = {
        "surface_exact": sorted(
            path.name for path in (root / APP_ROOT).glob("*.py")
        ) == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6
        and all("P1-P47 frozen" in text and "no P48" in text for text in docs),
        "deterministic_formulas_present": all(
            term in app_text
            for term in ("variance", "standard_deviation", "quantile", "Decimal")
        ),
        "point_in_time_present": all(
            term in app_text for term in ("event_at_utc", "available_at_utc", "as_of_utc")
        ),
        "no_prohibited_runtime": all(token not in app_text.lower() for token in PROHIBITED),
        "boundary_closed": (
            boundary.paper_only
            and boundary.local_only
            and boundary.registered_artifact_only
            and boundary.read_only_presentation
            and boundary.operator_review_required
            and not boundary.network_access_allowed
            and not boundary.credential_access_allowed
            and not boundary.remote_data_allowed
            and not boundary.factor_activation_allowed
            and not boundary.official_scoring_allowed
            and not boundary.candidate_ranking_allowed
            and not boundary.order_path_allowed
            and not boundary.real_execution_allowed
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r2_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R2 historical baseline guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
