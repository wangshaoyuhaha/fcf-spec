from __future__ import annotations

from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.multi_market_adapters_stage_6 import (
    AdapterStatus,
    FindingStatus,
    MARKET_ADAPTER_DEFINITIONS,
    MULTI_MARKET_ADAPTER_BOUNDARY,
    MarketAdapterId,
    MarketAdapterRequest,
    MarketRuleProfile,
    MultiMarketAdapterService,
    build_stage6_acceptance,
)
from apps.read_only_data_gateway_app_1 import (
    ArtifactFormat,
    NormalizedArtifactEnvelope,
)


NOW = "2026-07-16T00:00:00+00:00"
EVIDENCE_ID = "market-evidence-a"


def _rules(adapter_id: MarketAdapterId) -> dict[str, object]:
    required = MARKET_ADAPTER_DEFINITIONS[adapter_id].required_rules
    rules: dict[str, object] = {item: "policy-v1" for item in required}
    if "allowed_sessions" in rules:
        rules["allowed_sessions"] = (
            "REGULAR",
            "PRE_MARKET",
            "AFTER_HOURS",
            "AUCTION",
            "DAY",
            "NIGHT",
        )
    if adapter_id is MarketAdapterId.CHINA_A_SHARE:
        rules.update(
            {
                "price_limit_pct_by_board": {"MAIN": 0.10, "STAR": 0.20},
                "settlement_cycle": "T+1",
                "special_treatment_price_limit_pct": 0.05,
            }
        )
    elif adapter_id is MarketAdapterId.GOLD_COMMODITY:
        rules["allowed_instrument_families"] = (
            "spot-gold",
            "gold-futures",
            "gold-etf",
            "gold-mining-equity",
        )
    elif adapter_id is MarketAdapterId.DIGITAL_ASSET:
        rules["continuous_session_value"] = "CONTINUOUS"
    elif adapter_id is MarketAdapterId.FUTURES:
        rules["roll_review_days"] = 10
    return rules


def _record(adapter_id: MarketAdapterId) -> dict[str, object]:
    common: dict[str, object] = {
        "market_adapter_id": adapter_id.value,
        "symbol": "SAMPLE",
    }
    if adapter_id is MarketAdapterId.CHINA_A_SHARE:
        common.update(
            {
                "board": "MAIN",
                "last_price": 10.5,
                "previous_close": 10.0,
                "session": "REGULAR",
                "special_treatment": False,
                "suspended": False,
            }
        )
    elif adapter_id is MarketAdapterId.US_EQUITY:
        common.update(
            {
                "corporate_action_status": "CLEAR",
                "currency": "USD",
                "filing_status": "CURRENT",
                "last_price": 200.0,
                "session": "PRE_MARKET",
            }
        )
    elif adapter_id is MarketAdapterId.HONG_KONG_EQUITY:
        common.update(
            {
                "board_lot": 100,
                "currency": "HKD",
                "quantity": 200,
                "session": "REGULAR",
                "short_sale_eligible": True,
                "stock_connect_eligible": True,
            }
        )
    elif adapter_id is MarketAdapterId.GOLD_COMMODITY:
        common.update(
            {
                "corporate_action_status": "NONE",
                "currency": "USD",
                "expiry_utc": None,
                "instrument_family": "spot-gold",
                "last_price": 2400.0,
                "session": "REGULAR",
            }
        )
    elif adapter_id is MarketAdapterId.DIGITAL_ASSET:
        common.update(
            {
                "counterparty_risk": "LOW",
                "custody_risk": "LOW",
                "funding_rate": 0.0001,
                "liquidation_notional": 1000.0,
                "mark_price": 65000.0,
                "open_interest": 5000000.0,
                "session": "CONTINUOUS",
                "venue": "registered-venue-a",
            }
        )
    elif adapter_id is MarketAdapterId.FUTURES:
        common.update(
            {
                "basis": 1.5,
                "contract_code": "IF2608",
                "exchange": "registered-exchange-a",
                "expiry_utc": "2026-08-20T00:00:00+00:00",
                "last_price": 4000.0,
                "margin_rate": 0.12,
                "session": "DAY",
                "settlement_method": "CASH",
                "term_structure": "CONTANGO",
            }
        )
    return common


def _artifact(
    adapter_id: MarketAdapterId,
    record: dict[str, object] | None = None,
    freshness: str = "CURRENT",
    evidence_id: str = EVIDENCE_ID,
) -> NormalizedArtifactEnvelope:
    return NormalizedArtifactEnvelope(
        source_id="market-source-a",
        evidence_id=evidence_id,
        artifact_format=ArtifactFormat.JSON,
        artifact_sha256="1" * 64,
        normalized_records_sha256="2" * 64,
        records=(MappingProxyType(record or _record(adapter_id)),),
        source_class="MARKET_DATA",
        trust_level="HIGH",
        license_type="APPROVED",
        allowed_use="RESEARCH",
        freshness_status=freshness,
    )


def _request(
    adapter_id: MarketAdapterId,
    record: dict[str, object] | None = None,
    rules: dict[str, object] | None = None,
    freshness: str = "CURRENT",
    evidence_id: str = EVIDENCE_ID,
) -> MarketAdapterRequest:
    profile = MarketRuleProfile(
        adapter_id=adapter_id,
        profile_id=f"profile-{adapter_id.name.lower().replace('_', '-')}",
        version="v1",
        effective_from_utc=NOW,
        evidence_ids=(EVIDENCE_ID,),
        rules=rules or _rules(adapter_id),
    )
    return MarketAdapterRequest(
        request_id=f"request-{adapter_id.name.lower().replace('_', '-')}",
        correlation_id="correlation-stage-6",
        adapter_id=adapter_id,
        as_of_utc=NOW,
        profile=profile,
        artifact=_artifact(adapter_id, record, freshness, evidence_id),
    )


def _evaluate(adapter_id: MarketAdapterId, **kwargs: object):
    return MultiMarketAdapterService().evaluate(_request(adapter_id, **kwargs))


def test_d1_boundary_rejects_network_credentials_connections_and_execution():
    prohibited = (
        "network_retrieval_allowed",
        "credential_access_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "order_path_allowed",
        "real_execution_allowed",
        "live_model_invocation_allowed",
    )
    for field_name in prohibited:
        with pytest.raises(ValueError, match="prohibited multi-market"):
            replace(MULTI_MARKET_ADAPTER_BOUNDARY, **{field_name: True})


def test_d1_a_share_uses_versioned_limits_and_t_plus_rule():
    outcome = _evaluate(MarketAdapterId.CHINA_A_SHARE)
    finding = outcome.findings[0]
    assert outcome.status is AdapterStatus.READY_FOR_OPERATOR_REVIEW
    assert finding.derived_values["configured_settlement_cycle"] == "T+1"
    assert finding.derived_values["upper_price_limit"] == pytest.approx(11.0)


def test_d1_a_share_suspension_fails_closed():
    record = _record(MarketAdapterId.CHINA_A_SHARE)
    record["suspended"] = True
    outcome = _evaluate(MarketAdapterId.CHINA_A_SHARE, record=record)
    assert outcome.status is AdapterStatus.BLOCKED
    assert "security-suspended" in outcome.findings[0].reason_codes


def test_d2_us_equity_supports_extended_sessions_and_filing_review():
    record = _record(MarketAdapterId.US_EQUITY)
    record["filing_status"] = "PENDING"
    outcome = _evaluate(MarketAdapterId.US_EQUITY, record=record)
    assert outcome.status is AdapterStatus.DEGRADED
    assert outcome.findings[0].status is FindingStatus.REVIEW
    assert outcome.findings[0].derived_values["session_class"] == "PRE_MARKET"


def test_d3_hong_kong_marks_odd_lot_for_operator_review():
    record = _record(MarketAdapterId.HONG_KONG_EQUITY)
    record["quantity"] = 250
    outcome = _evaluate(MarketAdapterId.HONG_KONG_EQUITY, record=record)
    assert outcome.status is AdapterStatus.DEGRADED
    assert outcome.findings[0].derived_values["odd_lot"] is True


@pytest.mark.parametrize(
    "family",
    ("spot-gold", "gold-futures", "gold-etf", "gold-mining-equity"),
)
def test_d4_gold_distinguishes_required_instrument_families(family: str):
    record = _record(MarketAdapterId.GOLD_COMMODITY)
    record["instrument_family"] = family
    if family == "gold-futures":
        record["expiry_utc"] = "2026-12-01T00:00:00+00:00"
    outcome = _evaluate(MarketAdapterId.GOLD_COMMODITY, record=record)
    assert outcome.status is AdapterStatus.READY_FOR_OPERATOR_REVIEW
    assert outcome.findings[0].derived_values["instrument_family"] == family


def test_d5_digital_asset_preserves_continuous_market_metrics():
    outcome = _evaluate(MarketAdapterId.DIGITAL_ASSET)
    finding = outcome.findings[0]
    assert outcome.status is AdapterStatus.READY_FOR_OPERATOR_REVIEW
    assert finding.derived_values["mark_price"] == 65000.0
    assert finding.derived_values["open_interest"] == 5000000.0


def test_d5_digital_asset_surfaces_custody_and_counterparty_risk():
    record = _record(MarketAdapterId.DIGITAL_ASSET)
    record["custody_risk"] = "HIGH"
    record["counterparty_risk"] = "MEDIUM"
    outcome = _evaluate(MarketAdapterId.DIGITAL_ASSET, record=record)
    assert outcome.status is AdapterStatus.DEGRADED
    assert set(outcome.findings[0].reason_codes) == {
        "counterparty-risk-review",
        "custody-risk-review",
    }


def test_d6_futures_surfaces_roll_window_without_execution():
    record = _record(MarketAdapterId.FUTURES)
    record["expiry_utc"] = "2026-07-20T00:00:00+00:00"
    outcome = _evaluate(MarketAdapterId.FUTURES, record=record)
    assert outcome.status is AdapterStatus.DEGRADED
    assert "roll-window-review" in outcome.findings[0].reason_codes
    assert outcome.findings[0].derived_values["days_to_expiry"] == 4.0


def test_d6_futures_rejects_expired_contract():
    record = _record(MarketAdapterId.FUTURES)
    record["expiry_utc"] = "2026-07-01T00:00:00+00:00"
    outcome = _evaluate(MarketAdapterId.FUTURES, record=record)
    assert outcome.status is AdapterStatus.BLOCKED
    assert "contract-expired" in outcome.findings[0].reason_codes


def test_registered_evidence_mismatch_blocks_adapter():
    outcome = _evaluate(
        MarketAdapterId.US_EQUITY,
        evidence_id="unapproved-evidence",
    )
    assert outcome.status is AdapterStatus.BLOCKED
    assert "artifact-evidence-not-approved" in outcome.reason_codes


def test_missing_versioned_rule_blocks_adapter():
    rules = _rules(MarketAdapterId.HONG_KONG_EQUITY)
    del rules["tax_policy_id"]
    outcome = _evaluate(MarketAdapterId.HONG_KONG_EQUITY, rules=rules)
    assert outcome.status is AdapterStatus.BLOCKED
    assert "missing-rule-tax_policy_id" in outcome.reason_codes


def test_review_packet_preserves_original_records_and_is_immutable():
    service = MultiMarketAdapterService()
    outcome = service.evaluate(_request(MarketAdapterId.DIGITAL_ASSET))
    packet = service.build_review_packet(outcome)
    assert packet.payload["original_records"][0]["symbol"] == "SAMPLE"
    assert packet.payload["operator_review_required"] is True
    assert packet.payload["automatic_activation_allowed"] is False
    with pytest.raises(TypeError):
        packet.payload["status"] = "TAMPERED"


def test_d6_registry_and_acceptance_require_all_six_ordered_adapters():
    service = MultiMarketAdapterService()
    outcomes = tuple(service.evaluate(_request(item)) for item in MarketAdapterId)
    packets = tuple(service.build_review_packet(item) for item in outcomes)
    acceptance = build_stage6_acceptance(outcomes, packets)
    assert acceptance.status == "PASS"
    assert acceptance.adapter_ids == tuple(item.value for item in MarketAdapterId)
    assert len(MARKET_ADAPTER_DEFINITIONS) == 6


def test_d6_acceptance_rejects_incomplete_group():
    service = MultiMarketAdapterService()
    outcomes = tuple(service.evaluate(_request(item)) for item in MarketAdapterId)[:-1]
    packets = tuple(service.build_review_packet(item) for item in outcomes)
    with pytest.raises(ValueError, match="all six ordered adapters"):
        build_stage6_acceptance(outcomes, packets)
