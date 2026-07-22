from __future__ import annotations

from decimal import Decimal

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTCPerpetualPaperStressScenarioRegistry,
)
from apps.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1 import (
    BTCPerpetualPaperStressCoverageSnapshot,
)

from .contracts import (
    BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA,
    BTCPerpetualPaperStressScenarioParameterDomainSnapshot,
)


def _validate_value(value: Decimal, domain_id: str) -> None:
    if domain_id == "signed-finite-decimal":
        return
    if domain_id == "bounded-ratio-zero-one":
        if not Decimal("0") <= value <= Decimal("1"):
            raise ValueError("bounded stress parameter domain rejected the value")
        return
    if domain_id == "positive-bounded-ratio-zero-one":
        if not Decimal("0") < value <= Decimal("1"):
            raise ValueError("positive bounded stress parameter domain rejected the value")
        return
    if domain_id == "positive-integer":
        if value <= 0 or value != value.to_integral_value():
            raise ValueError("positive integral stress parameter domain rejected the value")
        return
    raise ValueError("stress parameter domain is not registered")


def build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
    registry: BTCPerpetualPaperStressScenarioRegistry,
    coverage_snapshot: BTCPerpetualPaperStressCoverageSnapshot,
    *,
    hardening_id: str = "btc-paper-stress-parameter-domain-hardening-v1",
) -> BTCPerpetualPaperStressScenarioParameterDomainSnapshot:
    if not isinstance(registry, BTCPerpetualPaperStressScenarioRegistry):
        raise TypeError("registry must be typed FCP-0056 evidence")
    if not isinstance(coverage_snapshot, BTCPerpetualPaperStressCoverageSnapshot):
        raise TypeError("coverage_snapshot must be typed FCP-0057 evidence")
    if coverage_snapshot.registry_hash != registry.registry_hash:
        raise ValueError("stress parameter registry lineage mismatch")
    if (
        coverage_snapshot.complete_rule_bundle_hash
        != registry.complete_rule_bundle.snapshot_hash
    ):
        raise ValueError("stress parameter complete-rule lineage mismatch")
    if (
        coverage_snapshot.venue_id != registry.complete_rule_bundle.venue_id
        or coverage_snapshot.contract_id != registry.complete_rule_bundle.contract_id
    ):
        raise ValueError("stress parameter venue or contract lineage mismatch")
    scenario_kinds = tuple(item.scenario_kind for item in registry.definitions)
    definition_hashes = tuple(item.definition_hash for item in registry.definitions)
    if scenario_kinds != coverage_snapshot.covered_scenario_kinds:
        raise ValueError("stress parameter scenario lineage mismatch")
    if definition_hashes != coverage_snapshot.definition_hashes:
        raise ValueError("stress parameter definition lineage mismatch")
    domains = {
        kind: (parameter_id, unit_id, domain_id)
        for kind, parameter_id, unit_id, domain_id in (
            BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA
        )
    }
    for definition in registry.definitions:
        parameter_id, unit_id, domain_id = domains[definition.scenario_kind]
        if len(definition.parameters) != 1:
            raise ValueError("stress parameter domain requires one parameter per kind")
        parameter = definition.parameters[0]
        if (
            parameter.parameter_id != parameter_id
            or parameter.unit_id != unit_id
        ):
            raise ValueError("stress parameter domain schema mismatch")
        _validate_value(parameter.value, domain_id)
    parameter_domain_schema_hash = canonical_sha256(
        {
            "domains": [
                {
                    "domain_id": domain_id,
                    "parameter_id": parameter_id,
                    "scenario_kind": kind,
                    "unit_id": unit_id,
                }
                for kind, parameter_id, unit_id, domain_id in (
                    BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA
                )
            ],
            "schema_version": (
                "btc-perpetual-paper-stress-parameter-domain-schema-v1"
            ),
        }
    )
    return BTCPerpetualPaperStressScenarioParameterDomainSnapshot(
        hardening_id=hardening_id,
        registry_id=registry.registry_id,
        registry_hash=registry.registry_hash,
        coverage_snapshot_hash=coverage_snapshot.snapshot_hash,
        complete_rule_bundle_hash=registry.complete_rule_bundle.snapshot_hash,
        venue_id=registry.complete_rule_bundle.venue_id,
        contract_id=registry.complete_rule_bundle.contract_id,
        as_of_utc=registry.as_of_utc,
        validated_scenario_kinds=scenario_kinds,
        validated_definition_hashes=definition_hashes,
        parameter_schema_hash=coverage_snapshot.parameter_schema_hash,
        parameter_domain_schema_hash=parameter_domain_schema_hash,
    )
