from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalPolicyLanguageEvidenceRegistry


@dataclass(frozen=True)
class LocalPolicyLanguageEvidenceReadModel:
    payload: Mapping[str, object]


def build_read_model(registry: LocalPolicyLanguageEvidenceRegistry) -> LocalPolicyLanguageEvidenceReadModel:
    return LocalPolicyLanguageEvidenceReadModel(MappingProxyType({"document_count": len(registry.documents), "record_count": len(registry.records), "registered_artifact_only": True, "operator_review_required": True, "semantic_direction": False, "industry_benefit": False, "policy_causation": False, "automatic_taxonomy_mapping": False, "factor_activation": False, "factor_or_score": False, "signal_or_recommendation": False, "order_or_execution": False}))
