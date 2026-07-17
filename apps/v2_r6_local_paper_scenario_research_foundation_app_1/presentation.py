from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .ledger import PaperScenarioLedger


@dataclass(frozen=True)
class LocalPaperScenarioReadModel:
    payload: Mapping[str, object]


def build_read_model(ledger: PaperScenarioLedger) -> LocalPaperScenarioReadModel:
    payload = MappingProxyType(
        {
            "evidence_count": len(ledger.evidence),
            "evaluated_count": sum(item.state == "EVALUATED" for item in ledger.evidence),
            "blocked_count": sum(item.state == "BLOCKED" for item in ledger.evidence),
            "evidence_hashes": tuple(item.evidence_hash for item in ledger.evidence),
            "registered_artifact_only": True,
            "operator_review_required": True,
            "market_calibrated": False,
            "virtual_account": False,
            "paper_order": False,
            "portfolio": False,
            "position": False,
            "leverage": False,
            "liquidation": False,
            "real_execution": False,
        }
    )
    return LocalPaperScenarioReadModel(payload=payload)
