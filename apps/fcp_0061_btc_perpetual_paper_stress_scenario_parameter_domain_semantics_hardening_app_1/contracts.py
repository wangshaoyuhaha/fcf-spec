from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1 import (
    BTC_STRESS_PARAMETER_SCHEMA,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, utc


BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA = (
    (
        "COLLATERAL_DRAWDOWN",
        "collateral-drawdown-rate",
        "ratio",
        "positive-bounded-ratio-zero-one",
    ),
    (
        "FUNDING_SHOCK",
        "funding-rate-shock",
        "ratio",
        "signed-finite-decimal",
    ),
    (
        "LIQUIDATION_DISTANCE",
        "liquidation-distance-rate",
        "ratio",
        "bounded-ratio-zero-one",
    ),
    (
        "LOSS_STREAK",
        "consecutive-loss-count",
        "count",
        "positive-integer",
    ),
    (
        "PRICE_GAP",
        "gap-rate",
        "ratio",
        "positive-bounded-ratio-zero-one",
    ),
    (
        "RESYNC",
        "resync-gap-seconds",
        "seconds",
        "positive-integer",
    ),
    (
        "THIN_BOOK",
        "depth-retention-rate",
        "ratio",
        "bounded-ratio-zero-one",
    ),
    (
        "VENUE_OUTAGE",
        "outage-seconds",
        "seconds",
        "positive-integer",
    ),
)

if tuple(item[0] for item in BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA) != (
    BTC_STRESS_SCENARIO_KINDS
):
    raise RuntimeError("stress parameter domains must match the closed kinds")
if tuple((item[0], ((item[1], item[2]),)) for item in (
    BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA
)) != BTC_STRESS_PARAMETER_SCHEMA:
    raise RuntimeError("stress parameter domains must match the FCP-0057 schema")


def _digest(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


@dataclass(frozen=True)
class BTCPerpetualPaperStressScenarioParameterDomainSnapshot:
    hardening_id: str
    registry_id: str
    registry_hash: str
    coverage_snapshot_hash: str
    complete_rule_bundle_hash: str
    venue_id: str
    contract_id: str
    as_of_utc: str
    validated_scenario_kinds: tuple[str, ...]
    validated_definition_hashes: tuple[str, ...]
    parameter_schema_hash: str
    parameter_domain_schema_hash: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    validation_only: bool = True
    domain_validated: bool = True
    direction_defined: bool = False
    source_selected: bool = False
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-parameter-domain-snapshot-v1"
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("hardening_id", "registry_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digests = {
            name: _digest(getattr(self, name), name)
            for name in (
                "registry_hash",
                "coverage_snapshot_hash",
                "complete_rule_bundle_hash",
                "parameter_schema_hash",
                "parameter_domain_schema_hash",
            )
        }
        definition_hashes = tuple(
            _digest(value, "definition_hash")
            for value in self.validated_definition_hashes
        )
        if self.validated_scenario_kinds != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("domain snapshot requires every closed scenario kind")
        if len(definition_hashes) != len(BTC_STRESS_SCENARIO_KINDS):
            raise ValueError("domain snapshot requires one definition hash per kind")
        forbidden = (
            self.direction_defined,
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
            or self.domain_validated is not True
            or any(forbidden)
        ):
            raise ValueError("domain snapshot cannot direct, evaluate, calculate, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("domain snapshot authority identities are immutable")
        if self.schema_version != (
            "btc-perpetual-paper-stress-parameter-domain-snapshot-v1"
        ):
            raise ValueError("schema_version is not registered")
        as_of = utc(self.as_of_utc, "as_of_utc")
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(self, "validated_definition_hashes", definition_hashes)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "as_of_utc": as_of,
                    "complete_rule_bundle_hash": digests[
                        "complete_rule_bundle_hash"
                    ],
                    "contract_id": self.contract_id,
                    "coverage_snapshot_hash": digests["coverage_snapshot_hash"],
                    "hardening_id": self.hardening_id,
                    "parameter_domain_schema_hash": digests[
                        "parameter_domain_schema_hash"
                    ],
                    "parameter_schema_hash": digests["parameter_schema_hash"],
                    "registry_hash": digests["registry_hash"],
                    "registry_id": self.registry_id,
                    "schema_version": self.schema_version,
                    "validated_definition_hashes": list(definition_hashes),
                    "validated_scenario_kinds": list(
                        self.validated_scenario_kinds
                    ),
                    "venue_id": self.venue_id,
                }
            ),
        )
