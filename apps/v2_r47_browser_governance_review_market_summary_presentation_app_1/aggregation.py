from collections import defaultdict

from apps.v2_r43_browser_governance_review_queue_presentation_app_1 import BrowserGovernanceReviewQueue
from apps.v2_r46_browser_governance_review_coverage_summary_presentation_app_1 import BrowserGovernanceReviewCoverageSummary

from .contracts import BrowserGovernanceReviewMarketCount, BrowserGovernanceReviewMarketSummary


def build_governance_review_market_summary(
    queue: BrowserGovernanceReviewQueue,
    coverage: BrowserGovernanceReviewCoverageSummary,
) -> BrowserGovernanceReviewMarketSummary:
    if not isinstance(queue, BrowserGovernanceReviewQueue):
        raise ValueError("validated governance review queue is required")
    if not isinstance(coverage, BrowserGovernanceReviewCoverageSummary):
        raise ValueError("validated governance review coverage summary is required")
    coverage_by_key = {(item.artifact_id, item.projection_id): item for item in coverage.items}
    queue_keys = {(item.artifact_id, item.projection_id) for item in queue.items}
    if len(coverage_by_key) != len(coverage.items) or set(coverage_by_key) != queue_keys:
        raise ValueError("governance review coverage must align to queue")
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for item in queue.items:
        market_counts = counts[item.market]
        market_counts["queue"] += 1
        market_counts[item.attention_class] += 1
        covered = coverage_by_key[(item.artifact_id, item.projection_id)].evidence_registered
        market_counts["covered" if covered else "missing"] += 1
    items = tuple(
        BrowserGovernanceReviewMarketCount(
            market=market,
            queue_item_count=value["queue"],
            blocked_count=value["BLOCKED"],
            incomplete_count=value["INCOMPLETE"],
            review_required_count=value["REVIEW_REQUIRED"],
            covered_item_count=value["covered"],
            missing_evidence_count=value["missing"],
        )
        for market, value in sorted(counts.items())
    )
    return BrowserGovernanceReviewMarketSummary(
        status="REGISTERED_REVIEW_MARKETS_AVAILABLE" if items else "NO_REGISTERED_REVIEW_MARKETS",
        items=items,
        queue_item_count=len(queue.items),
        covered_item_count=coverage.covered_item_count,
        missing_evidence_count=coverage.missing_evidence_count,
    )
