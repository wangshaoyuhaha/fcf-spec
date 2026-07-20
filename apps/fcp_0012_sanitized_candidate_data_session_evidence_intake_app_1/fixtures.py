from __future__ import annotations

import json
from pathlib import Path

from apps.fcp_0011_candidate_data_source_onboarding_evidence_review_app_1 import (
    CandidateSourceProfile,
    build_operator_declared_candidate_profiles,
)

from .contracts import RegisteredSessionEvidenceArtifact
from .loader import load_registered_session_evidence


REGISTRY_PATH = Path("FCF_REGISTERED_EVIDENCE_FCP_0012_RQDATA_TRIAL_SESSION.json")


def build_rqdata_trial_registration(root: Path) -> RegisteredSessionEvidenceArtifact:
    data = json.loads((root / REGISTRY_PATH).read_text(encoding="ascii"))
    artifact = data["artifact"]
    return RegisteredSessionEvidenceArtifact(
        artifact_id=artifact["artifact_id"],
        artifact_path=artifact["artifact_path"],
        artifact_sha256=artifact["artifact_sha256"],
        byte_length=artifact["byte_length"],
        candidate_id=artifact["candidate_id"],
        evidence_id=data["evidence_id"],
        source_kind=artifact["source_kind"],
        usage_scope=artifact["usage_scope"],
        credentials_committed=artifact["credentials_committed"],
        raw_market_values_committed=artifact["raw_market_values_committed"],
        network_used_by_sidecar=data["network_used_by_sidecar"],
        provider_selected=data["provider_selected"],
        entitlement_state=data["entitlement_state"],
        retention_state=data["retention_state"],
        operator_review_required=data["operator_review_required"],
    )


def load_rqdata_trial_session(root: Path):
    registration = build_rqdata_trial_registration(root)
    evidence = load_registered_session_evidence(
        root / registration.artifact_path,
        registration,
    )
    profile = next(
        item
        for item in build_operator_declared_candidate_profiles()
        if item.candidate_id == registration.candidate_id
    )
    return profile, registration, evidence


def rqdata_candidate_profile() -> CandidateSourceProfile:
    return next(
        item
        for item in build_operator_declared_candidate_profiles()
        if item.candidate_id == "candidate-rqdata"
    )
