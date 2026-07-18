from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalFactorValidationEvidenceRegistry


@dataclass(frozen=True)
class LocalFactorValidationEvidenceReadModel:
    payload: Mapping[str, object]


def build_read_model(registry: LocalFactorValidationEvidenceRegistry) -> LocalFactorValidationEvidenceReadModel:
    return LocalFactorValidationEvidenceReadModel(
        MappingProxyType(
            {
                "check_count": len(registry.checks),
                "packet_count": len(registry.packets),
                "failed_check_count": sum(item.outcome == "FAILED" for item in registry.checks),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "automatic_pass": False,
                "automatic_promotion": False,
                "factor_activation": False,
                "order_or_execution": False,
            }
        )
    )
