from types import MappingProxyType

from apps.v2_r1_factor_contract_foundation_app_1 import (
    FactorRegistry,
    ForecastTargetRegistry,
    build_v2_r1_operator_acceptance,
)

from .fixtures import factor_definition, forecast_target_definition, state_sync_anchor


def test_d6_acceptance_is_ready_for_review_but_never_auto_approved():
    acceptance = build_v2_r1_operator_acceptance(
        FactorRegistry().register(factor_definition()),
        ForecastTargetRegistry().register(forecast_target_definition()),
        (state_sync_anchor(),),
    )
    payload = acceptance.to_payload()

    assert acceptance.status == "READY_FOR_OPERATOR_REVIEW"
    assert acceptance.operator_review_required is True
    assert acceptance.automatic_approval_allowed is False
    assert isinstance(payload, MappingProxyType)
    assert payload["factor_calculation_allowed"] is False
    assert payload["official_scoring_allowed"] is False
    assert payload["automatic_activation_allowed"] is False
    assert payload["order_path_allowed"] is False
    assert payload["real_execution_allowed"] is False


def test_d6_acceptance_fails_closed_when_required_contracts_are_missing():
    acceptance = build_v2_r1_operator_acceptance(
        FactorRegistry(),
        ForecastTargetRegistry(),
        (),
        unresolved_items=("registered-fixture-required",),
    )

    assert acceptance.status == "BLOCKED"
    assert acceptance.unresolved_items == ("registered-fixture-required",)
