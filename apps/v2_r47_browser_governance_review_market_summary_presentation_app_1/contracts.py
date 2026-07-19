from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserGovernanceReviewMarketCount:
    market: str
    queue_item_count: int
    blocked_count: int
    incomplete_count: int
    review_required_count: int
    covered_item_count: int
    missing_evidence_count: int

    def __post_init__(self) -> None:
        if not self.market.strip():
            raise ValueError("review market is required")
        counts = (self.queue_item_count, self.blocked_count, self.incomplete_count, self.review_required_count, self.covered_item_count, self.missing_evidence_count)
        if any(value < 0 for value in counts):
            raise ValueError("review market counts cannot be negative")
        if self.queue_item_count != sum(counts[1:4]):
            raise ValueError("review attention counts must match market queue count")
        if self.queue_item_count != self.covered_item_count + self.missing_evidence_count:
            raise ValueError("review coverage counts must match market queue count")


@dataclass(frozen=True)
class BrowserGovernanceReviewMarketSummary:
    status: str
    items: tuple[BrowserGovernanceReviewMarketCount, ...]
    queue_item_count: int
    covered_item_count: int
    missing_evidence_count: int
    registered_artifact_only: bool = True
    registered_evidence_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False

    def __post_init__(self) -> None:
        items = tuple(self.items)
        expected = "REGISTERED_REVIEW_MARKETS_AVAILABLE" if items else "NO_REGISTERED_REVIEW_MARKETS"
        if self.status != expected or not all(isinstance(item, BrowserGovernanceReviewMarketCount) for item in items):
            raise ValueError("review market summary is invalid")
        if self.queue_item_count != sum(item.queue_item_count for item in items):
            raise ValueError("review market queue total does not match")
        if self.covered_item_count != sum(item.covered_item_count for item in items):
            raise ValueError("review market coverage total does not match")
        if self.missing_evidence_count != sum(item.missing_evidence_count for item in items):
            raise ValueError("review market missing total does not match")
        required = (self.registered_artifact_only, self.registered_evidence_only, self.read_only, self.operator_review_required)
        if not all(required) or self.action_created:
            raise ValueError("review market summary boundary is required")
        object.__setattr__(self, "items", items)

    @property
    def market_count(self) -> int:
        return len(self.items)
