from __future__ import annotations

from .contracts import AccessApplicationState, CandidateSourceProfile


def build_operator_declared_candidate_profiles() -> tuple[CandidateSourceProfile, ...]:
    candidates = (
        ("candidate-akshare", "AKShare", AccessApplicationState.NOT_APPLIED),
        ("candidate-baostock", "Baostock", AccessApplicationState.NOT_APPLIED),
        ("candidate-guojin-qmt", "Guojin QMT", AccessApplicationState.PENDING),
        ("candidate-rqdata", "RQData", AccessApplicationState.PENDING),
        ("candidate-tushare", "Tushare", AccessApplicationState.PENDING),
    )
    return tuple(
        CandidateSourceProfile(
            candidate_id=candidate_id,
            display_name=display_name,
            access_application_state=state,
        )
        for candidate_id, display_name, state in candidates
    )


def build_complete_synthetic_candidate() -> CandidateSourceProfile:
    return CandidateSourceProfile(
        candidate_id="candidate-synthetic-complete",
        display_name="Synthetic Complete Candidate",
        access_application_state=AccessApplicationState.APPROVED_DECLARATION_ONLY,
        declared_market_ids=("A-SHARE",),
        declared_canonical_fields={
            "TICK": ("instrument_id", "event_at", "last", "volume"),
            "MINUTE_BAR": (
                "instrument_id",
                "event_at",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "interval",
            ),
            "ORDER_BOOK": (
                "instrument_id",
                "event_at",
                "bid_price_1",
                "bid_size_1",
                "ask_price_1",
                "ask_size_1",
            ),
        },
        evidence_by_category={
            "cost-quota": ("evidence-cost-v1",),
            "freshness-latency": ("evidence-sla-v1",),
            "lineage": ("evidence-lineage-v1",),
            "permitted-use": ("evidence-use-v1",),
            "retention": ("evidence-retention-v1",),
            "rights": ("evidence-rights-v1",),
            "schema": ("evidence-schema-v1",),
            "timestamp-revision": ("evidence-clock-v1",),
        },
        source_evidence_ids=("evidence-source-v1",),
    )
