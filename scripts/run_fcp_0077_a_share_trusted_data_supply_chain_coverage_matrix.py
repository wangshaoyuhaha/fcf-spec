from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0077_a_share_trusted_data_supply_chain_coverage_evidence_matrix_app_1 import (  # noqa: E402
    build_coverage_matrix,
    coverage_requirements,
    current_repository_evidence,
)


def main() -> int:
    matrix = build_coverage_matrix(
        ROOT,
        coverage_requirements(),
        current_repository_evidence(ROOT),
        evaluated_at_utc="2026-07-23T01:00:00Z",
    )
    print(json.dumps(asdict(matrix), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
