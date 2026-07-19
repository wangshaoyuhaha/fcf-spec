from apps.v2_r43_browser_governance_review_queue_presentation_app_1 import (
    BrowserGovernanceReviewQueue,
)
from apps.v2_r44_browser_governance_review_evidence_trace_presentation_app_1 import (
    BrowserGovernanceReviewEvidenceTrace,
)

from .contracts import (
    BrowserGovernanceReviewCoverageItem,
    BrowserGovernanceReviewCoverageSummary,
)


def build_governance_review_coverage_summary(
    queue: BrowserGovernanceReviewQueue,
    evidence_trace: BrowserGovernanceReviewEvidenceTrace,
) -> BrowserGovernanceReviewCoverageSummary:
    if not isinstance(queue, BrowserGovernanceReviewQueue):
        raise ValueError("validated governance review queue is required")
    if not isinstance(evidence_trace, BrowserGovernanceReviewEvidenceTrace):
        raise ValueError("validated governance review evidence trace is required")

    queue_keys = [(item.artifact_id, item.projection_id) for item in queue.items]
    trace_keys = [
        (item.artifact_id, item.projection_id) for item in evidence_trace.items
    ]
    if len(set(queue_keys)) != len(queue_keys):
        raise ValueError("governance review queue identities must be unique")
    if len(set(trace_keys)) != len(trace_keys):
        raise ValueError("governance review evidence identities must be unique")
    if not set(trace_keys) <= set(queue_keys):
        raise ValueError("orphan governance review evidence trace is not allowed")

    trace_by_key = {
        (item.artifact_id, item.projection_id): item
        for item in evidence_trace.items
    }
    items = tuple(
        BrowserGovernanceReviewCoverageItem(
            artifact_id=queue_item.artifact_id,
            projection_id=queue_item.projection_id,
            attention_class=queue_item.attention_class,
            evidence_registered=trace is not None,
            observed_field_count=trace.observed_field_count if trace else 0,
            inferred_field_count=trace.inferred_field_count if trace else 0,
            source_snapshot_count=trace.source_snapshot_count if trace else 0,
        )
        for queue_item in queue.items
        for trace in (trace_by_key.get((queue_item.artifact_id, queue_item.projection_id)),)
    )
    covered_item_count = sum(item.evidence_registered for item in items)
    missing_evidence_count = len(items) - covered_item_count
    return BrowserGovernanceReviewCoverageSummary(
        status=(
            "NO_REGISTERED_REVIEW_ITEMS"
            if not items
            else "COMPLETE_REGISTERED_EVIDENCE_COVERAGE"
            if missing_evidence_count == 0
            else "INCOMPLETE_REGISTERED_EVIDENCE_COVERAGE"
        ),
        items=items,
        covered_item_count=covered_item_count,
        missing_evidence_count=missing_evidence_count,
    )
