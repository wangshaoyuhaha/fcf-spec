from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_decimal,
    canonical_sha256,
    decimal_value,
    digest,
    identifier,
    instant,
    utc,
)


ACTION_TYPES = (
    "BONUS_SHARE",
    "CASH_DIVIDEND",
    "RIGHTS_ISSUE",
    "STOCK_SPLIT",
)
PRICE_VIEWS = ("FORWARD_ADJUSTED", "RAW")
REVISION_STATES = ("CANCELLED", "ORIGINAL", "REVISED")
RESOLUTION_STATES = (
    "ACTION_LINEAGE_MISMATCH",
    "ADJUSTED_RESOLVED",
    "FACTOR_NOT_OBSERVABLE",
    "RAW_RESOLVED",
)
CONTRACT_SCHEMA_VERSION = "FCP-0079-V1"
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


def _instrument(value: object) -> str:
    result = str(value).strip().upper()
    if _INSTRUMENT.fullmatch(result) is None:
        raise ValueError("instrument_id must be an A-share exchange identifier")
    return result


def _revision(
    instance: object,
    *,
    number: int,
    state: str,
    predecessor: str | None,
) -> tuple[int, str, str | None]:
    if isinstance(number, bool) or not isinstance(number, int) or number < 0:
        raise ValueError("revision_number must be a nonnegative integer")
    state = _closed(state, REVISION_STATES, "revision_state")
    if number == 0:
        if state != "ORIGINAL" or predecessor is not None:
            raise ValueError("revision zero must be original without predecessor")
    else:
        if state == "ORIGINAL" or predecessor is None:
            raise ValueError("later revision must identify a predecessor")
        predecessor = digest(predecessor, "revises_record_hash")
    return number, state, predecessor


@dataclass(frozen=True)
class CorporateActionRevision:
    record_id: str
    action_id: str
    instrument_id: str
    action_type: str
    publication_clock_hash: str
    publication_at_utc: str
    effective_date: str
    action_payload_sha256: str
    source_artifact_sha256: str
    observable_at_utc: str
    revision_number: int = 0
    revision_state: str = "ORIGINAL"
    revises_record_hash: str | None = None
    observed_not_inferred: bool = True
    operator_review_required: bool = True
    claims_data_authority: bool = False
    closes_gap: bool = False
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("record_id", "action_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "instrument_id", _instrument(self.instrument_id))
        object.__setattr__(
            self,
            "action_type",
            _closed(self.action_type, ACTION_TYPES, "action_type"),
        )
        for name in (
            "publication_clock_hash",
            "action_payload_sha256",
            "source_artifact_sha256",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        object.__setattr__(
            self,
            "publication_at_utc",
            utc(self.publication_at_utc, "publication_at_utc"),
        )
        object.__setattr__(
            self,
            "observable_at_utc",
            utc(self.observable_at_utc, "observable_at_utc"),
        )
        object.__setattr__(
            self,
            "effective_date",
            _iso_date(self.effective_date, "effective_date"),
        )
        if instant(self.publication_at_utc, "publication_at_utc") > instant(
            self.observable_at_utc,
            "observable_at_utc",
        ):
            raise ValueError("corporate action cannot be observable before publication")
        if self.publication_at_utc[:10] > self.effective_date:
            raise ValueError("corporate action publication cannot follow effective date")
        number, state, predecessor = _revision(
            self,
            number=self.revision_number,
            state=self.revision_state,
            predecessor=self.revises_record_hash,
        )
        object.__setattr__(self, "revision_number", number)
        object.__setattr__(self, "revision_state", state)
        object.__setattr__(self, "revises_record_hash", predecessor)
        if self.observed_not_inferred is not True or self.operator_review_required is not True:
            raise ValueError("corporate action lineage must remain observed and reviewable")
        if self.claims_data_authority is not False or self.closes_gap is not False:
            raise ValueError("corporate action lineage cannot establish authority or close gaps")
        object.__setattr__(self, "record_hash", canonical_sha256(self.payload()))

    def payload(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "action_payload_sha256": self.action_payload_sha256,
            "action_type": self.action_type,
            "claims_data_authority": False,
            "closes_gap": False,
            "effective_date": self.effective_date,
            "instrument_id": self.instrument_id,
            "observable_at_utc": self.observable_at_utc,
            "observed_not_inferred": True,
            "operator_review_required": True,
            "publication_at_utc": self.publication_at_utc,
            "publication_clock_hash": self.publication_clock_hash,
            "record_id": self.record_id,
            "revises_record_hash": self.revises_record_hash,
            "revision_number": self.revision_number,
            "revision_state": self.revision_state,
            "source_artifact_sha256": self.source_artifact_sha256,
        }


@dataclass(frozen=True)
class AdjustmentFactorRevision:
    record_id: str
    factor_id: str
    instrument_id: str
    trade_date: str
    factor_value: Decimal
    action_record_hashes: tuple[str, ...]
    factor_available_at_utc: str
    source_artifact_sha256: str
    revision_number: int = 0
    revision_state: str = "ORIGINAL"
    revises_record_hash: str | None = None
    provider_default_used: bool = False
    claims_official_factor: bool = False
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("record_id", "factor_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "instrument_id", _instrument(self.instrument_id))
        object.__setattr__(self, "trade_date", _iso_date(self.trade_date, "trade_date"))
        object.__setattr__(
            self,
            "factor_value",
            decimal_value(self.factor_value, "factor_value", positive=True),
        )
        actions = tuple(sorted(digest(item, "action_record_hash") for item in self.action_record_hashes))
        if not actions or len(actions) != len(set(actions)):
            raise ValueError("factor requires unique registered action revisions")
        object.__setattr__(self, "action_record_hashes", actions)
        object.__setattr__(
            self,
            "factor_available_at_utc",
            utc(self.factor_available_at_utc, "factor_available_at_utc"),
        )
        object.__setattr__(
            self,
            "source_artifact_sha256",
            digest(self.source_artifact_sha256, "source_artifact_sha256"),
        )
        number, state, predecessor = _revision(
            self,
            number=self.revision_number,
            state=self.revision_state,
            predecessor=self.revises_record_hash,
        )
        object.__setattr__(self, "revision_number", number)
        object.__setattr__(self, "revision_state", state)
        object.__setattr__(self, "revises_record_hash", predecessor)
        if self.provider_default_used is not False or self.claims_official_factor is not False:
            raise ValueError("factor lineage cannot use defaults or claim official authority")
        object.__setattr__(self, "record_hash", canonical_sha256(self.payload()))

    def payload(self) -> dict[str, object]:
        return {
            "action_record_hashes": list(self.action_record_hashes),
            "claims_official_factor": False,
            "factor_available_at_utc": self.factor_available_at_utc,
            "factor_id": self.factor_id,
            "factor_value": canonical_decimal(self.factor_value),
            "instrument_id": self.instrument_id,
            "provider_default_used": False,
            "record_id": self.record_id,
            "revises_record_hash": self.revises_record_hash,
            "revision_number": self.revision_number,
            "revision_state": self.revision_state,
            "source_artifact_sha256": self.source_artifact_sha256,
            "trade_date": self.trade_date,
        }


@dataclass(frozen=True)
class PriceQueryPolicy:
    policy_id: str
    price_view: str
    schema_version: str = CONTRACT_SCHEMA_VERSION
    factor_selection: str = "LATEST_OBSERVABLE_AS_OF"
    source_prices_immutable: bool = True
    unspecified_view_allowed: bool = False
    future_revisions_allowed: bool = False
    operator_review_required: bool = True
    policy_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_id", identifier(self.policy_id, "policy_id"))
        object.__setattr__(self, "schema_version", identifier(self.schema_version, "schema_version"))
        object.__setattr__(self, "price_view", _closed(self.price_view, PRICE_VIEWS, "price_view"))
        if self.factor_selection != "LATEST_OBSERVABLE_AS_OF":
            raise ValueError("factor_selection is not registered")
        if (
            self.source_prices_immutable is not True
            or self.unspecified_view_allowed is not False
            or self.future_revisions_allowed is not False
            or self.operator_review_required is not True
        ):
            raise ValueError("query policy exceeds fail-closed lineage scope")
        object.__setattr__(self, "policy_hash", canonical_sha256(self.payload()))

    def payload(self) -> dict[str, object]:
        return {
            "factor_selection": self.factor_selection,
            "future_revisions_allowed": False,
            "operator_review_required": True,
            "policy_id": self.policy_id,
            "price_view": self.price_view,
            "schema_version": self.schema_version,
            "source_prices_immutable": True,
            "unspecified_view_allowed": False,
        }


@dataclass(frozen=True)
class RawPriceReference:
    observation_sha256: str
    instrument_id: str
    trade_date: str
    revision_at_utc: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_sha256", digest(self.observation_sha256, "observation_sha256"))
        object.__setattr__(self, "instrument_id", _instrument(self.instrument_id))
        object.__setattr__(self, "trade_date", _iso_date(self.trade_date, "trade_date"))
        object.__setattr__(self, "revision_at_utc", utc(self.revision_at_utc, "revision_at_utc"))


@dataclass(frozen=True)
class PriceLineageResolution:
    raw_price: RawPriceReference
    policy: PriceQueryPolicy
    evaluated_at_utc: str
    resolution_state: str
    selected_action_hashes: tuple[str, ...]
    selected_factor: AdjustmentFactorRevision | None
    claims_data_authority: bool = False
    closes_gap: bool = False
    result_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.raw_price, RawPriceReference):
            raise TypeError("raw_price must be RawPriceReference")
        if not isinstance(self.policy, PriceQueryPolicy):
            raise TypeError("policy must be PriceQueryPolicy")
        object.__setattr__(self, "evaluated_at_utc", utc(self.evaluated_at_utc, "evaluated_at_utc"))
        state = _closed(self.resolution_state, RESOLUTION_STATES, "resolution_state")
        object.__setattr__(self, "resolution_state", state)
        actions = tuple(sorted(digest(item, "selected_action_hash") for item in self.selected_action_hashes))
        if len(actions) != len(set(actions)):
            raise ValueError("selected action hashes must be unique")
        object.__setattr__(self, "selected_action_hashes", actions)
        factor = self.selected_factor
        if factor is not None and not isinstance(factor, AdjustmentFactorRevision):
            raise TypeError("selected_factor must be AdjustmentFactorRevision")
        if state == "RAW_RESOLVED":
            if self.policy.price_view != "RAW" or factor is not None:
                raise ValueError("raw resolution disagrees with query policy")
        elif state == "ADJUSTED_RESOLVED":
            if self.policy.price_view != "FORWARD_ADJUSTED" or factor is None:
                raise ValueError("adjusted resolution requires an explicit factor")
            if factor.action_record_hashes != actions:
                raise ValueError("adjusted resolution action lineage disagrees")
        elif factor is not None:
            raise ValueError("blocked resolution cannot select a factor")
        if self.claims_data_authority is not False or self.closes_gap is not False:
            raise ValueError("price lineage cannot establish authority or close gaps")
        object.__setattr__(
            self,
            "result_hash",
            canonical_sha256(
                {
                    "claims_data_authority": False,
                    "closes_gap": False,
                    "evaluated_at_utc": self.evaluated_at_utc,
                    "policy_hash": self.policy.policy_hash,
                    "raw_observation_sha256": self.raw_price.observation_sha256,
                    "resolution_state": self.resolution_state,
                    "selected_action_hashes": list(actions),
                    "selected_factor_hash": factor.record_hash if factor else None,
                }
            ),
        )
