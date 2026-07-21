from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
    decimal_text,
)
from apps.fcp_0046_btc_perpetual_venue_contract_lifecycle_registry_app_1 import (
    BTCPerpetualContractLifecycleRegistry,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    LocalEventRights,
    identifier,
    instant,
    utc,
)


FUNDING_METHODS = ("PREMIUM_INDEX_CLAMPED", "DIRECT_VENUE_RATE")
FUNDING_BASES = ("PREMIUM_INDEX", "MARK_INDEX_BASIS", "DIRECT_RATE")
POSITIVE_RATE_PAYERS = ("LONG", "SHORT")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _signed_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{name} must use an exact decimal value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be decimal-compatible") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class RegisteredBTCFundingRuleArtifact:
    artifact_id: str
    content_sha256: str
    byte_length: int
    rights: LocalEventRights
    observed_at_utc: str
    registered_at_utc: str
    media_type: str = "application/json"
    market: str = "BTC-PERPETUAL"
    operator_registered: bool = True
    local_only: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "content_sha256", _digest(self.content_sha256, "content_sha256"))
        if isinstance(self.byte_length, bool) or not isinstance(self.byte_length, int) or self.byte_length <= 0:
            raise ValueError("byte_length must be a positive integer")
        if not isinstance(self.rights, LocalEventRights):
            raise ValueError("artifact requires explicit registered local rights")
        observed = utc(self.observed_at_utc, "observed_at_utc")
        registered = utc(self.registered_at_utc, "registered_at_utc")
        if instant(observed) > instant(registered):
            raise ValueError("artifact observation cannot follow registration")
        if self.media_type != "application/json" or self.market != "BTC-PERPETUAL":
            raise ValueError("artifact media type and market are closed")
        if self.operator_registered is not True or self.local_only is not True:
            raise ValueError("artifact must remain registered and local")
        object.__setattr__(self, "observed_at_utc", observed)
        object.__setattr__(self, "registered_at_utc", registered)


@dataclass(frozen=True)
class BTCPerpetualFundingRuleVersion:
    entry_id: str
    version_id: str
    artifact_id: str
    contract_entry_hash: str
    venue_id: str
    contract_id: str
    funding_method: str
    funding_basis: str
    funding_interval_seconds: int
    settlement_anchor_utc: str
    rate_floor: Decimal
    rate_cap: Decimal
    interest_component_rate: Decimal
    positive_rate_payer: str
    effective_from_utc: str
    effective_to_utc: str | None
    schema_version: str = "btc-perpetual-funding-rule-version-v1"
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("entry_id", "version_id", "artifact_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "contract_entry_hash", _digest(self.contract_entry_hash, "contract_entry_hash"))
        method = str(self.funding_method).strip().upper()
        basis = str(self.funding_basis).strip().upper()
        payer = str(self.positive_rate_payer).strip().upper()
        if method not in FUNDING_METHODS or basis not in FUNDING_BASES:
            raise ValueError("funding method or basis is not registered")
        if payer not in POSITIVE_RATE_PAYERS:
            raise ValueError("positive-rate payer is not registered")
        if isinstance(self.funding_interval_seconds, bool) or not isinstance(self.funding_interval_seconds, int) or self.funding_interval_seconds <= 0:
            raise ValueError("funding_interval_seconds must be a positive integer")
        if method == "DIRECT_VENUE_RATE" and basis != "DIRECT_RATE":
            raise ValueError("direct funding method requires direct-rate basis")
        if method == "PREMIUM_INDEX_CLAMPED" and basis == "DIRECT_RATE":
            raise ValueError("premium funding method requires a derived basis")
        anchor = utc(self.settlement_anchor_utc, "settlement_anchor_utc")
        floor = _signed_decimal(self.rate_floor, "rate_floor")
        cap = _signed_decimal(self.rate_cap, "rate_cap")
        interest = _signed_decimal(self.interest_component_rate, "interest_component_rate")
        if floor > cap:
            raise ValueError("funding rate floor cannot exceed cap")
        effective_from = utc(self.effective_from_utc, "effective_from_utc")
        effective_to = utc(self.effective_to_utc, "effective_to_utc") if self.effective_to_utc is not None else None
        if effective_to is not None and instant(effective_to) <= instant(effective_from):
            raise ValueError("effective interval must be strictly increasing")
        if self.schema_version != "btc-perpetual-funding-rule-version-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "funding_method", method)
        object.__setattr__(self, "funding_basis", basis)
        object.__setattr__(self, "positive_rate_payer", payer)
        object.__setattr__(self, "settlement_anchor_utc", anchor)
        object.__setattr__(self, "rate_floor", floor)
        object.__setattr__(self, "rate_cap", cap)
        object.__setattr__(self, "interest_component_rate", interest)
        object.__setattr__(self, "effective_from_utc", effective_from)
        object.__setattr__(self, "effective_to_utc", effective_to)
        object.__setattr__(
            self,
            "entry_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact_id,
                    "contract_entry_hash": self.contract_entry_hash,
                    "contract_id": self.contract_id,
                    "effective_from_utc": effective_from,
                    "effective_to_utc": effective_to,
                    "entry_id": self.entry_id,
                    "funding_basis": basis,
                    "funding_interval_seconds": self.funding_interval_seconds,
                    "funding_method": method,
                    "interest_component_rate": decimal_text(interest),
                    "positive_rate_payer": payer,
                    "rate_cap": decimal_text(cap),
                    "rate_floor": decimal_text(floor),
                    "schema_version": self.schema_version,
                    "settlement_anchor_utc": anchor,
                    "venue_id": self.venue_id,
                    "version_id": self.version_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualFundingMethodScheduleRegistry:
    registry_id: str
    artifact: RegisteredBTCFundingRuleArtifact
    contract_registry: BTCPerpetualContractLifecycleRegistry
    versions: tuple[BTCPerpetualFundingRuleVersion, ...]
    as_of_utc: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    source_selected: bool = False
    funding_rate_calculation_allowed: bool = False
    funding_payment_calculation_allowed: bool = False
    balance_calculation_allowed: bool = False
    position_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    liquidation_calculation_allowed: bool = False
    fee_calculation_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        registry_id = identifier(self.registry_id, "registry_id")
        if not isinstance(self.artifact, RegisteredBTCFundingRuleArtifact):
            raise ValueError("registry requires a typed funding artifact")
        if not isinstance(self.contract_registry, BTCPerpetualContractLifecycleRegistry):
            raise ValueError("registry requires typed FCP-0046 contract evidence")
        versions = tuple(self.versions)
        if not versions or not all(isinstance(item, BTCPerpetualFundingRuleVersion) for item in versions):
            raise ValueError("registry requires typed funding rule versions")
        keys = tuple((item.venue_id, item.contract_id, item.effective_from_utc) for item in versions)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("funding versions must be deterministically ordered and unique")
        if len({item.entry_id for item in versions}) != len(versions) or len({item.version_id for item in versions}) != len(versions):
            raise ValueError("funding entry and version identities must be unique")
        if any(item.artifact_id != self.artifact.artifact_id for item in versions):
            raise ValueError("funding version artifact lineage mismatch")
        contract_entries = {item.entry_hash: (item.venue_id, item.contract_id) for item in self.contract_registry.entries}
        if any(contract_entries.get(item.contract_entry_hash) != (item.venue_id, item.contract_id) for item in versions):
            raise ValueError("FCP-0046 contract lineage mismatch")
        groups: dict[tuple[str, str], list[BTCPerpetualFundingRuleVersion]] = {}
        for item in versions:
            groups.setdefault((item.venue_id, item.contract_id), []).append(item)
        for items in groups.values():
            for left, right in zip(items, items[1:]):
                if left.effective_to_utc is None or instant(left.effective_to_utc) > instant(right.effective_from_utc):
                    raise ValueError("funding effective intervals overlap")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(self.artifact.registered_at_utc) > instant(as_of):
            raise ValueError("registry cannot use evidence after as_of_utc")
        if instant(self.contract_registry.as_of_utc) > instant(as_of):
            raise ValueError("contract registry cannot be newer than funding registry")
        forbidden = (
            self.funding_rate_calculation_allowed,
            self.funding_payment_calculation_allowed,
            self.balance_calculation_allowed,
            self.position_calculation_allowed,
            self.pnl_calculation_allowed,
            self.liquidation_calculation_allowed,
            self.fee_calculation_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if self.operator_review_required is not True or self.source_selected is not False or any(forbidden):
            raise ValueError("registry cannot calculate, select, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("registry authority identities are immutable")
        object.__setattr__(self, "registry_id", registry_id)
        object.__setattr__(self, "versions", versions)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "registry_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact.artifact_id,
                    "artifact_sha256": self.artifact.content_sha256,
                    "as_of_utc": as_of,
                    "contract_registry_hash": self.contract_registry.registry_hash,
                    "registry_id": registry_id,
                    "version_hashes": [item.entry_hash for item in versions],
                }
            ),
        )
