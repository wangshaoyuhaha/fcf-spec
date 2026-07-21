from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
    decimal_text,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    LocalEventRights,
    identifier,
    instant,
    utc,
)


SETTLEMENT_TYPES = ("LINEAR", "INVERSE")
LIFECYCLE_STATES = ("ACTIVE", "CLOSE_ONLY", "DELISTED", "MIGRATED")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _positive_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{name} must use an exact decimal value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be decimal-compatible") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return result


@dataclass(frozen=True)
class RegisteredBTCContractRuleArtifact:
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
class BTCPerpetualContractVersion:
    entry_id: str
    version_id: str
    artifact_id: str
    venue_id: str
    contract_id: str
    venue_symbol: str
    settlement_type: str
    base_asset: str
    quote_asset: str
    settlement_asset: str
    collateral_assets: tuple[str, ...]
    contract_multiplier: Decimal
    price_tick: Decimal
    quantity_step: Decimal
    minimum_quantity: Decimal
    minimum_notional: Decimal
    effective_from_utc: str
    effective_to_utc: str | None
    lifecycle_state: str
    migration_contract_id: str | None = None
    schema_version: str = "btc-perpetual-contract-version-v1"
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "entry_id",
            "version_id",
            "artifact_id",
            "venue_id",
            "contract_id",
            "venue_symbol",
            "base_asset",
            "quote_asset",
            "settlement_asset",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        settlement = str(self.settlement_type).strip().upper()
        lifecycle = str(self.lifecycle_state).strip().upper()
        if settlement not in SETTLEMENT_TYPES:
            raise ValueError("settlement_type is not registered")
        if lifecycle not in LIFECYCLE_STATES:
            raise ValueError("lifecycle_state is not registered")
        collateral = tuple(identifier(item, "collateral_asset") for item in self.collateral_assets)
        if not collateral or collateral != tuple(sorted(set(collateral))):
            raise ValueError("collateral assets must be nonempty, ordered, and unique")
        if self.settlement_asset not in collateral:
            raise ValueError("settlement asset must be registered collateral")
        if settlement == "LINEAR" and self.settlement_asset != self.quote_asset:
            raise ValueError("linear contracts must settle in the quote asset")
        if settlement == "INVERSE" and self.settlement_asset != self.base_asset:
            raise ValueError("inverse contracts must settle in the base asset")
        decimal_names = (
            "contract_multiplier",
            "price_tick",
            "quantity_step",
            "minimum_quantity",
            "minimum_notional",
        )
        decimals = {
            name: _positive_decimal(getattr(self, name), name) for name in decimal_names
        }
        effective_from = utc(self.effective_from_utc, "effective_from_utc")
        effective_to = (
            utc(self.effective_to_utc, "effective_to_utc")
            if self.effective_to_utc is not None
            else None
        )
        if effective_to is not None and instant(effective_to) <= instant(effective_from):
            raise ValueError("effective interval must be strictly increasing")
        migration = (
            identifier(self.migration_contract_id, "migration_contract_id")
            if self.migration_contract_id is not None
            else None
        )
        if lifecycle == "MIGRATED":
            if migration is None or migration == self.contract_id:
                raise ValueError("migrated contracts require a distinct target")
        elif migration is not None:
            raise ValueError("only migrated contracts may declare a target")
        if self.schema_version != "btc-perpetual-contract-version-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "settlement_type", settlement)
        object.__setattr__(self, "lifecycle_state", lifecycle)
        object.__setattr__(self, "collateral_assets", collateral)
        object.__setattr__(self, "effective_from_utc", effective_from)
        object.__setattr__(self, "effective_to_utc", effective_to)
        object.__setattr__(self, "migration_contract_id", migration)
        for name, value in decimals.items():
            object.__setattr__(self, name, value)
        object.__setattr__(
            self,
            "entry_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact_id,
                    "base_asset": self.base_asset,
                    "collateral_assets": collateral,
                    "contract_id": self.contract_id,
                    "contract_multiplier": decimal_text(decimals["contract_multiplier"]),
                    "effective_from_utc": effective_from,
                    "effective_to_utc": effective_to,
                    "entry_id": self.entry_id,
                    "lifecycle_state": lifecycle,
                    "migration_contract_id": migration,
                    "minimum_notional": decimal_text(decimals["minimum_notional"]),
                    "minimum_quantity": decimal_text(decimals["minimum_quantity"]),
                    "price_tick": decimal_text(decimals["price_tick"]),
                    "quantity_step": decimal_text(decimals["quantity_step"]),
                    "quote_asset": self.quote_asset,
                    "schema_version": self.schema_version,
                    "settlement_asset": self.settlement_asset,
                    "settlement_type": settlement,
                    "venue_id": self.venue_id,
                    "venue_symbol": self.venue_symbol,
                    "version_id": self.version_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualContractLifecycleRegistry:
    registry_id: str
    artifact: RegisteredBTCContractRuleArtifact
    entries: tuple[BTCPerpetualContractVersion, ...]
    as_of_utc: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    source_selected: bool = False
    margin_calculation_allowed: bool = False
    liquidation_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    funding_calculation_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        registry_id = identifier(self.registry_id, "registry_id")
        if not isinstance(self.artifact, RegisteredBTCContractRuleArtifact):
            raise ValueError("registry requires a typed registered artifact")
        entries = tuple(self.entries)
        if not entries or not all(isinstance(item, BTCPerpetualContractVersion) for item in entries):
            raise ValueError("registry requires typed contract versions")
        keys = tuple((item.venue_id, item.contract_id, item.effective_from_utc) for item in entries)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("contract versions must be deterministically ordered and unique")
        if len({item.entry_id for item in entries}) != len(entries) or len({item.version_id for item in entries}) != len(entries):
            raise ValueError("contract entry and version identities must be unique")
        if any(item.artifact_id != self.artifact.artifact_id for item in entries):
            raise ValueError("contract version artifact lineage mismatch")
        groups: dict[tuple[str, str], list[BTCPerpetualContractVersion]] = {}
        for item in entries:
            groups.setdefault((item.venue_id, item.contract_id), []).append(item)
        for versions in groups.values():
            for left, right in zip(versions, versions[1:]):
                if left.effective_to_utc is None or instant(left.effective_to_utc) > instant(right.effective_from_utc):
                    raise ValueError("contract effective intervals overlap")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(self.artifact.registered_at_utc) > instant(as_of):
            raise ValueError("registry cannot use evidence after as_of_utc")
        if (
            self.operator_review_required is not True
            or self.source_selected is not False
            or any(
                (
                    self.margin_calculation_allowed,
                    self.liquidation_calculation_allowed,
                    self.pnl_calculation_allowed,
                    self.funding_calculation_allowed,
                    self.execution_allowed,
                    self.gap_closed,
                )
            )
        ):
            raise ValueError("registry cannot calculate, select, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("registry authority identities are immutable")
        object.__setattr__(self, "registry_id", registry_id)
        object.__setattr__(self, "entries", entries)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "registry_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact.artifact_id,
                    "artifact_sha256": self.artifact.content_sha256,
                    "as_of_utc": as_of,
                    "entry_hashes": [item.entry_hash for item in entries],
                    "registry_id": registry_id,
                }
            ),
        )
