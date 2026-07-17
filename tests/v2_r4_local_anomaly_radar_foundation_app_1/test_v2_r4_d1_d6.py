from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from apps.v2_r2_historical_factor_baseline_app_1 import (
    BaselineRequest,
    DataRightsDeclaration,
    HistoricalObservation,
    HistoricalObservationRegistry,
    build_historical_baseline,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import (
    LocalEventEnvelope,
    LocalEventRights,
)
from apps.v2_r4_local_anomaly_radar_foundation_app_1 import (
    V2_R4_LOCAL_ANOMALY_RADAR_BOUNDARY,
    AnomalyRule,
    ResearchAlertLedger,
    build_operator_acceptance,
    build_read_model,
    evaluate_anomaly_window,
)


def _baseline():
    rights = DataRightsDeclaration(
        license_id="operator-local-license-v1",
        permitted_use="local-paper-research",
        retention_days=30,
    )
    registry = HistoricalObservationRegistry()
    for index, value in enumerate((0, 1, 2, 3, 4), start=1):
        registry = registry.register(
            HistoricalObservation(
                observation_id=f"historical-price-{index}",
                instrument_id="registered-instrument",
                field_id="price",
                event_at_utc=f"2026-01-0{index}T00:00:00Z",
                available_at_utc=f"2026-01-0{index}T00:00:01Z",
                value=Decimal(value),
                quality_status="verified",
                source_id="operator-local-source",
                registered_artifact_id="registered-history-v1",
                timezone_id="UTC",
                calendar_id="registered-calendar-v1",
                adjustment_policy="none",
                missing_policy="abstain",
                duplicate_policy="reject",
                suspension_policy="preserve-missing",
                rights=rights,
            )
        )
    return build_historical_baseline(
        registry,
        BaselineRequest(
            request_id="price-baseline-request",
            instrument_id="registered-instrument",
            field_id="price",
            as_of_utc="2026-01-06T00:00:00Z",
            window_size=5,
            minimum_history=5,
        ),
    )


def _event(
    sequence: int,
    value: object,
    *,
    clock_quality: str = "SYNCED",
    negative: object | None = None,
) -> LocalEventEnvelope:
    payload = {"price": value}
    if negative is not None:
        payload["risk_flag"] = negative
    return LocalEventEnvelope(
        event_id=f"registered-anomaly-event-{sequence}",
        stream_id="registered-instrument-stream",
        source_id="operator-local-source",
        registered_artifact_id="registered-events-v1",
        event_type="field-observation",
        source_sequence=sequence,
        event_at_utc=f"2026-01-06T00:0{sequence - 1}:00Z",
        received_at_utc=f"2026-01-06T00:0{sequence - 1}:01Z",
        processed_at_utc=f"2026-01-06T00:0{sequence - 1}:02Z",
        payload=payload,
        rights=LocalEventRights(
            license_id="operator-local-license-v1",
            permitted_use="local-paper-research",
            retention_days=30,
        ),
        clock_quality=clock_quality,
    )


def _rule(baseline, **overrides: object) -> AnomalyRule:
    values = {
        "rule_id": "registered-price-anomaly-rule",
        "rule_version": "v1",
        "context_id": "registered-local-replay-context",
        "field_key": "price",
        "direction": "UP",
        "minimum_abs_z": Decimal("2"),
        "minimum_abs_velocity": Decimal("0.01"),
        "minimum_persistence": 2,
        "max_event_age_seconds": 300,
        "cooldown_seconds": 300,
        "evidence_ttl_seconds": 120,
        "baseline_replay_hash": baseline.replay_hash,
        "negative_evidence_keys": ("risk_flag",),
    }
    values.update(overrides)
    return AnomalyRule(**values)


def test_d1_boundary_and_rule_prohibit_live_or_global_behavior() -> None:
    boundary = V2_R4_LOCAL_ANOMALY_RADAR_BOUNDARY

    assert boundary.local_only is True
    assert boundary.operator_review_required is True
    assert boundary.live_source_allowed is False
    assert boundary.universe_scan_allowed is False
    assert boundary.official_scoring_allowed is False
    assert boundary.candidate_ranking_allowed is False
    assert boundary.recommendation_allowed is False
    assert boundary.order_path_allowed is False
    with pytest.raises(ValueError, match="global thresholds"):
        _rule(_baseline(), permanent_global_threshold=True)
    with pytest.raises(ValueError, match="no prediction target"):
        _rule(_baseline(), target_label="future-return")


def test_d2_rule_and_evidence_are_immutable() -> None:
    baseline = _baseline()
    rule = _rule(baseline)
    evidence = evaluate_anomaly_window(
        (_event(1, Decimal("6")),),
        baseline,
        rule,
        as_of_utc="2026-01-06T00:01:00Z",
    )

    with pytest.raises(FrozenInstanceError):
        rule.direction = "DOWN"
    with pytest.raises(FrozenInstanceError):
        evidence.state = "NORMAL"


def test_d3_confirmed_requires_z_velocity_and_persistence() -> None:
    baseline = _baseline()
    rule = _rule(baseline)
    events = (_event(1, Decimal("6")), _event(2, Decimal("8")))

    evidence = evaluate_anomaly_window(
        events,
        baseline,
        rule,
        as_of_utc="2026-01-06T00:02:00Z",
    )
    repeated = evaluate_anomaly_window(
        events,
        baseline,
        rule,
        as_of_utc="2026-01-06T00:02:00Z",
    )

    assert evidence.state == "CONFIRMED"
    assert evidence.persistence_count == 2
    assert evidence.velocity_per_second > Decimal("0.03")
    assert evidence.evidence_hash == repeated.evidence_hash


def test_d3_watch_and_normal_states_are_distinct() -> None:
    baseline = _baseline()
    rule = _rule(baseline)

    watch = evaluate_anomaly_window(
        (_event(1, Decimal("6")),),
        baseline,
        rule,
        as_of_utc="2026-01-06T00:01:00Z",
    )
    normal = evaluate_anomaly_window(
        (_event(1, Decimal("2")), _event(2, Decimal("2.1"))),
        baseline,
        rule,
        as_of_utc="2026-01-06T00:02:00Z",
    )

    assert watch.state == "WATCH"
    assert normal.state == "NORMAL"


def test_d4_negative_evidence_clock_and_baseline_mismatch_degrade() -> None:
    baseline = _baseline()
    rule = _rule(baseline)

    negative = evaluate_anomaly_window(
        (_event(1, Decimal("6")), _event(2, Decimal("8"), negative=True)),
        baseline,
        rule,
        as_of_utc="2026-01-06T00:02:00Z",
    )
    clock = evaluate_anomaly_window(
        (_event(1, Decimal("6"), clock_quality="DEGRADED"),),
        baseline,
        rule,
        as_of_utc="2026-01-06T00:01:00Z",
    )
    mismatch = evaluate_anomaly_window(
        (_event(1, Decimal("6")),),
        baseline,
        replace(rule, baseline_replay_hash="0" * 64),
        as_of_utc="2026-01-06T00:01:00Z",
    )

    assert negative.state == "DEGRADED"
    assert negative.negative_evidence == ("risk_flag",)
    assert clock.reason_codes == ("CLOCK_DEGRADED",)
    assert mismatch.reason_codes == ("BASELINE_BLOCKED",)


def test_d4_invalid_window_and_payload_fail_closed() -> None:
    baseline = _baseline()
    rule = _rule(baseline)

    with pytest.raises(ValueError, match="contiguous"):
        evaluate_anomaly_window(
            (_event(1, Decimal("6")), _event(3, Decimal("8"))),
            baseline,
            rule,
            as_of_utc="2026-01-06T00:03:00Z",
        )
    with pytest.raises(ValueError, match="integer or Decimal"):
        evaluate_anomaly_window(
            (_event(1, "not-numeric"),),
            baseline,
            rule,
            as_of_utc="2026-01-06T00:01:00Z",
        )


def test_d5_ledger_rejects_duplicate_and_cooldown() -> None:
    baseline = _baseline()
    rule = _rule(baseline)
    first = evaluate_anomaly_window(
        (_event(1, Decimal("6")), _event(2, Decimal("8"))),
        baseline,
        rule,
        as_of_utc="2026-01-06T00:02:00Z",
    )
    ledger = ResearchAlertLedger().register(first, rule)

    with pytest.raises(ValueError, match="duplicate"):
        ledger.register(first, rule)
    second = evaluate_anomaly_window(
        (_event(2, Decimal("8")), _event(3, Decimal("10"))),
        baseline,
        rule,
        as_of_utc="2026-01-06T00:03:00Z",
    )
    with pytest.raises(ValueError, match="cooldown"):
        ledger.register(second, rule)


def test_d5_active_ledger_excludes_expired_evidence() -> None:
    baseline = _baseline()
    rule = _rule(baseline)
    evidence = evaluate_anomaly_window(
        (_event(1, Decimal("6")),),
        baseline,
        rule,
        as_of_utc="2026-01-06T00:01:00Z",
    )
    ledger = ResearchAlertLedger().register(evidence, rule)

    assert len(ledger.active(as_of_utc="2026-01-06T00:01:30Z")) == 1
    assert ledger.active(as_of_utc="2026-01-06T00:03:00Z") == ()


def test_d6_read_model_and_operator_acceptance_remain_read_only() -> None:
    baseline = _baseline()
    rule = _rule(baseline)
    evidence = evaluate_anomaly_window(
        (_event(1, Decimal("6")), _event(2, Decimal("8"))),
        baseline,
        rule,
        as_of_utc="2026-01-06T00:02:00Z",
    )
    ledger = ResearchAlertLedger().register(evidence, rule)
    model = build_read_model(ledger)
    acceptance = build_operator_acceptance(ledger)

    assert model.payload["read_only"] is True
    assert model.payload["official_scoring_allowed"] is False
    assert model.payload["recommendation_allowed"] is False
    assert model.payload["order_path_allowed"] is False
    assert acceptance.status == "READY_FOR_OPERATOR_REVIEW"
    assert acceptance.confirmed_count == 1
    assert acceptance.automatic_approval_allowed is False
    with pytest.raises(TypeError):
        model.payload["record_count"] = 0
