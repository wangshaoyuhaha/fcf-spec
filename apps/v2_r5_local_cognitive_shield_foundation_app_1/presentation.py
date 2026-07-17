from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .ledger import CognitiveShieldLedger


@dataclass(frozen=True)
class LocalCognitiveShieldReadModel:
    payload: Mapping[str, object]


def build_read_model(ledger: CognitiveShieldLedger) -> LocalCognitiveShieldReadModel:
    counts = {
        state: sum(1 for item in ledger.evidence if item.shield_state == state)
        for state in (
            "SUPPORTED_REVIEW",
            "CONTRADICTION_REVIEW",
            "ABSTAIN_REVIEW_REQUIRED",
            "DEGRADED",
            "BLOCKED",
        )
    }
    payload = MappingProxyType(
        {
            "task_count": len(ledger.tasks),
            "evidence_count": len(ledger.evidence),
            "state_counts": MappingProxyType(counts),
            "evidence_hashes": tuple(
                item.shield_evidence_hash for item in ledger.evidence
            ),
            "registered_artifact_only": True,
            "deterministic_evidence_preserved": True,
            "operator_review_required": True,
            "model_invocation": False,
            "prompt_execution": False,
            "automatic_routing": False,
            "automatic_learning": False,
            "order_path": False,
            "real_execution": False,
        }
    )
    return LocalCognitiveShieldReadModel(payload=payload)
