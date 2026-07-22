from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.fcp_0061_btc_perpetual_paper_stress_scenario_parameter_domain_semantics_hardening_app_1 import (
    BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA,
)
from apps.fcp_0066_btc_perpetual_paper_stress_evaluation_direction_semantics_registry_app_1 import (
    BTC_STRESS_EVALUATION_DIRECTION_SCHEMA,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA = (
    (
        "COLLATERAL_DRAWDOWN",
        "POSITIVE_RELATIVE_DECREASE",
        ("baseline", "current"),
        "collateral-drawdown-rate",
        "ratio",
        "ratio",
        "IDENTITY_PARAMETER",
        "REJECT_NONPOSITIVE_BASELINE",
    ),
    (
        "FUNDING_SHOCK",
        "ABSOLUTE_DIFFERENCE",
        ("baseline", "current"),
        "funding-rate-shock",
        "ratio",
        "ratio",
        "ABSOLUTE_PARAMETER_MAGNITUDE",
        "NOT_APPLICABLE",
    ),
    (
        "LIQUIDATION_DISTANCE",
        "DIRECT_OBSERVATION",
        ("observed",),
        "liquidation-distance-rate",
        "ratio",
        "ratio",
        "IDENTITY_PARAMETER",
        "NOT_APPLICABLE",
    ),
    (
        "LOSS_STREAK",
        "DIRECT_OBSERVATION",
        ("observed",),
        "consecutive-loss-count",
        "count",
        "count",
        "IDENTITY_PARAMETER",
        "NOT_APPLICABLE",
    ),
    (
        "PRICE_GAP",
        "ABSOLUTE_RELATIVE_DIFFERENCE",
        ("baseline", "current"),
        "gap-rate",
        "ratio",
        "ratio",
        "IDENTITY_PARAMETER",
        "REJECT_NONPOSITIVE_BASELINE",
    ),
    (
        "RESYNC",
        "DIRECT_OBSERVATION",
        ("observed",),
        "resync-gap-seconds",
        "seconds",
        "seconds",
        "IDENTITY_PARAMETER",
        "NOT_APPLICABLE",
    ),
    (
        "THIN_BOOK",
        "CURRENT_BASELINE_RETENTION_RATIO",
        ("baseline", "current"),
        "depth-retention-rate",
        "ratio",
        "ratio",
        "IDENTITY_PARAMETER",
        "REJECT_NONPOSITIVE_BASELINE",
    ),
    (
        "VENUE_OUTAGE",
        "DIRECT_OBSERVATION",
        ("observed",),
        "outage-seconds",
        "seconds",
        "seconds",
        "IDENTITY_PARAMETER",
        "NOT_APPLICABLE",
    ),
)

if tuple(item[0] for item in BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA) != (
    BTC_STRESS_SCENARIO_KINDS
):
    raise RuntimeError("stress formula schema must match the closed scenario kinds")

_DIRECTION_ROLES_BY_KIND = {
    kind: roles
    for kind, _direction, _comparison, roles, _equality in (
        BTC_STRESS_EVALUATION_DIRECTION_SCHEMA
    )
}
_PARAMETERS_BY_KIND = {
    kind: (parameter_id, unit_id)
    for kind, parameter_id, unit_id, _domain in (
        BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA
    )
}
if any(
    roles != _DIRECTION_ROLES_BY_KIND[kind]
    or (parameter_id, parameter_unit_id) != _PARAMETERS_BY_KIND[kind]
    for (
        kind,
        _formula,
        roles,
        parameter_id,
        parameter_unit_id,
        _output_unit,
        _transform,
        _denominator,
    ) in BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA
):
    raise RuntimeError("stress formulas must match direction roles and parameters")

_FORMULA_BY_KIND = {
    item[0]: item[1:] for item in BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA
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
class BTCPerpetualPaperStressMeasureFormulaSemantics:
    scenario_kind: str
    formula_family_id: str
    operand_roles: tuple[str, ...]
    parameter_id: str
    parameter_unit_id: str
    output_unit_id: str
    parameter_transform_id: str
    denominator_policy_id: str
    semantics_hash: str = field(init=False)

    def __post_init__(self) -> None:
        kind = str(self.scenario_kind).strip().upper()
        if kind not in _FORMULA_BY_KIND:
            raise ValueError("scenario_kind is not registered")
        values = (
            identifier(self.formula_family_id, "formula_family_id"),
            tuple(identifier(value, "operand_role") for value in self.operand_roles),
            identifier(self.parameter_id, "parameter_id"),
            identifier(self.parameter_unit_id, "parameter_unit_id"),
            identifier(self.output_unit_id, "output_unit_id"),
            identifier(self.parameter_transform_id, "parameter_transform_id"),
            identifier(self.denominator_policy_id, "denominator_policy_id"),
        )
        if values != _FORMULA_BY_KIND[kind]:
            raise ValueError("formula semantics must match the closed kind schema")
        (
            formula_family_id,
            roles,
            parameter_id,
            parameter_unit_id,
            output_unit_id,
            parameter_transform_id,
            denominator_policy_id,
        ) = values
        object.__setattr__(self, "scenario_kind", kind)
        object.__setattr__(self, "formula_family_id", formula_family_id)
        object.__setattr__(self, "operand_roles", roles)
        object.__setattr__(self, "parameter_id", parameter_id)
        object.__setattr__(self, "parameter_unit_id", parameter_unit_id)
        object.__setattr__(self, "output_unit_id", output_unit_id)
        object.__setattr__(self, "parameter_transform_id", parameter_transform_id)
        object.__setattr__(self, "denominator_policy_id", denominator_policy_id)
        object.__setattr__(
            self,
            "semantics_hash",
            canonical_sha256(
                {
                    "denominator_policy_id": denominator_policy_id,
                    "formula_family_id": formula_family_id,
                    "operand_roles": list(roles),
                    "output_unit_id": output_unit_id,
                    "parameter_id": parameter_id,
                    "parameter_transform_id": parameter_transform_id,
                    "parameter_unit_id": parameter_unit_id,
                    "scenario_kind": kind,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressMeasureFormulaSemanticsRegistry:
    registry_id: str
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
    direction_as_of_utc: str
    as_of_utc: str
    scenario_kinds: tuple[str, ...]
    semantics: tuple[BTCPerpetualPaperStressMeasureFormulaSemantics, ...]
    formula_schema_hash: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    formula_semantics_only: bool = True
    direction_defined: bool = True
    formula_registered: bool = True
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-measure-formula-semantics-v1"
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("registry_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digest_names = (
            "direction_registry_hash",
            "direction_schema_hash",
            "evaluation_context_snapshot_hash",
            "scenario_registry_hash",
            "extended_readiness_snapshot_hash",
            "operand_evidence_registry_hash",
            "operand_schema_snapshot_hash",
            "complete_rule_bundle_hash",
            "formula_schema_hash",
        )
        digests = {name: _digest(getattr(self, name), name) for name in digest_names}
        semantics = tuple(self.semantics)
        if not all(
            isinstance(item, BTCPerpetualPaperStressMeasureFormulaSemantics)
            for item in semantics
        ):
            raise ValueError("formula registry requires typed semantics")
        observed = tuple(
            (
                item.scenario_kind,
                item.formula_family_id,
                item.operand_roles,
                item.parameter_id,
                item.parameter_unit_id,
                item.output_unit_id,
                item.parameter_transform_id,
                item.denominator_policy_id,
            )
            for item in semantics
        )
        if observed != BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA:
            raise ValueError("formula semantics must match the closed schema exactly")
        if self.scenario_kinds != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("formula registry requires every closed scenario kind")
        calculated_schema_hash = canonical_sha256(
            {
                "schema_version": self.schema_version,
                "semantics": [
                    {
                        "denominator_policy_id": item.denominator_policy_id,
                        "formula_family_id": item.formula_family_id,
                        "operand_roles": list(item.operand_roles),
                        "output_unit_id": item.output_unit_id,
                        "parameter_id": item.parameter_id,
                        "parameter_transform_id": item.parameter_transform_id,
                        "parameter_unit_id": item.parameter_unit_id,
                        "scenario_kind": item.scenario_kind,
                    }
                    for item in semantics
                ],
            }
        )
        if digests["formula_schema_hash"] != calculated_schema_hash:
            raise ValueError("formula_schema_hash does not match the closed schema")
        direction_as_of = utc(self.direction_as_of_utc, "direction_as_of_utc")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(direction_as_of) > instant(as_of):
            raise ValueError("formula registry cannot precede direction registry")
        forbidden = (
            self.evaluation_allowed,
            self.calculation_allowed,
            self.account_state_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_required is not True
            or self.formula_semantics_only is not True
            or self.direction_defined is not True
            or self.formula_registered is not True
            or any(forbidden)
        ):
            raise ValueError("formula registry cannot evaluate, calculate, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("formula registry authority identities are immutable")
        if self.schema_version != (
            "btc-perpetual-paper-stress-measure-formula-semantics-v1"
        ):
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "direction_as_of_utc", direction_as_of)
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
                    "direction_as_of_utc": direction_as_of,
                    "direction_registry_hash": digests["direction_registry_hash"],
                    "direction_schema_hash": digests["direction_schema_hash"],
                    "evaluation_context_snapshot_hash": digests[
                        "evaluation_context_snapshot_hash"
                    ],
                    "extended_readiness_snapshot_hash": digests[
                        "extended_readiness_snapshot_hash"
                    ],
                    "formula_schema_hash": calculated_schema_hash,
                    "operand_evidence_registry_hash": digests[
                        "operand_evidence_registry_hash"
                    ],
                    "operand_schema_snapshot_hash": digests[
                        "operand_schema_snapshot_hash"
                    ],
                    "registry_id": self.registry_id,
                    "scenario_kinds": list(self.scenario_kinds),
                    "scenario_registry_hash": digests["scenario_registry_hash"],
                    "schema_version": self.schema_version,
                    "semantics_hashes": [item.semantics_hash for item in semantics],
                    "venue_id": self.venue_id,
                }
            ),
        )
