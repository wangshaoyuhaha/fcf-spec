from __future__ import annotations

import json

from .contracts import (
    ContinuityRoute,
    RuntimeCompatibilityEvidence,
    build_route,
    build_runtime_evidence,
)


def build_registered_runtime_evidence() -> RuntimeCompatibilityEvidence:
    return build_runtime_evidence(
        terminal_liveness_snapshot_sha256=(
            "36ee940434fe1518407ed4fba97e9b11e5ae93deac42928b727f9743d9ff24b3"
        ),
        terminal_liveness_evidence_hash=(
            "05350a9ec5b1277aea198187f1bd70e639b51015015e094a38d32136d375d085"
        ),
        probe_terminal_snapshot_sha256=(
            "e71ed4b97081299c7d62ffb96f983d1e783c5ea35714d29ef531871cb68602c1"
        ),
        local_cache_probe_evidence_hash=(
            "cc4d16812ee8f2986f5052fb3a52c352c4fb96df804891c54cfa0288d485be0b"
        ),
    )


def build_continuity_route() -> ContinuityRoute:
    return build_route(
        build_registered_runtime_evidence(),
        decision_id="guojin-qmt-local-export-continuity-v1",
        decided_at_utc="2026-07-23T09:45:00Z",
    )


def render_continuity_route_json(route: ContinuityRoute) -> str:
    if not isinstance(route, ContinuityRoute):
        raise TypeError("route must be ContinuityRoute")
    return json.dumps(
        route.payload(),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
