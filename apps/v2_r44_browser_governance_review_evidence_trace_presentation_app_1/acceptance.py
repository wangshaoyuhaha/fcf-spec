from dataclasses import dataclass

from .contracts import BrowserGovernanceReviewEvidenceTrace


@dataclass(frozen=True)
class V2R44GovernanceReviewEvidenceTraceAcceptance:
    status: str
    trace_item_count: int
    observed_field_count: int
    inferred_field_count: int
    source_snapshot_count: int
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False


def build_governance_review_evidence_trace_acceptance(
    trace: BrowserGovernanceReviewEvidenceTrace,
) -> V2R44GovernanceReviewEvidenceTraceAcceptance:
    if not isinstance(trace, BrowserGovernanceReviewEvidenceTrace):
        raise ValueError("governance review evidence trace is required")
    return V2R44GovernanceReviewEvidenceTraceAcceptance(
        status="PASSED_READ_ONLY_REGISTERED_EVIDENCE_TRACE",
        trace_item_count=len(trace.items),
        observed_field_count=sum(item.observed_field_count for item in trace.items),
        inferred_field_count=sum(item.inferred_field_count for item in trace.items),
        source_snapshot_count=sum(item.source_snapshot_count for item in trace.items),
    )
