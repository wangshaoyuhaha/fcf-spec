from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserGovernanceReviewQueueItem:
    attention_class: str
    artifact_id: str
    projection_id: str
    candidate_id: str
    factor_id: str
    market: str
    state: str
    confidence: str
    reason_codes: tuple[str, ...]
    projection_hash: str
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if self.attention_class not in {"BLOCKED", "INCOMPLETE", "REVIEW_REQUIRED"}:
            raise ValueError("review queue attention class is not registered")
        for field_name in ("artifact_id", "projection_id", "candidate_id", "factor_id", "market", "state", "confidence", "projection_hash"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")
        if not self.reason_codes:
            raise ValueError("review queue reason codes are required")
        if not all((self.registered_artifact_only, self.read_only, self.operator_review_required)):
            raise ValueError("review queue safety boundary is required")
        object.__setattr__(self, "reason_codes", tuple(self.reason_codes))


@dataclass(frozen=True)
class BrowserGovernanceReviewQueue:
    status: str
    items: tuple[BrowserGovernanceReviewQueueItem, ...]
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    approval_created: bool = False
    factor_activated: bool = False
    action_created: bool = False

    def __post_init__(self) -> None:
        rows = tuple(self.items)
        expected = "OPERATOR_REVIEW_REQUIRED" if rows else "NO_REGISTERED_REVIEW_ITEMS"
        if self.status != expected:
            raise ValueError("review queue status does not match its items")
        if not all(isinstance(item, BrowserGovernanceReviewQueueItem) for item in rows):
            raise ValueError("validated review queue items are required")
        if not all((self.registered_artifact_only, self.read_only, self.operator_review_required)):
            raise ValueError("review queue safety boundary is required")
        if self.approval_created or self.factor_activated or self.action_created:
            raise ValueError("review queue cannot create actions")
        object.__setattr__(self, "items", rows)

    @property
    def blocked_count(self) -> int:
        return sum(item.attention_class == "BLOCKED" for item in self.items)

    @property
    def incomplete_count(self) -> int:
        return sum(item.attention_class == "INCOMPLETE" for item in self.items)
