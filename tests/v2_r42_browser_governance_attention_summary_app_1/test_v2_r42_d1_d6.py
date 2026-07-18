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
from apps.v2_r42_browser_governance_attention_summary_app_1 import (
    V2_R42_BROWSER_GOVERNANCE_ATTENTION_SUMMARY_BOUNDARY,
    V2R42BrowserGovernanceAttentionSummaryBoundary,
    build_governance_attention_acceptance,
    build_governance_attention_summary,
)


ROOT = Path(__file__).resolve().parents[2]


def _presentation(
    *,
    state: str = "REVIEW_REQUIRED",
    confidence: str = "MEDIUM",
) -> BrowserFactorGovernanceFieldPresentation:
    return BrowserFactorGovernanceFieldPresentation(
        artifact_id="attention-artifact",
        projection_id="attention-projection",
        candidate_id="attention-candidate",
        factor_id="attention-factor",
        market="a-share",
        evaluated_at_utc="2026-07-23T00:00:00Z",
        state=state,
        confidence=confidence,
        fields=(
            BrowserGovernanceFieldPresentationRow(
                "observed", "value", "OBSERVED", "HIGH", ("a" * 64,)
            ),
            BrowserGovernanceFieldPresentationRow(
                "inferred", "value", "INFERRED", "MEDIUM", ("b" * 64,)
            ),
        ),
        reason_codes=("operator-review-required",),
        projection_hash="c" * 64,
    )


def _empty_model() -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="r42-empty",
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
    boundary = V2_R42_BROWSER_GOVERNANCE_ATTENTION_SUMMARY_BOUNDARY
    assert boundary.read_only and boundary.operator_review_required
    assert not boundary.approval_allowed and not boundary.write_controls_allowed
    with pytest.raises(FrozenInstanceError):
        boundary.read_only = False  # type: ignore[misc]


def test_d1_boundary_rejects_approval_capability():
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R42BrowserGovernanceAttentionSummaryBoundary(approval_allowed=True)


def test_d2_empty_summary_is_explicit_and_non_actionable():
    summary = build_governance_attention_summary(())
    assert summary.status == "NO_REGISTERED_GOVERNANCE_PROJECTIONS"
    assert summary.projection_count == 0
    assert not summary.approval_created and not summary.action_created


def test_d2_summary_counts_origins_review_and_confidence():
    summary = build_governance_attention_summary((_presentation(),))
    assert summary.status == "OPERATOR_REVIEW_REQUIRED"
    assert summary.operator_review_required_count == 1
    assert summary.observed_field_count == 1
    assert summary.inferred_field_count == 1
    assert summary.confidence_counts == {"MEDIUM": 1}


def test_d2_confidence_counts_are_immutable():
    summary = build_governance_attention_summary((_presentation(),))
    assert isinstance(summary.confidence_counts, MappingProxyType)
    with pytest.raises(TypeError):
        summary.confidence_counts["HIGH"] = 2  # type: ignore[index]


def test_d3_blocked_and_incomplete_states_are_counted_deterministically():
    summary = build_governance_attention_summary(
        (
            _presentation(state="BLOCKED_INTEGRITY", confidence="LOW"),
            _presentation(state="INCOMPLETE", confidence="UNAVAILABLE"),
        )
    )
    assert summary.blocked_count == 1
    assert summary.incomplete_count == 1
    assert tuple(summary.confidence_counts) == ("LOW", "UNAVAILABLE")


def test_d3_unknown_input_fails_closed():
    with pytest.raises(ValueError, match="validated"):
        build_governance_attention_summary((object(),))  # type: ignore[arg-type]


def test_d4_workspace_always_contains_attention_summary():
    workspace = build_governance_workspace_model(_empty_model())
    assert workspace.attention_summary is not None
    assert workspace.attention_summary.projection_count == 0


def test_d4_starter_workspace_summary_requires_operator_review():
    workspace = build_governance_workspace_model(_starter_model())
    summary = workspace.attention_summary
    assert summary is not None
    assert summary.projection_count == 1
    assert summary.operator_review_required_count == 1


def test_d5_http_page_renders_attention_summary_before_detail():
    body = BrowserProductConsoleApplication(_starter_model()).dispatch(
        "GET", "/governance"
    ).body.decode("utf-8")
    assert "Operator Attention Summary" in body
    assert "OPERATOR_REVIEW_REQUIRED" in body
    assert body.index("Operator Attention Summary") < body.index(
        "Factor Governance Field Detail"
    )


def test_d5_http_attention_summary_is_non_actionable():
    app = BrowserProductConsoleApplication(_starter_model())
    body = app.dispatch("GET", "/governance").body.decode("utf-8").lower()
    assert "<form" not in body and "<button" not in body
    assert app.dispatch("POST", "/governance").status == 405


def test_d6_acceptance_preserves_review_and_read_only_state():
    summary = build_governance_attention_summary((_presentation(),))
    acceptance = build_governance_attention_acceptance(summary)
    assert acceptance.status == "PASSED_READ_ONLY_ATTENTION_SUMMARY"
    assert acceptance.projection_count == 1
    assert acceptance.review_required_count == 1
    assert acceptance.read_only and acceptance.operator_review_required


def test_d6_starter_summary_reports_both_field_origins():
    summary = build_governance_workspace_model(_starter_model()).attention_summary
    assert summary is not None
    assert summary.observed_field_count == 1
    assert summary.inferred_field_count == 1
