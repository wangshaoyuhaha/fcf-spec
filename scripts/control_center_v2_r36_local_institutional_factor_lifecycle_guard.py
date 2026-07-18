import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r36_local_institutional_factor_lifecycle_foundation_app_1 import V2_R36_LOCAL_INSTITUTIONAL_FACTOR_LIFECYCLE_BOUNDARY

APP_ROOT = Path("apps/v2_r36_local_institutional_factor_lifecycle_foundation_app_1")
APP_FILES = ("__init__.py", "acceptance.py", "boundary.py", "contracts.py", "presentation.py", "registry.py", "resolver.py")
DOCS = tuple(Path(f"docs/V2_R36_LOCAL_INSTITUTIONAL_FACTOR_LIFECYCLE_FOUNDATION_APP_1_D{i}.md") for i in range(1, 7))
PROHIBITED = ("import requests", "import socket", "from urllib", "import subprocess", "websocket", "place_order", "activate_factor")


def build_v2_r36_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        text = "\n".join((root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES)
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        text, docs, ascii_only = "", (), False
    boundary = V2_R36_LOCAL_INSTITUTIONAL_FACTOR_LIFECYCLE_BOUNDARY
    checks = {
        "surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py")) == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6 and all("P1-P47 frozen" in item and "No P48" in item for item in docs),
        "contract_present": all(item in text for item in ("InstitutionalFactorCandidate", "OperatorLifecycleDecision", "REGISTERED_PAPER_FACTOR", "REJECTED_HISTORY_PRESERVED", "NO_FACTOR_ACTIVATION")),
        "no_prohibited_runtime": all(item not in text.lower() for item in PROHIBITED),
        "boundary_closed": boundary.local_only and boundary.registered_artifact_only and not boundary.network_access_allowed and not boundary.automatic_approval_allowed and not boundary.factor_activation_allowed and not boundary.formula_override_allowed and not boundary.score_or_rank_allowed and not boundary.order_or_execution_allowed,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r36_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R36 factor lifecycle guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
