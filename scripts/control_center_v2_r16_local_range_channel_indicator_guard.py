import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r16_local_range_channel_indicator_foundation_app_1 import V2_R16_CHANNEL_INDICATOR_BOUNDARY  # noqa: E402

APP_ROOT = Path("apps/v2_r16_local_range_channel_indicator_foundation_app_1")
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "boundary.py",
    "contracts.py",
    "indicator.py",
    "ledger.py",
    "presentation.py",
)
DOCS = tuple(
    Path(f"docs/V2_R16_LOCAL_RANGE_CHANNEL_INDICATOR_FOUNDATION_APP_1_D{i}.md")
    for i in range(1, 7)
)
PROHIBITED = (
    "import requests",
    "import socket",
    "from urllib",
    "import subprocess",
    "websocket",
    "datetime.now",
    "place_order",
)


def build_v2_r16_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        app_text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii")
            for name in APP_FILES
        )
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        app_text, docs, ascii_only = "", (), False
    boundary = V2_R16_CHANNEL_INDICATOR_BOUNDARY
    checks = {
        "surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py"))
        == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6
        and all(
            "P1-P47 frozen" in document and "no P48" in document
            for document in docs
        ),
        "registered_dependency_present": all(
            token in app_text
            for token in (
                "RegisteredOHLCSeries",
                "FactorRegistryEvidence",
                "factor_definition_ref",
            )
        ),
        "deterministic_channel_present": all(
            token in app_text
            for token in (
                "DONCHIAN_CHANNEL",
                "ROUND_HALF_EVEN",
                "INSUFFICIENT_WINDOW_BLOCKED",
                "CHANNEL_READY",
                "close_position_percent",
            )
        ),
        "no_prohibited_runtime": all(
            token not in app_text.lower() for token in PROHIBITED
        ),
        "boundary_closed": boundary.local_only
        and boundary.registered_artifact_only
        and boundary.operator_review_required
        and not boundary.live_source_allowed
        and not boundary.prediction_allowed
        and not boundary.breakout_signal_allowed
        and not boundary.score_rank_or_signal_allowed
        and not boundary.network_access_allowed
        and not boundary.account_or_execution_allowed,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r16_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R16 local range channel indicator guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
