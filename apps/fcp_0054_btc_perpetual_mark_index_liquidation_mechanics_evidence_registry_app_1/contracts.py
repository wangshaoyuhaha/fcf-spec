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


MARK_PRICE_METHODS = (
    "DIRECT_VENUE_MARK",
    "INDEX_PREMIUM_CLAMPED",
    "MEDIAN_REFERENCE_CLAMPED",
)
INDEX_PRICE_METHODS = (
    "DIRECT_VENUE_INDEX",
    "MEDIAN_COMPONENT_SET",
    "WEIGHTED_COMPONENT_SET",
)
LIQUIDATION_MODES = ("FULL", "PARTIAL_LADDER")
ADL_RANKING_METHODS = (
    "PROFIT_LEVERAGE",
    "PROFIT_MARGIN_RATIO",
    "VENUE_DEFINED",
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _decimal(value: object, name: str, *, minimum: Decimal) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{name} must use an exact decimal value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be decimal-compatible") from exc
    if not result.is_finite() or result < minimum:
        raise ValueError(f"{name} is outside its registered range")
    return result


def _unit_rate(value: object, name: str, *, zero_allowed: bool) -> Decimal:
    result = _decimal(value, name, minimum=Decimal("0"))
    if result > 1 or (result == 0 and not zero_allowed):
        raise ValueError(f"{name} must be a registered unit rate")
    return result


@dataclass(frozen=True)
class RegisteredBTCLiquidationMechanicsArtifact:
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
        object.__setattr__(
            self,
            "content_sha256",
            _digest(self.content_sha256, "content_sha256"),
        )
        if (
            isinstance(self.byte_length, bool)
            or not isinstance(self.byte_length, int)
            or self.byte_length <= 0
        ):
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
class BTCPartialLiquidationTier:
    tier_id: str
    notional_floor: Decimal
    notional_cap: Decimal
    position_reduction_rate: Decimal
    liquidation_fee_rate: Decimal
    tier_hash: str = field(init=False)

    def __post_init__(self) -> None:
        tier_id = identifier(self.tier_id, "tier_id")
        floor = _decimal(self.notional_floor, "notional_floor", minimum=Decimal("0"))
        cap = _decimal(self.notional_cap, "notional_cap", minimum=Decimal("0"))
        reduction = _unit_rate(
            self.position_reduction_rate,
            "position_reduction_rate",
            zero_allowed=False,
        )
        fee = _unit_rate(
            self.liquidation_fee_rate,
            "liquidation_fee_rate",
            zero_allowed=True,
        )
        if floor >= cap:
            raise ValueError("liquidation tier interval must be strictly increasing")
        object.__setattr__(self, "tier_id", tier_id)
        object.__setattr__(self, "notional_floor", floor)
        object.__setattr__(self, "notional_cap", cap)
        object.__setattr__(self, "position_reduction_rate", reduction)
        object.__setattr__(self, "liquidation_fee_rate", fee)
        object.__setattr__(
            self,
            "tier_hash",
            canonical_sha256(
                {
                    "liquidation_fee_rate": decimal_text(fee),
                    "notional_cap": decimal_text(cap),
                    "notional_floor": decimal_text(floor),
                    "position_reduction_rate": decimal_text(reduction),
                    "tier_id": tier_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualLiquidationMechanicsVersion:
    entry_id: str
    version_id: str
    artifact_id: str
    contract_entry_hash: str
    venue_id: str
    contract_id: str
    mark_price_method: str
    index_price_method: str
    index_component_set_hash: str
    bankruptcy_price_method_id: str
    liquidation_price_method_id: str
    liquidation_mode: str
    partial_liquidation_tiers: tuple[BTCPartialLiquidationTier, ...]
    liquidation_fee_asset: str
    insurance_fund_policy_id: str
    adl_ranking_method: str
    cascade_state_policy_id: str
    effective_from_utc: str
    effective_to_utc: str | None
    schema_version: str = "btc-perpetual-liquidation-mechanics-version-v1"
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "entry_id",
            "version_id",
            "artifact_id",
            "venue_id",
            "contract_id",
            "bankruptcy_price_method_id",
            "liquidation_price_method_id",
            "liquidation_fee_asset",
            "insurance_fund_policy_id",
            "cascade_state_policy_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        contract_entry_hash = _digest(self.contract_entry_hash, "contract_entry_hash")
        component_hash = _digest(
            self.index_component_set_hash,
            "index_component_set_hash",
        )
        mark_method = str(self.mark_price_method).strip().upper()
        index_method = str(self.index_price_method).strip().upper()
        liquidation_mode = str(self.liquidation_mode).strip().upper()
        adl_method = str(self.adl_ranking_method).strip().upper()
        if mark_method not in MARK_PRICE_METHODS:
            raise ValueError("mark_price_method is not registered")
        if index_method not in INDEX_PRICE_METHODS:
            raise ValueError("index_price_method is not registered")
        if liquidation_mode not in LIQUIDATION_MODES:
            raise ValueError("liquidation_mode is not registered")
        if adl_method not in ADL_RANKING_METHODS:
            raise ValueError("adl_ranking_method is not registered")
        tiers = tuple(self.partial_liquidation_tiers)
        if not all(isinstance(item, BTCPartialLiquidationTier) for item in tiers):
            raise ValueError("partial liquidation requires typed tiers")
        if liquidation_mode == "PARTIAL_LADDER" and not tiers:
            raise ValueError("partial liquidation mode requires tiers")
        if liquidation_mode == "FULL" and tiers:
            raise ValueError("full liquidation mode cannot declare partial tiers")
        if tiers:
            keys = tuple((item.notional_floor, item.tier_id) for item in tiers)
            if keys != tuple(sorted(keys)) or len({item.tier_id for item in tiers}) != len(tiers):
                raise ValueError("partial liquidation tiers must be ordered and unique")
            if tiers[0].notional_floor != 0:
                raise ValueError("partial liquidation tiers must begin at zero")
            for left, right in zip(tiers, tiers[1:]):
                if left.notional_cap != right.notional_floor:
                    raise ValueError("partial liquidation tiers must be contiguous")
        effective_from = utc(self.effective_from_utc, "effective_from_utc")
        effective_to = (
            utc(self.effective_to_utc, "effective_to_utc")
            if self.effective_to_utc is not None
            else None
        )
        if effective_to is not None and instant(effective_to) <= instant(effective_from):
            raise ValueError("effective interval must be strictly increasing")
        if self.schema_version != "btc-perpetual-liquidation-mechanics-version-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "contract_entry_hash", contract_entry_hash)
        object.__setattr__(self, "index_component_set_hash", component_hash)
        object.__setattr__(self, "mark_price_method", mark_method)
        object.__setattr__(self, "index_price_method", index_method)
        object.__setattr__(self, "liquidation_mode", liquidation_mode)
        object.__setattr__(self, "adl_ranking_method", adl_method)
        object.__setattr__(self, "partial_liquidation_tiers", tiers)
        object.__setattr__(self, "effective_from_utc", effective_from)
        object.__setattr__(self, "effective_to_utc", effective_to)
        object.__setattr__(
            self,
            "entry_hash",
            canonical_sha256(
                {
                    "adl_ranking_method": adl_method,
                    "artifact_id": self.artifact_id,
                    "bankruptcy_price_method_id": self.bankruptcy_price_method_id,
                    "cascade_state_policy_id": self.cascade_state_policy_id,
                    "contract_entry_hash": contract_entry_hash,
                    "contract_id": self.contract_id,
                    "effective_from_utc": effective_from,
                    "effective_to_utc": effective_to,
                    "entry_id": self.entry_id,
                    "index_component_set_hash": component_hash,
                    "index_price_method": index_method,
                    "insurance_fund_policy_id": self.insurance_fund_policy_id,
                    "liquidation_fee_asset": self.liquidation_fee_asset,
                    "liquidation_mode": liquidation_mode,
                    "liquidation_price_method_id": self.liquidation_price_method_id,
                    "mark_price_method": mark_method,
                    "partial_liquidation_tier_hashes": [
                        item.tier_hash for item in tiers
                    ],
                    "schema_version": self.schema_version,
                    "venue_id": self.venue_id,
                    "version_id": self.version_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualLiquidationMechanicsRegistry:
    registry_id: str
    artifact: RegisteredBTCLiquidationMechanicsArtifact
    contract_registry: BTCPerpetualContractLifecycleRegistry
    versions: tuple[BTCPerpetualLiquidationMechanicsVersion, ...]
    as_of_utc: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    source_selected: bool = False
    price_calculation_allowed: bool = False
    margin_calculation_allowed: bool = False
    liquidation_calculation_allowed: bool = False
    balance_calculation_allowed: bool = False
    position_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    insurance_fund_mutation_allowed: bool = False
    adl_action_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        registry_id = identifier(self.registry_id, "registry_id")
        if not isinstance(self.artifact, RegisteredBTCLiquidationMechanicsArtifact):
            raise ValueError("registry requires a typed liquidation artifact")
        if not isinstance(self.contract_registry, BTCPerpetualContractLifecycleRegistry):
            raise ValueError("registry requires typed FCP-0046 contract evidence")
        versions = tuple(self.versions)
        if not versions or not all(
            isinstance(item, BTCPerpetualLiquidationMechanicsVersion)
            for item in versions
        ):
            raise ValueError("registry requires typed liquidation mechanics versions")
        keys = tuple(
            (item.venue_id, item.contract_id, item.effective_from_utc)
            for item in versions
        )
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("liquidation versions must be ordered and unique")
        if len({item.entry_id for item in versions}) != len(versions) or len(
            {item.version_id for item in versions}
        ) != len(versions):
            raise ValueError("liquidation entry and version identities must be unique")
        if any(item.artifact_id != self.artifact.artifact_id for item in versions):
            raise ValueError("liquidation version artifact lineage mismatch")
        contract_entries = {
            item.entry_hash: (item.venue_id, item.contract_id)
            for item in self.contract_registry.entries
        }
        if any(
            contract_entries.get(item.contract_entry_hash)
            != (item.venue_id, item.contract_id)
            for item in versions
        ):
            raise ValueError("FCP-0046 contract lineage mismatch")
        groups: dict[
            tuple[str, str], list[BTCPerpetualLiquidationMechanicsVersion]
        ] = {}
        for item in versions:
            groups.setdefault((item.venue_id, item.contract_id), []).append(item)
        for items in groups.values():
            for left, right in zip(items, items[1:]):
                if left.effective_to_utc is None or instant(
                    left.effective_to_utc
                ) > instant(right.effective_from_utc):
                    raise ValueError("liquidation effective intervals overlap")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(self.artifact.registered_at_utc) > instant(as_of):
            raise ValueError("registry cannot use evidence after as_of_utc")
        if instant(self.contract_registry.as_of_utc) > instant(as_of):
            raise ValueError("contract registry cannot be newer than liquidation registry")
        forbidden = (
            self.price_calculation_allowed,
            self.margin_calculation_allowed,
            self.liquidation_calculation_allowed,
            self.balance_calculation_allowed,
            self.position_calculation_allowed,
            self.pnl_calculation_allowed,
            self.insurance_fund_mutation_allowed,
            self.adl_action_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if self.operator_review_required is not True or self.source_selected is not False or any(forbidden):
            raise ValueError("registry cannot calculate, mutate, select, execute, or close")
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
