import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r10_local_turnover_definition_research_foundation_app_1 import V2_R10_LOCAL_TURNOVER_BOUNDARY  # noqa: E402

APP_ROOT = Path("apps/v2_r10_local_turnover_definition_research_foundation_app_1")
APP_FILES = ("__init__.py", "acceptance.py", "boundary.py", "contracts.py", "ledger.py", "presentation.py", "turnover.py")
DOCS = tuple(Path(f"docs/V2_R10_LOCAL_TURNOVER_DEFINITION_RESEARCH_FOUNDATION_APP_1_D{i}.md") for i in range(1, 7))
PROHIBITED = ("import requests", "import socket", "from urllib", "import subprocess", "websocket", "datetime.now", "place_order")


def build_v2_r10_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        app_text = "\n".join((root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES)
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        app_text, docs, ascii_only = "", (), False
    boundary = V2_R10_LOCAL_TURNOVER_BOUNDARY
    checks = {
        "surface_exact": sorted(p.name for p in (root / APP_ROOT).glob("*.py")) == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6 and all("P1-P47 frozen" in d and "no P48" in d for d in docs),
        "point_in_time_contract_present": all(t in app_text for t in ("share_base_effective_at_utc", "share_base_available_at_utc", "denominator_type", "FREE_FLOAT_SHARES", "TOTAL_SHARES")),
        "deterministic_turnover_present": all(t in app_text for t in ("TURNOVER_READY", "ROUND_HALF_EVEN", "ZERO_SHARE_BASE_BLOCKED", "PERCENT", "FRACTION")),
        "no_prohibited_runtime": all(t not in app_text.lower() for t in PROHIBITED),
        "boundary_closed": boundary.local_only and boundary.registered_artifact_only and boundary.operator_review_required and not boundary.network_access_allowed and not boundary.live_source_allowed and not boundary.factor_activation_allowed and not boundary.score_or_rank_allowed and not boundary.order_or_execution_allowed,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r10_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R10 local turnover guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
