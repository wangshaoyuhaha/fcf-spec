from collections.abc import Iterable

from apps.v2_r40_browser_factor_governance_field_presentation_app_1 import BrowserFactorGovernanceFieldPresentation

from .contracts import BrowserGovernanceReviewQueue, BrowserGovernanceReviewQueueItem


_ATTENTION_RANK = {"BLOCKED": 0, "INCOMPLETE": 1, "REVIEW_REQUIRED": 2}


def _attention_class(state: str) -> str:
    if state.startswith("BLOCKED_"):
        return "BLOCKED"
    if state == "INCOMPLETE":
        return "INCOMPLETE"
    return "REVIEW_REQUIRED"


def build_governance_review_queue(presentations: Iterable[BrowserFactorGovernanceFieldPresentation]) -> BrowserGovernanceReviewQueue:
    source = tuple(presentations)
    if any(not isinstance(item, BrowserFactorGovernanceFieldPresentation) for item in source):
        raise ValueError("validated governance presentations are required")
    rows = tuple(sorted((BrowserGovernanceReviewQueueItem(
        attention_class=_attention_class(item.state), artifact_id=item.artifact_id,
        projection_id=item.projection_id, candidate_id=item.candidate_id,
        factor_id=item.factor_id, market=item.market, state=item.state,
        confidence=item.confidence, reason_codes=item.reason_codes,
        projection_hash=item.projection_hash,
    ) for item in source), key=lambda item: (
        _ATTENTION_RANK[item.attention_class], item.candidate_id, item.factor_id,
        item.projection_id, item.artifact_id,
    )))
    return BrowserGovernanceReviewQueue(
        status="OPERATOR_REVIEW_REQUIRED" if rows else "NO_REGISTERED_REVIEW_ITEMS",
        items=rows,
    )
