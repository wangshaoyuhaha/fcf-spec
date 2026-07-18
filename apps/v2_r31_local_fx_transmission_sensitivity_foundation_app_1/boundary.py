from dataclasses import dataclass
@dataclass(frozen=True)
class V2R31LocalFXTransmissionSensitivityBoundary:
    paper_only: bool=True; local_only: bool=True; loopback_only: bool=True; sidecar_only: bool=True; registered_artifact_only: bool=True; read_only_presentation: bool=True; operator_review_required: bool=True; deterministic_engine_authority_preserved: bool=True; registered_evidence_authority_preserved: bool=True
    network_access_allowed: bool=False; live_source_allowed: bool=False; foreign_flow_inference_allowed: bool=False; causal_conclusion_allowed: bool=False; factor_activation_allowed: bool=False; factor_or_score_allowed: bool=False; signal_or_recommendation_allowed: bool=False; model_invocation_allowed: bool=False; automatic_learning_allowed: bool=False; order_or_execution_allowed: bool=False
    def __post_init__(self)->None:
        if not all((self.paper_only,self.local_only,self.loopback_only,self.sidecar_only,self.registered_artifact_only,self.read_only_presentation,self.operator_review_required,self.deterministic_engine_authority_preserved,self.registered_evidence_authority_preserved)): raise ValueError("V2-R31 required authority boundary is disabled")
        if any((self.network_access_allowed,self.live_source_allowed,self.foreign_flow_inference_allowed,self.causal_conclusion_allowed,self.factor_activation_allowed,self.factor_or_score_allowed,self.signal_or_recommendation_allowed,self.model_invocation_allowed,self.automatic_learning_allowed,self.order_or_execution_allowed)): raise ValueError("V2-R31 prohibited capability is enabled")
V2_R31_LOCAL_FX_TRANSMISSION_SENSITIVITY_BOUNDARY=V2R31LocalFXTransmissionSensitivityBoundary()
