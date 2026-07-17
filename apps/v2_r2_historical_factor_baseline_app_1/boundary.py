from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class V2R2HistoricalBaselineBoundary:
    paper_only: bool = True
    local_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_engine_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    ai_advisory_only: bool = True
    network_access_allowed: bool = False
    credential_access_allowed: bool = False
    remote_data_allowed: bool = False
    model_invocation_allowed: bool = False
    factor_activation_allowed: bool = False
    official_scoring_allowed: bool = False
    candidate_ranking_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_engine_authority_preserved,
            self.registered_evidence_authority_preserved,
            self.ai_advisory_only,
        )
        prohibited = (
            self.network_access_allowed,
            self.credential_access_allowed,
            self.remote_data_allowed,
            self.model_invocation_allowed,
            self.factor_activation_allowed,
            self.official_scoring_allowed,
            self.candidate_ranking_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
        )
        if not all(value is True for value in required):
            raise ValueError("V2-R2 required authority boundary is disabled")
        if any(value is not False for value in prohibited):
            raise ValueError("V2-R2 prohibited capability is enabled")


V2_R2_HISTORICAL_BASELINE_BOUNDARY = V2R2HistoricalBaselineBoundary()
