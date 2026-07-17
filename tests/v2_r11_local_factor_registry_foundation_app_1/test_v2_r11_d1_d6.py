from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r11_local_factor_registry_foundation_app_1 import (
    V2_R11_LOCAL_FACTOR_REGISTRY_BOUNDARY,
    FactorDefinition,
    FactorRegistryLedger,
    FactorRegistryPolicy,
    V2R11FactorRegistryBoundary,
    build_factor_registry,
    build_operator_acceptance,
    build_read_model,
)


def _definition(**changes: object) -> FactorDefinition:
    data: dict[str, object] = dict(
        factor_id="registered-close-ma",
        version="v1",
        family="TECHNICAL",
        lifecycle="RESEARCH",
        source_type="DETERMINISTIC_CODE",
        calculation_spec_hash="a" * 64,
        output_unit="price",
        asset_scopes=("btc", "equity"),
        input_field_ids=("close",),
        minimum_lookback=5,
        maximum_lookback=200,
    )
    data.update(changes)
    return FactorDefinition(**data)  # type: ignore[arg-type]


def _policy(**changes: object) -> FactorRegistryPolicy:
    data: dict[str, object] = dict(
        registry_id="registered-factor-registry",
        registry_version="v1",
    )
    data.update(changes)
    return FactorRegistryPolicy(**data)  # type: ignore[arg-type]


def _build(
    definitions: tuple[FactorDefinition, ...] | None = None,
    policy: FactorRegistryPolicy | None = None,
):
    return build_factor_registry(
        definitions or (_definition(),),
        policy or _policy(),
        as_of_utc="2026-01-05T01:06:00Z",
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert V2_R11_LOCAL_FACTOR_REGISTRY_BOUNDARY.factor_activation_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R11FactorRegistryBoundary(factor_calculation_allowed=True)
    with pytest.raises(FrozenInstanceError):
        V2_R11_LOCAL_FACTOR_REGISTRY_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_definition_is_immutable_and_normalized() -> None:
    definition = _definition(family="technical", lifecycle="research")
    assert definition.natural_key == "registered-close-ma@v1"
    assert definition.family == "TECHNICAL"
    with pytest.raises(FrozenInstanceError):
        definition.family = "VOLUME"  # type: ignore[misc]


def test_d2_contract_rejects_activation_and_invalid_bounds() -> None:
    with pytest.raises(ValueError, match="registry-only"):
        _definition(scoring_allowed=True)
    with pytest.raises(ValueError, match="lookback"):
        _definition(minimum_lookback=20, maximum_lookback=5)


def test_d3_registry_snapshot_is_deterministic_and_sorted() -> None:
    first = _definition()
    second = _definition(
        factor_id="registered-volume-ratio",
        family="VOLUME",
        calculation_spec_hash="b" * 64,
        output_unit="ratio",
        input_field_ids=("volume",),
    )
    evidence = _build((second, first))
    assert evidence.state == "REGISTRY_READY"
    assert evidence.definition_keys == (
        "registered-close-ma@v1",
        "registered-volume-ratio@v1",
    )
    assert evidence.evidence_hash == _build((first, second)).evidence_hash
    assert isinstance(evidence.definition_hashes, MappingProxyType)


def test_d3_definition_hash_changes_with_registered_metadata() -> None:
    baseline = _build()
    changed = _build((_definition(maximum_lookback=250),))
    assert baseline.definition_hashes != changed.definition_hashes
    assert baseline.evidence_hash != changed.evidence_hash


def test_d4_duplicate_natural_key_is_blocked() -> None:
    evidence = _build((_definition(), _definition()))
    assert evidence.state == "BLOCKED"
    assert evidence.reason_codes == ("DUPLICATE_FACTOR_NATURAL_KEY",)


def test_d4_unregistered_dependency_is_blocked() -> None:
    evidence = _build(
        (_definition(dependency_factor_refs=("registered-missing@v1",)),)
    )
    assert evidence.reason_codes == ("UNREGISTERED_DEPENDENCY_BLOCKED",)


def test_d4_dependency_cycle_is_blocked() -> None:
    first = _definition(
        factor_id="registered-a",
        dependency_factor_refs=("registered-b@v1",),
    )
    second = _definition(
        factor_id="registered-b",
        calculation_spec_hash="b" * 64,
        dependency_factor_refs=("registered-a@v1",),
    )
    evidence = _build((first, second))
    assert evidence.reason_codes == ("DEPENDENCY_CYCLE_BLOCKED",)


def test_d4_policy_family_and_capacity_are_fail_closed() -> None:
    family = _build(policy=_policy(allowed_families=("VOLUME",)))
    capacity = _build(
        (_definition(), _definition(factor_id="registered-second")),
        _policy(maximum_definitions=1),
    )
    assert family.reason_codes == ("FACTOR_FAMILY_NOT_ALLOWED",)
    assert capacity.reason_codes == ("REGISTRY_CAPACITY_BLOCKED",)


def test_d5_ledger_rejects_hash_and_natural_key_duplicates() -> None:
    evidence = _build()
    ledger = FactorRegistryLedger().append(evidence)
    with pytest.raises(ValueError, match="hash"):
        ledger.append(evidence)
    with pytest.raises(ValueError, match="natural key"):
        ledger.append(replace(evidence, evidence_hash="d" * 64))


def test_d5_ledger_capacity_is_bounded() -> None:
    with pytest.raises(ValueError, match="capacity"):
        FactorRegistryLedger(capacity=0)


def test_d6_read_model_and_acceptance_remain_non_activating() -> None:
    evidence = _build()
    model = build_read_model(FactorRegistryLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["factor_calculation_activated"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.factor_activation_allowed is False
