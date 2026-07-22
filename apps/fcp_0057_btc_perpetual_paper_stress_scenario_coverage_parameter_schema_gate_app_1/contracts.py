from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, utc


BTC_STRESS_PARAMETER_SCHEMA = (
    ("COLLATERAL_DRAWDOWN", (("collateral-drawdown-rate", "ratio"),)),
    ("FUNDING_SHOCK", (("funding-rate-shock", "ratio"),)),
    ("LIQUIDATION_DISTANCE", (("liquidation-distance-rate", "ratio"),)),
    ("LOSS_STREAK", (("consecutive-loss-count", "count"),)),
    ("PRICE_GAP", (("gap-rate", "ratio"),)),
    ("RESYNC", (("resync-gap-seconds", "seconds"),)),
    ("THIN_BOOK", (("depth-retention-rate", "ratio"),)),
    ("VENUE_OUTAGE", (("outage-seconds", "seconds"),)),
)

if tuple(item[0] for item in BTC_STRESS_PARAMETER_SCHEMA) != BTC_STRESS_SCENARIO_KINDS:
    raise RuntimeError("stress parameter schema must match the closed kind vocabulary")


@dataclass(frozen=True)
class BTCPerpetualPaperStressCoverageSnapshot:
    gate_id: str
    registry_id: str
    registry_hash: str
    complete_rule_bundle_hash: str
    venue_id: str
    contract_id: str
    registry_as_of_utc: str
    covered_scenario_kinds: tuple[str, ...]
    definition_hashes: tuple[str, ...]
    parameter_schema_hash: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    validation_only: bool = True
    coverage_complete: bool = True
    source_selected: bool = False
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-coverage-snapshot-v1"
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("gate_id", "registry_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        as_of = utc(self.registry_as_of_utc, "registry_as_of_utc")
        if self.covered_scenario_kinds != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("coverage snapshot must preserve every closed scenario kind")
        if len(self.definition_hashes) != len(BTC_STRESS_SCENARIO_KINDS):
            raise ValueError("coverage snapshot requires one definition hash per kind")
        digests = (
            self.registry_hash,
            self.complete_rule_bundle_hash,
            self.parameter_schema_hash,
            *self.definition_hashes,
        )
        if any(
            not isinstance(item, str)
            or len(item) != 64
            or any(character not in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise ValueError("coverage snapshot hashes must be lowercase SHA-256")
        forbidden = (
            self.source_selected,
            self.evaluation_allowed,
            self.calculation_allowed,
            self.account_state_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_required is not True
            or self.validation_only is not True
            or self.coverage_complete is not True
            or any(forbidden)
        ):
            raise ValueError("coverage snapshot cannot evaluate, calculate, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("coverage snapshot authority identities are immutable")
        if self.schema_version != "btc-perpetual-paper-stress-coverage-snapshot-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "registry_as_of_utc", as_of)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "complete_rule_bundle_hash": self.complete_rule_bundle_hash,
                    "contract_id": self.contract_id,
                    "covered_scenario_kinds": list(self.covered_scenario_kinds),
                    "definition_hashes": list(self.definition_hashes),
                    "gate_id": self.gate_id,
                    "parameter_schema_hash": self.parameter_schema_hash,
                    "registry_as_of_utc": as_of,
                    "registry_hash": self.registry_hash,
                    "registry_id": self.registry_id,
                    "schema_version": self.schema_version,
                    "venue_id": self.venue_id,
                }
            ),
        )
