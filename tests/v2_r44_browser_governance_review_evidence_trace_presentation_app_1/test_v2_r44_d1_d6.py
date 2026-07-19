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
from apps.v2_r44_browser_governance_review_evidence_trace_presentation_app_1 import (
    V2_R44_BROWSER_GOVERNANCE_REVIEW_EVIDENCE_TRACE_BOUNDARY,
    V2R44BrowserGovernanceReviewEvidenceTraceBoundary,
    build_governance_review_evidence_trace,
    build_governance_review_evidence_trace_acceptance,
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
            BrowserGovernanceFieldPresentationRow("observed", "value", "OBSERVED", "HIGH", ("b" * 64, "a" * 64)),
            BrowserGovernanceFieldPresentationRow("inferred", "value", "INFERRED", "MEDIUM", ("b" * 64,)),
        ),
        reason_codes=(f"reason-{name}",),
        projection_hash="c" * 64,
    )


def _empty_model() -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="r44-empty",
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
    boundary = V2_R44_BROWSER_GOVERNANCE_REVIEW_EVIDENCE_TRACE_BOUNDARY
    assert boundary.registered_evidence_only and boundary.read_only
    assert boundary.operator_review_required and not boundary.approval_allowed
    with pytest.raises(FrozenInstanceError):
        boundary.read_only = False  # type: ignore[misc]


def test_d1_boundary_rejects_network_capability():
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R44BrowserGovernanceReviewEvidenceTraceBoundary(network_fetch_allowed=True)


def test_d2_empty_trace_is_explicit_and_non_actionable():
    trace = build_governance_review_evidence_trace(())
    assert trace.status == "NO_REGISTERED_EVIDENCE_TRACE"
    assert trace.items == () and not trace.action_created


def test_d2_trace_items_are_immutable():
    item = build_governance_review_evidence_trace((_presentation("one"),)).items[0]
    assert item.source_snapshot_hashes == ("a" * 64, "b" * 64)
    with pytest.raises(FrozenInstanceError):
        item.observed_field_count = 0  # type: ignore[misc]


def test_d3_aggregation_counts_origins_and_deduplicates_sources():
    item = build_governance_review_evidence_trace((_presentation("one"),)).items[0]
    assert item.observed_field_count == 1 and item.inferred_field_count == 1
    assert item.field_count == 2 and item.source_snapshot_count == 2


def test_d3_aggregation_orders_identity_deterministically():
    trace = build_governance_review_evidence_trace((_presentation("z"), _presentation("a")))
    assert tuple(item.projection_id for item in trace.items) == ("projection-a", "projection-z")


def test_d3_unknown_input_fails_closed():
    with pytest.raises(ValueError, match="validated"):
        build_governance_review_evidence_trace((object(),))  # type: ignore[arg-type]


def test_d4_workspace_always_contains_evidence_trace():
    trace = build_governance_workspace_model(_empty_model()).review_evidence_trace
    assert trace is not None and trace.status == "NO_REGISTERED_EVIDENCE_TRACE"


def test_d4_starter_trace_aligns_with_review_queue():
    workspace = build_governance_workspace_model(_starter_model())
    trace = workspace.review_evidence_trace
    assert trace is not None and len(trace.items) == len(workspace.review_queue.items) == 1


def test_d5_http_page_renders_registered_evidence_trace_columns():
    body = BrowserProductConsoleApplication(_starter_model()).dispatch("GET", "/governance").body.decode("utf-8")
    assert "Observed fields" in body and "Inferred fields" in body
    assert "Source snapshot hashes" in body and "Registered sources" in body


def test_d5_http_trace_is_non_actionable():
    app = BrowserProductConsoleApplication(_starter_model())
    body = app.dispatch("GET", "/governance").body.decode("utf-8").lower()
    assert "registered evidence traces" in body and "<form" not in body and "<button" not in body
    assert app.dispatch("POST", "/governance").status == 405


def test_d6_acceptance_preserves_registered_evidence_authority():
    trace = build_governance_review_evidence_trace((_presentation("one"),))
    acceptance = build_governance_review_evidence_trace_acceptance(trace)
    assert acceptance.status == "PASSED_READ_ONLY_REGISTERED_EVIDENCE_TRACE"
    assert acceptance.trace_item_count == 1 and acceptance.source_snapshot_count == 2
    assert acceptance.read_only and acceptance.operator_review_required


def test_d6_acceptance_counts_observed_and_inferred_fields():
    trace = build_governance_review_evidence_trace((_presentation("one"), _presentation("two")))
    acceptance = build_governance_review_evidence_trace_acceptance(trace)
    assert acceptance.observed_field_count == 2 and acceptance.inferred_field_count == 2
