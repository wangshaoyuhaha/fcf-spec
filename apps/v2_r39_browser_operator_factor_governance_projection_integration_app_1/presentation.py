from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .contracts import RegisteredBrowserGovernanceProjection


@dataclass(frozen=True)
class BrowserGovernanceProjectionReadModel:
    payload: Mapping[str, object]


def build_read_model(
    artifact: RegisteredBrowserGovernanceProjection,
) -> BrowserGovernanceProjectionReadModel:
    projection = artifact.projection
    return BrowserGovernanceProjectionReadModel(
        MappingProxyType(
            {
                "candidate_id": projection.candidate_id,
                "factor_id": projection.factor_id,
                "state": projection.state,
                "confidence": projection.confidence,
                "field_origins": MappingProxyType(
                    {field.field_id: field.origin for field in projection.fields}
                ),
                "registered_artifact_only": True,
                "read_only": True,
                "operator_review_required": True,
                "factor_activation": False,
                "order_or_execution": False,
            }
        )
    )
