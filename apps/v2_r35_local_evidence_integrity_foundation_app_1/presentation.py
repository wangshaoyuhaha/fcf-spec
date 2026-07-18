from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalEvidenceIntegrityRegistry


@dataclass(frozen=True)
class LocalEvidenceIntegrityReadModel:
    payload: Mapping[str, object]


def build_read_model(registry: LocalEvidenceIntegrityRegistry) -> LocalEvidenceIntegrityReadModel:
    return LocalEvidenceIntegrityReadModel(
        MappingProxyType(
            {
                "record_count": len(registry.records),
                "observed_count": sum(item.origin == "OBSERVED" for item in registry.records),
                "inferred_count": sum(item.origin == "INFERRED" for item in registry.records),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "digest_bypass": False,
                "inferred_as_observed": False,
                "stale_as_fresh": False,
                "factor_or_score": False,
                "signal_or_recommendation": False,
                "order_or_execution": False,
            }
        )
    )
