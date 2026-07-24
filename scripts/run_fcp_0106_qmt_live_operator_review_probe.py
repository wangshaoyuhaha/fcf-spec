from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0106_a_share_qmt_internal_read_only_market_bridge_app_1 import (
    build_live_operator_review_evidence,
    read_registered_spool,
)


def _arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Observe one fresh local QMT quote for Operator review.",
    )
    parser.add_argument("--spool-root", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--poll-milliseconds", type=int, default=250)
    parser.add_argument("--minimum-events", type=int, default=5)
    values = parser.parse_args(argv)
    if not 1 <= values.timeout_seconds <= 600:
        parser.error("--timeout-seconds must be between 1 and 600")
    if not 50 <= values.poll_milliseconds <= 5000:
        parser.error("--poll-milliseconds must be between 50 and 5000")
    if not 1 <= values.minimum_events <= 100:
        parser.error("--minimum-events must be between 1 and 100")
    return values


def main(argv: list[str] | None = None) -> int:
    values = _arguments(argv)
    deadline = time.monotonic() + values.timeout_seconds
    while True:
        observed_at_ms = int(time.time() * 1000)
        try:
            snapshot = read_registered_spool(
                values.spool_root,
                now_ms=observed_at_ms,
            )
        except (OSError, ValueError) as exc:
            if str(exc) != "spool_root contains no registered events":
                print(
                    json.dumps(
                        {
                            "error": str(exc),
                            "ok": False,
                            "operator_review_required": True,
                            "status": "FAILED_CLOSED",
                        },
                        ensure_ascii=True,
                        sort_keys=True,
                    )
                )
                return 1
        else:
            if len(snapshot.accepted_events) >= values.minimum_events:
                evidence = build_live_operator_review_evidence(
                    snapshot,
                    observed_at_ms=observed_at_ms,
                    minimum_event_count=values.minimum_events,
                )
                print(
                    json.dumps(
                        dict(evidence),
                        ensure_ascii=True,
                        separators=(",", ":"),
                        sort_keys=True,
                    )
                )
                return 0
        if time.monotonic() >= deadline:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "operator_review_required": True,
                        "status": "WAITING_FOR_FRESH_QMT_EVENT",
                    },
                    ensure_ascii=True,
                    sort_keys=True,
                )
            )
            return 2
        time.sleep(values.poll_milliseconds / 1000)


if __name__ == "__main__":
    raise SystemExit(main())
