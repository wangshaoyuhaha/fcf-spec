from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class BrowserGovernanceAttentionSummary:
    status: str
    projection_count: int
    operator_review_required_count: int
    blocked_count: int
    incomplete_count: int
    observed_field_count: int
    inferred_field_count: int
    confidence_counts: Mapping[str, int]
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    approval_created: bool = False
    factor_activated: bool = False
    action_created: bool = False

    def __post_init__(self) -> None:
        if self.status not in {
            "NO_REGISTERED_GOVERNANCE_PROJECTIONS",
            "OPERATOR_REVIEW_REQUIRED",
        }:
            raise ValueError("attention summary status is not registered")
        counts = (
            self.projection_count,
            self.operator_review_required_count,
            self.blocked_count,
            self.incomplete_count,
            self.observed_field_count,
            self.inferred_field_count,
            *self.confidence_counts.values(),
        )
        if any(value < 0 for value in counts):
            raise ValueError("attention summary counts must be non-negative")
        if self.operator_review_required_count > self.projection_count:
            raise ValueError("review count cannot exceed projection count")
        if not all(
            (
                self.registered_artifact_only,
                self.read_only,
                self.operator_review_required,
            )
        ):
            raise ValueError("attention summary boundary is required")
        if self.approval_created or self.factor_activated or self.action_created:
            raise ValueError("attention summary cannot create actions")
        object.__setattr__(
            self,
            "confidence_counts",
            MappingProxyType(dict(sorted(self.confidence_counts.items()))),
        )
