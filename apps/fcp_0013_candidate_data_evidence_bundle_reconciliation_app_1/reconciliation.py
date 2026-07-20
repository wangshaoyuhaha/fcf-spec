from __future__ import annotations

from .contracts import CandidateEvidenceBundle, CandidateEvidenceReconciliationPacket


def reconcile_candidate_evidence_bundle(
    bundle: CandidateEvidenceBundle,
) -> CandidateEvidenceReconciliationPacket:
    if not isinstance(bundle, CandidateEvidenceBundle):
        raise TypeError("bundle must be CandidateEvidenceBundle")
    capabilities = tuple(
        sorted({value for reference in bundle.references for value in reference.observed_capabilities})
    )
    kinds = {reference.evidence_kind: reference for reference in bundle.references}
    if set(kinds) != {"HISTORICAL_DAILY_DEMO", "TRIAL_SESSION_PROBE"}:
        raise ValueError("bundle evidence kinds are incomplete")
    context_codes = []
    demo = kinds["HISTORICAL_DAILY_DEMO"]
    session = kinds["TRIAL_SESSION_PROBE"]
    if demo.observed_to < session.observed_from:
        context_codes.append("NON_OVERLAPPING_OBSERVATION_WINDOWS")
    missing = set(bundle.missing_evidence_categories)
    missing.update(
        {
            "commercial-entitlement",
            "provider-selection-evidence",
            "realtime-coverage",
            "retention-rights",
        }
    )
    return CandidateEvidenceReconciliationPacket(
        candidate_id=bundle.candidate_id,
        bundle_evidence_id=bundle.evidence_id,
        source_evidence_ids=tuple(reference.evidence_id for reference in bundle.references),
        observed_capabilities=capabilities,
        capability_overlap=("DAILY_BAR",),
        conflict_codes=(),
        context_codes=tuple(sorted(context_codes)),
        missing_evidence_categories=tuple(sorted(missing)),
        missing_fields_by_kind=bundle.missing_fields_by_kind,
    )
