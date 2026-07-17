from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r7_local_market_session_registry_foundation_app_1 import (  # noqa: E402
    V2_R7_LOCAL_MARKET_SESSION_BOUNDARY,
)


APP_ROOT = Path("apps/v2_r7_local_market_session_registry_foundation_app_1")
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "boundary.py",
    "contracts.py",
    "presentation.py",
    "registry.py",
    "resolver.py",
)
DOCS = tuple(
    Path(f"docs/V2_R7_LOCAL_MARKET_SESSION_REGISTRY_FOUNDATION_APP_1_D{index}.md")
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


def build_v2_r7_guard_report(root: Path = ROOT) -> dict[str, object]:
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
    boundary = V2_R7_LOCAL_MARKET_SESSION_BOUNDARY
    checks = {
        "surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py"))
        == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6
        and all("P1-P47 frozen" in text and "no P48" in text for text in docs),
        "registered_contract_present": all(
            term in app_text
            for term in (
                "MarketSessionDefinition",
                "RegisteredSessionInterval",
                "calendar_version",
                "rule_version",
                "available_at_utc",
                "effective_from_utc",
                "definition_hash",
            )
        ),
        "deterministic_resolution_present": all(
            term in app_text
            for term in (
                "CALL_AUCTION",
                "CONTINUOUS_SESSION",
                "LATE_SESSION",
                "OUTSIDE_REGISTERED_SESSION",
                "REGISTERED_SESSION_RESOLVED",
            )
        ),
        "no_prohibited_runtime": all(token not in lower_app for token in PROHIBITED),
        "boundary_closed": (
            boundary.local_only
            and boundary.registered_artifact_only
            and boundary.operator_review_required
            and not boundary.network_access_allowed
            and not boundary.live_source_allowed
            and not boundary.system_clock_authority_allowed
            and not boundary.exchange_calendar_service_allowed
            and not boundary.hardcoded_venue_schedule_allowed
            and not boundary.signal_or_recommendation_allowed
            and not boundary.model_invocation_allowed
            and not boundary.order_or_execution_allowed
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r7_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R7 local market session guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
