from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .contracts import BrowserFactorGovernanceFieldPresentation


@dataclass(frozen=True)
class BrowserFactorGovernancePresentationReadModel:
    payload: Mapping[str, object]


def build_read_model(
    presentation: BrowserFactorGovernanceFieldPresentation,
) -> BrowserFactorGovernancePresentationReadModel:
    return BrowserFactorGovernancePresentationReadModel(
        MappingProxyType(
            {
                "candidate_id": presentation.candidate_id,
                "factor_id": presentation.factor_id,
                "state": presentation.state,
                "confidence": presentation.confidence,
                "field_count": len(presentation.fields),
                "observed_field_count": sum(
                    field.origin == "OBSERVED" for field in presentation.fields
                ),
                "inferred_field_count": sum(
                    field.origin == "INFERRED" for field in presentation.fields
                ),
                "registered_artifact_only": True,
                "read_only": True,
                "operator_review_required": True,
                "factor_activation": False,
                "order_or_execution": False,
            }
        )
    )
