import pytest

from apps.data_and_credential_governance import (
    FreshnessBand,
    FreshnessPolicy,
    FreshnessPolicyRegistry,
    GovernanceDecisionStatus,
    GovernanceRequest,
    PolicyIdentity,
    StaleAction,
    evaluate_data_freshness,
)


def _request(source_id="source-a", evaluated_at="2026-07-16T06:00:00Z"):
    return GovernanceRequest("request-a", "correlation-a", source_id, evaluated_at, "LOCAL_RESEARCH")


def _policy(**updates):
    values = dict(
        source_id="source-a",
        source_evidence_id="source-evidence-a",
        identity=PolicyIdentity("freshness-policy-a", "v1", "freshness-evidence-a"),
        fresh_for_seconds=60,
        aging_for_seconds=300,
    )
    values.update(updates)
    return FreshnessPolicy(**values)


def test_d3_policy_rejects_invalid_windows_and_review_bypass():
    with pytest.raises(ValueError, match="non-negative"):
        _policy(fresh_for_seconds=-1)
    with pytest.raises(ValueError, match="must not be less"):
        _policy(fresh_for_seconds=301)
    with pytest.raises(ValueError, match="operator_review_required"):
        _policy(operator_review_required=False)


def test_d3_registry_validates_type_before_sorting():
    with pytest.raises(TypeError, match="FreshnessPolicy"):
        FreshnessPolicyRegistry(("invalid",))


def test_d3_registry_is_reproducible_and_rejects_duplicates():
    other = _policy(
        source_id="source-b",
        source_evidence_id="source-evidence-b",
        identity=PolicyIdentity("freshness-policy-b", "v1", "freshness-evidence-b"),
    )
    assert FreshnessPolicyRegistry((_policy(), other)).registry_sha256 == FreshnessPolicyRegistry((other, _policy())).registry_sha256
    with pytest.raises(ValueError, match="source_id"):
        FreshnessPolicyRegistry((_policy(), _policy()))


def test_d3_missing_policy_is_blocked_unknown():
    band, decision = evaluate_data_freshness(_request("missing"), "2026-07-16T05:59:30Z", FreshnessPolicyRegistry((_policy(),)))
    assert band is FreshnessBand.UNKNOWN
    assert decision.status is GovernanceDecisionStatus.BLOCKED


@pytest.mark.parametrize(
    "published,band,status,reason",
    (
        ("2026-07-16T05:59:30Z", FreshnessBand.FRESH, GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW, None),
        ("2026-07-16T05:58:00Z", FreshnessBand.AGING, GovernanceDecisionStatus.DEGRADED, "source-aging"),
        ("2026-07-16T05:50:00Z", FreshnessBand.STALE, GovernanceDecisionStatus.BLOCKED, "source-stale"),
        ("2026-07-16T06:00:01Z", FreshnessBand.FUTURE_DATED, GovernanceDecisionStatus.BLOCKED, "source-future-dated"),
    ),
)
def test_d3_as_of_evaluation_is_deterministic(published, band, status, reason):
    actual_band, decision = evaluate_data_freshness(_request(), published, FreshnessPolicyRegistry((_policy(),)))
    assert actual_band is band
    assert decision.status is status
    if reason:
        assert reason in decision.blocking_reasons + decision.degradation_reasons


def test_d3_stale_degrade_policy_remains_operator_reviewable():
    policy = _policy(stale_action=StaleAction.DEGRADE)
    band, decision = evaluate_data_freshness(_request(), "2026-07-16T05:00:00Z", FreshnessPolicyRegistry((policy,)))
    assert band is FreshnessBand.STALE
    assert decision.status is GovernanceDecisionStatus.DEGRADED
    assert decision.automatic_activation_allowed is False


def test_d3_rejects_non_utc_timestamp_and_wrong_types():
    registry = FreshnessPolicyRegistry((_policy(),))
    with pytest.raises(ValueError, match="must be UTC"):
        evaluate_data_freshness(_request(), "2026-07-16T14:00:00+08:00", registry)
    with pytest.raises(TypeError, match="GovernanceRequest"):
        evaluate_data_freshness({}, "2026-07-16T06:00:00Z", registry)
