from collections.abc import Iterable

from apps.v2_r40_browser_factor_governance_field_presentation_app_1 import (
    BrowserFactorGovernanceFieldPresentation,
)

from .contracts import BrowserGovernanceAttentionSummary


def build_governance_attention_summary(
    presentations: Iterable[BrowserFactorGovernanceFieldPresentation],
) -> BrowserGovernanceAttentionSummary:
    rows = tuple(presentations)
    if any(
        not isinstance(item, BrowserFactorGovernanceFieldPresentation)
        for item in rows
    ):
        raise ValueError("validated governance presentations are required")
    confidence_counts: dict[str, int] = {}
    for item in rows:
        confidence_counts[item.confidence] = (
            confidence_counts.get(item.confidence, 0) + 1
        )
    return BrowserGovernanceAttentionSummary(
        status=(
            "OPERATOR_REVIEW_REQUIRED"
            if rows
            else "NO_REGISTERED_GOVERNANCE_PROJECTIONS"
        ),
        projection_count=len(rows),
        operator_review_required_count=len(rows),
        blocked_count=sum(item.state.startswith("BLOCKED_") for item in rows),
        incomplete_count=sum(item.state == "INCOMPLETE" for item in rows),
        observed_field_count=sum(
            field.origin == "OBSERVED"
            for item in rows
            for field in item.fields
        ),
        inferred_field_count=sum(
            field.origin == "INFERRED"
            for item in rows
            for field in item.fields
        ),
        confidence_counts=confidence_counts,
    )
