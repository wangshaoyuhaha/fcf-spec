from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping
from .ledger import NormalizationLedger


@dataclass(frozen=True)
class NormalizationReadModel:
    payload: Mapping[str, object]
    def __post_init__(self) -> None: object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


def build_read_model(ledger: NormalizationLedger) -> NormalizationReadModel:
    return NormalizationReadModel({"evidence_count": len(ledger.evidence), "ready_count": sum(item.state == "NORMALIZATION_READY" for item in ledger.evidence), "missing_state_count": sum(item.state == "MISSING_STATE_RECORDED" for item in ledger.evidence), "direction_weight_score_rank": False, "prediction": False, "recommendation": False, "network_access": False, "order_or_execution": False, "operator_review_required": True, "read_only": True})
