from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserGovernanceReviewCoverageItem:
    artifact_id: str
    projection_id: str
    attention_class: str
    evidence_registered: bool
    observed_field_count: int
    inferred_field_count: int
    source_snapshot_count: int

    def __post_init__(self) -> None:
        for field_name in ("artifact_id", "projection_id", "attention_class"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")
        counts = (
            self.observed_field_count,
            self.inferred_field_count,
            self.source_snapshot_count,
        )
        if any(value < 0 for value in counts):
            raise ValueError("review coverage counts cannot be negative")
        if not self.evidence_registered and any(counts):
            raise ValueError("uncovered review items cannot claim evidence counts")


@dataclass(frozen=True)
class BrowserGovernanceReviewCoverageSummary:
    status: str
    items: tuple[BrowserGovernanceReviewCoverageItem, ...]
    covered_item_count: int
    missing_evidence_count: int
    registered_artifact_only: bool = True
    registered_evidence_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False

    def __post_init__(self) -> None:
        items = tuple(self.items)
        if not all(isinstance(item, BrowserGovernanceReviewCoverageItem) for item in items):
            raise ValueError("validated review coverage items are required")
        expected = (
            "NO_REGISTERED_REVIEW_ITEMS"
            if not items
            else "COMPLETE_REGISTERED_EVIDENCE_COVERAGE"
            if self.missing_evidence_count == 0
            else "INCOMPLETE_REGISTERED_EVIDENCE_COVERAGE"
        )
        if self.status != expected:
            raise ValueError("review coverage status does not match items")
        if self.covered_item_count != sum(item.evidence_registered for item in items):
            raise ValueError("covered review item count does not match items")
        if self.missing_evidence_count != len(items) - self.covered_item_count:
            raise ValueError("missing evidence count does not match items")
        required = (
            self.registered_artifact_only,
            self.registered_evidence_only,
            self.read_only,
            self.operator_review_required,
        )
        if not all(required) or self.action_created:
            raise ValueError("review coverage summary boundary is required")
        object.__setattr__(self, "items", items)

    @property
    def queue_item_count(self) -> int:
        return len(self.items)

    @property
    def observed_field_count(self) -> int:
        return sum(item.observed_field_count for item in self.items)

    @property
    def inferred_field_count(self) -> int:
        return sum(item.inferred_field_count for item in self.items)

    @property
    def source_snapshot_count(self) -> int:
        return sum(item.source_snapshot_count for item in self.items)
