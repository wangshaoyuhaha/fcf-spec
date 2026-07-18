import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r39_browser_operator_factor_governance_projection_integration_app_1 import (
    V2_R39_BROWSER_OPERATOR_FACTOR_GOVERNANCE_PROJECTION_BOUNDARY,
)

APP_ROOT = Path(
    "apps/v2_r39_browser_operator_factor_governance_projection_integration_app_1"
)
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "adapter.py",
    "boundary.py",
    "contracts.py",
    "presentation.py",
    "registry.py",
)
BROWSER_FILES = (
    Path("apps/browser_product_console_runtime_app_1/artifact_index.py"),
    Path("apps/browser_product_console_runtime_app_1/read_model.py"),
    Path("apps/browser_product_console_runtime_app_1/research_workspace_views.py"),
)
DOCS = tuple(
    Path(
        f"docs/V2_R39_BROWSER_OPERATOR_FACTOR_GOVERNANCE_PROJECTION_INTEGRATION_APP_1_D{i}.md"
    )
    for i in range(1, 7)
)
PROHIBITED = (
    "import requests",
    "import socket",
    "from urllib",
    "import subprocess",
    "websocket",
    "place_order",
    "activate_factor",
)


def build_v2_r39_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii")
            for name in APP_FILES
        )
        browser_text = "\n".join(
            (root / path).read_text(encoding="ascii") for path in BROWSER_FILES
        )
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        text, browser_text, docs, ascii_only = "", "", (), False
    boundary = V2_R39_BROWSER_OPERATOR_FACTOR_GOVERNANCE_PROJECTION_BOUNDARY
    checks = {
        "surface_exact": sorted(
            path.name for path in (root / APP_ROOT).glob("*.py")
        )
        == sorted(APP_FILES),
        "app_browser_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6
        and all("P1-P47 frozen" in item and "No P48" in item for item in docs),
        "contract_present": all(
            item in text
            for item in (
                "factor_governance_projection",
                "projection_hash",
                "OBSERVED",
                "INFERRED",
                "operator_review_required",
                "read_only",
            )
        ),
        "browser_integration_present": (
            browser_text.count("factor_governance_projection") >= 3
            and "parse_registered_browser_governance_projection(payload)"
            in browser_text
        ),
        "no_prohibited_runtime": all(
            item not in text.lower() for item in PROHIBITED
        ),
        "boundary_closed": boundary.local_only
        and boundary.loopback_only
        and boundary.registered_artifact_only
        and not boundary.network_fetch_allowed
        and not boundary.write_controls_allowed
        and not boundary.automatic_approval_allowed
        and not boundary.factor_activation_allowed
        and not boundary.order_or_execution_allowed,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r39_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R39 browser governance projection guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
