from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.fcp_0063_btc_perpetual_paper_stress_evaluation_operand_schema_registry_app_1 import (
    BTC_STRESS_EVALUATION_OPERAND_SCHEMA,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


BTC_STRESS_EVALUATION_DIRECTION_SCHEMA = (
    (
        "COLLATERAL_DRAWDOWN",
        "LOWER_IS_MORE_STRESSFUL",
        "BASELINE_CURRENT_DECREASE",
        ("baseline", "current"),
        "EQUALITY_IS_NON_TRIGGERING",
    ),
    (
        "FUNDING_SHOCK",
        "ABSOLUTE_DIVERGENCE_IS_MORE_STRESSFUL",
        "BASELINE_CURRENT_ABSOLUTE_DIVERGENCE",
        ("baseline", "current"),
        "EQUALITY_IS_NON_TRIGGERING",
    ),
    (
        "LIQUIDATION_DISTANCE",
        "LOWER_IS_MORE_STRESSFUL",
        "OBSERVED_LOWER_BOUND",
        ("observed",),
        "EQUALITY_IS_TRIGGERING",
    ),
    (
        "LOSS_STREAK",
        "HIGHER_IS_MORE_STRESSFUL",
        "OBSERVED_UPPER_BOUND",
        ("observed",),
        "EQUALITY_IS_TRIGGERING",
    ),
    (
        "PRICE_GAP",
        "ABSOLUTE_DIVERGENCE_IS_MORE_STRESSFUL",
        "BASELINE_CURRENT_ABSOLUTE_DIVERGENCE",
        ("baseline", "current"),
        "EQUALITY_IS_NON_TRIGGERING",
    ),
    (
        "RESYNC",
        "HIGHER_IS_MORE_STRESSFUL",
        "OBSERVED_UPPER_BOUND",
        ("observed",),
        "EQUALITY_IS_TRIGGERING",
    ),
    (
        "THIN_BOOK",
        "LOWER_IS_MORE_STRESSFUL",
        "BASELINE_CURRENT_DECREASE",
        ("baseline", "current"),
        "EQUALITY_IS_NON_TRIGGERING",
    ),
    (
        "VENUE_OUTAGE",
        "HIGHER_IS_MORE_STRESSFUL",
        "OBSERVED_UPPER_BOUND",
        ("observed",),
        "EQUALITY_IS_TRIGGERING",
    ),
)

if tuple(item[0] for item in BTC_STRESS_EVALUATION_DIRECTION_SCHEMA) != (
    BTC_STRESS_SCENARIO_KINDS
):
    raise RuntimeError("stress direction schema must match the closed scenario kinds")
_OPERAND_ROLES_BY_KIND = {
    kind: tuple(operand[0] for operand in operands)
    for kind, _mode, operands in BTC_STRESS_EVALUATION_OPERAND_SCHEMA
}
if any(
    operand_roles != _OPERAND_ROLES_BY_KIND[kind]
    for kind, _direction, _comparison, operand_roles, _equality in (
        BTC_STRESS_EVALUATION_DIRECTION_SCHEMA
    )
):
    raise RuntimeError("stress direction roles must match the closed operand schema")

_DIRECTION_BY_KIND = {
    item[0]: item[1:] for item in BTC_STRESS_EVALUATION_DIRECTION_SCHEMA
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
class BTCPerpetualPaperStressDirectionSemantics:
    scenario_kind: str
    direction_id: str
    comparison_family_id: str
    operand_roles: tuple[str, ...]
    equality_policy_id: str
    semantics_hash: str = field(init=False)

    def __post_init__(self) -> None:
        kind = str(self.scenario_kind).strip().upper()
        if kind not in _DIRECTION_BY_KIND:
            raise ValueError("scenario_kind is not registered")
        direction_id = identifier(self.direction_id, "direction_id")
        comparison_family_id = identifier(
            self.comparison_family_id,
            "comparison_family_id",
        )
        roles = tuple(identifier(value, "operand_role") for value in self.operand_roles)
        equality_policy_id = identifier(
            self.equality_policy_id,
            "equality_policy_id",
        )
        if (
            direction_id,
            comparison_family_id,
            roles,
            equality_policy_id,
        ) != _DIRECTION_BY_KIND[kind]:
            raise ValueError("direction semantics must match the closed kind schema")
        object.__setattr__(self, "scenario_kind", kind)
        object.__setattr__(self, "direction_id", direction_id)
        object.__setattr__(self, "comparison_family_id", comparison_family_id)
        object.__setattr__(self, "operand_roles", roles)
        object.__setattr__(self, "equality_policy_id", equality_policy_id)
        object.__setattr__(
            self,
            "semantics_hash",
            canonical_sha256(
                {
                    "comparison_family_id": comparison_family_id,
                    "direction_id": direction_id,
                    "equality_policy_id": equality_policy_id,
                    "operand_roles": list(roles),
                    "scenario_kind": kind,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressDirectionSemanticsRegistry:
    registry_id: str
    evaluation_context_snapshot_hash: str
    scenario_registry_hash: str
    extended_readiness_snapshot_hash: str
    operand_evidence_registry_hash: str
    operand_schema_snapshot_hash: str
    complete_rule_bundle_hash: str
    venue_id: str
    contract_id: str
    context_as_of_utc: str
    as_of_utc: str
    scenario_kinds: tuple[str, ...]
    semantics: tuple[BTCPerpetualPaperStressDirectionSemantics, ...]
    direction_schema_hash: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    semantics_only: bool = True
    direction_defined: bool = True
    formula_registered: bool = False
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-direction-semantics-v1"
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("registry_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digest_names = (
            "evaluation_context_snapshot_hash",
            "scenario_registry_hash",
            "extended_readiness_snapshot_hash",
            "operand_evidence_registry_hash",
            "operand_schema_snapshot_hash",
            "complete_rule_bundle_hash",
            "direction_schema_hash",
        )
        digests = {name: _digest(getattr(self, name), name) for name in digest_names}
        semantics = tuple(self.semantics)
        if not all(
            isinstance(item, BTCPerpetualPaperStressDirectionSemantics)
            for item in semantics
        ):
            raise ValueError("direction registry requires typed semantics")
        observed = tuple(
            (
                item.scenario_kind,
                item.direction_id,
                item.comparison_family_id,
                item.operand_roles,
                item.equality_policy_id,
            )
            for item in semantics
        )
        if observed != BTC_STRESS_EVALUATION_DIRECTION_SCHEMA:
            raise ValueError("direction semantics must match the closed schema exactly")
        if self.scenario_kinds != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("direction registry requires every closed scenario kind")
        calculated_schema_hash = canonical_sha256(
            {
                "schema_version": self.schema_version,
                "semantics": [
                    {
                        "comparison_family_id": item.comparison_family_id,
                        "direction_id": item.direction_id,
                        "equality_policy_id": item.equality_policy_id,
                        "operand_roles": list(item.operand_roles),
                        "scenario_kind": item.scenario_kind,
                    }
                    for item in semantics
                ],
            }
        )
        if digests["direction_schema_hash"] != calculated_schema_hash:
            raise ValueError("direction_schema_hash does not match the closed schema")
        context_as_of = utc(self.context_as_of_utc, "context_as_of_utc")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(context_as_of) > instant(as_of):
            raise ValueError("direction registry cannot precede evaluation context")
        forbidden = (
            self.formula_registered,
            self.evaluation_allowed,
            self.calculation_allowed,
            self.account_state_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_required is not True
            or self.semantics_only is not True
            or self.direction_defined is not True
            or any(forbidden)
        ):
            raise ValueError("direction registry cannot formulate, evaluate, calculate, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("direction registry authority identities are immutable")
        if self.schema_version != "btc-perpetual-paper-stress-direction-semantics-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "context_as_of_utc", context_as_of)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(self, "semantics", semantics)
        object.__setattr__(
            self,
            "registry_hash",
            canonical_sha256(
                {
                    "as_of_utc": as_of,
                    "complete_rule_bundle_hash": digests["complete_rule_bundle_hash"],
                    "context_as_of_utc": context_as_of,
                    "contract_id": self.contract_id,
                    "direction_schema_hash": calculated_schema_hash,
                    "evaluation_context_snapshot_hash": digests[
                        "evaluation_context_snapshot_hash"
                    ],
                    "extended_readiness_snapshot_hash": digests[
                        "extended_readiness_snapshot_hash"
                    ],
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
