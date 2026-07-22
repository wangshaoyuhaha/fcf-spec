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
class BTCPerpetualPaperStressEvaluationInputBinding:
    scenario_kind: str
    predicate_semantics_hash: str
    operand_roles: tuple[str, ...]
    observation_hashes: tuple[str, ...]
    parameter_id: str
    parameter_hash: str
    binding_hash: str = field(init=False)

    def __post_init__(self) -> None:
        kind = str(self.scenario_kind).strip().upper()
        if kind not in BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("scenario_kind is not registered")
        predicate_hash = _digest(
            self.predicate_semantics_hash,
            "predicate_semantics_hash",
        )
        roles = tuple(identifier(value, "operand_role") for value in self.operand_roles)
        observations = tuple(
            _digest(value, "observation_hash") for value in self.observation_hashes
        )
        if not roles or len(roles) != len(observations):
            raise ValueError("operand roles and observations must be aligned")
        if len(roles) != len(set(roles)):
            raise ValueError("operand roles must be unique")
        parameter_id = identifier(self.parameter_id, "parameter_id")
        parameter_hash = _digest(self.parameter_hash, "parameter_hash")
        object.__setattr__(self, "scenario_kind", kind)
        object.__setattr__(self, "predicate_semantics_hash", predicate_hash)
        object.__setattr__(self, "operand_roles", roles)
        object.__setattr__(self, "observation_hashes", observations)
        object.__setattr__(self, "parameter_id", parameter_id)
        object.__setattr__(self, "parameter_hash", parameter_hash)
        object.__setattr__(
            self,
            "binding_hash",
            canonical_sha256(
                {
                    "observation_hashes": list(observations),
                    "operand_roles": list(roles),
                    "parameter_hash": parameter_hash,
                    "parameter_id": parameter_id,
                    "predicate_semantics_hash": predicate_hash,
                    "scenario_kind": kind,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressEvaluationInputBindingRegistry:
    registry_id: str
    predicate_registry_hash: str
    predicate_schema_hash: str
    operand_evidence_registry_hash: str
    operand_schema_snapshot_hash: str
    scenario_registry_hash: str
    complete_rule_bundle_hash: str
    venue_id: str
    contract_id: str
    predicate_as_of_utc: str
    operand_evidence_as_of_utc: str
    scenario_as_of_utc: str
    as_of_utc: str
    bindings: tuple[BTCPerpetualPaperStressEvaluationInputBinding, ...]
    binding_schema_hash: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    input_binding_only: bool = True
    predicate_registered: bool = True
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-evaluation-input-binding-v1"
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("registry_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digest_names = (
            "predicate_registry_hash",
            "predicate_schema_hash",
            "operand_evidence_registry_hash",
            "operand_schema_snapshot_hash",
            "scenario_registry_hash",
            "complete_rule_bundle_hash",
            "binding_schema_hash",
        )
        digests = {name: _digest(getattr(self, name), name) for name in digest_names}
        bindings = tuple(self.bindings)
        if not all(
            isinstance(item, BTCPerpetualPaperStressEvaluationInputBinding)
            for item in bindings
        ):
            raise ValueError("input binding registry requires typed bindings")
        if tuple(item.scenario_kind for item in bindings) != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("input bindings must match every closed scenario kind")
        calculated_schema_hash = canonical_sha256(
            {
                "bindings": [
                    {
                        "observation_hashes": list(item.observation_hashes),
                        "operand_roles": list(item.operand_roles),
                        "parameter_hash": item.parameter_hash,
                        "parameter_id": item.parameter_id,
                        "predicate_semantics_hash": item.predicate_semantics_hash,
                        "scenario_kind": item.scenario_kind,
                    }
                    for item in bindings
                ],
                "schema_version": self.schema_version,
            }
        )
        if digests["binding_schema_hash"] != calculated_schema_hash:
            raise ValueError("binding_schema_hash does not match the closed bindings")
        times = {
            name: utc(getattr(self, name), name)
            for name in (
                "predicate_as_of_utc",
                "operand_evidence_as_of_utc",
                "scenario_as_of_utc",
                "as_of_utc",
            )
        }
        if any(
            instant(times[name]) > instant(times["as_of_utc"])
            for name in (
                "predicate_as_of_utc",
                "operand_evidence_as_of_utc",
                "scenario_as_of_utc",
            )
        ):
            raise ValueError("input binding cannot precede registered inputs")
        forbidden = (
            self.evaluation_allowed,
            self.calculation_allowed,
            self.account_state_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_required is not True
            or self.input_binding_only is not True
            or self.predicate_registered is not True
            or any(forbidden)
        ):
            raise ValueError("input bindings cannot evaluate, calculate, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("input binding authority identities are immutable")
        if self.schema_version != (
            "btc-perpetual-paper-stress-evaluation-input-binding-v1"
        ):
            raise ValueError("schema_version is not registered")
        for name, value in times.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "bindings", bindings)
        object.__setattr__(
            self,
            "registry_hash",
            canonical_sha256(
                {
                    "as_of_utc": times["as_of_utc"],
                    "binding_hashes": [item.binding_hash for item in bindings],
                    "binding_schema_hash": calculated_schema_hash,
                    "complete_rule_bundle_hash": digests["complete_rule_bundle_hash"],
                    "contract_id": self.contract_id,
                    "operand_evidence_as_of_utc": times[
                        "operand_evidence_as_of_utc"
                    ],
                    "operand_evidence_registry_hash": digests[
                        "operand_evidence_registry_hash"
                    ],
                    "operand_schema_snapshot_hash": digests[
                        "operand_schema_snapshot_hash"
                    ],
                    "predicate_as_of_utc": times["predicate_as_of_utc"],
                    "predicate_registry_hash": digests["predicate_registry_hash"],
                    "predicate_schema_hash": digests["predicate_schema_hash"],
                    "registry_id": self.registry_id,
                    "scenario_as_of_utc": times["scenario_as_of_utc"],
                    "scenario_registry_hash": digests["scenario_registry_hash"],
                    "schema_version": self.schema_version,
                    "venue_id": self.venue_id,
                }
            ),
        )
