from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping
from .registry import LocalEarningsAccountingQualityRegistry


@dataclass(frozen=True)
class LocalEarningsAccountingQualityReadModel:
    payload: Mapping[str, object]


def build_read_model(registry: LocalEarningsAccountingQualityRegistry) -> LocalEarningsAccountingQualityReadModel:
    return LocalEarningsAccountingQualityReadModel(MappingProxyType({"stage_count": len(registry.stages), "observation_count": len(registry.observations), "challenge_count": len(registry.challenges), "registered_artifact_only": True, "operator_review_required": True, "ai_audit_verdict": False, "fraud_conclusion": False, "factor_activation": False, "factor_or_score": False, "signal_or_recommendation": False, "order_or_execution": False}))
