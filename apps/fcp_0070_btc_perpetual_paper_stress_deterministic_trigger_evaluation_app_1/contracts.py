from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
    decimal_text,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.fcp_0067_btc_perpetual_paper_stress_evaluation_measure_formula_semantics_registry_app_1 import (
    BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA,
)
from apps.fcp_0068_btc_perpetual_paper_stress_evaluation_trigger_predicate_semantics_registry_app_1 import (
    BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


_RESULT_SCHEMA = {
    kind: (formula, output_unit, operator)
    for (
        kind,
        formula,
        _roles,
        _parameter_id,
        _parameter_unit,
        output_unit,
        _transform,
        _denominator,
    ), (
        predicate_kind,
        operator,
        _left,
        _right,
        _predicate_transform,
        _boundary,
    ) in zip(
        BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA,
        BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA,
        strict=True,
    )
    if kind == predicate_kind
}


def _digest(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _exact_decimal(value: object, name: str) -> Decimal:
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
class BTCPerpetualPaperStressDeterministicTriggerResult:
    scenario_kind: str
    formula_family_id: str
    comparison_operator_id: str
    measure_value: Decimal
    measure_unit_id: str
    transformed_parameter_value: Decimal
    parameter_unit_id: str
    triggered: bool
    input_binding_hash: str
    predicate_semantics_hash: str
    result_hash: str = field(init=False)

    def __post_init__(self) -> None:
        kind = str(self.scenario_kind).strip().upper()
        if kind not in _RESULT_SCHEMA:
            raise ValueError("scenario_kind is not registered")
        formula = identifier(self.formula_family_id, "formula_family_id")
        operator = identifier(self.comparison_operator_id, "comparison_operator_id")
        measure_unit = identifier(self.measure_unit_id, "measure_unit_id")
        parameter_unit = identifier(self.parameter_unit_id, "parameter_unit_id")
        expected_formula, expected_unit, expected_operator = _RESULT_SCHEMA[kind]
        if (formula, measure_unit, operator) != (
            expected_formula,
            expected_unit,
            expected_operator,
        ):
            raise ValueError("result semantics must match the closed schema")
        measure = _exact_decimal(self.measure_value, "measure_value")
        parameter = _exact_decimal(
            self.transformed_parameter_value,
            "transformed_parameter_value",
        )
        if parameter_unit != expected_unit:
            raise ValueError("result units must match the closed schema")
        if not isinstance(self.triggered, bool):
            raise ValueError("triggered must be boolean")
        binding_hash = _digest(self.input_binding_hash, "input_binding_hash")
        predicate_hash = _digest(
            self.predicate_semantics_hash,
            "predicate_semantics_hash",
        )
        object.__setattr__(self, "scenario_kind", kind)
        object.__setattr__(self, "formula_family_id", formula)
        object.__setattr__(self, "comparison_operator_id", operator)
        object.__setattr__(self, "measure_value", measure)
        object.__setattr__(self, "measure_unit_id", measure_unit)
        object.__setattr__(self, "transformed_parameter_value", parameter)
        object.__setattr__(self, "parameter_unit_id", parameter_unit)
        object.__setattr__(self, "input_binding_hash", binding_hash)
        object.__setattr__(self, "predicate_semantics_hash", predicate_hash)
        object.__setattr__(
            self,
            "result_hash",
            canonical_sha256(
                {
                    "comparison_operator_id": operator,
                    "formula_family_id": formula,
                    "input_binding_hash": binding_hash,
                    "measure_unit_id": measure_unit,
                    "measure_value": decimal_text(measure),
                    "parameter_unit_id": parameter_unit,
                    "predicate_semantics_hash": predicate_hash,
                    "scenario_kind": kind,
                    "transformed_parameter_value": decimal_text(parameter),
                    "triggered": self.triggered,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressDeterministicTriggerEvaluation:
    evaluation_id: str
    input_binding_registry_hash: str
    predicate_registry_hash: str
    operand_evidence_registry_hash: str
    scenario_registry_hash: str
    complete_rule_bundle_hash: str
    venue_id: str
    contract_id: str
    inputs_as_of_utc: str
    evaluated_at_utc: str
    results: tuple[BTCPerpetualPaperStressDeterministicTriggerResult, ...]
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    paper_evaluation_only: bool = True
    evaluation_allowed: bool = True
    calculation_allowed: bool = True
    account_state_allowed: bool = False
    margin_calculation_allowed: bool = False
    leverage_calculation_allowed: bool = False
    liquidation_price_calculation_allowed: bool = False
    balance_calculation_allowed: bool = False
    position_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    insurance_fund_mutation_allowed: bool = False
    adl_action_allowed: bool = False
    order_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = (
        "btc-perpetual-paper-stress-deterministic-trigger-evaluation-v1"
    )
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("evaluation_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digest_names = (
            "input_binding_registry_hash",
            "predicate_registry_hash",
            "operand_evidence_registry_hash",
            "scenario_registry_hash",
            "complete_rule_bundle_hash",
        )
        digests = {name: _digest(getattr(self, name), name) for name in digest_names}
        results = tuple(self.results)
        if not all(
            isinstance(item, BTCPerpetualPaperStressDeterministicTriggerResult)
            for item in results
        ):
            raise ValueError("evaluation requires typed trigger results")
        if tuple(item.scenario_kind for item in results) != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("evaluation results must match every closed scenario kind")
        inputs_as_of = utc(self.inputs_as_of_utc, "inputs_as_of_utc")
        evaluated_at = utc(self.evaluated_at_utc, "evaluated_at_utc")
        if instant(inputs_as_of) > instant(evaluated_at):
            raise ValueError("evaluation cannot precede registered inputs")
        forbidden = (
            self.account_state_allowed,
            self.margin_calculation_allowed,
            self.leverage_calculation_allowed,
            self.liquidation_price_calculation_allowed,
            self.balance_calculation_allowed,
            self.position_calculation_allowed,
            self.pnl_calculation_allowed,
            self.insurance_fund_mutation_allowed,
            self.adl_action_allowed,
            self.order_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_required is not True
            or self.paper_evaluation_only is not True
            or self.evaluation_allowed is not True
            or self.calculation_allowed is not True
            or any(forbidden)
        ):
            raise ValueError("evaluation authority is limited to local Paper calculation")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("evaluation authority identities are immutable")
        if self.schema_version != (
            "btc-perpetual-paper-stress-deterministic-trigger-evaluation-v1"
        ):
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "results", results)
        object.__setattr__(self, "inputs_as_of_utc", inputs_as_of)
        object.__setattr__(self, "evaluated_at_utc", evaluated_at)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "complete_rule_bundle_hash": digests["complete_rule_bundle_hash"],
                    "contract_id": self.contract_id,
                    "evaluated_at_utc": evaluated_at,
                    "evaluation_id": self.evaluation_id,
                    "input_binding_registry_hash": digests[
                        "input_binding_registry_hash"
                    ],
                    "inputs_as_of_utc": inputs_as_of,
                    "operand_evidence_registry_hash": digests[
                        "operand_evidence_registry_hash"
                    ],
                    "predicate_registry_hash": digests["predicate_registry_hash"],
                    "result_hashes": [item.result_hash for item in results],
                    "scenario_registry_hash": digests["scenario_registry_hash"],
                    "schema_version": self.schema_version,
                    "venue_id": self.venue_id,
                }
            ),
        )
