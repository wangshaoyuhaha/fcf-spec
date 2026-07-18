from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r28_local_a_share_earnings_lifecycle_accounting_quality_foundation_app_1 import V2_R28_LOCAL_A_SHARE_EARNINGS_ACCOUNTING_BOUNDARY  # noqa: E402

APP_ROOT = Path("apps/v2_r28_local_a_share_earnings_lifecycle_accounting_quality_foundation_app_1")
APP_FILES = ("__init__.py", "acceptance.py", "boundary.py", "contracts.py", "presentation.py", "registry.py", "resolver.py")
DOCS = tuple(Path(f"docs/V2_R28_LOCAL_A_SHARE_EARNINGS_LIFECYCLE_ACCOUNTING_QUALITY_FOUNDATION_APP_1_D{index}.md") for index in range(1, 7))
PROHIBITED = ("import requests", "import socket", "from urllib", "import subprocess", "import asyncio", "websocket", "datetime.now", "place_order", "score_candidate")


def build_v2_r28_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        app_text = "\n".join((root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES)
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        app_text, docs, ascii_only = "", (), False
    boundary = V2_R28_LOCAL_A_SHARE_EARNINGS_ACCOUNTING_BOUNDARY
    checks = {
        "surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py")) == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6 and all("P1-P47 frozen" in text and "No P48" in text for text in docs),
        "earnings_contract_present": all(term in app_text for term in ("RegisteredEarningsLifecycleStage", "RegisteredAccountingObservation", "AccountingQualityChallengeRecord", "EXPECTATION_DISCLOSURE", "IMMEDIATE_REACTION", "LOGIC_REBUILD")),
        "deterministic_challenges_present": all(term in app_text for term in ("NONRECURRING_SHARE_HIGH", "CASH_PROFIT_DIVERGENCE", "RECEIVABLES_GROWTH_PRESSURE", "MARGIN_COMPRESSION", "NO_FRAUD_CONCLUSION")),
        "no_prohibited_runtime": all(token not in app_text.lower() for token in PROHIBITED),
        "boundary_closed": boundary.local_only and boundary.registered_artifact_only and boundary.operator_review_required and not boundary.network_access_allowed and not boundary.live_source_allowed and not boundary.ai_audit_verdict_allowed and not boundary.fraud_conclusion_allowed and not boundary.factor_activation_allowed and not boundary.factor_or_score_allowed and not boundary.model_invocation_allowed and not boundary.order_or_execution_allowed,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r28_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R28 earnings accounting quality guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
