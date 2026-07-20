from __future__ import annotations

from apps.fcp_0011_candidate_data_source_onboarding_evidence_review_app_1 import (
    CandidateSourceProfile,
    review_candidate_source,
)

from .contracts import (
    CandidateSessionEvidence,
    CandidateSessionReviewPacket,
    RegisteredSessionEvidenceArtifact,
)


def review_candidate_session_evidence(
    profile: CandidateSourceProfile,
    registration: RegisteredSessionEvidenceArtifact,
    evidence: CandidateSessionEvidence,
) -> CandidateSessionReviewPacket:
    if not isinstance(profile, CandidateSourceProfile):
        raise TypeError("profile must be CandidateSourceProfile")
    if not isinstance(registration, RegisteredSessionEvidenceArtifact):
        raise TypeError("registration must be RegisteredSessionEvidenceArtifact")
    if not isinstance(evidence, CandidateSessionEvidence):
        raise TypeError("evidence must be CandidateSessionEvidence")
    if len({profile.candidate_id, registration.candidate_id, evidence.candidate_id}) != 1:
        raise ValueError("candidate identities must match")
    base = review_candidate_source(profile)
    observation_status = (
        "OBSERVED_READ_ONLY_PROBE"
        if evidence.probe.status == "SUCCEEDED"
        else "PROBE_NOT_CONFIRMED"
    )
    return CandidateSessionReviewPacket(
        candidate_id=evidence.candidate_id,
        evidence_id=registration.evidence_id,
        license_class=evidence.license_class,
        remaining_days=evidence.remaining_days,
        quota_limit_bytes=evidence.quota_limit_bytes,
        quota_used_bytes=evidence.quota_used_bytes,
        probe_kind=evidence.probe.kind,
        probe_status=evidence.probe.status,
        probe_row_count=evidence.probe.row_count,
        documentary_status=base.documentary_status,
        compatibility_status=base.compatibility_status,
        missing_evidence_categories=base.missing_evidence_categories,
        missing_fields_by_kind=base.missing_fields_by_kind,
        operational_observation_status=observation_status,
    )
