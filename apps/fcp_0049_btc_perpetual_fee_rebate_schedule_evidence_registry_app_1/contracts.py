from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import canonical_sha256, decimal_text
from apps.fcp_0046_btc_perpetual_venue_contract_lifecycle_registry_app_1 import BTCPerpetualContractLifecycleRegistry
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import LocalEventRights, identifier, instant, utc


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _decimal(value: object, name: str) -> Decimal:
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
class RegisteredBTCFeeRebateRuleArtifact:
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
class BTCFeeRebateTier:
    tier_id: str
    trailing_volume_floor: Decimal
    trailing_volume_cap: Decimal
    maker_rate: Decimal
    taker_rate: Decimal
    tier_hash: str = field(init=False)

    def __post_init__(self) -> None:
        tier_id = identifier(self.tier_id, "tier_id")
        floor = _decimal(self.trailing_volume_floor, "trailing_volume_floor")
        cap = _decimal(self.trailing_volume_cap, "trailing_volume_cap")
        maker = _decimal(self.maker_rate, "maker_rate")
        taker = _decimal(self.taker_rate, "taker_rate")
        if floor < 0 or cap <= floor:
            raise ValueError("volume tier interval must be nonnegative and increasing")
        if not (Decimal("-1") <= maker <= Decimal("1")) or not (Decimal("-1") <= taker <= Decimal("1")):
            raise ValueError("fee or rebate rate must be a signed unit rate")
        object.__setattr__(self, "tier_id", tier_id)
        object.__setattr__(self, "trailing_volume_floor", floor)
        object.__setattr__(self, "trailing_volume_cap", cap)
        object.__setattr__(self, "maker_rate", maker)
        object.__setattr__(self, "taker_rate", taker)
        object.__setattr__(
            self,
            "tier_hash",
            canonical_sha256(
                {
                    "maker_rate": decimal_text(maker),
                    "taker_rate": decimal_text(taker),
                    "tier_id": tier_id,
                    "trailing_volume_cap": decimal_text(cap),
                    "trailing_volume_floor": decimal_text(floor),
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualFeeRebateRuleVersion:
    entry_id: str
    version_id: str
    artifact_id: str
    contract_entry_hash: str
    venue_id: str
    contract_id: str
    measurement_asset: str
    trailing_window_seconds: int
    fee_assets: tuple[str, ...]
    tiers: tuple[BTCFeeRebateTier, ...]
    effective_from_utc: str
    effective_to_utc: str | None
    schema_version: str = "btc-perpetual-fee-rebate-rule-version-v1"
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("entry_id", "version_id", "artifact_id", "venue_id", "contract_id", "measurement_asset"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "contract_entry_hash", _digest(self.contract_entry_hash, "contract_entry_hash"))
        if isinstance(self.trailing_window_seconds, bool) or not isinstance(self.trailing_window_seconds, int) or self.trailing_window_seconds <= 0:
            raise ValueError("trailing_window_seconds must be a positive integer")
        fee_assets = tuple(identifier(item, "fee_asset") for item in self.fee_assets)
        if not fee_assets or fee_assets != tuple(sorted(set(fee_assets))):
            raise ValueError("fee assets must be nonempty, ordered, and unique")
        tiers = tuple(self.tiers)
        if not tiers or not all(isinstance(item, BTCFeeRebateTier) for item in tiers):
            raise ValueError("fee schedule requires typed tiers")
        keys = tuple((item.trailing_volume_floor, item.tier_id) for item in tiers)
        if keys != tuple(sorted(keys)) or len({item.tier_id for item in tiers}) != len(tiers):
            raise ValueError("fee tiers must be deterministically ordered and unique")
        if tiers[0].trailing_volume_floor != 0:
            raise ValueError("fee tiers must begin at zero volume")
        for left, right in zip(tiers, tiers[1:]):
            if left.trailing_volume_cap != right.trailing_volume_floor:
                raise ValueError("fee tiers must be contiguous and nonoverlapping")
        effective_from = utc(self.effective_from_utc, "effective_from_utc")
        effective_to = utc(self.effective_to_utc, "effective_to_utc") if self.effective_to_utc is not None else None
        if effective_to is not None and instant(effective_to) <= instant(effective_from):
            raise ValueError("effective interval must be strictly increasing")
        if self.schema_version != "btc-perpetual-fee-rebate-rule-version-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "fee_assets", fee_assets)
        object.__setattr__(self, "tiers", tiers)
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
                    "fee_assets": fee_assets,
                    "measurement_asset": self.measurement_asset,
                    "schema_version": self.schema_version,
                    "tier_hashes": [item.tier_hash for item in tiers],
                    "trailing_window_seconds": self.trailing_window_seconds,
                    "venue_id": self.venue_id,
                    "version_id": self.version_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualFeeRebateScheduleRegistry:
    registry_id: str
    artifact: RegisteredBTCFeeRebateRuleArtifact
    contract_registry: BTCPerpetualContractLifecycleRegistry
    versions: tuple[BTCPerpetualFeeRebateRuleVersion, ...]
    as_of_utc: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    source_selected: bool = False
    account_tier_selection_allowed: bool = False
    fee_calculation_allowed: bool = False
    rebate_calculation_allowed: bool = False
    balance_calculation_allowed: bool = False
    position_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    liquidation_calculation_allowed: bool = False
    funding_calculation_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        registry_id = identifier(self.registry_id, "registry_id")
        if not isinstance(self.artifact, RegisteredBTCFeeRebateRuleArtifact):
            raise ValueError("registry requires a typed fee artifact")
        if not isinstance(self.contract_registry, BTCPerpetualContractLifecycleRegistry):
            raise ValueError("registry requires typed FCP-0046 contract evidence")
        versions = tuple(self.versions)
        if not versions or not all(isinstance(item, BTCPerpetualFeeRebateRuleVersion) for item in versions):
            raise ValueError("registry requires typed fee rule versions")
        keys = tuple((item.venue_id, item.contract_id, item.effective_from_utc) for item in versions)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("fee versions must be deterministically ordered and unique")
        if len({item.entry_id for item in versions}) != len(versions) or len({item.version_id for item in versions}) != len(versions):
            raise ValueError("fee entry and version identities must be unique")
        if any(item.artifact_id != self.artifact.artifact_id for item in versions):
            raise ValueError("fee version artifact lineage mismatch")
        contract_entries = {item.entry_hash: (item.venue_id, item.contract_id) for item in self.contract_registry.entries}
        if any(contract_entries.get(item.contract_entry_hash) != (item.venue_id, item.contract_id) for item in versions):
            raise ValueError("FCP-0046 contract lineage mismatch")
        groups: dict[tuple[str, str], list[BTCPerpetualFeeRebateRuleVersion]] = {}
        for item in versions:
            groups.setdefault((item.venue_id, item.contract_id), []).append(item)
        for items in groups.values():
            for left, right in zip(items, items[1:]):
                if left.effective_to_utc is None or instant(left.effective_to_utc) > instant(right.effective_from_utc):
                    raise ValueError("fee effective intervals overlap")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(self.artifact.registered_at_utc) > instant(as_of):
            raise ValueError("registry cannot use evidence after as_of_utc")
        if instant(self.contract_registry.as_of_utc) > instant(as_of):
            raise ValueError("contract registry cannot be newer than fee registry")
        forbidden = (
            self.account_tier_selection_allowed,
            self.fee_calculation_allowed,
            self.rebate_calculation_allowed,
            self.balance_calculation_allowed,
            self.position_calculation_allowed,
            self.pnl_calculation_allowed,
            self.liquidation_calculation_allowed,
            self.funding_calculation_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if self.operator_review_required is not True or self.source_selected is not False or any(forbidden):
            raise ValueError("registry cannot calculate, select, execute, or close")
        if self.calculation_authority != "DETERMINISTIC_ENGINE" or self.evidence_authority != "REGISTERED_EVIDENCE" or self.ai_role != "ADVISORY_ONLY":
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
