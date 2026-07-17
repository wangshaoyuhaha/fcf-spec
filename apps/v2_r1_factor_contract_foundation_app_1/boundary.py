from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class V2R1FactorContractBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_engine_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    ai_advisory_only: bool = True
    live_data_allowed: bool = False
    network_access_allowed: bool = False
    credential_access_allowed: bool = False
    model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    factor_calculation_allowed: bool = False
    official_scoring_allowed: bool = False
    automatic_activation_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required_true = (
            "paper_only",
            "local_only",
            "loopback_only",
            "sidecar_only",
            "registered_artifact_only",
            "read_only_presentation",
            "operator_review_required",
            "deterministic_engine_authority_preserved",
            "registered_evidence_authority_preserved",
            "ai_advisory_only",
        )
        prohibited = (
            "live_data_allowed",
            "network_access_allowed",
            "credential_access_allowed",
            "model_invocation_allowed",
            "prompt_execution_allowed",
            "factor_calculation_allowed",
            "official_scoring_allowed",
            "automatic_activation_allowed",
            "order_path_allowed",
            "real_execution_allowed",
        )
        if any(getattr(self, name) is not True for name in required_true):
            raise ValueError("V2-R1 required authority boundary is disabled")
        if any(getattr(self, name) is not False for name in prohibited):
            raise ValueError("V2-R1 prohibited capability is enabled")


V2_R1_FACTOR_CONTRACT_BOUNDARY = V2R1FactorContractBoundary()
