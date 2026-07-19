from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserGovernanceReviewEvidenceTraceItem:
    artifact_id: str
    projection_id: str
    observed_field_count: int
    inferred_field_count: int
    source_snapshot_hashes: tuple[str, ...]
    registered_artifact_only: bool = True
    registered_evidence_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if not self.artifact_id.strip() or not self.projection_id.strip():
            raise ValueError("evidence trace identity is required")
        if self.observed_field_count < 0 or self.inferred_field_count < 0:
            raise ValueError("evidence trace counts cannot be negative")
        hashes = tuple(self.source_snapshot_hashes)
        if not hashes or hashes != tuple(sorted(set(hashes))):
            raise ValueError("evidence trace hashes must be unique and sorted")
        if any(len(value) != 64 for value in hashes):
            raise ValueError("evidence trace hashes must be SHA-256 values")
        if not all(
            (
                self.registered_artifact_only,
                self.registered_evidence_only,
                self.read_only,
                self.operator_review_required,
            )
        ):
            raise ValueError("evidence trace safety boundary is required")
        object.__setattr__(self, "source_snapshot_hashes", hashes)

    @property
    def field_count(self) -> int:
        return self.observed_field_count + self.inferred_field_count

    @property
    def source_snapshot_count(self) -> int:
        return len(self.source_snapshot_hashes)


@dataclass(frozen=True)
class BrowserGovernanceReviewEvidenceTrace:
    status: str
    items: tuple[BrowserGovernanceReviewEvidenceTraceItem, ...]
    registered_artifact_only: bool = True
    registered_evidence_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    action_created: bool = False

    def __post_init__(self) -> None:
        items = tuple(self.items)
        expected = "REGISTERED_EVIDENCE_TRACE_AVAILABLE" if items else "NO_REGISTERED_EVIDENCE_TRACE"
        if self.status != expected:
            raise ValueError("evidence trace status does not match its items")
        if not all(isinstance(item, BrowserGovernanceReviewEvidenceTraceItem) for item in items):
            raise ValueError("validated evidence trace items are required")
        if not all((self.registered_artifact_only, self.registered_evidence_only, self.read_only, self.operator_review_required)):
            raise ValueError("evidence trace safety boundary is required")
        if self.action_created:
            raise ValueError("evidence trace cannot create actions")
        object.__setattr__(self, "items", items)
