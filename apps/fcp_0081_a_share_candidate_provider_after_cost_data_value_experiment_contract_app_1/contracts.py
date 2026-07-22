from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_decimal,
    canonical_sha256,
    decimal_value,
    digest,
    identifier,
    utc,
)


METRIC_IDS = (
    "ADJUSTMENT_LINEAGE_COMPLETENESS_RATIO",
    "CONFLICT_RATE",
    "COVERAGE_RATIO",
    "FRESHNESS_DELAY_SECONDS",
    "POINT_IN_TIME_COMPLETENESS_RATIO",
    "RIGHTS_RETENTION_COMPLETENESS_RATIO",
    "TRADING_STATUS_COMPLETENESS_RATIO",
)
RATIO_METRICS = tuple(item for item in METRIC_IDS if item != "FRESHNESS_DELAY_SECONDS")
LOWER_IS_BETTER = ("CONFLICT_RATE", "FRESHNESS_DELAY_SECONDS")
RIGHTS_STATES = ("REGISTERED_REVIEW_COMPLETE", "UNRESOLVED")
RETENTION_STATES = ("REGISTERED_REVIEW_COMPLETE", "UNRESOLVED")
DECISION_STATES = (
    "CONTINUE_LOCAL_RESEARCH",
    "INSUFFICIENT_EVIDENCE",
    "OPERATOR_REVIEW_ELIGIBLE",
    "STOP_COST_EXCEEDS_AUTHORIZED_SPEND",
    "STOP_NO_INCREMENTAL_VALUE",
)
CONTRACT_SCHEMA_VERSION = "FCP-0081-V1"
_INSTRUMENT = re.compile(r"^[0-9]{6}\.(?:XSHG|XSHE)$")


def _closed(value: object, allowed: tuple[str, ...], name: str) -> str:
    result = str(value).strip().upper()
    if result not in allowed:
        raise ValueError(f"{name} is not registered")
    return result


def _iso_date(value: object, name: str) -> str:
    result = str(value).strip()
    try:
        date.fromisoformat(result)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an ISO date") from exc
    return result


def _signed_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, (bool, float)):
        raise ValueError(f"{name} must be an exact decimal")
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be an exact decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class DataValueExperimentSpecification:
    experiment_id: str
    baseline_candidate_id: str
    candidate_id: str
    baseline_profile_hash: str
    candidate_profile_hash: str
    baseline_artifact_sha256: str
    candidate_artifact_sha256: str
    instrument_ids: tuple[str, ...]
    start_date: str
    end_date: str
    required_metrics: tuple[str, ...] = METRIC_IDS
    authorized_spend_cny: Decimal = Decimal("0")
    schema_version: str = CONTRACT_SCHEMA_VERSION
    local_registered_artifacts_only: bool = True
    provider_selected: bool = False
    purchase_allowed: bool = False
    renewal_allowed: bool = False
    cancellation_allowed: bool = False
    operator_review_required: bool = True
    specification_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("experiment_id", "baseline_candidate_id", "candidate_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        if self.baseline_candidate_id == self.candidate_id:
            raise ValueError("baseline and candidate must be distinct")
        for name in (
            "baseline_profile_hash",
            "candidate_profile_hash",
            "baseline_artifact_sha256",
            "candidate_artifact_sha256",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        instruments = tuple(sorted(set(str(item).strip().upper() for item in self.instrument_ids)))
        if not instruments or len(instruments) != len(self.instrument_ids):
            raise ValueError("instrument_ids must be nonempty and unique")
        if any(_INSTRUMENT.fullmatch(item) is None for item in instruments):
            raise ValueError("instrument_ids must use canonical A-share identifiers")
        object.__setattr__(self, "instrument_ids", instruments)
        object.__setattr__(self, "start_date", _iso_date(self.start_date, "start_date"))
        object.__setattr__(self, "end_date", _iso_date(self.end_date, "end_date"))
        if self.start_date > self.end_date:
            raise ValueError("experiment date range is reversed")
        metrics = tuple(self.required_metrics)
        if metrics != METRIC_IDS:
            raise ValueError("required_metrics must remain exact and ordered")
        object.__setattr__(self, "required_metrics", metrics)
        spend = decimal_value(self.authorized_spend_cny, "authorized_spend_cny")
        if spend != Decimal("0"):
            raise ValueError("current authorized spend must remain zero")
        object.__setattr__(self, "authorized_spend_cny", spend)
        object.__setattr__(self, "schema_version", identifier(self.schema_version, "schema_version"))
        flags = (
            self.local_registered_artifacts_only is True
            and self.provider_selected is False
            and self.purchase_allowed is False
            and self.renewal_allowed is False
            and self.cancellation_allowed is False
            and self.operator_review_required is True
        )
        if not flags:
            raise ValueError("experiment specification exceeds approved scope")
        object.__setattr__(self, "specification_hash", canonical_sha256(self.payload()))

    def payload(self) -> dict[str, object]:
        return {
            "authorized_spend_cny": canonical_decimal(self.authorized_spend_cny),
            "baseline_artifact_sha256": self.baseline_artifact_sha256,
            "baseline_candidate_id": self.baseline_candidate_id,
            "baseline_profile_hash": self.baseline_profile_hash,
            "cancellation_allowed": False,
            "candidate_artifact_sha256": self.candidate_artifact_sha256,
            "candidate_id": self.candidate_id,
            "candidate_profile_hash": self.candidate_profile_hash,
            "end_date": self.end_date,
            "experiment_id": self.experiment_id,
            "instrument_ids": list(self.instrument_ids),
            "local_registered_artifacts_only": True,
            "operator_review_required": True,
            "provider_selected": False,
            "purchase_allowed": False,
            "renewal_allowed": False,
            "required_metrics": list(self.required_metrics),
            "schema_version": self.schema_version,
            "start_date": self.start_date,
        }


@dataclass(frozen=True)
class ComparableMetricObservation:
    specification_hash: str
    metric_id: str
    baseline_value: Decimal
    candidate_value: Decimal
    comparable_window_hash: str
    evidence_sha256: str
    observed_at_utc: str
    observed_not_inferred: bool = True
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("specification_hash", "comparable_window_hash", "evidence_sha256"):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        object.__setattr__(self, "metric_id", _closed(self.metric_id, METRIC_IDS, "metric_id"))
        baseline = decimal_value(self.baseline_value, "baseline_value")
        candidate = decimal_value(self.candidate_value, "candidate_value")
        if self.metric_id in RATIO_METRICS and (baseline > 1 or candidate > 1):
            raise ValueError("ratio metric must remain in the closed interval")
        object.__setattr__(self, "baseline_value", baseline)
        object.__setattr__(self, "candidate_value", candidate)
        object.__setattr__(self, "observed_at_utc", utc(self.observed_at_utc, "observed_at_utc"))
        if self.observed_not_inferred is not True:
            raise ValueError("metric observations must be observed, not inferred")
        object.__setattr__(self, "observation_hash", canonical_sha256(self.payload()))

    def improvement(self) -> Decimal:
        if self.metric_id in LOWER_IS_BETTER:
            return self.baseline_value - self.candidate_value
        return self.candidate_value - self.baseline_value

    def payload(self) -> dict[str, object]:
        return {
            "baseline_value": canonical_decimal(self.baseline_value),
            "candidate_value": canonical_decimal(self.candidate_value),
            "comparable_window_hash": self.comparable_window_hash,
            "evidence_sha256": self.evidence_sha256,
            "metric_id": self.metric_id,
            "observed_at_utc": self.observed_at_utc,
            "observed_not_inferred": True,
            "specification_hash": self.specification_hash,
        }


@dataclass(frozen=True)
class AfterCostEvidence:
    specification_hash: str
    fixed_cost_cny: Decimal
    measured_benefit_cny: Decimal
    cost_evidence_sha256: str
    benefit_evidence_sha256: str
    rights_state: str
    retention_state: str
    observed_at_utc: str
    provider_quote_is_authority: bool = False
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "specification_hash", digest(self.specification_hash, "specification_hash"))
        object.__setattr__(self, "fixed_cost_cny", decimal_value(self.fixed_cost_cny, "fixed_cost_cny"))
        object.__setattr__(self, "measured_benefit_cny", decimal_value(self.measured_benefit_cny, "measured_benefit_cny"))
        for name in ("cost_evidence_sha256", "benefit_evidence_sha256"):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        object.__setattr__(self, "rights_state", _closed(self.rights_state, RIGHTS_STATES, "rights_state"))
        object.__setattr__(self, "retention_state", _closed(self.retention_state, RETENTION_STATES, "retention_state"))
        object.__setattr__(self, "observed_at_utc", utc(self.observed_at_utc, "observed_at_utc"))
        if self.provider_quote_is_authority is not False:
            raise ValueError("a provider quote cannot establish cost or value authority")
        object.__setattr__(self, "evidence_hash", canonical_sha256(self.payload()))

    def after_cost_value(self) -> Decimal:
        return self.measured_benefit_cny - self.fixed_cost_cny

    def payload(self) -> dict[str, object]:
        return {
            "benefit_evidence_sha256": self.benefit_evidence_sha256,
            "cost_evidence_sha256": self.cost_evidence_sha256,
            "fixed_cost_cny": canonical_decimal(self.fixed_cost_cny),
            "measured_benefit_cny": canonical_decimal(self.measured_benefit_cny),
            "observed_at_utc": self.observed_at_utc,
            "provider_quote_is_authority": False,
            "retention_state": self.retention_state,
            "rights_state": self.rights_state,
            "specification_hash": self.specification_hash,
        }


@dataclass(frozen=True)
class DataValueReviewPacket:
    specification_hash: str
    decision_state: str
    observation_hashes: tuple[str, ...]
    after_cost_evidence_hash: str
    missing_metrics: tuple[str, ...]
    improved_metrics: tuple[str, ...]
    regressed_metrics: tuple[str, ...]
    after_cost_value_cny: Decimal
    operator_review_required: bool = True
    provider_selected: bool = False
    purchase_authorized: bool = False
    renewal_authorized: bool = False
    cancellation_authorized: bool = False
    claims_profitability: bool = False
    closes_gap: bool = False
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "specification_hash", digest(self.specification_hash, "specification_hash"))
        object.__setattr__(self, "decision_state", _closed(self.decision_state, DECISION_STATES, "decision_state"))
        hashes = tuple(digest(item, "observation_hash") for item in self.observation_hashes)
        if len(hashes) != len(set(hashes)):
            raise ValueError("observation hashes must be unique")
        object.__setattr__(self, "observation_hashes", hashes)
        object.__setattr__(self, "after_cost_evidence_hash", digest(self.after_cost_evidence_hash, "after_cost_evidence_hash"))
        for name in ("missing_metrics", "improved_metrics", "regressed_metrics"):
            values = tuple(getattr(self, name))
            if values != tuple(sorted(set(values))) or any(item not in METRIC_IDS for item in values):
                raise ValueError(f"{name} must be closed, unique, and sorted")
            object.__setattr__(self, name, values)
        object.__setattr__(self, "after_cost_value_cny", _signed_decimal(self.after_cost_value_cny, "after_cost_value_cny"))
        flags = (
            self.operator_review_required is True
            and self.provider_selected is False
            and self.purchase_authorized is False
            and self.renewal_authorized is False
            and self.cancellation_authorized is False
            and self.claims_profitability is False
            and self.closes_gap is False
        )
        if not flags:
            raise ValueError("review packet exceeds non-authorizing scope")
        object.__setattr__(self, "packet_hash", canonical_sha256(self.payload()))

    def payload(self) -> dict[str, object]:
        return {
            "after_cost_evidence_hash": self.after_cost_evidence_hash,
            "after_cost_value_cny": canonical_decimal(self.after_cost_value_cny),
            "cancellation_authorized": False,
            "claims_profitability": False,
            "closes_gap": False,
            "decision_state": self.decision_state,
            "improved_metrics": list(self.improved_metrics),
            "missing_metrics": list(self.missing_metrics),
            "observation_hashes": list(self.observation_hashes),
            "operator_review_required": True,
            "provider_selected": False,
            "purchase_authorized": False,
            "regressed_metrics": list(self.regressed_metrics),
            "renewal_authorized": False,
            "specification_hash": self.specification_hash,
        }
