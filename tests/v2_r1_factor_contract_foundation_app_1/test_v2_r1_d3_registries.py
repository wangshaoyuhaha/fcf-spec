from dataclasses import replace

import pytest

from apps.v2_r1_factor_contract_foundation_app_1 import (
    FactorLifecycle,
    FactorLifecycleEvent,
    FactorRegistry,
    ForecastTargetRegistry,
    ValidationStatus,
)

from .fixtures import factor_definition, forecast_target_definition


def _event(
    event_id: str,
    from_state: FactorLifecycle,
    to_state: FactorLifecycle,
    *,
    replacement_factor_id: str | None = None,
) -> FactorLifecycleEvent:
    return FactorLifecycleEvent(
        event_id=event_id,
        factor_id="factor.ma20.distance",
        from_state=from_state,
        to_state=to_state,
        occurred_at_utc="2026-07-17T02:00:00Z",
        operator_id="operator.fixture",
        evidence_refs=("evidence.lifecycle.fixture",),
        replacement_factor_id=replacement_factor_id,
    )


def test_d3_registries_are_append_only_and_reject_duplicates():
    empty_factors = FactorRegistry()
    factors = empty_factors.register(factor_definition())
    empty_targets = ForecastTargetRegistry()
    targets = empty_targets.register(forecast_target_definition())

    assert not empty_factors.definitions
    assert tuple(factors.definitions) == ("factor.ma20.distance",)
    assert not empty_targets.definitions
    assert tuple(targets.definitions) == ("target.return.1d",)
    with pytest.raises(ValueError, match="already registered"):
        factors.register(factor_definition())
    with pytest.raises(ValueError, match="already registered"):
        targets.register(forecast_target_definition())


def test_d3_dependencies_must_exist_before_registration():
    dependent = factor_definition(
        "factor.composite.fixture", dependencies=("factor.missing",)
    )

    with pytest.raises(ValueError, match="dependency"):
        FactorRegistry().register(dependent)


def test_d3_lifecycle_requires_operator_evidence_and_allowed_sequence():
    registry = FactorRegistry().register(factor_definition())
    research = _event(
        "event.lifecycle.001", FactorLifecycle.DRAFT, FactorLifecycle.RESEARCH
    )
    challenger = _event(
        "event.lifecycle.002",
        FactorLifecycle.RESEARCH,
        FactorLifecycle.CHALLENGER,
    )
    qualified = _event(
        "event.lifecycle.003",
        FactorLifecycle.CHALLENGER,
        FactorLifecycle.QUALIFIED,
    )
    champion = _event(
        "event.lifecycle.004",
        FactorLifecycle.QUALIFIED,
        FactorLifecycle.CHAMPION,
    )

    registry = registry.transition(research).transition(challenger)
    registry = registry.transition(qualified).transition(champion)

    assert (
        registry.current_lifecycle("factor.ma20.distance")
        is FactorLifecycle.CHAMPION
    )
    assert (
        registry.effective_definition("factor.ma20.distance").lifecycle
        is FactorLifecycle.CHAMPION
    )
    assert len(registry.lifecycle_events) == 4
    with pytest.raises(ValueError, match="start at current"):
        registry.transition(
            _event(
                "event.lifecycle.wrong-start",
                FactorLifecycle.DRAFT,
                FactorLifecycle.RESEARCH,
            )
        )


def test_d3_qualification_fails_closed_without_validation_and_approval():
    unvalidated = replace(
        factor_definition(),
        validation_status=ValidationStatus.RESEARCH_REQUIRED,
        approved_by="NONE",
    )
    registry = FactorRegistry().register(unvalidated)
    registry = registry.transition(
        _event(
            "event.lifecycle.unvalidated.001",
            FactorLifecycle.DRAFT,
            FactorLifecycle.RESEARCH,
        )
    ).transition(
        _event(
            "event.lifecycle.unvalidated.002",
            FactorLifecycle.RESEARCH,
            FactorLifecycle.CHALLENGER,
        )
    )

    with pytest.raises(ValueError, match="validation and approval"):
        registry.transition(
            _event(
                "event.lifecycle.unvalidated.003",
                FactorLifecycle.CHALLENGER,
                FactorLifecycle.QUALIFIED,
            )
        )
    with pytest.raises(ValueError, match="not allowed"):
        FactorRegistry().register(factor_definition()).transition(
            _event(
                "event.lifecycle.invalid",
                FactorLifecycle.DRAFT,
                FactorLifecycle.CHAMPION,
            )
        )
