from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .ledger import FactorRegistryLedger


@dataclass(frozen=True)
class FactorRegistryReadModel:
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


def build_read_model(ledger: FactorRegistryLedger) -> FactorRegistryReadModel:
    ready = sum(item.state == "REGISTRY_READY" for item in ledger.evidence)
    return FactorRegistryReadModel(
        {
            "evidence_count": len(ledger.evidence),
            "ready_count": ready,
            "blocked_count": len(ledger.evidence) - ready,
            "latest_evidence_hash": ledger.evidence[-1].evidence_hash if ledger.evidence else None,
            "factor_calculation_activated": False,
            "factor_scoring_or_ranking": False,
            "network_access": False,
            "order_or_execution": False,
            "operator_review_required": True,
            "read_only": True,
        }
    )
