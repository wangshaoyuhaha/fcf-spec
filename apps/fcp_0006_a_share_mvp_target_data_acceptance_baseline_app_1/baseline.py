from __future__ import annotations

from .contracts import (
    DATA_DOMAINS,
    OBLIGATION_CATEGORIES,
    TARGET_FAMILIES,
    AShareMvpBaselineRegistry,
    AShareMvpBaselineResult,
    AShareTargetContract,
    AcceptanceEvidenceObligation,
    PointInTimeDataRequirement,
    digest,
)


CANONICAL_DATA_FIELDS = (
    ("adjustment-factor", "CORPORATE_ACTION", "split-dividend-adjustment-v1", False),
    ("available-at", "MARKET_CALENDAR", "source-availability-time-v1", True),
    ("best-ask-price", "QUOTE_L1", "best-visible-ask-v1", True),
    ("best-ask-size", "QUOTE_L1", "best-visible-ask-size-v1", True),
    ("best-bid-price", "QUOTE_L1", "best-visible-bid-v1", True),
    ("best-bid-size", "QUOTE_L1", "best-visible-bid-size-v1", True),
    ("close", "OHLCV", "session-adjusted-close-v1", True),
    ("event-time", "MARKET_CALENDAR", "exchange-event-time-v1", True),
    ("exchange-id", "INSTRUMENT_MASTER", "registered-venue-identity-v1", False),
    ("halt-state", "PRICE_LIMIT_AND_HALT", "venue-halt-state-v1", True),
    ("high", "OHLCV", "session-high-v1", True),
    ("instrument-id", "INSTRUMENT_MASTER", "point-in-time-instrument-id-v1", False),
    ("limit-down-price", "PRICE_LIMIT_AND_HALT", "venue-limit-down-v1", True),
    ("limit-up-price", "PRICE_LIMIT_AND_HALT", "venue-limit-up-v1", True),
    ("low", "OHLCV", "session-low-v1", True),
    ("notional", "OHLCV", "traded-notional-v1", True),
    ("open", "OHLCV", "session-open-v1", True),
    ("sector-id", "SECTOR_CLASSIFICATION", "point-in-time-sector-id-v1", False),
    ("session-calendar-version", "MARKET_CALENDAR", "calendar-version-v1", True),
    ("session-id", "MARKET_CALENDAR", "registered-session-id-v1", True),
    ("trade-price", "TRADE_PRINT", "observable-trade-price-v1", True),
    ("trade-size", "TRADE_PRINT", "observable-trade-size-v1", True),
    ("trading-date", "MARKET_CALENDAR", "exchange-trading-date-v1", True),
    ("universe-effective-at", "UNIVERSE_SNAPSHOT", "universe-availability-v1", False),
    ("volume", "OHLCV", "traded-volume-v1", True),
)

CANONICAL_OBLIGATIONS = (
    ("cost-model", "COST_MODEL", "fees-slippage-impact-latency-v1"),
    ("failure-threshold", "FAILURE_THRESHOLD", "drawdown-error-instability-v1"),
    ("leakage-control", "LEAKAGE_CONTROL", "purged-walk-forward-pit-audit-v1"),
    ("replay-protocol", "REPLAY_PROTOCOL", "session-aware-label-maturity-replay-v1"),
    ("stop-rule", "STOP_RULE", "rights-cost-drift-evidence-expiry-stop-v1"),
    ("success-threshold", "SUCCESS_THRESHOLD", "net-excess-calibration-stability-v1"),
)


def build_canonical_a_share_mvp_baseline() -> AShareMvpBaselineRegistry:
    targets = (
        AShareTargetContract(
            target_id="a-share-five-session-excess-return-v1",
            target_family="FIVE_SESSION_EXCESS_RETURN",
            horizon_id="five-trading-sessions",
            benchmark_id="registered-a-share-broad-market-benchmark-v1",
            universe_policy_id="point-in-time-eligible-a-share-universe-v1",
            label_maturity_id="after-five-session-close-v1",
        ),
        AShareTargetContract(
            target_id="a-share-late-session-next-open-excess-return-v1",
            target_family="LATE_SESSION_TO_NEXT_OPEN_EXCESS_RETURN",
            horizon_id="late-session-to-next-open",
            benchmark_id="registered-a-share-broad-market-benchmark-v1",
            universe_policy_id="point-in-time-eligible-a-share-universe-v1",
            label_maturity_id="after-next-session-open-v1",
        ),
        AShareTargetContract(
            target_id="a-share-next-session-excess-return-v1",
            target_family="NEXT_SESSION_EXCESS_RETURN",
            horizon_id="next-trading-session",
            benchmark_id="registered-a-share-broad-market-benchmark-v1",
            universe_policy_id="point-in-time-eligible-a-share-universe-v1",
            label_maturity_id="after-next-session-close-v1",
        ),
    )
    requirements = tuple(
        PointInTimeDataRequirement(
            field_id=field_id,
            domain=domain,
            source_semantics_id=semantics,
            market_session_version_required=session_required,
        )
        for field_id, domain, semantics, session_required in CANONICAL_DATA_FIELDS
    )
    obligations = tuple(
        AcceptanceEvidenceObligation(
            obligation_id=obligation_id,
            category=category,
            metric_id=metric_id,
        )
        for obligation_id, category, metric_id in CANONICAL_OBLIGATIONS
    )
    return AShareMvpBaselineRegistry(targets, requirements, obligations)


def evaluate_a_share_mvp_baseline(
    registry: AShareMvpBaselineRegistry,
) -> AShareMvpBaselineResult:
    target_families = {item.target_family for item in registry.targets}
    data_domains = {
        item.domain
        for item in registry.data_requirements
        if item.requirement_level == "REQUIRED"
    }
    obligation_categories = {item.category for item in registry.obligations}
    missing_target_families = tuple(sorted(set(TARGET_FAMILIES) - target_families))
    missing_data_domains = tuple(sorted(set(DATA_DOMAINS) - data_domains))
    missing_obligation_categories = tuple(
        sorted(set(OBLIGATION_CATEGORIES) - obligation_categories)
    )
    evidence_required_ids = tuple(
        item.obligation_id
        for item in registry.obligations
        if item.evidence_state == "EVIDENCE_REQUIRED"
    )
    registered_ids = tuple(
        item.obligation_id
        for item in registry.obligations
        if item.evidence_state == "REGISTERED"
    )
    if missing_target_families or missing_data_domains or missing_obligation_categories:
        state = "BASELINE_INCOMPLETE"
    elif evidence_required_ids:
        state = "READY_FOR_EVIDENCE_COLLECTION"
    else:
        state = "READY_FOR_OPERATOR_EVIDENCE_REGISTRATION"
    payload = {
        "evidence_required_obligation_ids": evidence_required_ids,
        "fcp_0005_readiness_claimed": False,
        "missing_data_domains": missing_data_domains,
        "missing_obligation_categories": missing_obligation_categories,
        "missing_target_families": missing_target_families,
        "product_phase_authorized": False,
        "production_gap_closure_claimed": False,
        "registered_evidence_obligation_ids": registered_ids,
        "registry_hash": registry.registry_hash,
        "research_priority_market_id": registry.research_priority_market_id,
        "selected_market_id": None,
        "state": state,
    }
    return AShareMvpBaselineResult(result_hash=digest(payload), **payload)
