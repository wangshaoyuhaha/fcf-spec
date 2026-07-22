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
class BTCPerpetualPaperStressEvaluationContextSnapshot:
    gate_id: str
    scenario_registry_id: str
    scenario_registry_hash: str
    extended_readiness_snapshot_hash: str
    operand_evidence_registry_hash: str
    operand_schema_snapshot_hash: str
    complete_rule_bundle_hash: str
    coverage_snapshot_hash: str
    parameter_domain_snapshot_hash: str
    venue_id: str
    contract_id: str
    scenario_registry_as_of_utc: str
    extended_readiness_as_of_utc: str
    operand_evidence_as_of_utc: str
    context_as_of_utc: str
    scenario_kinds: tuple[str, ...]
    scenario_ids: tuple[str, ...]
    version_ids: tuple[str, ...]
    definition_hashes: tuple[str, ...]
    parameter_hash_groups: tuple[tuple[str, ...], ...]
    operand_observation_hashes: tuple[str, ...]
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    context_only: bool = True
    coherence_validated: bool = True
    direction_defined: bool = False
    formula_registered: bool = False
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-evaluation-context-v1"
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "gate_id",
            "scenario_registry_id",
            "venue_id",
            "contract_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digest_names = (
            "scenario_registry_hash",
            "extended_readiness_snapshot_hash",
            "operand_evidence_registry_hash",
            "operand_schema_snapshot_hash",
            "complete_rule_bundle_hash",
            "coverage_snapshot_hash",
            "parameter_domain_snapshot_hash",
        )
        digests = {name: _digest(getattr(self, name), name) for name in digest_names}
        if self.scenario_kinds != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("context requires every closed scenario kind")
        scenario_ids = tuple(identifier(value, "scenario_id") for value in self.scenario_ids)
        version_ids = tuple(identifier(value, "version_id") for value in self.version_ids)
        definition_hashes = tuple(_digest(value, "definition_hash") for value in self.definition_hashes)
        parameter_hash_groups = tuple(
            tuple(_digest(value, "parameter_hash") for value in group)
            for group in self.parameter_hash_groups
        )
        observation_hashes = tuple(
            _digest(value, "operand_observation_hash")
            for value in self.operand_observation_hashes
        )
        count = len(BTC_STRESS_SCENARIO_KINDS)
        if not all(
            len(values) == count
            for values in (
                scenario_ids,
                version_ids,
                definition_hashes,
                parameter_hash_groups,
            )
        ):
            raise ValueError("context requires one definition record per kind")
        if any(not group for group in parameter_hash_groups):
            raise ValueError("context requires typed parameter lineage per kind")
        if len(observation_hashes) != 12:
            raise ValueError("context requires every FCP-0064 operand observation")
        times = {
            name: utc(getattr(self, name), name)
            for name in (
                "scenario_registry_as_of_utc",
                "extended_readiness_as_of_utc",
                "operand_evidence_as_of_utc",
                "context_as_of_utc",
            )
        }
        if not (
            instant(times["scenario_registry_as_of_utc"])
            <= instant(times["extended_readiness_as_of_utc"])
            <= instant(times["operand_evidence_as_of_utc"])
            <= instant(times["context_as_of_utc"])
        ):
            raise ValueError("context UTC lineage must be monotonic")
        forbidden = (
            self.direction_defined,
            self.formula_registered,
            self.evaluation_allowed,
            self.calculation_allowed,
            self.account_state_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_required is not True
            or self.context_only is not True
            or self.coherence_validated is not True
            or any(forbidden)
        ):
            raise ValueError("context cannot direct, formulate, evaluate, calculate, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("context authority identities are immutable")
        if self.schema_version != "btc-perpetual-paper-stress-evaluation-context-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "scenario_ids", scenario_ids)
        object.__setattr__(self, "version_ids", version_ids)
        object.__setattr__(self, "definition_hashes", definition_hashes)
        object.__setattr__(self, "parameter_hash_groups", parameter_hash_groups)
        object.__setattr__(self, "operand_observation_hashes", observation_hashes)
        for name, value in times.items():
            object.__setattr__(self, name, value)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "complete_rule_bundle_hash": digests["complete_rule_bundle_hash"],
                    "context_as_of_utc": times["context_as_of_utc"],
                    "contract_id": self.contract_id,
                    "coverage_snapshot_hash": digests["coverage_snapshot_hash"],
                    "definition_hashes": list(definition_hashes),
                    "extended_readiness_as_of_utc": times["extended_readiness_as_of_utc"],
                    "extended_readiness_snapshot_hash": digests["extended_readiness_snapshot_hash"],
                    "gate_id": self.gate_id,
                    "operand_evidence_as_of_utc": times["operand_evidence_as_of_utc"],
                    "operand_evidence_registry_hash": digests["operand_evidence_registry_hash"],
                    "operand_observation_hashes": list(observation_hashes),
                    "operand_schema_snapshot_hash": digests["operand_schema_snapshot_hash"],
                    "parameter_domain_snapshot_hash": digests["parameter_domain_snapshot_hash"],
                    "parameter_hash_groups": [list(group) for group in parameter_hash_groups],
                    "scenario_ids": list(scenario_ids),
                    "scenario_kinds": list(self.scenario_kinds),
                    "scenario_registry_as_of_utc": times["scenario_registry_as_of_utc"],
                    "scenario_registry_hash": digests["scenario_registry_hash"],
                    "scenario_registry_id": self.scenario_registry_id,
                    "schema_version": self.schema_version,
                    "venue_id": self.venue_id,
                    "version_ids": list(version_ids),
                }
            ),
        )
