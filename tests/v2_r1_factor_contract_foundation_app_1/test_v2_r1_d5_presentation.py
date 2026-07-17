from types import MappingProxyType

import pytest

from apps.v2_r1_factor_contract_foundation_app_1 import (
    FactorRegistry,
    ForecastTargetRegistry,
    build_v2_r1_read_model,
)

from .fixtures import factor_definition, forecast_target_definition, state_sync_anchor


def test_d5_read_model_is_immutable_read_only_and_authority_safe():
    factors = FactorRegistry().register(factor_definition())
    targets = ForecastTargetRegistry().register(forecast_target_definition())
    read_model = build_v2_r1_read_model(
        factors,
        targets,
        (state_sync_anchor(),),
        as_of_utc="2026-07-17T01:00:30Z",
    )
    payload = read_model.payload

    assert isinstance(payload, MappingProxyType)
    assert payload["factor_count"] == 1
    assert payload["forecast_target_count"] == 1
    assert payload["state_sync_count"] == 1
    assert payload["read_only"] is True
    assert payload["operator_review_required"] is True
    assert payload["deterministic_engine_authority"] is True
    assert payload["registered_evidence_authority"] is True
    assert payload["factor_calculation_allowed"] is False
    assert payload["official_scoring_allowed"] is False
    assert payload["automatic_activation_allowed"] is False
    assert payload["order_path_allowed"] is False
    assert payload["real_execution_allowed"] is False
    with pytest.raises(TypeError):
        payload["factor_count"] = 2


def test_d5_read_model_rejects_duplicate_state_events():
    anchor = state_sync_anchor()
    with pytest.raises(ValueError, match="event ids"):
        build_v2_r1_read_model(
            FactorRegistry().register(factor_definition()),
            ForecastTargetRegistry().register(forecast_target_definition()),
            (anchor, anchor),
            as_of_utc="2026-07-17T01:00:30Z",
        )
