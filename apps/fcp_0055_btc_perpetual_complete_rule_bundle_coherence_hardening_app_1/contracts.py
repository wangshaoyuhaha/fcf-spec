from __future__ import annotations

import re
from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0046_btc_perpetual_venue_contract_lifecycle_registry_app_1 import (
    LIFECYCLE_STATES,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, utc


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


@dataclass(frozen=True)
class BTCPerpetualCompleteRuleBundleSnapshot:
    venue_id: str
    contract_id: str
    effective_at_utc: str
    margin_mode: str
    position_mode: str
    lifecycle_state: str
    base_rule_bundle_hash: str
    contract_registry_hash: str
    margin_registry_hash: str
    funding_registry_hash: str
    fee_registry_hash: str
    liquidation_registry_hash: str
    contract_entry_hash: str
    margin_rule_entry_hash: str
    funding_rule_entry_hash: str
    fee_rule_entry_hash: str
    liquidation_rule_entry_hash: str
    liquidation_effective_from_utc: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    source_selected: bool = False
    account_state_allowed: bool = False
    calculation_allowed: bool = False
    insurance_fund_mutation_allowed: bool = False
    adl_action_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-complete-rule-bundle-snapshot-v1"
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        venue_id = identifier(self.venue_id, "venue_id")
        contract_id = identifier(self.contract_id, "contract_id")
        margin_mode = identifier(self.margin_mode, "margin_mode").upper()
        position_mode = identifier(self.position_mode, "position_mode").upper()
        lifecycle_state = str(self.lifecycle_state).strip().upper()
        if lifecycle_state not in LIFECYCLE_STATES:
            raise ValueError("lifecycle_state is not registered")
        effective_at = utc(self.effective_at_utc, "effective_at_utc")
        liquidation_effective_from = utc(
            self.liquidation_effective_from_utc,
            "liquidation_effective_from_utc",
        )
        digests = {
            name: _digest(getattr(self, name), name)
            for name in (
                "base_rule_bundle_hash",
                "contract_registry_hash",
                "margin_registry_hash",
                "funding_registry_hash",
                "fee_registry_hash",
                "liquidation_registry_hash",
                "contract_entry_hash",
                "margin_rule_entry_hash",
                "funding_rule_entry_hash",
                "fee_rule_entry_hash",
                "liquidation_rule_entry_hash",
            )
        }
        forbidden = (
            self.account_state_allowed,
            self.calculation_allowed,
            self.insurance_fund_mutation_allowed,
            self.adl_action_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if self.operator_review_required is not True or self.source_selected is not False or any(forbidden):
            raise ValueError("complete bundle cannot calculate, mutate, select, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("complete bundle authority identities are immutable")
        if self.schema_version != "btc-perpetual-complete-rule-bundle-snapshot-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "venue_id", venue_id)
        object.__setattr__(self, "contract_id", contract_id)
        object.__setattr__(self, "margin_mode", margin_mode)
        object.__setattr__(self, "position_mode", position_mode)
        object.__setattr__(self, "lifecycle_state", lifecycle_state)
        object.__setattr__(self, "effective_at_utc", effective_at)
        object.__setattr__(
            self,
            "liquidation_effective_from_utc",
            liquidation_effective_from,
        )
        for name, value in digests.items():
            object.__setattr__(self, name, value)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "base_rule_bundle_hash": digests["base_rule_bundle_hash"],
                    "contract_entry_hash": digests["contract_entry_hash"],
                    "contract_id": contract_id,
                    "contract_registry_hash": digests["contract_registry_hash"],
                    "effective_at_utc": effective_at,
                    "fee_registry_hash": digests["fee_registry_hash"],
                    "fee_rule_entry_hash": digests["fee_rule_entry_hash"],
                    "funding_registry_hash": digests["funding_registry_hash"],
                    "funding_rule_entry_hash": digests["funding_rule_entry_hash"],
                    "lifecycle_state": lifecycle_state,
                    "liquidation_effective_from_utc": liquidation_effective_from,
                    "liquidation_registry_hash": digests["liquidation_registry_hash"],
                    "liquidation_rule_entry_hash": digests["liquidation_rule_entry_hash"],
                    "margin_mode": margin_mode,
                    "margin_registry_hash": digests["margin_registry_hash"],
                    "margin_rule_entry_hash": digests["margin_rule_entry_hash"],
                    "position_mode": position_mode,
                    "schema_version": self.schema_version,
                    "venue_id": venue_id,
                }
            ),
        )
