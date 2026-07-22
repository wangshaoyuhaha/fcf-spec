from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.fcp_0058_btc_perpetual_paper_stress_evaluation_input_evidence_registry_app_1 import (
    BTC_STRESS_EVALUATION_INPUT_SCHEMA,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, utc


BTC_STRESS_EVALUATION_INPUT_DOMAIN_SCHEMA = (
    (
        "COLLATERAL_DRAWDOWN",
        "collateral-index-reference-level",
        "positive-decimal",
    ),
    ("FUNDING_SHOCK", "funding-reference-rate", "signed-finite-decimal"),
    (
        "LIQUIDATION_DISTANCE",
        "liquidation-distance-reference-rate",
        "bounded-ratio-zero-one",
    ),
    ("LOSS_STREAK", "consecutive-loss-reference-count", "nonnegative-integer"),
    ("PRICE_GAP", "mark-reference-price", "positive-decimal"),
    ("RESYNC", "resync-lag-reference-seconds", "nonnegative-integer"),
    ("THIN_BOOK", "bid-ask-depth-reference-notional", "positive-decimal"),
    ("VENUE_OUTAGE", "heartbeat-age-reference-seconds", "nonnegative-integer"),
)

if tuple(item[0] for item in BTC_STRESS_EVALUATION_INPUT_DOMAIN_SCHEMA) != (
    BTC_STRESS_SCENARIO_KINDS
):
    raise RuntimeError("stress input domain schema must match the closed kinds")
if tuple((item[0], item[1]) for item in BTC_STRESS_EVALUATION_INPUT_DOMAIN_SCHEMA) != (
    tuple((item[0], item[1]) for item in BTC_STRESS_EVALUATION_INPUT_SCHEMA)
):
    raise RuntimeError("stress input domains must match the FCP-0058 metric schema")


@dataclass(frozen=True)
class BTCPerpetualPaperStressEvaluationInputDomainSnapshot:
    hardening_id: str
    input_registry_id: str
    input_registry_hash: str
    coverage_snapshot_hash: str
    venue_id: str
    contract_id: str
    as_of_utc: str
    validated_scenario_kinds: tuple[str, ...]
    validated_observation_hashes: tuple[str, ...]
    domain_schema_hash: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    validation_only: bool = True
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-input-domain-snapshot-v1"
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "hardening_id",
            "input_registry_id",
            "venue_id",
            "contract_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digests = (
            self.input_registry_hash,
            self.coverage_snapshot_hash,
            self.domain_schema_hash,
            *self.validated_observation_hashes,
        )
        if any(
            not isinstance(item, str)
            or len(item) != 64
            or any(character not in "0123456789abcdef" for character in item)
            for item in digests
        ):
            raise ValueError("domain snapshot hashes must be lowercase SHA-256")
        if self.validated_scenario_kinds != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("domain snapshot must preserve every closed scenario kind")
        if len(self.validated_observation_hashes) != len(BTC_STRESS_SCENARIO_KINDS):
            raise ValueError("domain snapshot requires one observation hash per kind")
        forbidden = (
            self.evaluation_allowed,
            self.calculation_allowed,
            self.account_state_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_required is not True
            or self.validation_only is not True
            or any(forbidden)
        ):
            raise ValueError("domain snapshot cannot evaluate, calculate, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("domain snapshot authority identities are immutable")
        if self.schema_version != "btc-perpetual-paper-stress-input-domain-snapshot-v1":
            raise ValueError("schema_version is not registered")
        as_of = utc(self.as_of_utc, "as_of_utc")
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "as_of_utc": as_of,
                    "contract_id": self.contract_id,
                    "coverage_snapshot_hash": self.coverage_snapshot_hash,
                    "domain_schema_hash": self.domain_schema_hash,
                    "hardening_id": self.hardening_id,
                    "input_registry_hash": self.input_registry_hash,
                    "input_registry_id": self.input_registry_id,
                    "schema_version": self.schema_version,
                    "validated_observation_hashes": list(
                        self.validated_observation_hashes
                    ),
                    "validated_scenario_kinds": list(self.validated_scenario_kinds),
                    "venue_id": self.venue_id,
                }
            ),
        )
