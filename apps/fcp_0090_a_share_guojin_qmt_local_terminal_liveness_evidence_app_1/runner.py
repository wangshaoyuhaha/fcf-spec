from __future__ import annotations

from datetime import datetime, timezone

from .contracts import build_evidence, build_snapshot, render_evidence_json
from .observer import iter_local_process_image_names


def main() -> int:
    try:
        snapshot = build_snapshot(
            iter_local_process_image_names(),
            datetime.now(timezone.utc),
        )
        evidence = build_evidence(snapshot)
    except (OSError, TypeError, ValueError):
        return 2
    print(render_evidence_json(evidence))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
