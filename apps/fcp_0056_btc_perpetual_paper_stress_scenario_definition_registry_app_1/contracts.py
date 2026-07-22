from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
    decimal_text,
)
from apps.fcp_0055_btc_perpetual_complete_rule_bundle_coherence_hardening_app_1 import (
    BTCPerpetualCompleteRuleBundleSnapshot,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    LocalEventRights,
    identifier,
    instant,
    utc,
)


BTC_STRESS_SCENARIO_KINDS = (
    "COLLATERAL_DRAWDOWN",
    "FUNDING_SHOCK",
    "LIQUIDATION_DISTANCE",
    "LOSS_STREAK",
    "PRICE_GAP",
    "RESYNC",
    "THIN_BOOK",
    "VENUE_OUTAGE",
)
BTC_STRESS_SEVERITIES = ("LOW", "MEDIUM", "HIGH", "EXTREME")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MAX_HORIZON_SECONDS = 31_536_000


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


@dataclass(frozen=True)
class RegisteredBTCStressScenarioArtifact:
    artifact_id: str
    content_sha256: str
    byte_length: int
    rights: LocalEventRights
    observed_at_utc: str
    registered_at_utc: str
    media_type: str = "application/json"
    market: str = "BTC-PERPETUAL"
    operator_registered: bool = True
    local_only: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(
            self,
            "content_sha256",
            _digest(self.content_sha256, "content_sha256"),
        )
        if (
            isinstance(self.byte_length, bool)
            or not isinstance(self.byte_length, int)
            or self.byte_length <= 0
        ):
            raise ValueError("byte_length must be a positive integer")
        if not isinstance(self.rights, LocalEventRights):
            raise ValueError("artifact requires explicit registered local rights")
        observed = utc(self.observed_at_utc, "observed_at_utc")
        registered = utc(self.registered_at_utc, "registered_at_utc")
        if instant(observed) > instant(registered):
            raise ValueError("artifact observation cannot follow registration")
        if self.media_type != "application/json" or self.market != "BTC-PERPETUAL":
            raise ValueError("artifact media type and market are closed")
        if self.operator_registered is not True or self.local_only is not True:
            raise ValueError("artifact must remain registered and local")
        object.__setattr__(self, "observed_at_utc", observed)
        object.__setattr__(self, "registered_at_utc", registered)


@dataclass(frozen=True)
class BTCStressScenarioParameter:
    parameter_id: str
    value: Decimal
    unit_id: str
    parameter_hash: str = field(init=False)

    def __post_init__(self) -> None:
        parameter_id = identifier(self.parameter_id, "parameter_id")
        value = _exact_decimal(self.value, "value")
        unit_id = identifier(self.unit_id, "unit_id")
        object.__setattr__(self, "parameter_id", parameter_id)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "unit_id", unit_id)
        object.__setattr__(
            self,
            "parameter_hash",
            canonical_sha256(
                {
                    "parameter_id": parameter_id,
                    "unit_id": unit_id,
                    "value": decimal_text(value),
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressScenarioDefinition:
    scenario_id: str
    version_id: str
    artifact_id: str
    complete_rule_bundle_hash: str
    venue_id: str
    contract_id: str
    scenario_kind: str
    severity: str
    horizon_seconds: int
    parameters: tuple[BTCStressScenarioParameter, ...]
    schema_version: str = "btc-perpetual-paper-stress-scenario-definition-v1"
    definition_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "scenario_id",
            "version_id",
            "artifact_id",
            "venue_id",
            "contract_id",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        bundle_hash = _digest(
            self.complete_rule_bundle_hash,
            "complete_rule_bundle_hash",
        )
        scenario_kind = str(self.scenario_kind).strip().upper()
        severity = str(self.severity).strip().upper()
        if scenario_kind not in BTC_STRESS_SCENARIO_KINDS:
            raise ValueError("scenario_kind is not registered")
        if severity not in BTC_STRESS_SEVERITIES:
            raise ValueError("severity is not registered")
        if (
            isinstance(self.horizon_seconds, bool)
            or not isinstance(self.horizon_seconds, int)
            or not 0 < self.horizon_seconds <= _MAX_HORIZON_SECONDS
        ):
            raise ValueError("horizon_seconds is outside its registered range")
        parameters = tuple(self.parameters)
        if not parameters or not all(
            isinstance(item, BTCStressScenarioParameter) for item in parameters
        ):
            raise ValueError("scenario requires typed parameters")
        parameter_ids = tuple(item.parameter_id for item in parameters)
        if parameter_ids != tuple(sorted(parameter_ids)) or len(parameter_ids) != len(
            set(parameter_ids)
        ):
            raise ValueError("scenario parameters must be ordered and unique")
        if self.schema_version != "btc-perpetual-paper-stress-scenario-definition-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "complete_rule_bundle_hash", bundle_hash)
        object.__setattr__(self, "scenario_kind", scenario_kind)
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "parameters", parameters)
        object.__setattr__(
            self,
            "definition_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact_id,
                    "complete_rule_bundle_hash": bundle_hash,
                    "contract_id": self.contract_id,
                    "horizon_seconds": self.horizon_seconds,
                    "parameter_hashes": [item.parameter_hash for item in parameters],
                    "scenario_id": self.scenario_id,
                    "scenario_kind": scenario_kind,
                    "schema_version": self.schema_version,
                    "severity": severity,
                    "venue_id": self.venue_id,
                    "version_id": self.version_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperStressScenarioRegistry:
    registry_id: str
    artifact: RegisteredBTCStressScenarioArtifact
    complete_rule_bundle: BTCPerpetualCompleteRuleBundleSnapshot
    definitions: tuple[BTCPerpetualPaperStressScenarioDefinition, ...]
    as_of_utc: str
    operator_review_required: bool = True
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    definition_only: bool = True
    source_selected: bool = False
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
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        registry_id = identifier(self.registry_id, "registry_id")
        if not isinstance(self.artifact, RegisteredBTCStressScenarioArtifact):
            raise ValueError("registry requires a typed stress scenario artifact")
        if not isinstance(
            self.complete_rule_bundle,
            BTCPerpetualCompleteRuleBundleSnapshot,
        ):
            raise ValueError("registry requires a typed FCP-0055 complete bundle")
        definitions = tuple(self.definitions)
        if not definitions or not all(
            isinstance(item, BTCPerpetualPaperStressScenarioDefinition)
            for item in definitions
        ):
            raise ValueError("registry requires typed stress scenario definitions")
        keys = tuple((item.scenario_kind, item.scenario_id) for item in definitions)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("stress scenarios must be ordered and unique")
        if len({item.scenario_id for item in definitions}) != len(definitions) or len(
            {item.version_id for item in definitions}
        ) != len(definitions):
            raise ValueError("scenario and version identities must be unique")
        if any(item.artifact_id != self.artifact.artifact_id for item in definitions):
            raise ValueError("stress scenario artifact lineage mismatch")
        if any(
            item.complete_rule_bundle_hash
            != self.complete_rule_bundle.snapshot_hash
            for item in definitions
        ):
            raise ValueError("FCP-0055 complete bundle lineage mismatch")
        if any(
            item.venue_id != self.complete_rule_bundle.venue_id
            or item.contract_id != self.complete_rule_bundle.contract_id
            for item in definitions
        ):
            raise ValueError("stress scenario contract lineage mismatch")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(self.artifact.registered_at_utc) > instant(as_of):
            raise ValueError("registry cannot use evidence after as_of_utc")
        if instant(self.complete_rule_bundle.effective_at_utc) > instant(as_of):
            raise ValueError("complete bundle cannot be newer than stress registry")
        forbidden = (
            self.source_selected,
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
            or self.definition_only is not True
            or any(forbidden)
        ):
            raise ValueError("registry can only define reviewed local Paper stress evidence")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("registry authority identities are immutable")
        object.__setattr__(self, "registry_id", registry_id)
        object.__setattr__(self, "definitions", definitions)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "registry_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact.artifact_id,
                    "artifact_sha256": self.artifact.content_sha256,
                    "as_of_utc": as_of,
                    "complete_rule_bundle_hash": self.complete_rule_bundle.snapshot_hash,
                    "definition_hashes": [item.definition_hash for item in definitions],
                    "registry_id": registry_id,
                }
            ),
        )
