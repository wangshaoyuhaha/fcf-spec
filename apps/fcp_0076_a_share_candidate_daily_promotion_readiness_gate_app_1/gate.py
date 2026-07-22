from __future__ import annotations

from datetime import datetime

from apps.fcp_0075_a_share_external_candidate_daily_corpus_quality_quarantine_evidence_app_1 import (
    CandidateDailyCorpusQualityEvidence,
)

from .contracts import (
    AUTHORITY_DOMAIN_ORDER,
    CandidateDailyAuthorityReference,
    CandidateDailyPromotionReadinessGate,
)


QUALITY_BLOCKERS = (
    ("header_mismatch_file_count", "QUALITY_HEADER_MISMATCH"),
    ("invalid_filename_count", "QUALITY_INVALID_FILENAME"),
    ("unexpected_entry_count", "QUALITY_UNEXPECTED_ENTRY"),
    ("malformed_file_count", "QUALITY_MALFORMED_FILE"),
    ("malformed_row_count", "QUALITY_MALFORMED_ROW"),
    ("code_mismatch_row_count", "QUALITY_CODE_MISMATCH"),
    ("non_monotonic_date_count", "QUALITY_NON_MONOTONIC_DATE"),
    ("duplicate_date_count", "QUALITY_DUPLICATE_DATE"),
    ("invalid_ohlc_row_count", "QUALITY_INVALID_OHLC"),
    ("negative_numeric_row_count", "QUALITY_NEGATIVE_NUMERIC"),
    ("return_mismatch_row_count", "QUALITY_RETURN_MISMATCH"),
    ("adjustment_ratio_mismatch_row_count", "QUALITY_ADJUSTMENT_RATIO_MISMATCH"),
    ("stale_terminal_file_count", "QUALITY_STALE_TERMINAL"),
)
MISSING_AUTHORITY_BLOCKER = {
    domain: f"MISSING_{domain}" for domain in AUTHORITY_DOMAIN_ORDER
}


def _instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def evaluate_candidate_daily_promotion_readiness(
    quality_evidence: CandidateDailyCorpusQualityEvidence,
    authority_references: tuple[CandidateDailyAuthorityReference, ...],
    *,
    evaluated_at_utc: str,
    gate_id: str = "a-share-candidate-daily-promotion-readiness-v1",
) -> CandidateDailyPromotionReadinessGate:
    if type(quality_evidence) is not CandidateDailyCorpusQualityEvidence:
        raise ValueError("quality evidence must be exact typed FCP-0075 evidence")
    if _instant(quality_evidence.observed_at_utc) > _instant(evaluated_at_utc):
        raise ValueError("quality evidence cannot postdate gate evaluation")
    references = tuple(authority_references)
    if any(type(item) is not CandidateDailyAuthorityReference for item in references):
        raise ValueError("authority references must be exact typed references")
    present_domains = {item.domain for item in references}
    blockers = tuple(
        code for field_name, code in QUALITY_BLOCKERS if getattr(quality_evidence, field_name) > 0
    ) + tuple(
        MISSING_AUTHORITY_BLOCKER[domain]
        for domain in AUTHORITY_DOMAIN_ORDER
        if domain not in present_domains
    )
    ready = not blockers
    return CandidateDailyPromotionReadinessGate(
        gate_id=gate_id,
        evaluated_at_utc=evaluated_at_utc,
        quality_evidence_hash=quality_evidence.evidence_hash,
        authority_references=references,
        blocker_codes=blockers,
        status=(
            "READY_FOR_OPERATOR_REVIEW_NOT_PROMOTED"
            if ready
            else "BLOCKED_NOT_READY_FOR_OPERATOR_REVIEW"
        ),
        ready_for_operator_review=ready,
    )
