from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import InstitutionalCalendarEvent
from apps.v2_r26_local_consensus_expectation_gap_foundation_app_1 import ExpectationGapRecord
from apps.v2_r27_local_event_reaction_quality_foundation_app_1 import EventReactionQualityRecord


EARNINGS_STAGES = ("EXPECTATION_DISCLOSURE", "IMMEDIATE_REACTION", "LOGIC_REBUILD")
ACCOUNTING_STATES = ("OBSERVED", "MISSING", "STALE", "CONFLICT")
CHALLENGE_LABELS = (
    "NONRECURRING_SHARE_HIGH",
    "CASH_PROFIT_DIVERGENCE",
    "RECEIVABLES_GROWTH_PRESSURE",
    "MARGIN_COMPRESSION",
    "NO_REGISTERED_CHALLENGE",
)
MAX_ABSOLUTE_VALUE = Decimal("1E30")


def _hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    ).hexdigest()


def decimal_value(value: object, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite decimal")
    try:
        normalized = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be a finite decimal") from exc
    if not normalized.is_finite() or abs(normalized) > MAX_ABSOLUTE_VALUE:
        raise ValueError(f"{name} must be a finite bounded decimal")
    return normalized


def _bps(numerator: Decimal, denominator: Decimal) -> int | None:
    if denominator == 0:
        return None
    return int(((numerator / denominator) * Decimal("10000")).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))


@dataclass(frozen=True)
class RegisteredEarningsLifecycleStage:
    stage_id: str
    subject_id: str
    market: str
    horizon: str
    stage_kind: str
    effective_from_utc: str
    effective_to_utc: str
    matures_at_utc: str
    available_at_utc: str
    source_event: InstitutionalCalendarEvent
    expectation_gap: ExpectationGapRecord | None = None
    reaction_quality: EventReactionQualityRecord | None = None
    operator_registered: bool = True
    stage_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("stage_id", "subject_id", "market", "horizon"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        stage = str(self.stage_kind).strip().upper()
        if stage not in EARNINGS_STAGES:
            raise ValueError("stage_kind is not registered")
        object.__setattr__(self, "stage_kind", stage)
        for name in ("effective_from_utc", "effective_to_utc", "matures_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if not instant(self.effective_from_utc) < instant(self.effective_to_utc) <= instant(self.matures_at_utc):
            raise ValueError("earnings lifecycle stage times must be ordered")
        if not isinstance(self.source_event, InstitutionalCalendarEvent):
            raise ValueError("earnings stage requires registered R23 event evidence")
        if self.expectation_gap is not None and not isinstance(self.expectation_gap, ExpectationGapRecord):
            raise ValueError("expectation_gap must be registered R26 evidence")
        if self.reaction_quality is not None and not isinstance(self.reaction_quality, EventReactionQualityRecord):
            raise ValueError("reaction_quality must be registered R27 evidence")
        if stage == "IMMEDIATE_REACTION" and self.reaction_quality is None:
            raise ValueError("immediate reaction stage requires R27 reaction evidence")
        if instant(self.available_at_utc) < instant(self.source_event.ingested_at_utc):
            raise ValueError("earnings stage availability cannot precede source ingest")
        if self.operator_registered is not True:
            raise ValueError("earnings stage requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "effective_from_utc": self.effective_from_utc,
            "effective_to_utc": self.effective_to_utc,
            "expectation_gap_hash": None if self.expectation_gap is None else self.expectation_gap.gap_hash,
            "horizon": self.horizon,
            "market": self.market,
            "matures_at_utc": self.matures_at_utc,
            "operator_registered": self.operator_registered,
            "reaction_quality_hash": None if self.reaction_quality is None else self.reaction_quality.quality_hash,
            "source_event_hash": self.source_event.record_hash,
            "stage_id": self.stage_id,
            "stage_kind": self.stage_kind,
            "subject_id": self.subject_id,
        }
        object.__setattr__(self, "stage_hash", _hash(payload))


@dataclass(frozen=True)
class RegisteredAccountingObservation:
    observation_id: str
    stage: RegisteredEarningsLifecycleStage
    period_end_utc: str
    observed_at_utc: str
    available_at_utc: str
    reported_profit: Decimal | str | int | None
    adjusted_profit: Decimal | str | int | None
    operating_cash_flow: Decimal | str | int | None
    revenue: Decimal | str | int | None
    receivables: Decimal | str | int | None
    gross_profit: Decimal | str | int | None
    government_grants: Decimal | str | int | None
    asset_disposal_gains: Decimal | str | int | None
    other_nonrecurring: Decimal | str | int | None
    prior_revenue: Decimal | str | int | None
    prior_receivables: Decimal | str | int | None
    prior_gross_margin_bps: int | None
    accounting_state: str = "OBSERVED"
    missing_fields: tuple[str, ...] = ()
    operator_registered: bool = True
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_id", identifier(self.observation_id, "observation_id"))
        if not isinstance(self.stage, RegisteredEarningsLifecycleStage):
            raise ValueError("accounting observation requires registered earnings stage")
        for name in ("period_end_utc", "observed_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.available_at_utc) < max(instant(self.observed_at_utc), instant(self.stage.available_at_utc)):
            raise ValueError("accounting availability cannot precede evidence")
        state = str(self.accounting_state).strip().upper()
        if state not in ACCOUNTING_STATES:
            raise ValueError("accounting_state is not registered")
        object.__setattr__(self, "accounting_state", state)
        names = (
            "reported_profit", "adjusted_profit", "operating_cash_flow", "revenue",
            "receivables", "gross_profit", "government_grants", "asset_disposal_gains",
            "other_nonrecurring", "prior_revenue", "prior_receivables",
        )
        missing = tuple(identifier(item, "missing_field") for item in self.missing_fields)
        object.__setattr__(self, "missing_fields", missing)
        if len(set(missing)) != len(missing):
            raise ValueError("missing_fields cannot contain duplicates")
        if state == "OBSERVED":
            if missing or any(getattr(self, name) is None for name in names) or self.prior_gross_margin_bps is None:
                raise ValueError("observed accounting evidence requires complete measurements")
            for name in names:
                object.__setattr__(self, name, decimal_value(getattr(self, name), name))
            if self.revenue <= 0 or self.prior_revenue <= 0:  # type: ignore[operator]
                raise ValueError("revenue values must be positive")
            if self.receivables < 0 or self.prior_receivables < 0:  # type: ignore[operator]
                raise ValueError("receivables values must be nonnegative")
            if not 0 <= self.prior_gross_margin_bps <= 10000:
                raise ValueError("prior_gross_margin_bps must be between zero and 10000")
        else:
            if not missing:
                raise ValueError("non-observed accounting evidence requires missing_fields")
            if any(getattr(self, name) is not None for name in names) or self.prior_gross_margin_bps is not None:
                raise ValueError("non-observed accounting evidence cannot carry partial measurements")
        if self.operator_registered is not True:
            raise ValueError("accounting observation requires Operator registration")
        payload = {
            "accounting_state": self.accounting_state,
            "available_at_utc": self.available_at_utc,
            "measurements": {name: None if getattr(self, name) is None else str(getattr(self, name)) for name in names},
            "missing_fields": list(self.missing_fields),
            "observation_id": self.observation_id,
            "observed_at_utc": self.observed_at_utc,
            "operator_registered": self.operator_registered,
            "period_end_utc": self.period_end_utc,
            "prior_gross_margin_bps": self.prior_gross_margin_bps,
            "stage_hash": self.stage.stage_hash,
        }
        object.__setattr__(self, "observation_hash", _hash(payload))


@dataclass(frozen=True)
class AccountingQualityChallengeRecord:
    challenge_id: str
    observation: RegisteredAccountingObservation
    available_at_utc: str
    fraud_conclusion: bool = False
    factor_activated: bool = False
    operator_registered: bool = True
    nonrecurring_share_bps: int | None = field(init=False)
    cash_conversion_bps: int | None = field(init=False)
    receivables_growth_spread_bps: int | None = field(init=False)
    gross_margin_change_bps: int = field(init=False)
    challenge_labels: tuple[str, ...] = field(init=False)
    challenge_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "challenge_id", identifier(self.challenge_id, "challenge_id"))
        if not isinstance(self.observation, RegisteredAccountingObservation):
            raise ValueError("challenge requires registered accounting observation")
        if self.observation.accounting_state != "OBSERVED":
            raise ValueError("non-observed accounting evidence cannot create challenge")
        object.__setattr__(self, "available_at_utc", utc(self.available_at_utc, "available_at_utc"))
        if instant(self.available_at_utc) < max(instant(self.observation.available_at_utc), instant(self.observation.stage.matures_at_utc)):
            raise ValueError("accounting challenge cannot mature before stage")
        item = self.observation
        nonrecurring = item.reported_profit - item.adjusted_profit  # type: ignore[operator]
        nonrecurring_share = _bps(abs(nonrecurring), abs(item.reported_profit))  # type: ignore[arg-type]
        cash_conversion = _bps(item.operating_cash_flow, item.adjusted_profit)  # type: ignore[arg-type]
        revenue_growth = _bps(item.revenue - item.prior_revenue, item.prior_revenue)  # type: ignore[operator,arg-type]
        receivables_growth = _bps(item.receivables - item.prior_receivables, item.prior_receivables)  # type: ignore[operator,arg-type]
        growth_spread = None if revenue_growth is None or receivables_growth is None else receivables_growth - revenue_growth
        gross_margin = _bps(item.gross_profit, item.revenue)  # type: ignore[arg-type]
        margin_change = 0 if gross_margin is None else gross_margin - item.prior_gross_margin_bps  # type: ignore[operator]
        labels: list[str] = []
        if nonrecurring_share is not None and nonrecurring_share >= 3000:
            labels.append("NONRECURRING_SHARE_HIGH")
        if cash_conversion is not None and cash_conversion < 5000:
            labels.append("CASH_PROFIT_DIVERGENCE")
        if growth_spread is not None and growth_spread > 2000:
            labels.append("RECEIVABLES_GROWTH_PRESSURE")
        if margin_change < -500:
            labels.append("MARGIN_COMPRESSION")
        if not labels:
            labels.append("NO_REGISTERED_CHALLENGE")
        if any(label not in CHALLENGE_LABELS for label in labels):
            raise ValueError("accounting challenge label is not registered")
        object.__setattr__(self, "nonrecurring_share_bps", nonrecurring_share)
        object.__setattr__(self, "cash_conversion_bps", cash_conversion)
        object.__setattr__(self, "receivables_growth_spread_bps", growth_spread)
        object.__setattr__(self, "gross_margin_change_bps", margin_change)
        object.__setattr__(self, "challenge_labels", tuple(labels))
        if self.fraud_conclusion:
            raise ValueError("accounting challenge cannot create a fraud conclusion")
        if self.factor_activated:
            raise ValueError("accounting challenge cannot activate a factor")
        if self.operator_registered is not True:
            raise ValueError("accounting challenge requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "cash_conversion_bps": self.cash_conversion_bps,
            "challenge_id": self.challenge_id,
            "challenge_labels": list(self.challenge_labels),
            "factor_activated": self.factor_activated,
            "fraud_conclusion": self.fraud_conclusion,
            "gross_margin_change_bps": self.gross_margin_change_bps,
            "nonrecurring_share_bps": self.nonrecurring_share_bps,
            "observation_hash": item.observation_hash,
            "operator_registered": self.operator_registered,
            "receivables_growth_spread_bps": self.receivables_growth_spread_bps,
        }
        object.__setattr__(self, "challenge_hash", _hash(payload))
