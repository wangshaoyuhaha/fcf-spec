from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import V2_R4_LOCAL_ANOMALY_RADAR_BOUNDARY
from .ledger import ResearchAlertLedger


@dataclass(frozen=True)
class LocalAnomalyRadarReadModel:
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


def build_read_model(ledger: ResearchAlertLedger) -> LocalAnomalyRadarReadModel:
    boundary = V2_R4_LOCAL_ANOMALY_RADAR_BOUNDARY
    state_counts = {
        state: sum(record.state == state for record in ledger.records)
        for state in ("NORMAL", "WATCH", "CONFIRMED", "DEGRADED")
    }
    return LocalAnomalyRadarReadModel(
        {
            "phase": "V2-R4-LOCAL-ANOMALY-RADAR-FOUNDATION-APP-1",
            "record_count": len(ledger.records),
            "state_counts": MappingProxyType(state_counts),
            "evidence_hashes": tuple(record.evidence_hash for record in ledger.records),
            "read_only": boundary.read_only_presentation,
            "operator_review_required": boundary.operator_review_required,
            "registered_artifact_only": boundary.registered_artifact_only,
            "live_source_allowed": False,
            "universe_scan_allowed": False,
            "official_scoring_allowed": False,
            "candidate_ranking_allowed": False,
            "recommendation_allowed": False,
            "order_path_allowed": False,
            "real_execution_allowed": False,
        }
    )
