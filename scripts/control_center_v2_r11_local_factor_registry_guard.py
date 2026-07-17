import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r11_local_factor_registry_foundation_app_1 import (  # noqa: E402
    V2_R11_LOCAL_FACTOR_REGISTRY_BOUNDARY,
)

APP_ROOT = Path("apps/v2_r11_local_factor_registry_foundation_app_1")
APP_FILES = (
    "__init__.py",
    "acceptance.py",
    "boundary.py",
    "contracts.py",
    "ledger.py",
    "presentation.py",
    "registry.py",
)
DOCS = tuple(
    Path(f"docs/V2_R11_LOCAL_FACTOR_REGISTRY_FOUNDATION_APP_1_D{index}.md")
    for index in range(1, 7)
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


def build_v2_r11_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        app_text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii")
            for name in APP_FILES
        )
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        app_text, docs, ascii_only = "", (), False
    boundary = V2_R11_LOCAL_FACTOR_REGISTRY_BOUNDARY
    checks = {
        "surface_exact": sorted(
            path.name for path in (root / APP_ROOT).glob("*.py")
        )
        == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6
        and all("P1-P47 frozen" in document and "no P48" in document for document in docs),
        "factor_contract_present": all(
            token in app_text
            for token in (
                "factor_id",
                "version",
                "family",
                "lifecycle",
                "calculation_spec_hash",
                "dependency_factor_refs",
            )
        ),
        "deterministic_registry_present": all(
            token in app_text
            for token in (
                "REGISTRY_READY",
                "DUPLICATE_FACTOR_NATURAL_KEY",
                "UNREGISTERED_DEPENDENCY_BLOCKED",
                "DEPENDENCY_CYCLE_BLOCKED",
                "sha256",
            )
        ),
        "no_prohibited_runtime": all(
            token not in app_text.lower() for token in PROHIBITED
        ),
        "boundary_closed": boundary.local_only
        and boundary.registered_artifact_only
        and boundary.operator_review_required
        and not boundary.factor_calculation_allowed
        and not boundary.factor_activation_allowed
        and not boundary.scoring_or_ranking_allowed
        and not boundary.network_access_allowed
        and not boundary.account_or_execution_allowed,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r11_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R11 local factor registry guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
