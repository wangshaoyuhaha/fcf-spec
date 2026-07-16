from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from types import MappingProxyType
from typing import Any

from .contracts import (
    AdapterRecordFinding,
    AdapterStatus,
    FindingStatus,
    MarketAdapterId,
    MarketAdapterOutcome,
    MarketAdapterRequest,
    MarketAdapterReviewPacket,
    thaw,
)


RecordValidator = Callable[
    [Mapping[str, Any], Mapping[str, Any], str],
    tuple[list[str], list[str], dict[str, Any]],
]


@dataclass(frozen=True)
class MarketAdapterDefinition:
    adapter_id: MarketAdapterId
    market_family: str
    required_rules: tuple[str, ...]
    required_record_fields: tuple[str, ...]


def _decimal(value: Any, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc
    if not number.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return number


def _utc_datetime(value: Any, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field_name} must be UTC")
    return parsed


def _allowed(value: Any, allowed_values: Any) -> bool:
    return str(value) in {str(item) for item in allowed_values}


def _a_share(
    record: Mapping[str, Any], rules: Mapping[str, Any], _: str
) -> tuple[list[str], list[str], dict[str, Any]]:
    blocked: list[str] = []
    review: list[str] = []
    derived: dict[str, Any] = {}
    if not _allowed(record["session"], rules["allowed_sessions"]):
        blocked.append("session-not-allowed")
    if record["suspended"] is True:
        blocked.append("security-suspended")
    if record["special_treatment"] is True:
        review.append("special-treatment-review")
    board = str(record["board"])
    limits = rules["price_limit_pct_by_board"]
    if board not in limits:
        blocked.append("board-rule-missing")
        return blocked, review, derived
    limit = _decimal(
        rules["special_treatment_price_limit_pct"]
        if record["special_treatment"] is True
        else limits[board],
        "price_limit_pct",
    )
    previous_close = _decimal(record["previous_close"], "previous_close")
    last_price = _decimal(record["last_price"], "last_price")
    if previous_close <= 0 or last_price <= 0 or limit < 0:
        blocked.append("invalid-price-input")
    else:
        upper = previous_close * (Decimal("1") + limit)
        lower = previous_close * (Decimal("1") - limit)
        derived.update(
            {
                "configured_price_limit_pct": float(limit),
                "configured_settlement_cycle": str(rules["settlement_cycle"]),
                "lower_price_limit": float(lower),
                "upper_price_limit": float(upper),
            }
        )
        if last_price < lower or last_price > upper:
            blocked.append("price-outside-configured-limit")
    return blocked, review, derived


def _us_equity(
    record: Mapping[str, Any], rules: Mapping[str, Any], _: str
) -> tuple[list[str], list[str], dict[str, Any]]:
    blocked: list[str] = []
    review: list[str] = []
    if not _allowed(record["session"], rules["allowed_sessions"]):
        blocked.append("session-not-allowed")
    if str(record["filing_status"]).upper() != "CURRENT":
        review.append("filing-status-review")
    if str(record["corporate_action_status"]).upper() not in {"CLEAR", "NONE"}:
        review.append("corporate-action-review")
    if _decimal(record["last_price"], "last_price") <= 0:
        blocked.append("invalid-price-input")
    return blocked, review, {
        "configured_currency_context": str(rules["currency_context_id"]),
        "configured_rate_context": str(rules["rate_context_id"]),
        "configured_settlement": str(rules["settlement_policy_id"]),
        "session_class": str(record["session"]),
    }


def _hong_kong(
    record: Mapping[str, Any], rules: Mapping[str, Any], _: str
) -> tuple[list[str], list[str], dict[str, Any]]:
    blocked: list[str] = []
    review: list[str] = []
    if not _allowed(record["session"], rules["allowed_sessions"]):
        blocked.append("session-not-allowed")
    quantity = _decimal(record["quantity"], "quantity")
    board_lot = _decimal(record["board_lot"], "board_lot")
    if quantity < 0 or board_lot <= 0:
        blocked.append("invalid-lot-input")
        odd_lot = False
    else:
        odd_lot = quantity % board_lot != 0
        if odd_lot:
            review.append("odd-lot-review")
    if str(record["currency"]).upper() != "HKD":
        review.append("counter-currency-review")
    return blocked, review, {
        "board_lot": float(board_lot),
        "odd_lot": odd_lot,
        "short_sale_eligible": bool(record["short_sale_eligible"]),
        "stock_connect_eligible": bool(record["stock_connect_eligible"]),
    }


def _gold(
    record: Mapping[str, Any], rules: Mapping[str, Any], _: str
) -> tuple[list[str], list[str], dict[str, Any]]:
    blocked: list[str] = []
    review: list[str] = []
    family = str(record["instrument_family"])
    if not _allowed(family, rules["allowed_instrument_families"]):
        blocked.append("instrument-family-not-allowed")
    if not _allowed(record["session"], rules["allowed_sessions"]):
        blocked.append("session-not-allowed")
    if _decimal(record["last_price"], "last_price") <= 0:
        blocked.append("invalid-price-input")
    expiry = record["expiry_utc"]
    if family == "gold-futures" and not expiry:
        blocked.append("futures-expiry-required")
    if family == "gold-mining-equity" and str(
        record["corporate_action_status"]
    ).upper() not in {"CLEAR", "NONE"}:
        review.append("corporate-action-review")
    return blocked, review, {
        "benchmark_id": str(rules["benchmark_id"]),
        "currency": str(record["currency"]),
        "expiry_utc": expiry,
        "instrument_family": family,
    }


def _digital_asset(
    record: Mapping[str, Any], rules: Mapping[str, Any], _: str
) -> tuple[list[str], list[str], dict[str, Any]]:
    blocked: list[str] = []
    review: list[str] = []
    if str(record["session"]) != str(rules["continuous_session_value"]):
        blocked.append("continuous-session-required")
    mark_price = _decimal(record["mark_price"], "mark_price")
    open_interest = _decimal(record["open_interest"], "open_interest")
    liquidation = _decimal(record["liquidation_notional"], "liquidation_notional")
    if mark_price <= 0 or open_interest < 0 or liquidation < 0:
        blocked.append("invalid-market-metric")
    if str(record["custody_risk"]).upper() not in {"LOW", "NONE"}:
        review.append("custody-risk-review")
    if str(record["counterparty_risk"]).upper() not in {"LOW", "NONE"}:
        review.append("counterparty-risk-review")
    return blocked, review, {
        "funding_rate": float(_decimal(record["funding_rate"], "funding_rate")),
        "liquidation_notional": float(liquidation),
        "mark_price": float(mark_price),
        "open_interest": float(open_interest),
        "venue": str(record["venue"]),
    }


def _futures(
    record: Mapping[str, Any], rules: Mapping[str, Any], as_of_utc: str
) -> tuple[list[str], list[str], dict[str, Any]]:
    blocked: list[str] = []
    review: list[str] = []
    if not _allowed(record["session"], rules["allowed_sessions"]):
        blocked.append("session-not-allowed")
    expiry = _utc_datetime(record["expiry_utc"], "expiry_utc")
    as_of = _utc_datetime(as_of_utc, "as_of_utc")
    seconds = (expiry - as_of).total_seconds()
    days_to_expiry = seconds / 86400
    if seconds <= 0:
        blocked.append("contract-expired")
    elif days_to_expiry <= float(_decimal(rules["roll_review_days"], "roll_review_days")):
        review.append("roll-window-review")
    margin_rate = _decimal(record["margin_rate"], "margin_rate")
    if margin_rate <= 0:
        blocked.append("invalid-margin-rate")
    if _decimal(record["last_price"], "last_price") <= 0:
        blocked.append("invalid-price-input")
    return blocked, review, {
        "basis": float(_decimal(record["basis"], "basis")),
        "contract_code": str(record["contract_code"]),
        "days_to_expiry": days_to_expiry,
        "exchange": str(record["exchange"]),
        "margin_rate": float(margin_rate),
        "settlement_method": str(record["settlement_method"]),
        "term_structure": str(record["term_structure"]),
    }


_COMMON_FIELDS = ("symbol", "market_adapter_id")


def _definition(
    adapter_id: MarketAdapterId,
    family: str,
    rules: tuple[str, ...],
    fields: tuple[str, ...],
) -> MarketAdapterDefinition:
    return MarketAdapterDefinition(adapter_id, family, rules, _COMMON_FIELDS + fields)


MARKET_ADAPTER_DEFINITIONS = MappingProxyType(
    {
        MarketAdapterId.CHINA_A_SHARE: _definition(
            MarketAdapterId.CHINA_A_SHARE,
            "china-a-share",
            (
                "allowed_sessions", "calendar_id", "corporate_action_policy_id",
                "fee_schedule_id", "flow_source_policy_id", "liquidity_policy_id",
                "price_limit_pct_by_board", "risk_policy_id", "settlement_cycle",
                "special_treatment_price_limit_pct",
            ),
            ("session", "suspended", "special_treatment", "board", "last_price", "previous_close"),
        ),
        MarketAdapterId.US_EQUITY: _definition(
            MarketAdapterId.US_EQUITY,
            "us-equity",
            (
                "allowed_sessions", "calendar_id", "corporate_action_policy_id",
                "currency_context_id", "fee_schedule_id", "filing_policy_id",
                "institutional_data_policy_id", "liquidity_policy_id",
                "options_data_policy_id", "rate_context_id", "risk_policy_id",
                "settlement_policy_id",
            ),
            ("session", "filing_status", "corporate_action_status", "currency", "last_price"),
        ),
        MarketAdapterId.HONG_KONG_EQUITY: _definition(
            MarketAdapterId.HONG_KONG_EQUITY,
            "hong-kong-equity",
            (
                "allowed_sessions", "auction_policy_id", "board_lot_policy_id",
                "calendar_id", "corporate_action_policy_id", "fee_schedule_id",
                "flow_source_policy_id", "hkd_counter_policy_id", "liquidity_policy_id",
                "odd_lot_policy_id", "risk_policy_id", "settlement_policy_id",
                "short_sale_policy_id", "stock_connect_policy_id", "tax_policy_id",
            ),
            ("session", "quantity", "board_lot", "currency", "stock_connect_eligible", "short_sale_eligible"),
        ),
        MarketAdapterId.GOLD_COMMODITY: _definition(
            MarketAdapterId.GOLD_COMMODITY,
            "gold-commodity",
            (
                "allowed_instrument_families", "allowed_sessions", "benchmark_id",
                "corporate_action_policy_id", "currency_policy_id", "expiry_policy_id",
                "fee_schedule_id", "liquidity_policy_id", "risk_policy_id",
                "roll_policy_id", "settlement_policy_id",
            ),
            ("instrument_family", "session", "currency", "last_price", "expiry_utc", "corporate_action_status"),
        ),
        MarketAdapterId.DIGITAL_ASSET: _definition(
            MarketAdapterId.DIGITAL_ASSET,
            "digital-asset",
            (
                "continuous_session_value", "counterparty_risk_policy_id",
                "custody_risk_policy_id", "exchange_flow_policy_id", "fee_schedule_id",
                "funding_policy_id", "liquidation_policy_id", "mark_price_policy_id",
                "on_chain_policy_id", "open_interest_policy_id", "risk_policy_id",
                "settlement_policy_id", "venue_fragmentation_policy_id",
            ),
            ("session", "funding_rate", "mark_price", "open_interest", "liquidation_notional", "venue", "custody_risk", "counterparty_risk"),
        ),
        MarketAdapterId.FUTURES: _definition(
            MarketAdapterId.FUTURES,
            "futures",
            (
                "allowed_sessions", "basis_policy_id", "calendar_id", "contract_policy_id",
                "dominant_contract_policy_id", "exchange_policy_id", "expiry_policy_id",
                "fee_schedule_id", "liquidity_policy_id", "margin_policy_id",
                "risk_policy_id", "roll_policy_id", "roll_review_days",
                "settlement_policy_id", "term_structure_policy_id",
            ),
            ("contract_code", "session", "expiry_utc", "margin_rate", "basis", "term_structure", "settlement_method", "exchange", "last_price"),
        ),
    }
)


_VALIDATORS: Mapping[MarketAdapterId, RecordValidator] = MappingProxyType(
    {
        MarketAdapterId.CHINA_A_SHARE: _a_share,
        MarketAdapterId.US_EQUITY: _us_equity,
        MarketAdapterId.HONG_KONG_EQUITY: _hong_kong,
        MarketAdapterId.GOLD_COMMODITY: _gold,
        MarketAdapterId.DIGITAL_ASSET: _digital_asset,
        MarketAdapterId.FUTURES: _futures,
    }
)


class MultiMarketAdapterService:
    def definitions(self) -> Mapping[MarketAdapterId, MarketAdapterDefinition]:
        return MARKET_ADAPTER_DEFINITIONS

    def evaluate(self, request: MarketAdapterRequest) -> MarketAdapterOutcome:
        if not isinstance(request, MarketAdapterRequest):
            raise TypeError("request must be a MarketAdapterRequest")
        definition = MARKET_ADAPTER_DEFINITIONS[request.adapter_id]
        profile = request.profile
        artifact = request.artifact
        blocking_reasons: list[str] = []
        review_reasons: list[str] = []
        missing_rules = sorted(set(definition.required_rules) - set(profile.rules))
        if missing_rules:
            blocking_reasons.extend(f"missing-rule-{item}" for item in missing_rules)
        if artifact.evidence_id not in profile.evidence_ids:
            blocking_reasons.append("artifact-evidence-not-approved")
        if artifact.freshness_status not in {"CURRENT", "FRESH"}:
            review_reasons.append("artifact-freshness-review")
        findings: list[AdapterRecordFinding] = []
        if not missing_rules:
            validator = _VALIDATORS[request.adapter_id]
            for index, record in enumerate(artifact.records):
                missing_fields = sorted(
                    set(definition.required_record_fields) - set(record)
                )
                symbol = str(record.get("symbol", f"record-{index}"))
                blocked = [f"missing-field-{item}" for item in missing_fields]
                review: list[str] = []
                derived: dict[str, Any] = {}
                if not missing_fields:
                    if str(record["market_adapter_id"]) != request.adapter_id.value:
                        blocked.append("record-adapter-linkage-mismatch")
                    else:
                        try:
                            local_blocked, review, derived = validator(
                                record, profile.rules, request.as_of_utc
                            )
                            blocked.extend(local_blocked)
                        except (TypeError, ValueError, KeyError):
                            blocked.append("record-value-invalid")
                if blocked:
                    finding_status = FindingStatus.BLOCKED
                    reasons = blocked + review
                elif review:
                    finding_status = FindingStatus.REVIEW
                    reasons = review
                else:
                    finding_status = FindingStatus.PASS
                    reasons = []
                findings.append(
                    AdapterRecordFinding(
                        record_index=index,
                        symbol=symbol,
                        status=finding_status,
                        reason_codes=tuple(reasons),
                        derived_values=derived,
                    )
                )
        if blocking_reasons or not artifact.records or any(
            item.status is FindingStatus.BLOCKED for item in findings
        ):
            status = AdapterStatus.BLOCKED
        elif review_reasons or any(
            item.status is FindingStatus.REVIEW for item in findings
        ):
            status = AdapterStatus.DEGRADED
        else:
            status = AdapterStatus.READY_FOR_OPERATOR_REVIEW
        return MarketAdapterOutcome(
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            adapter_id=request.adapter_id,
            profile_id=profile.profile_id,
            profile_version=profile.version,
            evidence_id=artifact.evidence_id,
            artifact_sha256=artifact.artifact_sha256,
            normalized_records_sha256=artifact.normalized_records_sha256,
            status=status,
            findings=tuple(findings),
            reason_codes=tuple(blocking_reasons + review_reasons),
            original_records=artifact.records,
        )

    def build_review_packet(
        self, outcome: MarketAdapterOutcome
    ) -> MarketAdapterReviewPacket:
        if not isinstance(outcome, MarketAdapterOutcome):
            raise TypeError("outcome must be a MarketAdapterOutcome")
        return MarketAdapterReviewPacket(
            MappingProxyType(
                {
                    "adapter_id": outcome.adapter_id.value,
                    "artifact_sha256": outcome.artifact_sha256,
                    "automatic_activation_allowed": False,
                    "correlation_id": outcome.correlation_id,
                    "evidence_id": outcome.evidence_id,
                    "findings": tuple(
                        {
                            "derived_values": thaw(item.derived_values),
                            "reason_codes": item.reason_codes,
                            "record_index": item.record_index,
                            "status": item.status.value,
                            "symbol": item.symbol,
                        }
                        for item in outcome.findings
                    ),
                    "normalized_records_sha256": outcome.normalized_records_sha256,
                    "operator_review_required": True,
                    "original_records": tuple(
                        thaw(item) for item in outcome.original_records
                    ),
                    "profile_id": outcome.profile_id,
                    "profile_version": outcome.profile_version,
                    "reason_codes": outcome.reason_codes,
                    "request_id": outcome.request_id,
                    "status": outcome.status.value,
                }
            )
        )
