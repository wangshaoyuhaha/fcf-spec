from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .ledger import TurnoverLedger


@dataclass(frozen=True)
class LocalTurnoverReadModel:
    payload: Mapping[str, object]


def build_read_model(ledger: TurnoverLedger) -> LocalTurnoverReadModel:
    return LocalTurnoverReadModel(MappingProxyType({
        "evidence_count": len(ledger.evidence),
        "ready_count": sum(item.state == "TURNOVER_READY" for item in ledger.evidence),
        "blocked_count": sum(item.state == "BLOCKED" for item in ledger.evidence),
        "evidence_hashes": tuple(item.evidence_hash for item in ledger.evidence),
        "registered_artifact_only": True,
        "operator_review_required": True,
        "factor_activated": False,
        "score_or_rank": False,
        "order_or_execution": False,
    }))
