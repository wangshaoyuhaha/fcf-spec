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


MARGIN_MODES = ("ISOLATED", "CROSS")
POSITION_MODES = ("ONE_WAY", "HEDGE")
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


def _positive_decimal(value: object, name: str) -> Decimal:
    result = _decimal(value, name, minimum=Decimal("0"))
    if result == 0:
        raise ValueError(f"{name} must be positive")
    return result


def _rate(value: object, name: str, *, one_allowed: bool = True) -> Decimal:
    result = _decimal(value, name, minimum=Decimal("0"))
    if result > 1 or (result == 1 and not one_allowed):
        raise ValueError(f"{name} must be a registered unit rate")
    return result


@dataclass(frozen=True)
class RegisteredBTCMarginRuleArtifact:
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
class BTCMarginRiskTier:
    tier_id: str
    notional_floor: Decimal
    notional_cap: Decimal
    initial_margin_rate: Decimal
    maintenance_margin_rate: Decimal
    maintenance_amount_deduction: Decimal
    risk_limit: Decimal
    tier_hash: str = field(init=False)

    def __post_init__(self) -> None:
        tier_id = identifier(self.tier_id, "tier_id")
        floor = _decimal(self.notional_floor, "notional_floor", minimum=Decimal("0"))
        cap = _positive_decimal(self.notional_cap, "notional_cap")
        initial = _rate(self.initial_margin_rate, "initial_margin_rate")
        maintenance = _rate(self.maintenance_margin_rate, "maintenance_margin_rate")
        deduction = _decimal(
            self.maintenance_amount_deduction,
            "maintenance_amount_deduction",
            minimum=Decimal("0"),
        )
        risk_limit = _positive_decimal(self.risk_limit, "risk_limit")
        if floor >= cap:
            raise ValueError("tier notional interval must be strictly increasing")
        if maintenance <= 0 or initial <= 0 or maintenance > initial:
            raise ValueError("margin rates must satisfy 0 < maintenance <= initial")
        if risk_limit < cap:
            raise ValueError("risk_limit cannot be below notional_cap")
        object.__setattr__(self, "tier_id", tier_id)
        object.__setattr__(self, "notional_floor", floor)
        object.__setattr__(self, "notional_cap", cap)
        object.__setattr__(self, "initial_margin_rate", initial)
        object.__setattr__(self, "maintenance_margin_rate", maintenance)
        object.__setattr__(self, "maintenance_amount_deduction", deduction)
        object.__setattr__(self, "risk_limit", risk_limit)
        object.__setattr__(
            self,
            "tier_hash",
            canonical_sha256(
                {
                    "initial_margin_rate": decimal_text(initial),
                    "maintenance_amount_deduction": decimal_text(deduction),
                    "maintenance_margin_rate": decimal_text(maintenance),
                    "notional_cap": decimal_text(cap),
                    "notional_floor": decimal_text(floor),
                    "risk_limit": decimal_text(risk_limit),
                    "tier_id": tier_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCCollateralHaircutRule:
    collateral_asset: str
    valuation_asset: str
    haircut_rate: Decimal
    collateral_hash: str = field(init=False)

    def __post_init__(self) -> None:
        collateral = identifier(self.collateral_asset, "collateral_asset")
        valuation = identifier(self.valuation_asset, "valuation_asset")
        haircut = _rate(self.haircut_rate, "haircut_rate", one_allowed=False)
        object.__setattr__(self, "collateral_asset", collateral)
        object.__setattr__(self, "valuation_asset", valuation)
        object.__setattr__(self, "haircut_rate", haircut)
        object.__setattr__(
            self,
            "collateral_hash",
            canonical_sha256(
                {
                    "collateral_asset": collateral,
                    "haircut_rate": decimal_text(haircut),
                    "valuation_asset": valuation,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualMarginRuleVersion:
    entry_id: str
    version_id: str
    artifact_id: str
    contract_entry_hash: str
    venue_id: str
    contract_id: str
    margin_mode: str
    position_mode: str
    tiers: tuple[BTCMarginRiskTier, ...]
    collateral_rules: tuple[BTCCollateralHaircutRule, ...]
    effective_from_utc: str
    effective_to_utc: str | None
    schema_version: str = "btc-perpetual-margin-rule-version-v1"
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("entry_id", "version_id", "artifact_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "contract_entry_hash", _digest(self.contract_entry_hash, "contract_entry_hash"))
        margin_mode = str(self.margin_mode).strip().upper()
        position_mode = str(self.position_mode).strip().upper()
        if margin_mode not in MARGIN_MODES or position_mode not in POSITION_MODES:
            raise ValueError("margin or position mode is not registered")
        tiers = tuple(self.tiers)
        collateral = tuple(self.collateral_rules)
        if not tiers or not all(isinstance(item, BTCMarginRiskTier) for item in tiers):
            raise ValueError("margin version requires typed risk tiers")
        if not collateral or not all(isinstance(item, BTCCollateralHaircutRule) for item in collateral):
            raise ValueError("margin version requires typed collateral rules")
        tier_keys = tuple((item.notional_floor, item.tier_id) for item in tiers)
        if tier_keys != tuple(sorted(tier_keys)) or len({item.tier_id for item in tiers}) != len(tiers):
            raise ValueError("risk tiers must be deterministically ordered and unique")
        if tiers[0].notional_floor != 0:
            raise ValueError("risk tiers must begin at zero notional")
        for left, right in zip(tiers, tiers[1:]):
            if left.notional_cap != right.notional_floor:
                raise ValueError("risk tiers must be contiguous and nonoverlapping")
        collateral_keys = tuple((item.collateral_asset, item.valuation_asset) for item in collateral)
        if collateral_keys != tuple(sorted(collateral_keys)) or len(collateral_keys) != len(set(collateral_keys)):
            raise ValueError("collateral rules must be ordered and unique")
        effective_from = utc(self.effective_from_utc, "effective_from_utc")
        effective_to = utc(self.effective_to_utc, "effective_to_utc") if self.effective_to_utc is not None else None
        if effective_to is not None and instant(effective_to) <= instant(effective_from):
            raise ValueError("effective interval must be strictly increasing")
        if self.schema_version != "btc-perpetual-margin-rule-version-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "margin_mode", margin_mode)
        object.__setattr__(self, "position_mode", position_mode)
        object.__setattr__(self, "tiers", tiers)
        object.__setattr__(self, "collateral_rules", collateral)
        object.__setattr__(self, "effective_from_utc", effective_from)
        object.__setattr__(self, "effective_to_utc", effective_to)
        object.__setattr__(
            self,
            "entry_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact_id,
                    "collateral_hashes": [item.collateral_hash for item in collateral],
                    "contract_entry_hash": self.contract_entry_hash,
                    "contract_id": self.contract_id,
                    "effective_from_utc": effective_from,
                    "effective_to_utc": effective_to,
                    "entry_id": self.entry_id,
                    "margin_mode": margin_mode,
                    "position_mode": position_mode,
                    "schema_version": self.schema_version,
                    "tier_hashes": [item.tier_hash for item in tiers],
                    "venue_id": self.venue_id,
                    "version_id": self.version_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualMarginRiskTierRegistry:
    registry_id: str
    artifact: RegisteredBTCMarginRuleArtifact
    contract_registry: BTCPerpetualContractLifecycleRegistry
    versions: tuple[BTCPerpetualMarginRuleVersion, ...]
    as_of_utc: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    source_selected: bool = False
    balance_calculation_allowed: bool = False
    position_calculation_allowed: bool = False
    margin_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    liquidation_calculation_allowed: bool = False
    funding_calculation_allowed: bool = False
    fee_calculation_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        registry_id = identifier(self.registry_id, "registry_id")
        if not isinstance(self.artifact, RegisteredBTCMarginRuleArtifact):
            raise ValueError("registry requires a typed margin artifact")
        if not isinstance(self.contract_registry, BTCPerpetualContractLifecycleRegistry):
            raise ValueError("registry requires typed FCP-0046 contract evidence")
        versions = tuple(self.versions)
        if not versions or not all(isinstance(item, BTCPerpetualMarginRuleVersion) for item in versions):
            raise ValueError("registry requires typed margin rule versions")
        keys = tuple(
            (
                item.venue_id,
                item.contract_id,
                item.margin_mode,
                item.position_mode,
                item.effective_from_utc,
            )
            for item in versions
        )
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("margin versions must be deterministically ordered and unique")
        if len({item.entry_id for item in versions}) != len(versions) or len({item.version_id for item in versions}) != len(versions):
            raise ValueError("margin entry and version identities must be unique")
        if any(item.artifact_id != self.artifact.artifact_id for item in versions):
            raise ValueError("margin version artifact lineage mismatch")
        contract_entries = {
            item.entry_hash: (item.venue_id, item.contract_id)
            for item in self.contract_registry.entries
        }
        if any(contract_entries.get(item.contract_entry_hash) != (item.venue_id, item.contract_id) for item in versions):
            raise ValueError("FCP-0046 contract lineage mismatch")
        groups: dict[tuple[str, str, str, str], list[BTCPerpetualMarginRuleVersion]] = {}
        for item in versions:
            groups.setdefault(
                (item.venue_id, item.contract_id, item.margin_mode, item.position_mode),
                [],
            ).append(item)
        for items in groups.values():
            for left, right in zip(items, items[1:]):
                if left.effective_to_utc is None or instant(left.effective_to_utc) > instant(right.effective_from_utc):
                    raise ValueError("margin effective intervals overlap")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(self.artifact.registered_at_utc) > instant(as_of):
            raise ValueError("registry cannot use evidence after as_of_utc")
        if instant(self.contract_registry.as_of_utc) > instant(as_of):
            raise ValueError("contract registry cannot be newer than margin registry")
        forbidden = (
            self.balance_calculation_allowed,
            self.position_calculation_allowed,
            self.margin_calculation_allowed,
            self.pnl_calculation_allowed,
            self.liquidation_calculation_allowed,
            self.funding_calculation_allowed,
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
