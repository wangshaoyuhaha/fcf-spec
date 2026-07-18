from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.v2_r27_local_event_reaction_quality_foundation_app_1 import (  # noqa: E402
    V2_R27_LOCAL_EVENT_REACTION_QUALITY_BOUNDARY,
)


APP_ROOT = Path("apps/v2_r27_local_event_reaction_quality_foundation_app_1")
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
    Path(f"docs/V2_R27_LOCAL_EVENT_REACTION_QUALITY_FOUNDATION_APP_1_D{index}.md")
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
    "score_candidate",
)


def build_v2_r27_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        app_text = "\n".join(
            (root / APP_ROOT / name).read_text(encoding="ascii") for name in APP_FILES
        )
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError):
        app_text = ""
        docs = ()
        ascii_only = False
    lower_app = app_text.lower()
    boundary = V2_R27_LOCAL_EVENT_REACTION_QUALITY_BOUNDARY
    checks = {
        "surface_exact": sorted(path.name for path in (root / APP_ROOT).glob("*.py"))
        == sorted(APP_FILES),
        "app_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6
        and all("P1-P47 frozen" in text and "No P48" in text for text in docs),
        "reaction_contract_present": all(
            term in app_text
            for term in (
                "RegisteredReactionWindow",
                "RegisteredReactionObservation",
                "EventReactionQualityRecord",
                "previous_close",
                "first_tradable_price",
                "volume_ratio_bps",
                "turnover_bps",
                "spread_bps",
                "depth_imbalance_bps",
                "breadth_bps",
                "futures_basis_bps",
                "volatility_bps",
            )
        ),
        "maturity_and_divergence_present": all(
            term in app_text
            for term in (
                "IMMATURE",
                "FAVORABLE_WEAK_REACTION",
                "UNFAVORABLE_RESILIENT_REACTION",
                "REACTION_OUTCOME_NOT_MATURE_AT_AS_OF",
                "EXPECTATION_AND_REACTION_DIVERGE",
            )
        ),
        "no_prohibited_runtime": all(token not in lower_app for token in PROHIBITED),
        "boundary_closed": (
            boundary.local_only
            and boundary.registered_artifact_only
            and boundary.operator_review_required
            and not boundary.network_access_allowed
            and not boundary.live_source_allowed
            and not boundary.ai_generated_label_allowed
            and not boundary.participant_intent_inference_allowed
            and not boundary.immature_outcome_promotion_allowed
            and not boundary.factor_activation_allowed
            and not boundary.factor_or_score_allowed
            and not boundary.model_invocation_allowed
            and not boundary.order_or_execution_allowed
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r27_guard_report()
    if report["ok"] is not True:
        raise SystemExit("V2-R27 event reaction quality guard failed")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
