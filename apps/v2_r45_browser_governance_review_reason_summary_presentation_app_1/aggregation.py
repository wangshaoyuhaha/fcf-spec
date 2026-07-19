from collections import defaultdict

from apps.v2_r43_browser_governance_review_queue_presentation_app_1 import (
    BrowserGovernanceReviewQueue,
)

from .contracts import BrowserGovernanceReviewReasonCount, BrowserGovernanceReviewReasonSummary


def build_governance_review_reason_summary(
    queue: BrowserGovernanceReviewQueue,
) -> BrowserGovernanceReviewReasonSummary:
    if not isinstance(queue, BrowserGovernanceReviewQueue):
        raise ValueError("validated governance review queue is required")
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for item in queue.items:
        for reason_code in item.reason_codes:
            counts[reason_code][item.attention_class] += 1
    items = tuple(
        sorted(
            (
                BrowserGovernanceReviewReasonCount(
                    reason_code=reason_code,
                    occurrence_count=sum(class_counts.values()),
                    blocked_count=class_counts["BLOCKED"],
                    incomplete_count=class_counts["INCOMPLETE"],
                    review_required_count=class_counts["REVIEW_REQUIRED"],
                )
                for reason_code, class_counts in counts.items()
            ),
            key=lambda item: (-item.occurrence_count, item.reason_code),
        )
    )
    return BrowserGovernanceReviewReasonSummary(
        status="REVIEW_REASONS_AVAILABLE" if items else "NO_REGISTERED_REVIEW_REASONS",
        items=items,
        queue_item_count=len(queue.items),
        reason_occurrence_count=sum(item.occurrence_count for item in items),
    )
