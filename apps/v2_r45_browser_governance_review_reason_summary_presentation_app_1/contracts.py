from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserGovernanceReviewReasonCount:
    reason_code: str
    occurrence_count: int
    blocked_count: int
    incomplete_count: int
    review_required_count: int

    def __post_init__(self) -> None:
        if not self.reason_code.strip():
            raise ValueError("review reason code is required")
        counts = (self.occurrence_count, self.blocked_count, self.incomplete_count, self.review_required_count)
        if any(value < 0 for value in counts):
            raise ValueError("review reason counts cannot be negative")
        if self.occurrence_count != sum(counts[1:]) or self.occurrence_count == 0:
            raise ValueError("review reason count totals must match")


@dataclass(frozen=True)
class BrowserGovernanceReviewReasonSummary:
    status: str
    items: tuple[BrowserGovernanceReviewReasonCount, ...]
    queue_item_count: int
    reason_occurrence_count: int
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False

    def __post_init__(self) -> None:
        items = tuple(self.items)
        expected = "REVIEW_REASONS_AVAILABLE" if items else "NO_REGISTERED_REVIEW_REASONS"
        if self.status != expected:
            raise ValueError("review reason summary status does not match items")
        if not all(isinstance(item, BrowserGovernanceReviewReasonCount) for item in items):
            raise ValueError("validated review reason counts are required")
        if self.queue_item_count < 0 or self.reason_occurrence_count != sum(item.occurrence_count for item in items):
            raise ValueError("review reason summary counts do not match")
        if not all((self.registered_artifact_only, self.read_only, self.operator_review_required)) or self.action_created:
            raise ValueError("review reason summary boundary is required")
        object.__setattr__(self, "items", items)

    @property
    def unique_reason_count(self) -> int:
        return len(self.items)
