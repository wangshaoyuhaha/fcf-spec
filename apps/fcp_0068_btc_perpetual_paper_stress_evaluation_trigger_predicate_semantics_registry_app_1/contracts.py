from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.fcp_0066_btc_perpetual_paper_stress_evaluation_direction_semantics_registry_app_1 import (
    BTC_STRESS_EVALUATION_DIRECTION_SCHEMA,
)
from apps.fcp_0067_btc_perpetual_paper_stress_evaluation_measure_formula_semantics_registry_app_1 import (
    BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA = (
    (
        "COLLATERAL_DRAWDOWN",
        "MEASURE_GREATER_THAN_PARAMETER",
        "measure",
        "parameter",
        "IDENTITY_PARAMETER",
        "STRICT_BOUNDARY",
    ),
    (
        "FUNDING_SHOCK",
        "MEASURE_GREATER_THAN_PARAMETER",
        "measure",
        "parameter",
        "ABSOLUTE_PARAMETER_MAGNITUDE",
        "STRICT_BOUNDARY",
    ),
    (
        "LIQUIDATION_DISTANCE",
        "MEASURE_LESS_THAN_OR_EQUAL_PARAMETER",
        "measure",
        "parameter",
        "IDENTITY_PARAMETER",
        "INCLUSIVE_BOUNDARY",
    ),
    (
        "LOSS_STREAK",
        "MEASURE_GREATER_THAN_OR_EQUAL_PARAMETER",
        "measure",
        "parameter",
        "IDENTITY_PARAMETER",
        "INCLUSIVE_BOUNDARY",
    ),
    (
        "PRICE_GAP",
        "MEASURE_GREATER_THAN_PARAMETER",
        "measure",
        "parameter",
        "IDENTITY_PARAMETER",
        "STRICT_BOUNDARY",
    ),
    (
        "RESYNC",
        "MEASURE_GREATER_THAN_OR_EQUAL_PARAMETER",
        "measure",
        "parameter",
        "IDENTITY_PARAMETER",
        "INCLUSIVE_BOUNDARY",
    ),
    (
        "THIN_BOOK",
        "MEASURE_LESS_THAN_PARAMETER",
        "measure",
        "parameter",
        "IDENTITY_PARAMETER",
        "STRICT_BOUNDARY",
    ),
    (
        "VENUE_OUTAGE",
        "MEASURE_GREATER_THAN_OR_EQUAL_PARAMETER",
        "measure",
        "parameter",
        "IDENTITY_PARAMETER",
        "INCLUSIVE_BOUNDARY",
    ),
)

if tuple(item[0] for item in BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA) != (
    BTC_STRESS_SCENARIO_KINDS
):
    raise RuntimeError("stress predicate schema must match the closed scenario kinds")

_FORMULA_SEMANTICS_BY_KIND = {
    kind: (formula, transform)
    for (
        kind,
        formula,
        _roles,
        _parameter,
        _parameter_unit,
        _output_unit,
        transform,
        _denominator,
    ) in BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA
}
_DIRECTION_POLICY_BY_KIND = {
    kind: (direction, equality)
    for kind, direction, _comparison, _roles, equality in (
        BTC_STRESS_EVALUATION_DIRECTION_SCHEMA
    )
}
_MEASURE_DIRECTION_BY_FORMULA = {
    "POSITIVE_RELATIVE_DECREASE": "HIGHER",
    "ABSOLUTE_DIFFERENCE": "HIGHER",
    "ABSOLUTE_RELATIVE_DIFFERENCE": "HIGHER",
    "CURRENT_BASELINE_RETENTION_RATIO": "LOWER",
}


def _expected_operator_and_boundary(kind: str) -> tuple[str, str]:
    formula, _transform = _FORMULA_SEMANTICS_BY_KIND[kind]
    direction, equality = _DIRECTION_POLICY_BY_KIND[kind]
    measure_direction = _MEASURE_DIRECTION_BY_FORMULA.get(formula)
    if measure_direction is None:
        measure_direction = "LOWER" if direction == "LOWER_IS_MORE_STRESSFUL" else "HIGHER"
    inclusive = equality == "EQUALITY_IS_TRIGGERING"
    operator = {
        ("LOWER", False): "MEASURE_LESS_THAN_PARAMETER",
        ("LOWER", True): "MEASURE_LESS_THAN_OR_EQUAL_PARAMETER",
        ("HIGHER", False): "MEASURE_GREATER_THAN_PARAMETER",
        ("HIGHER", True): "MEASURE_GREATER_THAN_OR_EQUAL_PARAMETER",
    }[(measure_direction, inclusive)]
    boundary = "INCLUSIVE_BOUNDARY" if inclusive else "STRICT_BOUNDARY"
    return operator, boundary


if any(
    transform != _FORMULA_SEMANTICS_BY_KIND[kind][1]
    or (operator, boundary) != _expected_operator_and_boundary(kind)
    for kind, operator, _left, _right, transform, boundary in (
        BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA
    )
):
    raise RuntimeError("stress predicates must match formula and direction semantics")

_PREDICATE_BY_KIND = {
    item[0]: item[1:] for item in BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA
}


def _digest(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


@dataclass(frozen=True)
class BTCPerpetualPaperStressTriggerPredicateSemantics:
    scenario_kind: str
    comparison_operator_id: str
    left_role_id: str
    right_role_id: str
    parameter_transform_id: str
    boundary_policy_id: str
    semantics_hash: str = field(init=False)

    def __post_init__(self) -> None:
        kind = str(self.scenario_kind).strip().upper()
        if kind not in _PREDICATE_BY_KIND:
            raise ValueError("scenario_kind is not registered")
        values = tuple(
            identifier(value, name)
            for value, name in (
                (self.comparison_operator_id, "comparison_operator_id"),
                (self.left_role_id, "left_role_id"),
                (self.right_role_id, "right_role_id"),
                (self.parameter_transform_id, "parameter_transform_id"),
                (self.boundary_policy_id, "boundary_policy_id"),
            )
        )
        if values != _PREDICATE_BY_KIND[kind]:
            raise ValueError("predicate semantics must match the closed kind schema")
        (
            comparison_operator_id,
            left_role_id,
            right_role_id,
            parameter_transform_id,
            boundary_policy_id,
        ) = values
        object.__setattr__(self, "scenario_kind", kind)
        object.__setattr__(self, "comparison_operator_id", comparison_operator_id)
        object.__setattr__(self, "left_role_id", left_role_id)
        object.__setattr__(self, "right_role_id", right_role_id)
        object.__setattr__(self, "parameter_transform_id", parameter_transform_id)
        object.__setattr__(self, "boundary_policy_id", boundary_policy_id)
        object.__setattr__(
            self,
            "semantics_hash",
            canonical_sha256(
                {
                    "boundary_policy_id": boundary_policy_id,
                    "comparison_operator_id": comparison_operator_id,
                    "left_role_id": left_role_id,
                    "parameter_transform_id": parameter_transform_id,
                    "right_role_id": right_role_id,
                    "scenario_kind": kind,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressTriggerPredicateSemanticsRegistry:
    registry_id: str
    formula_registry_hash: str
    formula_schema_hash: str
    direction_registry_hash: str
    direction_schema_hash: str
    evaluation_context_snapshot_hash: str
    scenario_registry_hash: str
    extended_readiness_snapshot_hash: str
    operand_evidence_registry_hash: str
    operand_schema_snapshot_hash: str
    complete_rule_bundle_hash: str
    venue_id: str
    contract_id: str
    formula_as_of_utc: str
    as_of_utc: str
    scenario_kinds: tuple[str, ...]
    semantics: tuple[BTCPerpetualPaperStressTriggerPredicateSemantics, ...]
    predicate_schema_hash: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    predicate_semantics_only: bool = True
    direction_defined: bool = True
    formula_registered: bool = True
    predicate_registered: bool = True
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-trigger-predicate-semantics-v1"
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("registry_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digest_names = (
            "formula_registry_hash",
            "formula_schema_hash",
            "direction_registry_hash",
            "direction_schema_hash",
            "evaluation_context_snapshot_hash",
            "scenario_registry_hash",
            "extended_readiness_snapshot_hash",
            "operand_evidence_registry_hash",
            "operand_schema_snapshot_hash",
            "complete_rule_bundle_hash",
            "predicate_schema_hash",
        )
        digests = {name: _digest(getattr(self, name), name) for name in digest_names}
        semantics = tuple(self.semantics)
        if not all(
            isinstance(item, BTCPerpetualPaperStressTriggerPredicateSemantics)
            for item in semantics
        ):
            raise ValueError("predicate registry requires typed semantics")
        observed = tuple(
            (
                item.scenario_kind,
                item.comparison_operator_id,
                item.left_role_id,
                item.right_role_id,
                item.parameter_transform_id,
                item.boundary_policy_id,
            )
            for item in semantics
        )
        if observed != BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA:
            raise ValueError("predicate semantics must match the closed schema exactly")
        if self.scenario_kinds != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("predicate registry requires every closed scenario kind")
        calculated_schema_hash = canonical_sha256(
            {
                "schema_version": self.schema_version,
                "semantics": [
                    {
                        "boundary_policy_id": item.boundary_policy_id,
                        "comparison_operator_id": item.comparison_operator_id,
                        "left_role_id": item.left_role_id,
                        "parameter_transform_id": item.parameter_transform_id,
                        "right_role_id": item.right_role_id,
                        "scenario_kind": item.scenario_kind,
                    }
                    for item in semantics
                ],
            }
        )
        if digests["predicate_schema_hash"] != calculated_schema_hash:
            raise ValueError("predicate_schema_hash does not match the closed schema")
        formula_as_of = utc(self.formula_as_of_utc, "formula_as_of_utc")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(formula_as_of) > instant(as_of):
            raise ValueError("predicate registry cannot precede formula registry")
        forbidden = (
            self.evaluation_allowed,
            self.calculation_allowed,
            self.account_state_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_required is not True
            or self.predicate_semantics_only is not True
            or self.direction_defined is not True
            or self.formula_registered is not True
            or self.predicate_registered is not True
            or any(forbidden)
        ):
            raise ValueError(
                "predicate registry cannot evaluate, calculate, execute, or close"
            )
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("predicate registry authority identities are immutable")
        if self.schema_version != (
            "btc-perpetual-paper-stress-trigger-predicate-semantics-v1"
        ):
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "formula_as_of_utc", formula_as_of)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(self, "semantics", semantics)
        object.__setattr__(
            self,
            "registry_hash",
            canonical_sha256(
                {
                    "as_of_utc": as_of,
                    "complete_rule_bundle_hash": digests["complete_rule_bundle_hash"],
                    "contract_id": self.contract_id,
                    "direction_registry_hash": digests["direction_registry_hash"],
                    "direction_schema_hash": digests["direction_schema_hash"],
                    "evaluation_context_snapshot_hash": digests[
                        "evaluation_context_snapshot_hash"
                    ],
                    "extended_readiness_snapshot_hash": digests[
                        "extended_readiness_snapshot_hash"
                    ],
                    "formula_as_of_utc": formula_as_of,
                    "formula_registry_hash": digests["formula_registry_hash"],
                    "formula_schema_hash": digests["formula_schema_hash"],
                    "operand_evidence_registry_hash": digests[
                        "operand_evidence_registry_hash"
                    ],
                    "operand_schema_snapshot_hash": digests[
                        "operand_schema_snapshot_hash"
                    ],
                    "predicate_schema_hash": calculated_schema_hash,
                    "registry_id": self.registry_id,
                    "scenario_kinds": list(self.scenario_kinds),
                    "scenario_registry_hash": digests["scenario_registry_hash"],
                    "schema_version": self.schema_version,
                    "semantics_hashes": [item.semantics_hash for item in semantics],
                    "venue_id": self.venue_id,
                }
            ),
        )
