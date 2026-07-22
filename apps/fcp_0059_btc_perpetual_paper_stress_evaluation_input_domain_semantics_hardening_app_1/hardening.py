from __future__ import annotations

from decimal import Decimal

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0058_btc_perpetual_paper_stress_evaluation_input_evidence_registry_app_1 import (
    BTCPerpetualPaperStressEvaluationInputRegistry,
)

from .contracts import (
    BTC_STRESS_EVALUATION_INPUT_DOMAIN_SCHEMA,
    BTCPerpetualPaperStressEvaluationInputDomainSnapshot,
)


def _validate_value(value: Decimal, domain_id: str) -> None:
    if domain_id == "signed-finite-decimal":
        return
    if domain_id == "positive-decimal":
        if value <= 0:
            raise ValueError("positive stress input domain rejected the value")
        return
    if domain_id == "bounded-ratio-zero-one":
        if not Decimal("0") <= value <= Decimal("1"):
            raise ValueError("bounded stress input domain rejected the value")
        return
    if domain_id == "nonnegative-integer":
        if value < 0 or value != value.to_integral_value():
            raise ValueError("integral stress input domain rejected the value")
        return
    raise ValueError("stress input domain is not registered")


def build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
    registry: BTCPerpetualPaperStressEvaluationInputRegistry,
    *,
    hardening_id: str = "btc-paper-stress-input-domain-hardening-v1",
) -> BTCPerpetualPaperStressEvaluationInputDomainSnapshot:
    if not isinstance(registry, BTCPerpetualPaperStressEvaluationInputRegistry):
        raise TypeError("registry must be typed FCP-0058 evidence")
    domains = {
        kind: (metric_id, domain_id)
        for kind, metric_id, domain_id in BTC_STRESS_EVALUATION_INPUT_DOMAIN_SCHEMA
    }
    for observation in registry.observations:
        metric_id, domain_id = domains[observation.scenario_kind]
        if observation.metric_id != metric_id:
            raise ValueError("stress input domain metric mismatch")
        _validate_value(observation.value, domain_id)
    domain_schema_hash = canonical_sha256(
        {
            "domains": [
                {
                    "domain_id": domain_id,
                    "metric_id": metric_id,
                    "scenario_kind": kind,
                }
                for kind, metric_id, domain_id in (
                    BTC_STRESS_EVALUATION_INPUT_DOMAIN_SCHEMA
                )
            ],
            "schema_version": "btc-perpetual-paper-stress-input-domain-schema-v1",
        }
    )
    coverage = registry.coverage_snapshot
    return BTCPerpetualPaperStressEvaluationInputDomainSnapshot(
        hardening_id=hardening_id,
        input_registry_id=registry.registry_id,
        input_registry_hash=registry.registry_hash,
        coverage_snapshot_hash=coverage.snapshot_hash,
        venue_id=coverage.venue_id,
        contract_id=coverage.contract_id,
        as_of_utc=registry.as_of_utc,
        validated_scenario_kinds=tuple(
            item.scenario_kind for item in registry.observations
        ),
        validated_observation_hashes=tuple(
            item.observation_hash for item in registry.observations
        ),
        domain_schema_hash=domain_schema_hash,
    )
