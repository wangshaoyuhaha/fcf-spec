from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r3_local_event_ingress_foundation_app_1 import (  # noqa: E402
    V2_R3_LOCAL_EVENT_INGRESS_BOUNDARY,
)


APP_ROOT = Path("apps/v2_r3_local_event_ingress_foundation_app_1")
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "boundary.py",
    "contracts.py",
    "ingress.py",
    "presentation.py",
    "replay.py",
)
DOCS = tuple(
    Path(f"docs/V2_R3_LOCAL_EVENT_INGRESS_FOUNDATION_APP_1_D{index}.md")
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


def build_v2_r3_guard_report(root: Path = ROOT) -> dict[str, object]:
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
    boundary = V2_R3_LOCAL_EVENT_INGRESS_BOUNDARY
    checks = {
        "surface_exact": sorted(
            path.name for path in (root / APP_ROOT).glob("*.py")
        )
        == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6
        and all("P1-P47 frozen" in text and "no P48" in text for text in docs),
        "event_semantics_present": all(
            term in app_text
            for term in (
                "source_sequence",
                "event_at_utc",
                "received_at_utc",
                "processed_at_utc",
                "payload_sha256",
                "clock_quality",
            )
        ),
        "failure_closure_present": all(
            term in lower_app
            for term in (
                "duplicate",
                "out-of-order",
                "capacity exceeded",
                "expired",
                "checkpoint",
                "mismatch",
            )
        ),
        "no_prohibited_runtime": all(token not in lower_app for token in PROHIBITED),
        "boundary_closed": (
            boundary.paper_only
            and boundary.local_only
            and boundary.loopback_only
            and boundary.registered_artifact_only
            and boundary.read_only_presentation
            and boundary.operator_review_required
            and not boundary.network_access_allowed
            and not boundary.credential_access_allowed
            and not boundary.external_source_allowed
            and not boundary.daemon_allowed
            and not boundary.external_queue_allowed
            and not boundary.market_selection_allowed
            and not boundary.factor_activation_allowed
            and not boundary.official_scoring_allowed
            and not boundary.candidate_ranking_allowed
            and not boundary.order_path_allowed
            and not boundary.real_execution_allowed
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r3_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R3 local event ingress guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
