from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


def _digest(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


@dataclass(frozen=True)
class BTCPerpetualPaperStressEvaluationReadinessSnapshot:
    gate_id: str
    complete_rule_bundle_hash: str
    coverage_snapshot_hash: str
    input_domain_snapshot_hash: str
    input_registry_hash: str
    venue_id: str
    contract_id: str
    rule_effective_at_utc: str
    coverage_as_of_utc: str
    input_as_of_utc: str
    scenario_kinds: tuple[str, ...]
    definition_hashes: tuple[str, ...]
    observation_hashes: tuple[str, ...]
    parameter_schema_hash: str
    domain_schema_hash: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    readiness_only: bool = True
    coherence_validated: bool = True
    source_selected: bool = False
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-evaluation-readiness-v1"
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("gate_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digests = {
            name: _digest(getattr(self, name), name)
            for name in (
                "complete_rule_bundle_hash",
                "coverage_snapshot_hash",
                "input_domain_snapshot_hash",
                "input_registry_hash",
                "parameter_schema_hash",
                "domain_schema_hash",
            )
        }
        definition_hashes = tuple(
            _digest(value, "definition_hash") for value in self.definition_hashes
        )
        observation_hashes = tuple(
            _digest(value, "observation_hash") for value in self.observation_hashes
        )
        if self.scenario_kinds != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("readiness requires every closed stress scenario kind")
        if len(definition_hashes) != len(BTC_STRESS_SCENARIO_KINDS):
            raise ValueError("readiness requires one definition hash per kind")
        if len(observation_hashes) != len(BTC_STRESS_SCENARIO_KINDS):
            raise ValueError("readiness requires one observation hash per kind")
        rule_at = utc(self.rule_effective_at_utc, "rule_effective_at_utc")
        coverage_at = utc(self.coverage_as_of_utc, "coverage_as_of_utc")
        input_at = utc(self.input_as_of_utc, "input_as_of_utc")
        if not instant(rule_at) <= instant(coverage_at) <= instant(input_at):
            raise ValueError("readiness time lineage must be monotonic")
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
            or self.readiness_only is not True
            or self.coherence_validated is not True
            or any(forbidden)
        ):
            raise ValueError("readiness cannot evaluate, calculate, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("readiness authority identities are immutable")
        if self.schema_version != "btc-perpetual-paper-stress-evaluation-readiness-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "rule_effective_at_utc", rule_at)
        object.__setattr__(self, "coverage_as_of_utc", coverage_at)
        object.__setattr__(self, "input_as_of_utc", input_at)
        object.__setattr__(self, "definition_hashes", definition_hashes)
        object.__setattr__(self, "observation_hashes", observation_hashes)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "complete_rule_bundle_hash": digests[
                        "complete_rule_bundle_hash"
                    ],
                    "contract_id": self.contract_id,
                    "coverage_as_of_utc": coverage_at,
                    "coverage_snapshot_hash": digests["coverage_snapshot_hash"],
                    "definition_hashes": list(definition_hashes),
                    "domain_schema_hash": digests["domain_schema_hash"],
                    "gate_id": self.gate_id,
                    "input_as_of_utc": input_at,
                    "input_domain_snapshot_hash": digests[
                        "input_domain_snapshot_hash"
                    ],
                    "input_registry_hash": digests["input_registry_hash"],
                    "observation_hashes": list(observation_hashes),
                    "parameter_schema_hash": digests["parameter_schema_hash"],
                    "rule_effective_at_utc": rule_at,
                    "scenario_kinds": list(self.scenario_kinds),
                    "schema_version": self.schema_version,
                    "venue_id": self.venue_id,
                }
            ),
        )
