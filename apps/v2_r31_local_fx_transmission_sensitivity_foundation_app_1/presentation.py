from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping
from .registry import LocalFXTransmissionSensitivityRegistry
@dataclass(frozen=True)
class LocalFXTransmissionSensitivityReadModel: payload:Mapping[str,object]
def build_read_model(registry:LocalFXTransmissionSensitivityRegistry)->LocalFXTransmissionSensitivityReadModel:
    return LocalFXTransmissionSensitivityReadModel(MappingProxyType({"series_count":len(registry.series),"record_count":len(registry.records),"registered_artifact_only":True,"operator_review_required":True,"foreign_flow_inference":False,"causal_conclusion":False,"factor_activation":False,"factor_or_score":False,"signal_or_recommendation":False,"order_or_execution":False}))
