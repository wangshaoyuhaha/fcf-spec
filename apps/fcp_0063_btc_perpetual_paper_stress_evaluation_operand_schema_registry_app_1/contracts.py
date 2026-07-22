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


BTC_STRESS_EVALUATION_OPERAND_MODES = (
    "PAIRED_BASELINE_CURRENT",
    "THRESHOLD_OBSERVATION",
)
BTC_STRESS_EVALUATION_OPERAND_SCHEMA = (
    (
        "COLLATERAL_DRAWDOWN",
        "PAIRED_BASELINE_CURRENT",
        (
            ("baseline", "collateral-index-reference-level", "ratio"),
            ("current", "collateral-index-reference-level", "ratio"),
        ),
    ),
    (
        "FUNDING_SHOCK",
        "PAIRED_BASELINE_CURRENT",
        (
            ("baseline", "funding-reference-rate", "ratio"),
            ("current", "funding-reference-rate", "ratio"),
        ),
    ),
    (
        "LIQUIDATION_DISTANCE",
        "THRESHOLD_OBSERVATION",
        (("observed", "liquidation-distance-reference-rate", "ratio"),),
    ),
    (
        "LOSS_STREAK",
        "THRESHOLD_OBSERVATION",
        (("observed", "consecutive-loss-reference-count", "count"),),
    ),
    (
        "PRICE_GAP",
        "PAIRED_BASELINE_CURRENT",
        (
            ("baseline", "mark-reference-price", "quote-per-base"),
            ("current", "mark-reference-price", "quote-per-base"),
        ),
    ),
    (
        "RESYNC",
        "THRESHOLD_OBSERVATION",
        (("observed", "resync-lag-reference-seconds", "seconds"),),
    ),
    (
        "THIN_BOOK",
        "PAIRED_BASELINE_CURRENT",
        (
            ("baseline", "bid-ask-depth-reference-notional", "quote-notional"),
            ("current", "bid-ask-depth-reference-notional", "quote-notional"),
        ),
    ),
    (
        "VENUE_OUTAGE",
        "THRESHOLD_OBSERVATION",
        (("observed", "heartbeat-age-reference-seconds", "seconds"),),
    ),
)

if tuple(item[0] for item in BTC_STRESS_EVALUATION_OPERAND_SCHEMA) != (
    BTC_STRESS_SCENARIO_KINDS
):
    raise RuntimeError("stress operand schema must match the closed scenario kinds")

_INPUT_SCHEMA = {
    kind: (metric_id, unit_id)
    for kind, metric_id, unit_id in BTC_STRESS_EVALUATION_INPUT_SCHEMA
}
for _kind, _mode, _operands in BTC_STRESS_EVALUATION_OPERAND_SCHEMA:
    _roles = tuple(item[0] for item in _operands)
    if _mode == "PAIRED_BASELINE_CURRENT" and _roles != ("baseline", "current"):
        raise RuntimeError("paired stress operands must be baseline then current")
    if _mode == "THRESHOLD_OBSERVATION" and _roles != ("observed",):
        raise RuntimeError("threshold stress operands must contain one observation")
    if any((metric_id, unit_id) != _INPUT_SCHEMA[_kind] for _, metric_id, unit_id in _operands):
        raise RuntimeError("stress operand metrics must match FCP-0058 input schema")


def _digest(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


@dataclass(frozen=True)
class BTCPerpetualPaperStressEvaluationOperandRequirement:
    scenario_kind: str
    mode_id: str
    role_id: str
    metric_id: str
    unit_id: str
    requirement_hash: str = field(init=False)

    def __post_init__(self) -> None:
        kind = str(self.scenario_kind).strip().upper()
        mode = str(self.mode_id).strip().upper()
        if kind not in BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("scenario_kind is not registered")
        if mode not in BTC_STRESS_EVALUATION_OPERAND_MODES:
            raise ValueError("mode_id is not registered")
        role_id = identifier(self.role_id, "role_id")
        metric_id = identifier(self.metric_id, "metric_id")
        unit_id = identifier(self.unit_id, "unit_id")
        object.__setattr__(self, "scenario_kind", kind)
        object.__setattr__(self, "mode_id", mode)
        object.__setattr__(self, "role_id", role_id)
        object.__setattr__(self, "metric_id", metric_id)
        object.__setattr__(self, "unit_id", unit_id)
        object.__setattr__(
            self,
            "requirement_hash",
            canonical_sha256(
                {
                    "metric_id": metric_id,
                    "mode_id": mode,
                    "role_id": role_id,
                    "scenario_kind": kind,
                    "unit_id": unit_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot:
    registry_id: str
    extended_readiness_snapshot_hash: str
    readiness_snapshot_hash: str
    parameter_domain_snapshot_hash: str
    coverage_snapshot_hash: str
    complete_rule_bundle_hash: str
    venue_id: str
    contract_id: str
    as_of_utc: str
    scenario_kinds: tuple[str, ...]
    requirements: tuple[BTCPerpetualPaperStressEvaluationOperandRequirement, ...]
    operand_schema_hash: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    schema_only: bool = True
    direction_defined: bool = False
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = "btc-perpetual-paper-stress-evaluation-operand-schema-v1"
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("registry_id", "venue_id", "contract_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        digest_names = (
            "extended_readiness_snapshot_hash",
            "readiness_snapshot_hash",
            "parameter_domain_snapshot_hash",
            "coverage_snapshot_hash",
            "complete_rule_bundle_hash",
            "operand_schema_hash",
        )
        digests = {name: _digest(getattr(self, name), name) for name in digest_names}
        requirements = tuple(self.requirements)
        if not all(
            isinstance(item, BTCPerpetualPaperStressEvaluationOperandRequirement)
            for item in requirements
        ):
            raise ValueError("operand schema requires typed requirements")
        expected = tuple(
            (kind, mode, role_id, metric_id, unit_id)
            for kind, mode, operands in BTC_STRESS_EVALUATION_OPERAND_SCHEMA
            for role_id, metric_id, unit_id in operands
        )
        observed = tuple(
            (item.scenario_kind, item.mode_id, item.role_id, item.metric_id, item.unit_id)
            for item in requirements
        )
        if observed != expected:
            raise ValueError("operand requirements must match the closed schema exactly")
        if self.scenario_kinds != BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("operand schema requires every closed scenario kind")
        calculated_schema_hash = canonical_sha256(
            {
                "requirements": [
                    {
                        "metric_id": item.metric_id,
                        "mode_id": item.mode_id,
                        "role_id": item.role_id,
                        "scenario_kind": item.scenario_kind,
                        "unit_id": item.unit_id,
                    }
                    for item in requirements
                ],
                "schema_version": self.schema_version,
            }
        )
        if digests["operand_schema_hash"] != calculated_schema_hash:
            raise ValueError("operand_schema_hash does not match the closed schema")
        forbidden = (
            self.direction_defined,
            self.evaluation_allowed,
            self.calculation_allowed,
            self.account_state_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if self.operator_review_required is not True or self.schema_only is not True or any(forbidden):
            raise ValueError("operand schema cannot direct, evaluate, calculate, execute, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("operand schema authority identities are immutable")
        if self.schema_version != "btc-perpetual-paper-stress-evaluation-operand-schema-v1":
            raise ValueError("schema_version is not registered")
        as_of = utc(self.as_of_utc, "as_of_utc")
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(self, "requirements", requirements)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "as_of_utc": as_of,
                    "complete_rule_bundle_hash": digests["complete_rule_bundle_hash"],
                    "contract_id": self.contract_id,
                    "coverage_snapshot_hash": digests["coverage_snapshot_hash"],
                    "extended_readiness_snapshot_hash": digests[
                        "extended_readiness_snapshot_hash"
                    ],
                    "operand_schema_hash": calculated_schema_hash,
                    "parameter_domain_snapshot_hash": digests[
                        "parameter_domain_snapshot_hash"
                    ],
                    "readiness_snapshot_hash": digests["readiness_snapshot_hash"],
                    "registry_id": self.registry_id,
                    "requirement_hashes": [item.requirement_hash for item in requirements],
                    "scenario_kinds": list(self.scenario_kinds),
                    "schema_version": self.schema_version,
                    "venue_id": self.venue_id,
                }
            ),
        )
