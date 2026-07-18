from dataclasses import dataclass

from .contracts import BrowserGovernanceReviewQueue


@dataclass(frozen=True)
class V2R43GovernanceReviewQueueAcceptance:
    status: str
    queue_item_count: int
    blocked_count: int
    incomplete_count: int
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False


def build_governance_review_queue_acceptance(queue: BrowserGovernanceReviewQueue) -> V2R43GovernanceReviewQueueAcceptance:
    if not isinstance(queue, BrowserGovernanceReviewQueue):
        raise ValueError("governance review queue is required")
    return V2R43GovernanceReviewQueueAcceptance(
        status="PASSED_READ_ONLY_REVIEW_QUEUE", queue_item_count=len(queue.items),
        blocked_count=queue.blocked_count, incomplete_count=queue.incomplete_count,
    )
