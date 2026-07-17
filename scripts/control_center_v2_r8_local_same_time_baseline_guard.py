from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r8_local_same_time_baseline_foundation_app_1 import (  # noqa: E402
    V2_R8_LOCAL_SAME_TIME_BASELINE_BOUNDARY,
)


APP_ROOT = Path("apps/v2_r8_local_same_time_baseline_foundation_app_1")
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "baseline.py",
    "boundary.py",
    "contracts.py",
    "ledger.py",
    "presentation.py",
)
DOCS = tuple(
    Path(f"docs/V2_R8_LOCAL_SAME_TIME_BASELINE_FOUNDATION_APP_1_D{index}.md")
    for index in range(1, 7)
)
PROHIBITED = (
    "import requests",
    "import socket",
    "from urllib",
    "import subprocess",
    "import asyncio",
    "websocket",
    "datetime.now",
    "place_order",
)


def build_v2_r8_guard_report(root: Path = ROOT) -> dict[str, object]:
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
    boundary = V2_R8_LOCAL_SAME_TIME_BASELINE_BOUNDARY
    checks = {
        "surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py"))
        == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6
        and all("P1-P47 frozen" in text and "no P48" in text for text in docs),
        "session_linked_contract_present": all(
            term in app_text
            for term in (
                "SessionResolutionEvidence",
                "feature_id",
                "interval_id",
                "slot_index",
                "regime_id",
                "available_at_utc",
            )
        ),
        "deterministic_statistics_present": all(
            term in app_text
            for term in (
                "BASELINE_READY",
                "mean",
                "median",
                "minimum",
                "maximum",
                "FUTURE_AVAILABILITY_BLOCKED",
            )
        ),
        "no_prohibited_runtime": all(token not in lower_app for token in PROHIBITED),
        "boundary_closed": (
            boundary.local_only
            and boundary.registered_artifact_only
            and boundary.operator_review_required
            and not boundary.network_access_allowed
            and not boundary.live_source_allowed
            and not boundary.factor_activation_allowed
            and not boundary.score_or_rank_allowed
            and not boundary.signal_or_recommendation_allowed
            and not boundary.model_invocation_allowed
            and not boundary.order_or_execution_allowed
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r8_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R8 local same-time baseline guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
