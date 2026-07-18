from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalInstitutionalCrowdingRegistry


@dataclass(frozen=True)
class LocalInstitutionalCrowdingReadModel:
    payload: Mapping[str, object]


def build_read_model(
    registry: LocalInstitutionalCrowdingRegistry,
) -> LocalInstitutionalCrowdingReadModel:
    return LocalInstitutionalCrowdingReadModel(
        MappingProxyType(
            {
                "disclosure_count": len(registry.disclosures),
                "record_count": len(registry.records),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "current_manager_action_inference": False,
                "quarter_end_motive_inference": False,
                "manipulation_claim": False,
                "factor_activation": False,
                "factor_or_score": False,
                "signal_or_recommendation": False,
                "order_or_execution": False,
            }
        )
    )
