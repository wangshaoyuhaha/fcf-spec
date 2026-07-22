from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
    decimal_text,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.fcp_0063_btc_perpetual_paper_stress_evaluation_operand_schema_registry_app_1 import (
    BTC_STRESS_EVALUATION_OPERAND_MODES,
    BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    LocalEventRights,
    identifier,
    instant,
    utc,
)


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
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


def _validate_value_domain(metric_id: str, unit_id: str, value: Decimal) -> None:
    if metric_id == "funding-reference-rate":
        return
    if metric_id == "liquidation-distance-reference-rate":
        if not Decimal("0") <= value <= Decimal("1"):
            raise ValueError("liquidation distance must be between zero and one")
        return
    if metric_id == "collateral-index-reference-level":
        if value <= 0:
            raise ValueError("collateral index operand must be positive")
        return
    if unit_id in {"count", "seconds"}:
        if value < 0 or value != value.to_integral_value():
            raise ValueError("count and seconds operands must be nonnegative integers")
        return
    if unit_id in {"quote-per-base", "quote-notional"} and value <= 0:
        raise ValueError("price and depth operands must be positive")
    if value < 0:
        raise ValueError("stress evaluation operand cannot be negative")


@dataclass(frozen=True)
class BTCPerpetualPaperStressEvaluationOperandEvidenceObservation:
    observation_id: str
    scenario_kind: str
    mode_id: str
    role_id: str
    metric_id: str
    value: Decimal
    unit_id: str
    venue_id: str
    contract_id: str
    source_artifact_id: str
    source_content_sha256: str
    event_at_utc: str
    available_at_utc: str
    rights: LocalEventRights
    operator_registered: bool = True
    local_only: bool = True
    schema_version: str = "btc-perpetual-paper-stress-evaluation-operand-evidence-v1"
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "observation_id",
            "role_id",
            "metric_id",
            "unit_id",
            "venue_id",
            "contract_id",
            "source_artifact_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        kind = str(self.scenario_kind).strip().upper()
        mode = str(self.mode_id).strip().upper()
        if kind not in BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("scenario_kind is not registered")
        if mode not in BTC_STRESS_EVALUATION_OPERAND_MODES:
            raise ValueError("mode_id is not registered")
        allowed_roles = (
            {"baseline", "current"}
            if mode == "PAIRED_BASELINE_CURRENT"
            else {"observed"}
        )
        if self.role_id not in allowed_roles:
            raise ValueError("role_id is incompatible with mode_id")
        value = _exact_decimal(self.value, "value")
        _validate_value_domain(self.metric_id, self.unit_id, value)
        event_at = utc(self.event_at_utc, "event_at_utc")
        available_at = utc(self.available_at_utc, "available_at_utc")
        if instant(event_at) > instant(available_at):
            raise ValueError("operand event cannot follow availability")
        if not isinstance(self.rights, LocalEventRights):
            raise ValueError("operand evidence requires explicit registered local rights")
        if self.operator_registered is not True or self.local_only is not True:
            raise ValueError("operand evidence must remain Operator-registered and local")
        if self.schema_version != (
            "btc-perpetual-paper-stress-evaluation-operand-evidence-v1"
        ):
            raise ValueError("schema_version is not registered")
        digest = _digest(self.source_content_sha256, "source_content_sha256")
        object.__setattr__(self, "scenario_kind", kind)
        object.__setattr__(self, "mode_id", mode)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "source_content_sha256", digest)
        object.__setattr__(self, "event_at_utc", event_at)
        object.__setattr__(self, "available_at_utc", available_at)
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "available_at_utc": available_at,
                    "contract_id": self.contract_id,
                    "event_at_utc": event_at,
                    "metric_id": self.metric_id,
                    "mode_id": mode,
                    "observation_id": self.observation_id,
                    "rights": {
                        "license_id": self.rights.license_id,
                        "permitted_use": self.rights.permitted_use,
                        "retention_days": self.rights.retention_days,
                    },
                    "role_id": self.role_id,
                    "scenario_kind": kind,
                    "schema_version": self.schema_version,
                    "source_artifact_id": self.source_artifact_id,
                    "source_content_sha256": digest,
                    "unit_id": self.unit_id,
                    "value": decimal_text(value),
                    "venue_id": self.venue_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry:
    registry_id: str
    operand_schema_snapshot: BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot
    observations: tuple[
        BTCPerpetualPaperStressEvaluationOperandEvidenceObservation, ...
    ]
    as_of_utc: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    registration_only: bool = True
    direction_defined: bool = False
    evaluation_allowed: bool = False
    calculation_allowed: bool = False
    account_state_allowed: bool = False
    balance_calculation_allowed: bool = False
    position_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    liquidation_action_allowed: bool = False
    insurance_fund_mutation_allowed: bool = False
    adl_action_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    schema_version: str = (
        "btc-perpetual-paper-stress-evaluation-operand-evidence-registry-v1"
    )
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        registry_id = identifier(self.registry_id, "registry_id")
        if not isinstance(
            self.operand_schema_snapshot,
            BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot,
        ):
            raise ValueError("registry requires a typed FCP-0063 operand schema snapshot")
        observations = tuple(self.observations)
        if not observations or not all(
            isinstance(
                item,
                BTCPerpetualPaperStressEvaluationOperandEvidenceObservation,
            )
            for item in observations
        ):
            raise ValueError("registry requires typed operand evidence observations")
        expected = tuple(
            (
                item.scenario_kind,
                item.mode_id,
                item.role_id,
                item.metric_id,
                item.unit_id,
            )
            for item in self.operand_schema_snapshot.requirements
        )
        observed = tuple(
            (
                item.scenario_kind,
                item.mode_id,
                item.role_id,
                item.metric_id,
                item.unit_id,
            )
            for item in observations
        )
        if observed != expected:
            raise ValueError("operand evidence must match the FCP-0063 schema exactly")
        if len({item.observation_id for item in observations}) != len(observations):
            raise ValueError("operand evidence observation identities must be unique")
        if any(
            item.venue_id != self.operand_schema_snapshot.venue_id
            or item.contract_id != self.operand_schema_snapshot.contract_id
            for item in observations
        ):
            raise ValueError("operand evidence contract lineage mismatch")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(self.operand_schema_snapshot.as_of_utc) > instant(as_of):
            raise ValueError("operand schema snapshot cannot be newer than registry")
        if any(instant(item.available_at_utc) > instant(as_of) for item in observations):
            raise ValueError("operand evidence registry cannot read future availability")
        by_kind = {
            kind: tuple(item for item in observations if item.scenario_kind == kind)
            for kind in BTC_STRESS_SCENARIO_KINDS
        }
        for items in by_kind.values():
            if items[0].mode_id == "PAIRED_BASELINE_CURRENT" and not (
                instant(items[0].event_at_utc) < instant(items[1].event_at_utc)
            ):
                raise ValueError("paired baseline event must precede current event")
        forbidden = (
            self.direction_defined,
            self.evaluation_allowed,
            self.calculation_allowed,
            self.account_state_allowed,
            self.balance_calculation_allowed,
            self.position_calculation_allowed,
            self.pnl_calculation_allowed,
            self.liquidation_action_allowed,
            self.insurance_fund_mutation_allowed,
            self.adl_action_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_required is not True
            or self.registration_only is not True
            or any(forbidden)
        ):
            raise ValueError("registry can only register reviewed local Paper operands")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("registry authority identities are immutable")
        if self.schema_version != (
            "btc-perpetual-paper-stress-evaluation-operand-evidence-registry-v1"
        ):
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "registry_id", registry_id)
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "registry_hash",
            canonical_sha256(
                {
                    "as_of_utc": as_of,
                    "observation_hashes": [
                        item.observation_hash for item in observations
                    ],
                    "operand_schema_snapshot_hash": (
                        self.operand_schema_snapshot.snapshot_hash
                    ),
                    "registry_id": registry_id,
                    "schema_version": self.schema_version,
                }
            ),
        )
