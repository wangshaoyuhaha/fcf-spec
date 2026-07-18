from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalOperatorFactorGovernanceProjectionRegistry


@dataclass(frozen=True)
class LocalOperatorFactorGovernanceProjectionReadModel:
    payload: Mapping[str, object]


def build_read_model(
    registry: LocalOperatorFactorGovernanceProjectionRegistry,
) -> LocalOperatorFactorGovernanceProjectionReadModel:
    rows = tuple(
        MappingProxyType(
            {
                "candidate_id": item.candidate_id,
                "confidence": item.confidence,
                "evaluated_at_utc": item.evaluated_at_utc,
                "factor_id": item.factor_id,
                "field_origins": MappingProxyType(
                    {field.field_id: field.origin for field in item.fields}
                ),
                "operator_review_required": True,
                "projection_hash": item.projection_hash,
                "reason_codes": item.reason_codes,
                "state": item.state,
            }
        )
        for item in registry.projections
    )
    return LocalOperatorFactorGovernanceProjectionReadModel(
        MappingProxyType(
            {
                "projection_count": len(rows),
                "projections": rows,
                "registered_artifact_only": True,
                "read_only": True,
                "observed_inferred_explicit": True,
                "operator_review_required": True,
                "automatic_approval": False,
                "automatic_promotion": False,
                "factor_activation": False,
                "order_or_execution": False,
            }
        )
    )
