from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (  # noqa: E402
    build_registered_local_replay_fixture,
)


def main() -> int:
    adapter, snapshot = build_registered_local_replay_fixture()
    payload = {
        "activation_gate": {
            "credentials_state": adapter.activation_gate.credentials_state,
            "entitlement_state": adapter.activation_gate.entitlement_state,
            "external_activation_state": adapter.activation_gate.external_activation_state,
            "network_state": adapter.activation_gate.network_state,
            "provider_selection_state": adapter.activation_gate.provider_selection_state,
            "retention_state": adapter.activation_gate.retention_state,
        },
        "event_count": snapshot.event_count,
        "local_replay_state": snapshot.local_replay_state,
        "mapping_coverage": dict(snapshot.mapping_coverage),
        "observation_coverage": dict(snapshot.observation_coverage),
        "operator_review_required": snapshot.operator_review_required,
        "snapshot_hash": snapshot.snapshot_hash,
    }
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
