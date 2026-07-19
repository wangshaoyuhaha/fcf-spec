from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import BrowserProductConsoleApplication, ConsoleReadModel, build_console_read_model, build_default_operator_launch_profile, load_starter_artifact_package
from apps.browser_product_console_runtime_app_1.research_workspace_views import build_governance_workspace_model
from apps.v2_r40_browser_factor_governance_field_presentation_app_1 import BrowserFactorGovernanceFieldPresentation, BrowserGovernanceFieldPresentationRow
from apps.v2_r43_browser_governance_review_queue_presentation_app_1 import build_governance_review_queue
from apps.v2_r45_browser_governance_review_reason_summary_presentation_app_1 import V2_R45_BROWSER_GOVERNANCE_REVIEW_REASON_SUMMARY_BOUNDARY, V2R45BrowserGovernanceReviewReasonSummaryBoundary, build_governance_review_reason_summary, build_governance_review_reason_summary_acceptance


ROOT = Path(__file__).resolve().parents[2]


def _presentation(name: str, state: str, reasons: tuple[str, ...]) -> BrowserFactorGovernanceFieldPresentation:
    return BrowserFactorGovernanceFieldPresentation(
        artifact_id=f"artifact-{name}", projection_id=f"projection-{name}", candidate_id=f"candidate-{name}", factor_id=f"factor-{name}", market="a-share", evaluated_at_utc="2026-07-24T00:00:00Z", state=state, confidence="MEDIUM",
        fields=(BrowserGovernanceFieldPresentationRow("observed", "value", "OBSERVED", "HIGH", ("a" * 64,)),), reason_codes=reasons, projection_hash="b" * 64,
    )


def _queue(*presentations: BrowserFactorGovernanceFieldPresentation):
    return build_governance_review_queue(presentations)


def _empty_model() -> ConsoleReadModel:
    return ConsoleReadModel(correlation_id="r45-empty", candidates=(), sections=MappingProxyType({}), source_artifact_ids=(), artifact_records=())


def _starter_model() -> ConsoleReadModel:
    profile = build_default_operator_launch_profile(project_root=ROOT)
    _, loaded = load_starter_artifact_package(profile)
    return build_console_read_model(loaded)


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R45_BROWSER_GOVERNANCE_REVIEW_REASON_SUMMARY_BOUNDARY
    assert boundary.read_only and boundary.operator_review_required and not boundary.approval_allowed
    with pytest.raises(FrozenInstanceError):
        boundary.read_only = False  # type: ignore[misc]


def test_d1_boundary_rejects_write_capability():
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R45BrowserGovernanceReviewReasonSummaryBoundary(write_controls_allowed=True)


def test_d2_empty_summary_is_explicit_and_non_actionable():
    summary = build_governance_review_reason_summary(_queue())
    assert summary.status == "NO_REGISTERED_REVIEW_REASONS" and summary.items == ()
    assert not summary.action_created


def test_d2_reason_counts_are_immutable():
    item = build_governance_review_reason_summary(_queue(_presentation("one", "REVIEW_REQUIRED", ("reason",)))).items[0]
    with pytest.raises(FrozenInstanceError):
        item.occurrence_count = 2  # type: ignore[misc]


def test_d3_aggregation_counts_attention_classes():
    summary = build_governance_review_reason_summary(_queue(
        _presentation("blocked", "BLOCKED_INTEGRITY", ("shared",)),
        _presentation("incomplete", "INCOMPLETE", ("shared",)),
        _presentation("review", "REVIEW_REQUIRED", ("shared",)),
    ))
    item = summary.items[0]
    assert (item.occurrence_count, item.blocked_count, item.incomplete_count, item.review_required_count) == (3, 1, 1, 1)


def test_d3_aggregation_orders_count_then_code():
    summary = build_governance_review_reason_summary(_queue(
        _presentation("one", "REVIEW_REQUIRED", ("z", "common")),
        _presentation("two", "REVIEW_REQUIRED", ("a", "common")),
    ))
    assert tuple(item.reason_code for item in summary.items) == ("common", "a", "z")


def test_d3_unknown_input_fails_closed():
    with pytest.raises(ValueError, match="validated"):
        build_governance_review_reason_summary(object())  # type: ignore[arg-type]


def test_d4_workspace_always_contains_reason_summary():
    summary = build_governance_workspace_model(_empty_model()).review_reason_summary
    assert summary is not None and summary.status == "NO_REGISTERED_REVIEW_REASONS"


def test_d4_starter_summary_aligns_with_queue():
    workspace = build_governance_workspace_model(_starter_model())
    assert workspace.review_reason_summary.queue_item_count == len(workspace.review_queue.items) == 1


def test_d5_http_page_renders_reason_summary_before_queue():
    body = BrowserProductConsoleApplication(_starter_model()).dispatch("GET", "/governance").body.decode("utf-8")
    assert body.index("Governance Review Reason Summary") < body.index("Operator Governance Review Queue")
    assert "Reason occurrences" in body and "Review required" in body


def test_d5_http_summary_is_non_actionable():
    app = BrowserProductConsoleApplication(_starter_model())
    body = app.dispatch("GET", "/governance").body.decode("utf-8").lower()
    assert "derived deterministically" in body and "<form" not in body and "<button" not in body
    assert app.dispatch("POST", "/governance").status == 405


def test_d6_acceptance_preserves_read_only_review():
    summary = build_governance_review_reason_summary(_queue(_presentation("one", "REVIEW_REQUIRED", ("reason",))))
    acceptance = build_governance_review_reason_summary_acceptance(summary)
    assert acceptance.status == "PASSED_READ_ONLY_REVIEW_REASON_SUMMARY"
    assert acceptance.read_only and acceptance.operator_review_required and not acceptance.action_created


def test_d6_acceptance_counts_unique_and_total_reasons():
    summary = build_governance_review_reason_summary(_queue(_presentation("one", "REVIEW_REQUIRED", ("a", "b"))))
    acceptance = build_governance_review_reason_summary_acceptance(summary)
    assert acceptance.unique_reason_count == 2 and acceptance.reason_occurrence_count == 2
