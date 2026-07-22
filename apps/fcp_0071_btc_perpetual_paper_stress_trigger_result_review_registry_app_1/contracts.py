from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
    decimal_text,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
    BTC_STRESS_SEVERITIES,
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
class BTCPerpetualPaperStressTriggerResultReviewRecord:
    scenario_kind: str
    scenario_id: str
    version_id: str
    definition_hash: str
    severity: str
    horizon_seconds: int
    result_hash: str
    evaluation_snapshot_hash: str
    formula_family_id: str
    comparison_operator_id: str
    measure_value: Decimal
    measure_unit_id: str
    transformed_parameter_value: Decimal
    parameter_unit_id: str
    triggered: bool
    operator_review_status: str = "PENDING_OPERATOR_REVIEW"
    review_record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        kind = str(self.scenario_kind).strip().upper()
        severity = str(self.severity).strip().upper()
        if kind not in BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("scenario_kind is not registered")
        if severity not in BTC_STRESS_SEVERITIES:
            raise ValueError("severity is not registered")
        for name in (
            "scenario_id",
            "version_id",
            "formula_family_id",
            "comparison_operator_id",
            "measure_unit_id",
            "parameter_unit_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        if (
            isinstance(self.horizon_seconds, bool)
            or not isinstance(self.horizon_seconds, int)
            or self.horizon_seconds <= 0
        ):
            raise ValueError("horizon_seconds must be a positive integer")
        definition_hash = _digest(self.definition_hash, "definition_hash")
        result_hash = _digest(self.result_hash, "result_hash")
        evaluation_hash = _digest(
            self.evaluation_snapshot_hash,
            "evaluation_snapshot_hash",
        )
        measure = _exact_decimal(self.measure_value, "measure_value")
        parameter = _exact_decimal(
            self.transformed_parameter_value,
            "transformed_parameter_value",
        )
        if not isinstance(self.triggered, bool):
            raise ValueError("triggered must be boolean")
        if self.operator_review_status != "PENDING_OPERATOR_REVIEW":
            raise ValueError("review record must remain pending Operator review")
        object.__setattr__(self, "scenario_kind", kind)
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "definition_hash", definition_hash)
        object.__setattr__(self, "result_hash", result_hash)
        object.__setattr__(self, "evaluation_snapshot_hash", evaluation_hash)
        object.__setattr__(self, "measure_value", measure)
        object.__setattr__(self, "transformed_parameter_value", parameter)
        object.__setattr__(
            self,
            "review_record_hash",
            canonical_sha256(
                {
                    "comparison_operator_id": self.comparison_operator_id,
                    "definition_hash": definition_hash,
                    "evaluation_snapshot_hash": evaluation_hash,
                    "formula_family_id": self.formula_family_id,
                    "horizon_seconds": self.horizon_seconds,
                    "measure_unit_id": self.measure_unit_id,
                    "measure_value": decimal_text(measure),
                    "operator_review_status": self.operator_review_status,
                    "parameter_unit_id": self.parameter_unit_id,
                    "result_hash": result_hash,
                    "scenario_id": self.scenario_id,
                    "scenario_kind": kind,
                    "severity": severity,
                    "transformed_parameter_value": decimal_text(parameter),
                    "triggered": self.triggered,
                    "version_id": self.version_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressTriggerResultReviewRegistry:
    registry_id: str
    evaluation_snapshot_hash: str
    scenario_registry_hash: str
    complete_rule_bundle_hash: str
    venue_id: str
    contract_id: str
    evaluated_at_utc: str
    scenario_as_of_utc: str
    registered_at_utc: str
    records: tuple[BTCPerpetualPaperStressTriggerResultReviewRecord, ...]
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    registration_only: bool = True
    recalculation_allowed: bool = False
    recommendation_allowed: bool = False
    account_state_allowed: bool = False
    margin_calculation_allowed: bool = False
    leverage_calculation_allowed: bool = False
    liquidation_action_allowed: bool = False
    balance_calculation_allowed: bool = False
    position_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    insurance_fund_mutation_allowed: bool = False
    adl_action_allowed: bool = False
    order_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-trigger-result-review-registry-v1"
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("registry_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        evaluation_hash = _digest(
            self.evaluation_snapshot_hash,
            "evaluation_snapshot_hash",
        )
        scenario_hash = _digest(self.scenario_registry_hash, "scenario_registry_hash")
        bundle_hash = _digest(
            self.complete_rule_bundle_hash,
            "complete_rule_bundle_hash",
        )
        records = tuple(self.records)
        if not all(
            isinstance(item, BTCPerpetualPaperStressTriggerResultReviewRecord)
            for item in records
        ):
            raise ValueError("review registry requires typed records")
        if tuple(item.scenario_kind for item in records) != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("review records must match every closed scenario kind")
        if any(item.evaluation_snapshot_hash != evaluation_hash for item in records):
            raise ValueError("review record evaluation lineage mismatch")
        if len({item.scenario_id for item in records}) != len(records):
            raise ValueError("review scenario identities must be unique")
        evaluated = utc(self.evaluated_at_utc, "evaluated_at_utc")
        scenario_as_of = utc(self.scenario_as_of_utc, "scenario_as_of_utc")
        registered = utc(self.registered_at_utc, "registered_at_utc")
        if instant(scenario_as_of) > instant(evaluated):
            raise ValueError("evaluation cannot precede scenario evidence")
        if instant(evaluated) > instant(registered):
            raise ValueError("review registration cannot precede evaluation")
        forbidden = (
            self.recalculation_allowed,
            self.recommendation_allowed,
            self.account_state_allowed,
            self.margin_calculation_allowed,
            self.leverage_calculation_allowed,
            self.liquidation_action_allowed,
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
            or self.registration_only is not True
            or any(forbidden)
        ):
            raise ValueError("review registry cannot calculate, recommend, act, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("review registry authority identities are immutable")
        if self.schema_version != (
            "btc-perpetual-paper-stress-trigger-result-review-registry-v1"
        ):
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "evaluation_snapshot_hash", evaluation_hash)
        object.__setattr__(self, "scenario_registry_hash", scenario_hash)
        object.__setattr__(self, "complete_rule_bundle_hash", bundle_hash)
        object.__setattr__(self, "records", records)
        object.__setattr__(self, "evaluated_at_utc", evaluated)
        object.__setattr__(self, "scenario_as_of_utc", scenario_as_of)
        object.__setattr__(self, "registered_at_utc", registered)
        object.__setattr__(
            self,
            "registry_hash",
            canonical_sha256(
                {
                    "complete_rule_bundle_hash": bundle_hash,
                    "contract_id": self.contract_id,
                    "evaluated_at_utc": evaluated,
                    "evaluation_snapshot_hash": evaluation_hash,
                    "record_hashes": [item.review_record_hash for item in records],
                    "registered_at_utc": registered,
                    "registry_id": self.registry_id,
                    "scenario_as_of_utc": scenario_as_of,
                    "scenario_registry_hash": scenario_hash,
                    "schema_version": self.schema_version,
                    "venue_id": self.venue_id,
                }
            ),
        )
