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
from apps.browser_product_console_runtime_app_1.research_workspace_views import build_governance_workspace_model
from apps.v2_r40_browser_factor_governance_field_presentation_app_1 import (
    BrowserFactorGovernanceFieldPresentation,
    BrowserGovernanceFieldPresentationRow,
)
from apps.v2_r43_browser_governance_review_queue_presentation_app_1 import (
    V2_R43_BROWSER_GOVERNANCE_REVIEW_QUEUE_BOUNDARY,
    V2R43BrowserGovernanceReviewQueueBoundary,
    build_governance_review_queue,
    build_governance_review_queue_acceptance,
)


ROOT = Path(__file__).resolve().parents[2]


def _presentation(name: str, *, state: str = "REVIEW_REQUIRED", confidence: str = "MEDIUM") -> BrowserFactorGovernanceFieldPresentation:
    return BrowserFactorGovernanceFieldPresentation(
        artifact_id=f"artifact-{name}", projection_id=f"projection-{name}",
        candidate_id=f"candidate-{name}", factor_id=f"factor-{name}",
        market="a-share", evaluated_at_utc="2026-07-24T00:00:00Z",
        state=state, confidence=confidence,
        fields=(BrowserGovernanceFieldPresentationRow(
            "observed", "value", "OBSERVED", "HIGH", ("a" * 64,)
        ),), reason_codes=(f"reason-{name}",), projection_hash="b" * 64,
    )


def _empty_model() -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="r43-empty", candidates=(),
        sections=MappingProxyType({}), source_artifact_ids=(), artifact_records=(),
    )


def _starter_model() -> ConsoleReadModel:
    profile = build_default_operator_launch_profile(project_root=ROOT)
    _, loaded = load_starter_artifact_package(profile)
    return build_console_read_model(loaded)


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R43_BROWSER_GOVERNANCE_REVIEW_QUEUE_BOUNDARY
    assert boundary.read_only and boundary.operator_review_required
    assert not boundary.approval_allowed and not boundary.write_controls_allowed
    with pytest.raises(FrozenInstanceError):
        boundary.read_only = False  # type: ignore[misc]


def test_d1_boundary_rejects_approval_capability():
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R43BrowserGovernanceReviewQueueBoundary(approval_allowed=True)


def test_d2_empty_queue_is_explicit_and_non_actionable():
    queue = build_governance_review_queue(())
    assert queue.status == "NO_REGISTERED_REVIEW_ITEMS"
    assert queue.items == () and not queue.action_created


def test_d2_queue_items_are_immutable():
    item = build_governance_review_queue((_presentation("one"),)).items[0]
    assert isinstance(item.reason_codes, tuple)
    with pytest.raises(FrozenInstanceError):
        item.state = "OTHER"  # type: ignore[misc]


def test_d3_queue_orders_attention_classes_deterministically():
    queue = build_governance_review_queue((
        _presentation("review"),
        _presentation("incomplete", state="INCOMPLETE", confidence="UNAVAILABLE"),
        _presentation("blocked", state="BLOCKED_INTEGRITY", confidence="LOW"),
    ))
    assert tuple(item.attention_class for item in queue.items) == (
        "BLOCKED", "INCOMPLETE", "REVIEW_REQUIRED"
    )


def test_d3_queue_uses_stable_identity_tie_breakers():
    queue = build_governance_review_queue((_presentation("z"), _presentation("a")))
    assert tuple(item.candidate_id for item in queue.items) == (
        "candidate-a", "candidate-z"
    )


def test_d3_unknown_input_fails_closed():
    with pytest.raises(ValueError, match="validated"):
        build_governance_review_queue((object(),))  # type: ignore[arg-type]


def test_d4_workspace_always_contains_review_queue():
    queue = build_governance_workspace_model(_empty_model()).review_queue
    assert queue is not None and queue.status == "NO_REGISTERED_REVIEW_ITEMS"


def test_d4_starter_workspace_has_one_registered_review_item():
    queue = build_governance_workspace_model(_starter_model()).review_queue
    assert queue is not None and len(queue.items) == 1


def test_d5_http_page_renders_queue_between_summary_and_detail():
    body = BrowserProductConsoleApplication(_starter_model()).dispatch(
        "GET", "/governance"
    ).body.decode("utf-8")
    assert "Operator Governance Review Queue" in body
    assert body.index("Operator Attention Summary") < body.index(
        "Operator Governance Review Queue"
    ) < body.index("Factor Governance Field Detail")


def test_d5_http_queue_is_non_actionable():
    app = BrowserProductConsoleApplication(_starter_model())
    body = app.dispatch("GET", "/governance").body.decode("utf-8").lower()
    assert "projection hash" in body and "<form" not in body and "<button" not in body
    assert app.dispatch("POST", "/governance").status == 405


def test_d6_acceptance_preserves_review_and_read_only_state():
    queue = build_governance_review_queue((_presentation("one"),))
    acceptance = build_governance_review_queue_acceptance(queue)
    assert acceptance.status == "PASSED_READ_ONLY_REVIEW_QUEUE"
    assert acceptance.queue_item_count == 1
    assert acceptance.read_only and acceptance.operator_review_required


def test_d6_acceptance_counts_blocked_and_incomplete_rows():
    queue = build_governance_review_queue((
        _presentation("blocked", state="BLOCKED_INTEGRITY"),
        _presentation("incomplete", state="INCOMPLETE"),
    ))
    acceptance = build_governance_review_queue_acceptance(queue)
    assert acceptance.blocked_count == 1 and acceptance.incomplete_count == 1
