from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import BrowserProductConsoleApplication, ConsoleReadModel, build_console_read_model, build_default_operator_launch_profile, load_starter_artifact_package
from apps.browser_product_console_runtime_app_1.research_workspace_views import build_governance_workspace_model
from apps.v2_r40_browser_factor_governance_field_presentation_app_1 import BrowserFactorGovernanceFieldPresentation, BrowserGovernanceFieldPresentationRow
from apps.v2_r43_browser_governance_review_queue_presentation_app_1 import build_governance_review_queue
from apps.v2_r44_browser_governance_review_evidence_trace_presentation_app_1 import build_governance_review_evidence_trace
from apps.v2_r46_browser_governance_review_coverage_summary_presentation_app_1 import build_governance_review_coverage_summary
from apps.v2_r47_browser_governance_review_market_summary_presentation_app_1 import V2_R47_BROWSER_GOVERNANCE_REVIEW_MARKET_SUMMARY_BOUNDARY, V2R47BrowserGovernanceReviewMarketSummaryBoundary, build_governance_review_market_summary, build_governance_review_market_summary_acceptance

ROOT = Path(__file__).resolve().parents[2]


def _presentation(name: str, market: str, state: str = "REVIEW_REQUIRED") -> BrowserFactorGovernanceFieldPresentation:
    return BrowserFactorGovernanceFieldPresentation(
        artifact_id=f"artifact-{name}", projection_id=f"projection-{name}", candidate_id=f"candidate-{name}", factor_id=f"factor-{name}", market=market,
        evaluated_at_utc="2026-07-24T00:00:00Z", state=state, confidence="MEDIUM",
        fields=(BrowserGovernanceFieldPresentationRow("observed", "value", "OBSERVED", "HIGH", ("a" * 64,)),), reason_codes=(f"reason-{name}",), projection_hash="b" * 64,
    )


def _summary(items=(), traced=None):
    traced_items = items if traced is None else traced
    queue = build_governance_review_queue(items)
    trace = build_governance_review_evidence_trace(traced_items)
    coverage = build_governance_review_coverage_summary(queue, trace)
    return build_governance_review_market_summary(queue, coverage)


def _empty_model():
    return ConsoleReadModel(correlation_id="r47-empty", candidates=(), sections=MappingProxyType({}), source_artifact_ids=(), artifact_records=())


def _starter_model():
    profile = build_default_operator_launch_profile(project_root=ROOT)
    _, loaded = load_starter_artifact_package(profile)
    return build_console_read_model(loaded)


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R47_BROWSER_GOVERNANCE_REVIEW_MARKET_SUMMARY_BOUNDARY
    assert boundary.read_only and boundary.operator_review_required and not boundary.approval_allowed
    with pytest.raises(FrozenInstanceError):
        boundary.read_only = False  # type: ignore[misc]


def test_d1_boundary_rejects_write_capability():
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R47BrowserGovernanceReviewMarketSummaryBoundary(write_controls_allowed=True)


def test_d2_empty_summary_is_explicit_and_non_actionable():
    summary = _summary()
    assert summary.status == "NO_REGISTERED_REVIEW_MARKETS" and summary.items == ()
    assert not summary.action_created


def test_d2_market_counts_are_immutable():
    item = _summary((_presentation("one", "a-share"),)).items[0]
    with pytest.raises(FrozenInstanceError):
        item.queue_item_count = 2  # type: ignore[misc]


def test_d3_aggregation_groups_and_orders_markets():
    summary = _summary((_presentation("btc", "btc"), _presentation("a", "a-share")))
    assert tuple(item.market for item in summary.items) == ("a-share", "btc")
    assert summary.market_count == 2 and summary.queue_item_count == 2


def test_d3_aggregation_counts_attention_and_coverage():
    a = _presentation("a", "a-share", "BLOCKED_INTEGRITY")
    b = _presentation("b", "a-share", "INCOMPLETE")
    summary = _summary((a, b), (a,))
    item = summary.items[0]
    assert (item.blocked_count, item.incomplete_count) == (1, 1)
    assert (item.covered_item_count, item.missing_evidence_count) == (1, 1)


def test_d3_unknown_input_fails_closed():
    with pytest.raises(ValueError, match="validated"):
        build_governance_review_market_summary(object(), object())  # type: ignore[arg-type]


def test_d4_workspace_always_contains_market_summary():
    summary = build_governance_workspace_model(_empty_model()).review_market_summary
    assert summary is not None and summary.status == "NO_REGISTERED_REVIEW_MARKETS"


def test_d4_starter_market_summary_aligns_with_queue():
    workspace = build_governance_workspace_model(_starter_model())
    assert workspace.review_market_summary.queue_item_count == len(workspace.review_queue.items) == 1


def test_d5_http_page_renders_market_summary_before_queue():
    body = BrowserProductConsoleApplication(_starter_model()).dispatch("GET", "/governance").body.decode("utf-8")
    assert body.index("Governance Review Market Summary") < body.index("Operator Governance Review Queue")
    assert "Markets" in body and "Covered items" in body


def test_d5_http_market_summary_is_non_actionable():
    app = BrowserProductConsoleApplication(_starter_model())
    body = app.dispatch("GET", "/governance").body.decode("utf-8").lower()
    assert "do not rank markets" in body and "<form" not in body and "<button" not in body
    assert app.dispatch("POST", "/governance").status == 405


def test_d6_acceptance_preserves_read_only_review():
    acceptance = build_governance_review_market_summary_acceptance(_summary((_presentation("one", "btc"),)))
    assert acceptance.status == "PASSED_READ_ONLY_REVIEW_MARKET_SUMMARY"
    assert acceptance.market_count == 1 and acceptance.queue_item_count == 1
    assert acceptance.read_only and acceptance.operator_review_required and not acceptance.action_created
