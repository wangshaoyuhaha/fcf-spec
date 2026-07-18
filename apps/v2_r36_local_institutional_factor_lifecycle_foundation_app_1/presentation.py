from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalInstitutionalFactorLifecycleRegistry


@dataclass(frozen=True)
class LocalInstitutionalFactorLifecycleReadModel:
    payload: Mapping[str, object]


def build_read_model(registry: LocalInstitutionalFactorLifecycleRegistry) -> LocalInstitutionalFactorLifecycleReadModel:
    terminal = {"DEFERRED", "EXPIRED", "REJECTED", "RETIRED", "REVOKED", "SUPERSEDED"}
    return LocalInstitutionalFactorLifecycleReadModel(
        MappingProxyType(
            {
                "candidate_count": len(registry.candidates),
                "decision_count": len(registry.decisions),
                "terminal_decision_count": sum(item.to_state in terminal for item in registry.decisions),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "automatic_approval": False,
                "factor_activation": False,
                "score_or_rank": False,
                "order_or_execution": False,
            }
        )
    )
