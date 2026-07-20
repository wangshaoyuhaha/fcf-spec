from __future__ import annotations

from .contracts import (
    EVIDENCE_CATEGORIES,
    CandidateSourceProfile,
    CandidateSourceReviewPacket,
    required_canonical_fields,
)


def review_candidate_source(
    profile: CandidateSourceProfile,
) -> CandidateSourceReviewPacket:
    if not isinstance(profile, CandidateSourceProfile):
        raise TypeError("profile must be CandidateSourceProfile")
    missing_evidence = tuple(
        category
        for category in EVIDENCE_CATEGORIES
        if not profile.evidence_by_category.get(category, ())
    )
    missing_fields: dict[str, tuple[str, ...]] = {}
    for kind, required in required_canonical_fields().items():
        declared = set(profile.declared_canonical_fields.get(kind, ()))
        missing = tuple(field for field in required if field not in declared)
        if missing:
            missing_fields[kind] = missing
    documentary_status = (
        "COMPLETE_PENDING_OPERATOR_REVIEW" if not missing_evidence else "INCOMPLETE"
    )
    compatibility_status = "COMPLETE" if not missing_fields else "INCOMPLETE"
    return CandidateSourceReviewPacket(
        candidate_id=profile.candidate_id,
        documentary_status=documentary_status,
        compatibility_status=compatibility_status,
        missing_evidence_categories=missing_evidence,
        missing_fields_by_kind=missing_fields,
        access_application_state=profile.access_application_state.value,
    )


def review_candidate_sources(
    profiles: tuple[CandidateSourceProfile, ...],
) -> tuple[CandidateSourceReviewPacket, ...]:
    normalized = tuple(profiles)
    if not all(isinstance(profile, CandidateSourceProfile) for profile in normalized):
        raise TypeError("profiles must contain CandidateSourceProfile values")
    if len({profile.candidate_id for profile in normalized}) != len(normalized):
        raise ValueError("candidate_id values must be unique")
    return tuple(
        review_candidate_source(profile)
        for profile in sorted(normalized, key=lambda item: item.candidate_id)
    )
