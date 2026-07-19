import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r47_browser_governance_review_market_summary_presentation_app_1 import V2_R47_BROWSER_GOVERNANCE_REVIEW_MARKET_SUMMARY_BOUNDARY

APP_ROOT = Path("apps/v2_r47_browser_governance_review_market_summary_presentation_app_1")
APP_FILES = ("__init__.py", "acceptance.py", "aggregation.py", "boundary.py", "contracts.py")
BROWSER_FILES = (Path("apps/browser_product_console_runtime_app_1/research_workspace_views.py"), Path("apps/browser_product_console_runtime_app_1/web_console.py"))
DOCS = tuple(Path(f"docs/V2_R47_BROWSER_GOVERNANCE_REVIEW_MARKET_SUMMARY_PRESENTATION_APP_1_D{i}.md") for i in range(1, 7))
PROHIBITED = ("import requests", "import socket", "from urllib", "import subprocess", "websocket", "place_order", "activate_factor")


def build_v2_r47_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        text = "\n".join((root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES)
        browser_text = "\n".join((root / path).read_text(encoding="ascii") for path in BROWSER_FILES)
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        text, browser_text, docs, ascii_only = "", "", (), False
    boundary = V2_R47_BROWSER_GOVERNANCE_REVIEW_MARKET_SUMMARY_BOUNDARY
    checks = {
        "surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py")) == sorted(APP_FILES),
        "app_browser_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6 and all("P1-P47 frozen" in item and "No P48" in item for item in docs),
        "market_contract_present": all(item in text for item in ("market", "queue_item_count", "blocked_count", "missing_evidence_count")),
        "browser_integration_present": all(item in browser_text for item in ("review_market_summary", "Governance Review Market Summary", "Markets")),
        "no_prohibited_runtime": all(item not in text.lower() for item in PROHIBITED),
        "boundary_closed": boundary.local_only and boundary.loopback_only and boundary.registered_artifact_only and boundary.registered_evidence_only and boundary.read_only and boundary.operator_review_required and not boundary.network_fetch_allowed and not boundary.write_controls_allowed and not boundary.approval_allowed and not boundary.factor_activation_allowed and not boundary.order_or_execution_allowed,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r47_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R47 browser governance review market summary guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
