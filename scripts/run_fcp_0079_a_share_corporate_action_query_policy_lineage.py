from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0079_a_share_corporate_action_query_policy_lineage_contract_app_1 import (
    build_augmented_coverage_matrix,
)


def main() -> int:
    matrix = build_augmented_coverage_matrix(
        ROOT,
        evaluated_at_utc="2026-07-23T03:30:00Z",
    )
    payload = {
        "changes_gap_status": matrix.changes_gap_status,
        "evaluated_at_utc": matrix.evaluated_at_utc,
        "matrix_hash": matrix.matrix_hash,
        "promotes_candidate_data": matrix.promotes_candidate_data,
        "provider_selected": matrix.provider_selected,
        "rows": [
            {
                "coverage_state": row.coverage_state,
                "gap_id": row.requirement.gap_id,
                "gap_open": row.gap_open,
                "missing_capabilities": row.missing_capabilities,
                "observed_capabilities": row.observed_capabilities,
            }
            for row in matrix.rows
        ],
    }
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
