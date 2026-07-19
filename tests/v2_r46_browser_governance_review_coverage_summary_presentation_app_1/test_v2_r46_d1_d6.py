from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    build_console_read_model,
    build_default_operator_launch_profile,
    load_starter_artifact_package,
)
from apps.browser_product_console_runtime_app_1.research_workspace_views import (
    build_governance_workspace_model,
)
from apps.v2_r40_browser_factor_governance_field_presentation_app_1 import (
    BrowserFactorGovernanceFieldPresentation,
    BrowserGovernanceFieldPresentationRow,
)
from apps.v2_r43_browser_governance_review_queue_presentation_app_1 import (
    build_governance_review_queue,
)
from apps.v2_r44_browser_governance_review_evidence_trace_presentation_app_1 import (
    build_governance_review_evidence_trace,
)
from apps.v2_r46_browser_governance_review_coverage_summary_presentation_app_1 import (
    V2_R46_BROWSER_GOVERNANCE_REVIEW_COVERAGE_SUMMARY_BOUNDARY,
    V2R46BrowserGovernanceReviewCoverageSummaryBoundary,
    build_governance_review_coverage_summary,
    build_governance_review_coverage_summary_acceptance,
)


ROOT = Path(__file__).resolve().parents[2]


def _presentation(name: str) -> BrowserFactorGovernanceFieldPresentation:
    return BrowserFactorGovernanceFieldPresentation(
        artifact_id=f"artifact-{name}",
        projection_id=f"projection-{name}",
        candidate_id=f"candidate-{name}",
        factor_id=f"factor-{name}",
        market="a-share",
        evaluated_at_utc="2026-07-24T00:00:00Z",
        state="REVIEW_REQUIRED",
        confidence="MEDIUM",
        fields=(
            BrowserGovernanceFieldPresentationRow(
                "observed",
                "value",
                "OBSERVED",
                "HIGH",
                ("a" * 64, "b" * 64),
            ),
            BrowserGovernanceFieldPresentationRow(
                "inferred",
                "value",
                "INFERRED",
                "MEDIUM",
                ("b" * 64,),
            ),
        ),
        reason_codes=(f"reason-{name}",),
        projection_hash="c" * 64,
    )


def _summary(queue_presentations=(), trace_presentations=()):
    return build_governance_review_coverage_summary(
        build_governance_review_queue(queue_presentations),
        build_governance_review_evidence_trace(trace_presentations),
    )


def _empty_model() -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="r46-empty",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
        artifact_records=(),
    )


def _starter_model() -> ConsoleReadModel:
    profile = build_default_operator_launch_profile(project_root=ROOT)
    _, loaded = load_starter_artifact_package(profile)
    return build_console_read_model(loaded)


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R46_BROWSER_GOVERNANCE_REVIEW_COVERAGE_SUMMARY_BOUNDARY
    assert boundary.registered_evidence_only and boundary.read_only
    assert boundary.operator_review_required and not boundary.approval_allowed
    with pytest.raises(FrozenInstanceError):
        boundary.read_only = False  # type: ignore[misc]


def test_d1_boundary_rejects_network_capability():
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R46BrowserGovernanceReviewCoverageSummaryBoundary(
            network_fetch_allowed=True
        )


def test_d2_empty_summary_is_explicit_and_non_actionable():
    summary = _summary()
    assert summary.status == "NO_REGISTERED_REVIEW_ITEMS"
    assert summary.items == () and not summary.action_created


def test_d2_coverage_items_are_immutable():
    presentation = _presentation("one")
    item = _summary((presentation,), (presentation,)).items[0]
    with pytest.raises(FrozenInstanceError):
        item.evidence_registered = False  # type: ignore[misc]


def test_d3_complete_coverage_counts_registered_evidence():
    presentation = _presentation("one")
    summary = _summary((presentation,), (presentation,))
    assert summary.status == "COMPLETE_REGISTERED_EVIDENCE_COVERAGE"
    assert (summary.covered_item_count, summary.missing_evidence_count) == (1, 0)
    assert (summary.observed_field_count, summary.inferred_field_count) == (1, 1)
    assert summary.source_snapshot_count == 2


def test_d3_missing_evidence_remains_visible():
    summary = _summary((_presentation("one"),), ())
    assert summary.status == "INCOMPLETE_REGISTERED_EVIDENCE_COVERAGE"
    assert summary.covered_item_count == 0 and summary.missing_evidence_count == 1
    assert summary.items[0].evidence_registered is False


def test_d3_orphan_evidence_fails_closed():
    with pytest.raises(ValueError, match="orphan"):
        _summary((), (_presentation("orphan"),))


def test_d3_unknown_input_fails_closed():
    with pytest.raises(ValueError, match="validated"):
        build_governance_review_coverage_summary(object(), object())  # type: ignore[arg-type]


def test_d4_workspace_always_contains_coverage_summary():
    summary = build_governance_workspace_model(_empty_model()).review_coverage_summary
    assert summary is not None and summary.status == "NO_REGISTERED_REVIEW_ITEMS"


def test_d4_starter_coverage_aligns_with_queue_and_trace():
    workspace = build_governance_workspace_model(_starter_model())
    summary = workspace.review_coverage_summary
    assert summary is not None
    assert summary.queue_item_count == len(workspace.review_queue.items) == 1
    assert summary.covered_item_count == len(workspace.review_evidence_trace.items) == 1


def test_d5_http_page_renders_coverage_before_queue():
    body = BrowserProductConsoleApplication(_starter_model()).dispatch(
        "GET", "/governance"
    ).body.decode("utf-8")
    assert body.index("Governance Review Coverage Summary") < body.index(
        "Operator Governance Review Queue"
    )
    assert "Missing evidence" in body and "Evidence coverage" in body


def test_d5_http_coverage_is_non_actionable():
    app = BrowserProductConsoleApplication(_starter_model())
    body = app.dispatch("GET", "/governance").body.decode("utf-8").lower()
    assert "derived deterministically" in body
    assert "<form" not in body and "<button" not in body
    assert app.dispatch("POST", "/governance").status == 405


def test_d6_acceptance_preserves_registered_evidence_authority():
    presentation = _presentation("one")
    acceptance = build_governance_review_coverage_summary_acceptance(
        _summary((presentation,), (presentation,))
    )
    assert acceptance.status == (
        "PASSED_READ_ONLY_REGISTERED_EVIDENCE_COVERAGE_SUMMARY"
    )
    assert acceptance.read_only and acceptance.operator_review_required
    assert not acceptance.action_created


def test_d6_acceptance_preserves_missing_coverage_count():
    acceptance = build_governance_review_coverage_summary_acceptance(
        _summary((_presentation("one"),), ())
    )
    assert acceptance.queue_item_count == 1
    assert acceptance.covered_item_count == 0
    assert acceptance.missing_evidence_count == 1
